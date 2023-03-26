from django.conf import settings
from django.contrib import auth
from django.utils import timezone

class SessionIdleTimeout:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        if user.is_authenticated:
            last_activity = request.session.get('last_activity')

            if 'last_activity' in request.session and request.session['last_activity'] is not None:
                last_activity = timezone.datetime.fromisoformat(request.session['last_activity'])

                elapsed_time = timezone.now() - last_activity

                if elapsed_time.total_seconds() > settings.SESSION_IDLE_TIMEOUT:
                    auth.logout(request)
                    # del request.session['last_activity']
            else:
                request.session['last_activity'] = timezone.now().isoformat()

        response = self.get_response(request)

        if user.is_authenticated:
            request.session['last_activity'] = timezone.now().isoformat()

        return response
