(function ($) {
    $('.btn-color-reject').click(function () {
        var button = this;
        console.log($(button).data('href'))
        $.ajax({
            'url': $(button).data('href'),
            'type': 'POST'
        }).done(function () {
            $(button).parents('.color').remove();
        }).fail(function (e) {
            console.log(e);
        });
    });

    $('.btn-color-accept').click(function () {
        var button = this;
        $.ajax({
            'url': $(button).data('href'),
            'type': 'POST'
        }).done(function (ret) {
            $(".action_btn").remove()
            $("#confirming_btn").show()
        }).fail(function (e) {
            console.log(e);
        });
    });
})(jQuery);

