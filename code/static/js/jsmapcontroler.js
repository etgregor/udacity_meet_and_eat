var jsmapcontroler = new function () {
    var gmap;
    
    this.init = function() {
        gmap = new GMaps({
            div: '#map',
            lat: 19.2464696,
            lng: -99.10134979999998,
            click: function (e) {
                GMaps.geocode({
                    latLng: e.latLng,
                    callback: function (results, status) {
                        if (status == 'OK') {
                            var fistPlace = results[0];
                            var latlng = fistPlace.geometry.location;

                            gmap.addMarker({
                                lat: latlng.lat(),
                                lng: latlng.lng(),
                                details: { name: fistPlace.name, address: fistPlace.formatted_address },
                                title: fistPlace.name,
                                click: addRequest
                            });
                        }
                    }
                });
            }
        });

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function (position) {
                
                gmap.setCenter(position.coords.latitude, position.coords.longitude);
            });
        } 

        var input = document.getElementById('searchPlaceForEat');
        var searchBox = new google.maps.places.SearchBox(input);
        
        gmap.map.addListener('bounds_changed', function () {
            searchBox.setBounds(gmap.map.getBounds());
        });

        searchBox.addListener('places_changed', function() {
            var places = searchBox.getPlaces();

            if (places.length == 0) {
                return;
            }

            gmap.removeMarkers();
            var bounds = new google.maps.LatLngBounds();
            places.forEach(function(place) {
                var icon = {
                    url: place.icon,
                    size: new google.maps.Size(71, 71),
                    origin: new google.maps.Point(0, 0),
                    anchor: new google.maps.Point(17, 34),
                    scaledSize: new google.maps.Size(25, 25)
                };

                gmap.addMarker({
                    icon: icon,
                    position: place.geometry.location,
                    details: { name: place.name, address: place.formatted_address },
                    title: place.name,
                    click: addRequest
                });
                 
                if (place.geometry.viewport) {
                    bounds.union(place.geometry.viewport);
                } else {
                    bounds.extend(place.geometry.location);
                }
            });

            gmap.map.fitBounds(bounds);
        });

        var width = $(window).width();
        var height = $(window).height();
        resizeMap(width, height);

        $(window).resize(function () {
            var width = $(window).width();
            var height = $(window).height();
            resizeMap(width, height);
        });
    };

    function addRequest(markerInfo) {
        console.log(markerInfo.details)
    };
    
    function resizeMap(w, h) {
        $("#map").height(h - 100);
        $("#map").width(w);
    }
};