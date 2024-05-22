from functools import wraps
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.conf import settings
from django.core.exceptions import PermissionDenied
from . import models

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView
from django.contrib.auth.views import redirect_to_login 
from django.contrib.auth.decorators import login_required

def check_user_has_permission(request, permission, allow_superuser):
    if request.user.has_perm(permission):
        return True
    elif allow_superuser and request.user.is_superuser:
        return True
    return False

def user_has_permission(permission='django_flow_forge.django_flow_admin_access', allow_superuser=True):
    """
    A decorator to check if the user has a specific permission.
    Redirects to login page if not authenticated, and returns a 403 Forbidden response if lacking the permission.
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            # Check if the user has the permission
            ok = check_user_has_permission(request, permission, allow_superuser)
            if ok or settings.DEBUG:
                return view_func(request, *args, **kwargs)
            # If the user doesn't have the permission, return a HTTP 403 Forbidden response
            return HttpResponseForbidden('You have not been assigned with Permission to the Django Flow Forge admin group.')
        
        setattr(_wrapped_view, permission, True)
        return _wrapped_view
        

    return decorator

class FlowForgePermissionMixin(LoginRequiredMixin, AccessMixin):
    # Permission to check for
    permission_required = 'django_flow_forge.django_flow_admin_access'
    # Whether to allow superusers access regardless of the permission
    allow_superuser = True

    def dispatch(self, request, *args, **kwargs):
        if self.permission_required is None:
            raise AttributeError("UserHasPermissionMixin requires 'permission_required' attribute to be set.")

        # Check if the user is authenticated first (handled by LoginRequiredMixin)
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Utilize the check_user_has_permission function
        has_permission = check_user_has_permission(request, self.permission_required, self.allow_superuser)

        # Automatically grant access if in DEBUG mode, or if the permission check passes
        if settings.DEBUG or has_permission:
            return super(FlowForgePermissionMixin, self).dispatch(request, *args, **kwargs)
        else:
            return self.handle_no_permission()

    def handle_no_permission(self):
        if self.raise_exception or self.request.user.is_authenticated:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())