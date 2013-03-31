
var map = L.map('map', {
    fadeAnimation: true,
    minZoom: 4,
    maxZoom: 5,
    maxBounds: [[45, -45], [-45, 45]],
    // Equirectangular projection
    crs: L.CRS.EPSG4326,
    //crs: L.CRS.Simple,
    // inertia: true does not play well with maxBounds on IE
    inertia: false
});
map.setView([0, 0], 2);

var layerControl = L.control.layers(
    {},
    {},
    { autoZIndex: false }
);
layerControl.addTo(map);

var starLayer = null;
var constellationLayer = null;

function LoadTiles(az_offset, alt_offset) {
    /*L.tileLayer('/tiles/static/white.svg', {
        maxZoom: 9,
    }).addTo(map);*/

    if(starLayer !== null) {
        map.removeLayer(starLayer);
    }

    if(constellationLayer !== null) {
        map.removeLayer(constellationLayer);
        layerControl.removeLayer(constellationLayer);
    }

    starLayer = L.tileLayer('/tiles/2012/3/16/14/53/0/10/{az_offset}/{alt_offset}/{z}/{x}/{y}.svg', {
        az_offset: az_offset,
        alt_offset: alt_offset,
        maxZoom: 8,
        zIndex: 2,
        attribution: 'HYG Database'
    });
    starLayer.addTo(map);

    constellationLayer = L.tileLayer('/tiles/lines/2012/3/16/14/53/0/10/{az_offset}/{alt_offset}/{z}/{x}/{y}.svg', {
        az_offset: az_offset,
        alt_offset: alt_offset,
        maxZoom: 9,
        zIndex: 1,
        attribution: 'SFA Constellation Lines'
    });
    constellationLayer.addTo(map);
    layerControl.addOverlay(constellationLayer, "Constellation Lines");
}

LoadTiles(0, 0);
