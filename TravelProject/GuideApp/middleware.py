from django.http import HttpResponseForbidden



class GuideAppMobileOnlyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request is for GuideApp
        if request.path.startswith("/guide/"):  # Adjust based on your URL pattern
            user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
            mobile_keywords = ["mobile", "android", "iphone", "ipod", "opera mini", "blackberry"]

            if not any(keyword in user_agent for keyword in mobile_keywords):
                return HttpResponseForbidden("GuideApp is only accessible from mobile devices.")

        return self.get_response(request)

