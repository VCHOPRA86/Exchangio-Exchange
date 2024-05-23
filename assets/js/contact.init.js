// ----- CONTACT ----- //
 
$('#contact-form').submit(function(event) {
    event.preventDefault(); // Prevent the default form submission

    var action = $(this).attr('action');

    $("#message").slideUp(750, function() {
        $('#message').hide();

        $('#submit')
            .attr('disabled', 'disabled');

        $.post(action, {
                name: $('#name').val(),
                email: $('#email').val(),
                subject: $('#subject').val(),
                comments: $('#comments').val(),
            },
            function(data) {
                // Show the custom success message
                $('#message').html("<p>Your message has been sent.</p>");

                $('#message').slideDown('slow');
                $('#cform img.contact-loader').fadeOut('slow', function() {
                    $(this).remove();
                });
                $('#submit').removeAttr('disabled');

                // Optionally, you can handle form success response with the 'data' variable
                if (data.match('success') != null) {
                    $('#contact-form').slideUp('slow');
                }
            }
        );

    });

    return false; // Prevent the default form submission behavior
});
