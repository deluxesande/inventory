from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect

def check_user(user):
    return not user.is_authenticated


user_logout_required = user_passes_test(check_user, '/', None)

def auth_user_should_not_access(view_func):

    return user_logout_required(view_func)


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if request.user.is_authenticated:
                if request.user.user_type not in allowed_roles:
                    # Redirect to the previous page, or to the homepage if no previous page
                    return redirect('home')
            else:
                return redirect('login')  # Redirect to login page if user is not authenticated
            return view_func(request, *args, **kwargs)
        return wrapper_func
    return decorator