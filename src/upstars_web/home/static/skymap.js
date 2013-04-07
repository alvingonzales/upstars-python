

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
            map_settings.inertia = false;
        }

        if (L.Browser.mobileWebkit) {
            map_settings.fadeAnimation = false;
        }

        self.map = L.map('map', map_settings);
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
            lat: 10,
            az_offset: 0,
            alt_offset: 0
        };

        navigator.geolocation.getCurrentPosition(self.set_position);

        //self.refresh();
    };


    self.set_position = function(position) {
        self.apiParams.lon = position.coords.longitude.toFixed();
        self.apiParams.lat = position.coords.latitude.toFixed();
        self.refresh();
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