// ----- CONTACT ----- //
 
$(document).ready(function() {
    $('#contact-form').submit(function(event) {
        event.preventDefault(); // Prevent the default form submission

        var action = $(this).attr('action'); // Get the form's action attribute

            $('#submit')
                .attr('disabled', 'disabled'); // Disable the submit button to prevent multiple submissions

                  $.post(action, { // Send an AJAX POST request
                    name: $('#name').val(), // Get the value of the name input
                    email: $('#email').val(), // Get the value of the email input
                    subject: $('#subject').val(), // Get the value of the subject input
                    comments: $('#comments').val() // Get the value of the comments textarea
                },
                function(data) { // Callback function to handle the server's response
                    // Display a success message
                    $('#message').html("<p>Your message has been sent.</p>").slideDown('slow');
                    $('#submit').removeAttr('disabled'); // Re-enable the submit button

                    if (data.match('success') != null) { // Optionally, handle specific server response
                        $('#contact-form').slideUp('slow'); // Hide the form if the response indicates success
                    }
                }
            });
        });
