document.addEventListener("DOMContentLoaded", () => {
    const mapElement = document.getElementById("traderLocationMap");
    const latitudeInput = document.getElementById("id_latitude");
    const longitudeInput = document.getElementById("id_longitude");
    const status = document.getElementById("traderLocationStatus");
    const locateButton = document.getElementById("useBusinessLocation");

    if (!mapElement || !latitudeInput || !longitudeInput || !window.L) {
        if (status) {
            status.textContent = "The map could not be loaded. Please try again later.";
        }
        return;
    }

    const zambiaCenter = [-13.1339, 27.8493];
    const map = L.map(mapElement).setView(zambiaCenter, 6);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);

    let marker = null;
    const setPin = (latitude, longitude) => {
        latitudeInput.value = latitude.toFixed(6);
        longitudeInput.value = longitude.toFixed(6);
        if (marker) {
            marker.setLatLng([latitude, longitude]);
        } else {
            marker = L.marker([latitude, longitude]).addTo(map);
        }
        status.textContent = `Business pin selected: ${latitude.toFixed(5)}, ${longitude.toFixed(5)}.`;
    };

    const existingLatitude = Number.parseFloat(latitudeInput.value);
    const existingLongitude = Number.parseFloat(longitudeInput.value);
    if (Number.isFinite(existingLatitude) && Number.isFinite(existingLongitude)) {
        setPin(existingLatitude, existingLongitude);
        map.setView([existingLatitude, existingLongitude], 15);
    }

    map.on("click", (event) => {
        setPin(event.latlng.lat, event.latlng.lng);
    });

    locateButton.addEventListener("click", () => {
        if (!navigator.geolocation) {
            status.textContent = "This browser does not support device location. Tap the map to place your pin.";
            return;
        }
        status.textContent = "Requesting permission to use this device's location…";
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const { latitude, longitude } = position.coords;
                setPin(latitude, longitude);
                map.setView([latitude, longitude], 16);
            },
            () => {
                status.textContent = "Could not get your location. Allow location access or tap the map to place your pin.";
            },
            { enableHighAccuracy: true, timeout: 10000 },
        );
    });
});
