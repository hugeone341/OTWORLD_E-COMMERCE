document.addEventListener("DOMContentLoaded", () => {
    const mapElement = document.getElementById("homeMap");
    const status = document.getElementById("homeMapStatus");
    const placeForm = document.getElementById("mapPlaceSearch");
    const placeInput = document.getElementById("mapPlaceQuery");
    const originInput = document.getElementById("mapOrigin");
    const destinationInput = document.getElementById("mapDestination");
    const locateButton = document.getElementById("mapUseMyLocation");
    const routeButton = document.getElementById("mapShowRoute");
    const summary = document.getElementById("homeRouteSummary");
    const locationsData = document.getElementById("verified-trader-map-locations");

    if (
        !mapElement || !status || !placeForm || !placeInput || !originInput
        || !destinationInput || !locateButton || !routeButton || !window.L
    ) {
        if (status) {
            status.textContent = "The map could not be loaded. Please try again later.";
        }
        return;
    }

    const map = L.map(mapElement).setView([-13.1339, 27.8493], 6);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);

    let destinationCoordinates = null;
    let originCoordinates = null;
    let destinationMarker = null;
    let originMarker = null;
    let routeLayer = null;
    const traderLocations = locationsData ? JSON.parse(locationsData.textContent) : [];

    const createPopupContent = (label, url) => {
        const content = document.createElement("div");
        const name = document.createElement("p");
        name.textContent = label;
        content.append(name);
        if (url) {
            const directionsLink = document.createElement("a");
            directionsLink.href = url;
            directionsLink.textContent = "Trader details and directions";
            content.append(directionsLink);
        }
        return content;
    };

    const setDestination = (coordinates, label, zoom = 14) => {
        destinationCoordinates = coordinates;
        destinationInput.value = label;
        if (destinationMarker) {
            destinationMarker.setLatLng(coordinates);
        } else {
            destinationMarker = L.marker(coordinates).addTo(map);
        }
        destinationMarker.bindPopup(createPopupContent(label));
        map.setView(coordinates, zoom);
        status.textContent = `Destination selected: ${label}. Enter your starting location to get directions.`;
        summary.hidden = true;
    };

    for (const trader of traderLocations) {
        const coordinates = [trader.latitude, trader.longitude];
        const marker = L.marker(coordinates).addTo(map);
        const traderLabel = trader.address
            ? `${trader.name} - ${trader.address}`
            : trader.name;
        marker.bindPopup(createPopupContent(traderLabel, trader.url));
        marker.on("click", () => {
            setDestination(
                coordinates,
                trader.address ? `${trader.name}, ${trader.address}` : trader.name,
                15,
            );
        });
    }

    destinationInput.addEventListener("input", () => {
        destinationCoordinates = null;
        summary.hidden = true;
    });
    originInput.addEventListener("input", () => {
        originCoordinates = null;
        summary.hidden = true;
    });

    const geocode = async (place) => {
        const url = new URL("https://nominatim.openstreetmap.org/search");
        url.searchParams.set("format", "jsonv2");
        url.searchParams.set("limit", "1");
        url.searchParams.set("countrycodes", "zm");
        url.searchParams.set("q", `${place}, Zambia`);
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error("Place search is temporarily unavailable. Please try again later.");
        }
        const results = await response.json();
        if (!results.length) {
            throw new Error(`Could not find “${place}” in Zambia. Try a nearby town or area.`);
        }
        return [Number.parseFloat(results[0].lat), Number.parseFloat(results[0].lon)];
    };

    placeForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const place = placeInput.value.trim();
        if (!place) {
            status.textContent = "Enter a place to search for.";
            return;
        }
        status.textContent = "Searching for the place…";
        try {
            const coordinates = await geocode(place);
            setDestination(coordinates, place);
        } catch (error) {
            status.textContent = error instanceof Error
                ? error.message
                : "Place search failed. Please try again.";
        }
    });

    map.on("click", (event) => {
        setDestination(
            [event.latlng.lat, event.latlng.lng],
            `Map location (${event.latlng.lat.toFixed(5)}, ${event.latlng.lng.toFixed(5)})`,
        );
    });

    locateButton.addEventListener("click", () => {
        if (!navigator.geolocation) {
            status.textContent = "This browser does not support device location. Enter your starting place instead.";
            return;
        }
        status.textContent = "Requesting permission to use your current location…";
        navigator.geolocation.getCurrentPosition(
            (position) => {
                originCoordinates = [
                    position.coords.latitude,
                    position.coords.longitude,
                ];
                originInput.value = "Current device location";
                status.textContent = "Starting location ready. Select a destination and get directions.";
            },
            () => {
                originCoordinates = null;
                status.textContent = "Could not get your location. Allow access or enter your starting place.";
            },
            { enableHighAccuracy: true, timeout: 10000 },
        );
    });

    routeButton.addEventListener("click", async () => {
        const originText = originInput.value.trim();
        const destinationText = destinationInput.value.trim();
        if (!originText || !destinationText) {
            status.textContent = "Enter your current location and a destination, or select a map pin.";
            return;
        }

        status.textContent = "Finding the driving route…";
        summary.hidden = true;
        try {
            const origin = originCoordinates || await geocode(originText);
            const destination = destinationCoordinates || await geocode(destinationText);
            const coordinates = `${origin[1]},${origin[0]};${destination[1]},${destination[0]}`;
            const routeUrl = new URL(
                `https://router.project-osrm.org/route/v1/driving/${coordinates}`,
            );
            routeUrl.searchParams.set("overview", "full");
            routeUrl.searchParams.set("geometries", "geojson");
            const response = await fetch(routeUrl);
            if (!response.ok) {
                throw new Error("The public routing service is temporarily unavailable.");
            }
            const routeData = await response.json();
            if (routeData.code !== "Ok" || !routeData.routes.length) {
                throw new Error("No driving route was found between those places.");
            }

            const route = routeData.routes[0];
            if (routeLayer) {
                map.removeLayer(routeLayer);
            }
            if (originMarker) {
                map.removeLayer(originMarker);
            }
            if (destinationMarker) {
                map.removeLayer(destinationMarker);
            }
            const startPopup = document.createElement("span");
            startPopup.textContent = "Starting location";
            originMarker = L.marker(origin).addTo(map).bindPopup(startPopup);
            destinationMarker = L.marker(destination).addTo(map)
                .bindPopup(createPopupContent(destinationText));
            routeLayer = L.geoJSON(route.geometry, {
                style: { color: "#3278e5", weight: 6, opacity: 0.85 },
            }).addTo(map);
            map.fitBounds(routeLayer.getBounds(), { padding: [25, 25] });

            summary.textContent =
                `Route: ${(route.distance / 1000).toFixed(1)} km · about ${Math.round(route.duration / 60)} minutes by road.`;
            summary.hidden = false;
            status.textContent = "Route found. Check local road conditions before travelling.";
        } catch (error) {
            status.textContent = error instanceof Error
                ? error.message
                : "Could not get directions. Please try again.";
        }
    });
});
