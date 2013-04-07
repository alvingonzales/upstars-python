

var SkyMap = function(id) {
    self = {};

    self.init = function(id) {
        map_settings = {
            minZoom: 4,
            maxZoom: 6,
            maxBounds: [[45, -45], [-45, 45]],

            // Equirectangular projection
            crs: L.CRS.EPSG4326,
        }

        if (L.Browser.ie) {
            // IE does not properly enforce maxBounds w/ inertia on
            map_settings.inertia = false;
        }

        if (L.Browser.mobileWebkit) {
            // iOS svg image glitches on load with fading on
            map_settings.fadeAnimation = false;
        }

        self.map = L.map(id, map_settings);
        self.map.on("click", self.onclick);

        self.map.setView([0, 0], 2);

        self.layerControl = L.control.layers(
            {},
            {},
            { autoZIndex: false }
        );
        self.layerControl.addTo(self.map);

        self.starLayer = null;
        self.constellationLayer = null;
        self.labelLayer = null;
        self.marker = null;

        d = new Date()

        self.apiParams = {
            year: d.getFullYear(),
            month: d.getMonth() + 1,
            day: d.getDate(),
            hour: d.getHours(),
            minute: d.getMinutes(),
            lon: 0,
            lat: 0,
            az_offset: 0,
            alt_offset: 0
        };

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    self.set_position(position.coords.longitude.toFixed(), position.coords.latitude.toFixed());
                },
                function(failed) {
                    self.refresh();
                },
                { timeout: 3000 }
            );
        } else {
            self.refresh();
        }
    };


    self.params = function(obj) {
        return $.extend({}, self.apiParams, obj);
    }


    self.refresh = function() {
        if(self.starLayer !== null) {
            self.map.removeLayer(self.starLayer);
        }

        if(self.constellationLayer !== null) {
            self.map.removeLayer(self.constellationLayer);
            self.layerControl.removeLayer(self.constellationLayer);
        }

        if(self.labelLayer !== null) {
            self.map.removeLayer(self.labelLayer);
            self.layerControl.removeLayer(self.labelLayer);
        }

        if(self.marker !== null) {
            self.map.removeLayer(self.marker);
        }

        self.starLayer = L.tileLayer('/tiles/{year}/{month}/{day}/{hour}/{minute}/{lon}/{lat}/{az_offset}/{alt_offset}/{z}/{x}/{y}.svg', self.params({
            maxZoom: 8,
            zIndex: 1,
            attribution: 'HYG Database'
        }));

        self.starLayer.addTo(self.map);

        self.constellationLayer = L.tileLayer('/tiles/lines/{year}/{month}/{day}/{hour}/{minute}/{lon}/{lat}/{az_offset}/{alt_offset}/{z}/{x}/{y}.svg', self.params({
            maxZoom: 9,
            zIndex: 2,
            attribution: 'SFA Constellation Lines'
        }));
        self.constellationLayer.addTo(self.map);
        self.layerControl.addOverlay(self.constellationLayer, "Constellation Lines");

        self.labelLayer = L.tileLayer('/tiles/labels/{year}/{month}/{day}/{hour}/{minute}/{lon}/{lat}/{az_offset}/{alt_offset}/{z}/{x}/{y}.svg', self.params({
            maxZoom: 9,
            zIndex: 2,
        }));
        self.labelLayer.addTo(self.map);
        self.layerControl.addOverlay(self.labelLayer, "Labels");
    };


    self.aim = function(az_offset, alt_offset) {
        self.apiParams.az_offset = az_offset;
        self.apiParams.alt_offset = alt_offset;
        self.refresh();
    };


    self.set_position = function(lon, lat) {
        self.apiParams.lon = lon;
        self.apiParams.lat = lat;
        self.refresh();
    };


    self.setTimeAndPosition = function(year, month, day, hour, minute, lon, lat) {
        self.apiParams.year = year;
        self.apiParams.month = month;
        self.apiParams.day = day;
        self.apiParams.hour = hour;
        self.apiParams.minute = minute;
        self.set_position(lon, lat);
    };

    self.onclick = function(e) {
        $.getJSON('/find', self.params({az: e.latlng.lng, alt: e.latlng.lat}), function(result) {
            if (self.marker !== null) {
                self.map.removeLayer(self.marker);
            }

            self.marker = L.marker([result[2], result[1]], {
                icon: L.icon({
                    iconUrl: "static/marker.svg",
                    iconSize: [32, 32],
                    iconAnchor: [16, 16]
                })
            });
            self.marker.bindPopup(result[0]);
            self.marker.addTo(self.map);

            //alert(result);
        });
    };


    self.init(id);
    return self;
};

var map = SkyMap("map");