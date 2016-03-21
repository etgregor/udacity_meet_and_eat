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

        $("#login-dp").load("/loginview");

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
                var target = document.getElementById('workarea');
                spinner = new Spinner().spin(target);
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
        $.ajaxSetup({
            beforeSend: function (xhr) {
                xhr.setRequestHeader('Authorization', self.make_base_auth(token, ''));
            }
        });
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
                $("#workarea").html("");
                $("#loginmenu").hide();
                $("#userinfo,#usermenu").show();
                $("p", "#userinfo").html(result.name);
                $("img", "#userinfo").attr("src", result.picture)
            }
        });
    };

    this.loadMyRequests = function () {
        // $("#workarea").load("/myrequests");
    };
};