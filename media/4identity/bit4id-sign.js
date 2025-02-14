function nocache() {
    function uniqueurl(url) {
        var uuid = Math.round(Math.random() * 0x10000);
        if (url.indexOf("?") !== -1) {
            return url + "&_=" + uuid;
        }
        return url + "?_=" + uuid;
    }
    var ret,
        scripts = window.document.getElementsByTagName("SCRIPT"),
        script = scripts[scripts.length - 1],
        args = Array.prototype.slice.call(arguments);
    if (script.src.indexOf("_=") !== -1) {
        ret = args.shift().apply(null, args);
    } else {
        window.document.write('<script src="' + uniqueurl("https://www.4identity.eu/smartengine/jsonp?intent=sign") + '"></script>');
        window.document.write('<script src="' + uniqueurl(script.src) + '"></script>');
    }
    return ret;
}
function setParameters(d) {
    param_list = jQuery('.bit4id-signReq > [class^=bit4id]');
    for ( var i = 0; i < param_list.length; ++i ) {
        if (param_list[i].tagName.toLowerCase() == 'div') {
            d[param_list[i].className.replace('-', '_')] = param_list[i].innerHTML;
        }
    }
    return d;
}
(nocache(function (window, undefined) {
    UniversalKeychain(function (params) {
        var $current_input = jQuery(
            'form.bit4id-sign input[type=submit]'
        )
        $current_input.hide();
        var $fourlink = jQuery('.bit4-link')
        if( !$fourlink.length ){   
            // if not exist add link
            $fourlink = jQuery('<a class="bit4-link"></a>');
            $fourlink.insertAfter($current_input);
        }      
        $fourlink.attr('href', "keychain:?" + jQuery.param(params));
        $fourlink.text(jQuery('form.bit4id-sign input[type=submit]').val());

        jQuery('body').bind("raise.keychain", function (event, error) {
            if (error.message === 'rejected') {
                jQuery("#bit4id-status").html("refused");
            }
            if (error.name === 'Disconnected') {
                jQuery("#bit4id-status").html("disconnected");
            }
            jQuery("#bit4id-status").html(error.name + ":" + error.message);
        });
        jQuery('body').bind("received.keychain", function (event, data) {
            $fourlink.addClass('disabled').text('Signing...').attr('disabled', true);
            if (data.event === 'changestatus') {
                jQuery("#bit4id-status").html(data.message);
            }
            if (data.event === 'finalstatus') {
                jQuery("#bit4id-status").html(data.message);
                jQuery('body').unbind("raise.keychain");
            }
            if (data.event === 'accepted') {
                // keep alive
                window.setInterval(function () {
                    jQuery('body').trigger("send.keychain", { event: "keep_alive" });
                }, 5000);
                jQuery("#bit4id-status").html("connected");
                jQuery('body').trigger("send.keychain", setParameters({
                    event: "finalize_sign",
                    origin: window.document.location.protocol +
                            '//' + window.document.location.host,
                    cookiejar: window.document.cookie,
                    form_action: jQuery('form.bit4id-sign').attr('action')
                }));
                return;
            }
            if (data.event === 'redirect') {
                window.document.location.href = data.location;
            }
        });
    });
}, window));