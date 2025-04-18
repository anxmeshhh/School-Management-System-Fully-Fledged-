from django.shortcuts import redirect

class WwwRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the domain starts without 'www.'
        if not request.get_host().startswith('www.'):
            return redirect('https://www.' + request.get_host(), permanent=True)
        response = self.get_response(request)
        return response
