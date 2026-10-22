document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("directionsForm");
    const mapElement = document.getElementById("directionsMap");
    const originInput = document.getElementById("origin");
    const destinationInput = document.getElementById("destination");
    const locateButton = document.getElementById("useMyLocation");
    const status = document.getElementById("directionsStatus");
    const summary = document.getElementById("routeSummary");
    const distanceElement = document.getElementById("routeDistance");
    const stepsElement = document.getElementById("routeSteps");

    if (!form || !mapElement || !originInput || !destinationInput || !window.L) {
        if (status) {
            status.textContent = "The map could not be loaded. Please try again later.";
        }
        return;
    }

    const destination = [
        Number.parseFloat(form.dataset.destinationLat),
        Number.parseFloat(form.dataset.destinationLon),
    ];
    if (!destination.every(Number.isFinite)) {
        status.textContent = "This trader's map location is not available.";
        return;
    }

    const map = L.map(mapElement).setView(destination, 14);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);
    const destinationPopup = document.createElement("span");
    destinationPopup.textContent = destinationInput.value;
    const destinationMarker = L.marker(destination).addTo(map)
        .bindPopup(destinationPopup);
    let originMarker = null;
    let routeLine = null;
    let deviceOrigin = null;

    const geocode = async (place) => {
        const url = new URL("https://nominatim.openstreetmap.org/search");
        url.searchParams.set("format", "jsonv2");
        url.searchParams.set("limit", "1");
        url.searchParams.set("countrycodes", "zm");
        url.searchParams.set("q", `${place}, Zambia`);
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error("Location search is temporarily unavailable.");
        }
        const results = await response.json();
        if (!results.length) {
            throw new Error(`Could not find “${place}”. Try a nearby town or area.`);
        }
        return [Number.parseFloat(results[0].lat), Number.parseFloat(results[0].lon)];
    };

    const formatStep = (step) => {
        const maneuver = step.maneuver || {};
        const action = [maneuver.type, maneuver.modifier].filter(Boolean).join(" ");
        const road = step.name ? ` onto ${step.name}` : "";
        return `${action || "Continue"}${road}`;
    };

    locateButton.addEventListener("click", () => {
        if (!navigator.geolocation) {
            status.textContent = "This browser does not support device location. Enter your starting area instead.";
            return;
        }
        status.textContent = "Requesting permission to use your current location…";
        navigator.geolocation.getCurrentPosition(
            (position) => {
                deviceOrigin = [position.coords.latitude, position.coords.longitude];
                originInput.value = "Current device location";
                status.textContent = "Current location ready. Select Show route when you are ready.";
            },
            () => {
                deviceOrigin = null;
                status.textContent = "Could not get your location. Allow location access or enter your starting area.";
            },
            { enableHighAccuracy: true, timeout: 10000 },
        );
    });
    originInput.addEventListener("input", () => {
        deviceOrigin = null;
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const originText = originInput.value.trim();
        const destinationText = destinationInput.value.trim();
        if (!originText || !destinationText) {
            status.textContent = "Enter both your current location and destination.";
            return;
        }

        status.textContent = "Finding the route…";
        summary.hidden = true;
        try {
            const origin = deviceOrigin || await geocode(originText);
            const destinationLabel = destinationInput.dataset.pinnedLabel;
            const routeDestination = destinationText === destinationLabel
                ? destination
                : await geocode(destinationText);
            const coordinates = `${origin[1]},${origin[0]};${routeDestination[1]},${routeDestination[0]}`;
            const routeUrl = new URL(
                `https://router.project-osrm.org/route/v1/driving/${coordinates}`,
            );
            routeUrl.searchParams.set("overview", "full");
            routeUrl.searchParams.set("geometries", "geojson");
            routeUrl.searchParams.set("steps", "true");
            const response = await fetch(routeUrl);
            if (!response.ok) {
                throw new Error("The public routing service is temporarily unavailable.");
            }
            const routeData = await response.json();
            if (routeData.code !== "Ok" || !routeData.routes.length) {
                throw new Error("No driving route was found between those locations.");
            }

            const route = routeData.routes[0];
            if (routeLine) {
                map.removeLayer(routeLine);
            }
            if (originMarker) {
                map.removeLayer(originMarker);
            }
            const originPopup = document.createElement("span");
            originPopup.textContent = "Your starting point";
            originMarker = L.marker(origin).addTo(map).bindPopup(originPopup);
            destinationMarker.setLatLng(routeDestination);
            routeLine = L.geoJSON(route.geometry, {
                style: { color: "#3278e5", weight: 6, opacity: 0.85 },
            }).addTo(map);
            map.fitBounds(routeLine.getBounds(), { padding: [25, 25] });

            const distanceKm = (route.distance / 1000).toFixed(1);
            const durationMinutes = Math.round(route.duration / 60);
            distanceElement.textContent =
                `${distanceKm} km · about ${durationMinutes} minutes by road`;
            stepsElement.replaceChildren();
            const legs = route.legs || [];
            for (const step of legs.flatMap((leg) => leg.steps || [])) {
                const item = document.createElement("li");
                item.textContent = formatStep(step);
                stepsElement.append(item);
            }
            summary.hidden = false;
            status.textContent = "Route found. Check local road conditions before travelling.";
        } catch (error) {
            status.textContent = error instanceof Error
                ? error.message
                : "Could not get directions. Please try again.";
        }
    });
});
