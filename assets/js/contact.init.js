document.addEventListener("DOMContentLoaded", function() {
    var form = document.getElementById("contact-form");
    var status = document.getElementById("message");

    async function handleSubmit(event) {
        event.preventDefault();
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
                        status.textContent = "Oops! There was a problem submitting your form";
                    }
                });
            }
        }).catch(error => {
            status.textContent = "Oops! There was a problem submitting your form";
        });
    }

    form.addEventListener("submit", handleSubmit);
});
