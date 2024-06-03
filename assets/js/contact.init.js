ocument.addEventListener("DOMContentLoaded", function() {
    var form = document.getElementById("contact-form");
    var status = document.getElementById("contact-form-status");

    // Function to validate the form
    const validateForm = () => {
        // Get form inputs
        const nameInput = document.getElementById("name").value.trim();
        const emailInput = document.getElementById("email").value.trim();
        const subjectInput = document.getElementById("subject").value.trim();
        const commentsInput = document.getElementById("comments").value.trim();
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        // Check if any of the required fields are empty
        if (!nameInput || !emailInput || !subjectInput || !commentsInput) {
            status.textContent = "Please fill in all the required fields.";
            return false;
        }

        // Check for valid email format
        if (!emailPattern.test(emailInput)) {
            status.textContent = "Please enter a valid email address.";
            return false;
        }

        status.textContent = ""; // Clear status message if validation passes
        return true;
    };

    // Function to handle form submission
    async function handleSubmit(event) {
        event.preventDefault();

        // Validate the form before submission
        if (!validateForm()) {
            return;
        }

        var data = new FormData(event.target);
        fetch(event.target.action, {
            method: form.method,
            body: data,
            headers: {
                'Accept': 'application/json'
            }
        }).then(response => {
            if (response.ok) {
                status.textContent = "Thanks for your submission!";
                form.reset();
            } else {
                response.json().then(data => {
                    if (Object.hasOwn(data, 'errors')) {
                        status.textContent = data["errors"].map(error => error["message"]).join(", ");
                    } else {
                        status.textContent = "Oops! There was a problem submitting your form.";
                    }
                });
            }
        }).catch(error => {
            status.textContent = "Oops! There was a problem submitting your form.";
        });
    }

    form.addEventListener("submit", handleSubmit);
});
