function signInCallback(json) {
    var authResult = json;
    if (authResult['code']) {
        $('.signinButton').attr('style', 'display: none');
        $.ajax({
            type: 'POST',
            url: '/oauth/google',
            processData: false,
            data: JSON.stringify({ auth_code: authResult['code'] }),
            contentType: 'application/json; charset=utf-8',
            success: function (result) {
                jscontroler.setToken(result.token);
                jscontroler.loadHome();
            },
            error: function (jqXHR, textStatus) {
                alert(textStatus);
            }
        });
    }
}

var jscontroler = new function () {
    var token = '';
    var self = this;
    var spinner = null;

    this.init = function() {
        
        $(".dropdown").hover(
            function () {
                $('.dropdown-menu', this).stop(true, true).slideDown("fast");
                $(this).toggleClass('open');
            },
            function () {
                $('.dropdown-menu', this).stop(true, true).slideUp("fast");
                $(this).toggleClass('open');
            }
        );

        $('body').on("click", '.btn-google', function () {
            auth2.grantOfflineAccess({ 'redirect_uri': 'postmessage' }).then(signInCallback);
        });

        //auxToken = $.cookie("token");

        //if (typeof (auxToken) != "undefined" && auxToken !== '') {
        //    console.log(auxToken);
         //   jscontroler.setToken(auxToken);
        //    jscontroler.loadHome();            
        //} else {
            $("#login-dp,#userworkarea").load("/loginview");
        //}

        $('body').on("click", ".localSinginButton", function () {
            var parent = $(this).closest('.form-signin');

            var username = $("input#inputEmail", parent).val();
            var password = $("input#inputPassword", parent).val();

            $.ajax({
                type: 'POST',
                url: '/oauth/local',
                processData: false,
                data: JSON.stringify({ email: username, password: password }),
                contentType: 'application/json; charset=utf-8',
                success: function (result) {
                    jscontroler.setToken(result.token);
                    jscontroler.loadHome();
                },
                error: function (data, textStatus, jqXHR) {
                    var ex = $.parseJSON(data.responseText);
                    if (ex && ex.error) {
                        alert(ex.error.message);
                    }
                }
            });
        });

        $.ajaxSetup({
            beforeSend: function (xhr) {
                xhr.setRequestHeader('Authorization', self.make_base_auth(token, ''));
                if (spinner != null) {
                    var target = document.getElementById('workarea');
                    spinner = new Spinner().spin(target);
                }
            },
            complete: function () {
                if (spinner != null) {
                    spinner.stop();
                    spinner = null;
                }
            }
        });
    };

    this.make_base_auth = function (user, password) {
        var tok = user + ':' + password;
        var hash = btoa(tok);
        return "Basic " + hash;
    }

    this.setToken = function (accessToken) {
        token = accessToken;
        $.cookie("token", token);
    };

    this.loadHome = function () {
        self.loadMyProfile();

        self.loadMyRequests();    
    };

    this.loadMyProfile = function () {
        $.ajax({
            type: "GET",
            url: "/api/v1/me",
            success: function (result) {
                $("#loginmenu").hide();
                $("#userinfo,#usermenu").show();
                $("p", "#userinfo").html(result.name);
                $("img", "#userinfo").attr("src", result.picture)
            }
        });
    };

    this.loadMyRequests = function () {
        $("#userworkarea").html('<table id="myrequesttable"></table>')

        $.ajax({
            type: "GET",
            url: "/api/v1/request",
            success: function (data) {
                $('#myrequesttable').dataTable({
                    "paging": false,
                    "searching": false,
                    "data": data.requests,
                    "columns": [
                        { "data": "meal_time", "title": "Tiempo" },
                        { "data": "meal_type", "title": "Tipo" },
                        { "data": "location_address", "title": "Direccion" }
                    ]
                });
            }
        });
    };

    this.showAddRequestForm = function (lat, lng, name, address) {
        if (token !== '') {
            $("#userworkarea").load("/requestform", function () {
                $("#location_name").val(name);
                $("#location_address").val(address);
                $("#original_latitude").val(lat);
                $("#original_longitude").val(lng);

                $("#addrequestbutton").click(function(e) {
                    e.preventDefault();

                    var lat = 0;
                    var long = 0;

                    if ($("#original_latitude").val() != '') {
                        lat = parseFloat($("#original_latitude").val())
                    }
                    
                    if ($("#original_longitude").val() != '') {
                        long = parseFloat($("#original_longitude").val());
                    }

                    $.ajax({
                        type: 'POST',
                        url: '/api/v1/request',
                        processData: false,
                        data: JSON.stringify({
                            "meal_type": $("#meal_type").val(),
                            "meal_time": $("#meal_time").val(),
                            "location_name": $("#location_name").val(),
                            "location_address": $("#location_address").val(),
                            "original_latitude": lat,
                            "original_longitude": long
                        }),
                        contentType: 'application/json; charset=utf-8',
                        success: function(result) {
                            jscontroler.loadMyRequests();
                        },
                        error: function(data, textStatus, jqXHR) {
                            var ex = $.parseJSON(data.responseText);
                            if (ex && ex.error) {
                                alert(ex.error.message);
                            }
                        }
                    });
                });

                $("#canceladdrequest").click(function(e) {
                    e.preventDefault();
                    jscontroler.loadMyRequests();
                });
            });
        } else {
            $("#userworkarea .bg-warning").remove();
            $("#userworkarea").prepend('<p class="bg-warning">Debe iniciar sesion</p>');
        }
    };
};