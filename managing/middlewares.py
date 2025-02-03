from django.shortcuts import redirect
from django.urls import reverse
from django.http import Http404
from django.utils.deprecation import MiddlewareMixin

class RequireLoginMiddleware(MiddlewareMixin):
    """
    Middleware to enforce login requirement on specific apps.
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        protected_apps = {'Attendance', 'price', 'locations', 'managing'}

        if request.resolver_match and request.resolver_match.app_name in protected_apps:
            if not request.user.is_authenticated or not request.user.created_who:
                raise Http404("Page not found")

        return None


class StaffOnlyMiddleware(MiddlewareMixin):
    """
    Middleware to enforce staff-only access for managing app.
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.resolver_match and request.resolver_match.app_name == 'managing':
            if not request.user.is_authenticated or not request.user.is_staff:
                return redirect(reverse('Attendance:redirected_view'))
        return None
