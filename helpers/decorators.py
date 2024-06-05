from django.contrib.auth.decorators import user_passes_test

def check_user(user):
    return not user.is_authenticated


user_logout_required = user_passes_test(check_user, '/', None)

def auth_user_should_not_access(viewfunc):

    return user_logout_required(viewfunc)

def allowed_users(allowed_roles=[]):
    def decorator(viewfunc):
        def wrapper_func(request, *args, **kwargs):
            return viewfunc(request, *args, **kwargs)
        return wrapper_func
    return decorator