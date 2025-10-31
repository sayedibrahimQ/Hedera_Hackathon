from django.shortcuts import redirect

class WalletAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):=
        if (
            not request.session.get("user_id")
            and not request.path.startswith("/login")
            and not request.path.startswith("/api/")
            and not request.path.startswith("/admin")
        ):
            return redirect("/login/")
        return self.get_response(request)