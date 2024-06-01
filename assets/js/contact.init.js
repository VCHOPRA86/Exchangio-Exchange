// ----- CONTACT ----- //
 
$(document).ready(function() {
        // When the document is fully loaded and ready
    $('#contact-form').submit(function(event) {
        event.preventDefault(); // Prevent the default form submission

        var action = $(this).attr('action'); // Get the form's action attribute

        $("#message").slideUp(750, function() { // Hide any existing message with an animation
            $('#message').hide(); // Hide the message div

            $('#submit')
                .attr('disabled', 'disabled'); // Disable the submit button to prevent multiple submissions

            $.get(action, { // Send an AJAX GET request 
                    name: $('#name').val(), // Get the value of the name input
                    email: $('#email').val(), // Get the value of the email input
                    subject: $('#subject').val(), // Get the value of the subject input
                    comments: $('#comments').val() // Get the value of the comments textarea
                },
                function(data) { // Callback function to handle the server's response
                    // Display a success message
                    $('#message').html("<div class='alert alert-success'>Your message has been sent.</div>").slideDown('slow');
                    $('#submit').removeAttr('disabled'); // Re-enable the submit button

                    $('#contact-form').slideUp('slow'); // Hide the form
                }
            ).fail(function() {  // Handle failure case if failed
                $('#message').html("<div class='alert alert-danger'>There was an error sending your message. Please try again later.</div>").slideDown('slow');
                $('#submit').removeAttr('disabled'); // Re-enable the submit button
            });
        });
    });
});