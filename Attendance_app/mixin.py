from django.shortcuts import redirect

class CustomizedRquirementLogin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:

            return redirect("user:login")
        return super(CustomizedRquirementLogin, self, ).dispatch(request, *args, **kwargs)
