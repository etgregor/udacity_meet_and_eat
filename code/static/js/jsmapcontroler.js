var jsmapcontroler = new function () {
    var gmap;
    
    var posibleMarkers;

    this.init = function() {
        posibleMarkers = new Array();
        gmap = new GMaps({
            div: '#map',
            lat: 19.2464696,
            lng: -99.10134979999998,
            click: function (e) {
                GMaps.geocode({
                    latLng: e.latLng,
                    callback: function (results, status) {
                        if (status == 'OK') {
                            gmap.removeMarkers(posibleMarkers);
                            var fistPlace = results[0];
                            var latlng = fistPlace.geometry.location;
                            var lat = latlng.lat();
                            var lng = latlng.lng();
                            var name = fistPlace.name || '';
                            var address = fistPlace.formatted_address;

                            jscontroler.showAddRequestForm(lat, lng, name, address);

                            gmap.removeMarkers(posibleMarkers);
                            var clickMarker = gmap.addMarker({
                                lat: lat,
                                lng: lng,
                                details: { name: name, address: address },
                                title: fistPlace.name,
                                click: clickMarker
                            });

                            posibleMarkers.push(clickMarker);
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

            gmap.removeMarkers(posibleMarkers);
            var fistPlace = places[0];
            var latlng = fistPlace.geometry.location;
            var lat = latlng.lat();
            var lng = latlng.lng();
            var name = fistPlace.name || '';
            var address = fistPlace.formatted_address;

            jscontroler.showAddRequestForm(lat, lng, name, address);

            var bounds = new google.maps.LatLngBounds();
            places.forEach(function(place) {
                var marker = gmap.addMarker({
                    position: place.geometry.location,
                    details: { name: place.name, address: place.formatted_address },
                    title: place.name,
                    click: clickMarker
                });
                 
                if (place.geometry.viewport) {
                    bounds.union(place.geometry.viewport);
                } else {
                    bounds.extend(place.geometry.location);
                }

                posibleMarkers.push(marker);

            });

            gmap.map.fitBounds(bounds);
        });

        var height = $(window).height();
        resizeMap(height);

        $(window).resize(function () {
            var height = $(window).height();
            resizeMap(height);
        });
    };

    this.addmyrequests = function(requests){

    };

    this.addmyPropossal = function(proposal){

    };

    this.addmeals = function(meals){
        
    };

    function clickMarker(markerInfo) {
        var lat = markerInfo.position.lat();
        var lng = markerInfo.position.lng();
        jscontroler.showAddRequestForm(lat, lng, markerInfo.details.name, markerInfo.details.address);
    };

    function resizeMap(h) {
        $("#map").height(h - 100);
    }
};