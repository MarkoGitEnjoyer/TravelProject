document.addEventListener("DOMContentLoaded", function () {
    const buyButton = document.getElementById('buyButton');
    
    buyButton.addEventListener('click', function () {
        // Make an API call to send the email (You will need to replace with actual Mailjet integration)
        sendEmail();
    });
});

const apiKey = "your-mailjet-api-key";
const apiSecret = "your-mailjet-api-secret";
const fromEmail = "your-email@example.com";
const toEmail = "recipient-email@example.com";
const subject = "Hello from Mailjet!";
const message = "This is a test email sent using Mailjet.";
function sendEmail() {
    const emailData = {
        from: "your_email@example.com",
        to: "recipient@example.com",
        subject: "Registration Confirmation",
        text: "Thank you for registering for the trip!"
    };

    fetch('https://api.mailjet.com/v3.1/send', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + btoa('your_api_key:your_secret_key') // Use actual Mailjet credentials here
        },
        body: JSON.stringify({
            Messages: [
                {
                    From: {
                        Email: emailData.from
                    },
                    To: [
                        {
                            Email: emailData.to
                        }
                    ],
                    Subject: emailData.subject,
                    TextPart: emailData.text
                }
            ]
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.Messages[0].Status === "success") {
            alert("Email sent successfully!");
        } else {
            alert("Failed to send email.");
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("There was an error sending the email.");
    });
}







