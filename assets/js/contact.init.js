$(document).ready(function() {
    // Function to validate the form
    const validateForm = () => {
        // Get form inputs
        const nameInput = $('#name');
        const emailInput = $('#email');
        const subjectInput = $('#subject');
        const commentsInput = $('#comments');
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        // Check if any of the required fields are empty
        if (nameInput.val().trim() === "" || emailInput.val().trim() === "" || subjectInput.val().trim() === "" || commentsInput.val().trim() === "") {
            return false;
        }

        // Check for valid email format
        if (!emailPattern.test(emailInput.val().trim())) {
            return false;
        }

        return true;
    };

    // When the document is fully loaded and ready
    $('#contact-form').submit(function(event) {
        event.preventDefault(); // Prevent the default form submission

        // Validate the form fields
        if (!validateForm()) {
            // Display error message
            $('#message').html("<div class='alert alert-danger'>Please fill in all the required fields with valid information.</div>").slideDown('slow');
            return;
        }

        var action = $(this).attr('action'); // Get the form's action attribute

        $("#message").slideUp(750, function() { // Hide any existing message with an animation
            $('#message').hide(); // Hide the message div

            $('#submit')
                .attr('disabled', 'disabled'); // Disable the submit button to prevent multiple submissions

             $.ajax({
                url: action, // Formspree endpoint
                method: "POST",
                data: $(this).serialize(), // Serialize form data
                dataType: "json",
                success: function(data) { // Callback function to handle the server's response
                    // Display a success message
                    $('#message').html("<div class='alert alert-success'>Your message has been sent.</div>").slideDown('slow');
                    $('#submit').removeAttr('disabled'); // Re-enable the submit button

                    $('#contact-form').slideUp('slow'); // Hide the form
                },
                error: function(err) {  // Handle failure case
                    $('#message').html("<div class='alert alert-danger'>There was an error sending your message. Please try again later.</div>").slideDown('slow');
                    $('#submit').removeAttr('disabled'); // Re-enable the submit button
                }
            });
        });
    });
});
