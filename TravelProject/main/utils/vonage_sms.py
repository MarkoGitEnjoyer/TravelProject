from vonage import Auth, Vonage
from vonage_sms import SmsMessage, SmsResponse
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class VonageSMSService:
    """
    A service class for sending SMS messages using the Vonage API.
    """
    def __init__(self):
        """
        Initialize the Vonage SMS service.
        """
        self.client = None
        self.use_mock = True

        # Get API credentials from settings
        api_key = getattr(settings, 'VONAGE_API_KEY', None)
        api_secret = getattr(settings, 'VONAGE_API_SECRET', None)

        if api_key and api_secret:
            try:
                # Initialize using the new Vonage SDK pattern
                self.client = Vonage(Auth(api_key=api_key, api_secret=api_secret))
                self.use_mock = False
                logger.info("Vonage SMS service initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing Vonage client: {str(e)}")
        else:
            logger.warning("Vonage API credentials not found in settings")

    def send_message(self, phone_number, message):
        """
        Send an SMS message to the specified phone number.

        Args:
            phone_number (str): The recipient's phone number in international format.
            message (str): The message to send.

        Returns:
            dict: A response dictionary with success status and message ID or error.
        """
        if self.use_mock:
            return self._send_mock_message(phone_number, message)
            
        try:
            # Create message using the SmsMessage class
            sms_message = SmsMessage(
                to=phone_number,
                from_=getattr(settings, 'VONAGE_SENDER_ID', 'YourSenderID'),
                text=message
            )
            
            # Send the message using the new API
            response: SmsResponse = self.client.sms.send(sms_message)
            
            # Process the response
            if response.messages[0].status == "0":
                logger.info(f"Message sent successfully to {phone_number}")
                return {
                    "success": True,
                    "message_id": response.messages[0].message_id
                }
            else:
                error = response.messages[0].error_text
                logger.error(f"Message failed with error: {error}")
                return {
                    "success": False,
                    "error": error
                }

        except Exception as e:
            logger.error(f"Error sending SMS via Vonage API: {str(e)}")
            return {"success": False, "error": str(e)}

    def _send_mock_message(self, phone_number, message):
        """
        Mock implementation that logs message details but doesn't actually send SMS.
        """
        logger.info(f"[MOCK SMS] Would send to: {phone_number}")
        logger.info(f"[MOCK SMS] Message: {message}")

        return {
            "success": True,
            "message_id": f"mock-{phone_number.replace('+', '')}",
            "note": "This is a mock SMS (Vonage API not used)"
        }


def send_trip_confirmation(registration):
    """
    Send SMS confirmation for trip registration.

    Args:
        registration: A Registration model instance.

    Returns:
        dict: Response from the SMS service.
    """
    try:
        # Create SMS service
        sms_service = VonageSMSService()

        # Format the message
        message = (
            f"Hello {registration.first_name}, your registration for "
            f"{registration.trip.name} on {registration.trip.date} is confirmed! "
            f"Meeting point: {registration.trip.meeting_point}. Thank you!"
        )

        # Send the message
        return sms_service.send_message(
            phone_number=registration.phone,
            message=message
        )

    except Exception as e:
        logger.error(f"Error in send_trip_confirmation: {str(e)}")
        return {"success": False, "error": str(e)}