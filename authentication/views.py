from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from validate_email import validate_email
from .models import User
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from helpers.decorators import auth_user_should_not_access, allowed_users
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from .utils import generate_token
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import JsonResponse

'''
TODO: implement thread so as to have email sent concurently as user registers to avoid waiting for too long
'''

# def send_activation_email(user, request):
#     current_site = get_current_site(request)
#     email_subject ="Activation Needed for Account"
#     email_body = render_to_string('authentication/activate.html', {
#         'user': user,
#         'domain':current_site,
#         'uid':urlsafe_base64_encode(force_bytes(user.pk)),
#         'token': generate_token.make_token(user)
#     })

#     email = EmailMessage(subject=email_subject,
#                   body=email_body,
#                   from_email=settings.EMAIL_FROM_USER,
#                   to=[user.email]
#                   )
#     email.send()


@auth_user_should_not_access
def register(request):

    if request.method == "POST":
        context = {'has_error': False, 'data':request.POST}
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if len(password)<6:
            messages.add_message(request, messages.WARNING, "The password entered is too short")

            context['has_error'] = True
        
        if password != password2:
            messages.add_message(request, messages.WARNING, "The passwords entered do not match!")

            context['has_error'] = True

        # if not validate_email(email):
        #     messages.add_message(request, messages.WARNING, "Enter a valid email")

        #     context['has_error'] = True

        if not username:
            messages.add_message(request, messages.WARNING, "Enter your username!")

            context['has_error'] = True

        if User.objects.filter(username = username).exists():
            messages.add_message(request, messages.WARNING, "Username taken, please choose another one")
            return render(request, 'authentication/register.html', context, status=409)

        if User.objects.filter(email = email).exists():
            messages.add_message(request, messages.WARNING, "Email exists in our database, please use another one")
            return render(request, 'authentication/register.html', context, status=409)

        if context['has_error']:
            return render(request, 'authentication/register.html', context)
        
        user = User.objects.create_user(username=username, email=email)
        user.set_password(password)
        user.save()

        # send_activation_email(user, request)

        messages.add_message(request, messages.SUCCESS, "Registration Succesful! You may login")

        return redirect('login')
    
    return render(request, 'authentication/register.html')


# @auth_user_should_not_access
def create_user(request):

    if request.method == "POST":
        context = {'has_error': False, 'data':request.POST}
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if len(password)<6:
            messages.add_message(request, messages.WARNING, "The password entered is too short")

            context['has_error'] = True
        
        if password != password2:
            messages.add_message(request, messages.WARNING, "The passwords entered do not match!")

            context['has_error'] = True

        # if not validate_email(email):
        #     messages.add_message(request, messages.WARNING, "Enter a valid email")

        #     context['has_error'] = True

        if not username:
            messages.add_message(request, messages.WARNING, "Enter your username!")

            context['has_error'] = True

        if User.objects.filter(username = username).exists():
            messages.add_message(request, messages.WARNING, "Username taken, please choose another one")
            return render(request, 'authentication/register.html', context, status=409)

        if User.objects.filter(email = email).exists():
            messages.add_message(request, messages.WARNING, "Email exists in our database, please use another one")
            return render(request, 'authentication/register.html', context, status=409)

        if context['has_error']:
            return render(request, 'authentication/register.html', context)
        
        user = User.objects.create_user(username=username, email=email)
        user.set_password(password)
        user.save()

        # send_activation_email(user, request)

        messages.add_message(request, messages.SUCCESS, "Registration Succesful! You may login")

        return redirect('all-users')
    
    return render(request, 'authentication/create-user.html')


    
@auth_user_should_not_access
def login_user(request):
    if request.user.is_authenticated:
        return redirect(reverse('home'))

    if request.method == 'POST':
        context = {'data': request.POST}
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)


        # if not user.is_email_verified:
        #     messages.add_message(request, messages.WARNING, 'Email is NOT Verified, check email inbox or spam')

        #     return render(request, 'authentication/login.html', context)


        if not user:
            messages.add_message(request, messages.WARNING, 'Invalid credentials')

            return render(request, 'authentication/login.html', context)
        
        login(request, user)
        messages.add_message(request, messages.WARNING, f'Welcome {user.username}')

        """
         Redirects users based on whether they are in the admins group
        """
        return redirect(reverse('home'))
        



    return render(request, 'authentication/login.html')

def logout_user(request):

    logout(request)
    messages.add_message(request, messages.INFO, 'Successfully logged out!')

    return redirect(reverse('login'))

def get_users(request):
    users = User.objects.all()
    return render(request, 'dashboard/users-list.html', {'users': users})



def user_edit(request, id):
    user = get_object_or_404(User, id=id)  # Fetch the user by id

    if request.method == "POST":
        context = {'has_error': False, 'data': request.POST}
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        # Validate the inputs as before
        if len(password) < 6:
            messages.add_message(request, messages.WARNING, "The password entered is too short")
            context['has_error'] = True
        
        if password != password2:
            messages.add_message(request, messages.WARNING, "The passwords entered do not match!")
            context['has_error'] = True

        # to be done later
        # if not validate_email(email):
        #     messages.add_message(request, messages.WARNING, "Enter a valid email")
        #     context['has_error'] = True

        if not username:
            messages.add_message(request, messages.WARNING, "Enter your username!")
            context['has_error'] = True

        # Check if the username or email is taken by another user
        if User.objects.exclude(id=user.id).filter(username=username).exists():
            messages.add_message(request, messages.WARNING, "Username taken, please choose another one")
            context['has_error'] = True

        if User.objects.exclude(id=user.id).filter(email=email).exists():
            messages.add_message(request, messages.WARNING, "Email exists in our database, please use another one")
            context['has_error'] = True

        if context['has_error']:
            return render(request, 'authentication/edit_user.html', context)

        # Update user details
        user.username = username
        user.email = email
        if password:
            user.set_password(password)
        user.save()

        messages.add_message(request, messages.SUCCESS, "User details updated successfully!")
        return redirect('user_detail', id=user.id)  # Redirect to the user's detail page

    # If it's a GET request, show the user's details for editing
    context = {
        'user': user
    }
    return render(request, 'authentication/edit-user.html', context)



def delete_user(request, id):
    # Make sure only authorized users can delete
    if request.user.is_authenticated:
        user_to_delete = get_object_or_404(User, pk=id)
        user_to_delete.delete()
        messages.add_message(request, messages.SUCCESS, "User details updated successfully!")
    else:
        messages.add_message(request, messages.WARNING, "Error deleting user")

    return redirect(reverse('all-users'))


# def activate_user(request, uidb64, token):
    
#     try:
#         uid = force_str(urlsafe_base64_decode(uidb64))

#         user = User.objects.get(pk=uid)

#     except Exception as e:
#         user = None

#     if user and generate_token.check_token(user, token):
#         user.is_email_verified =True
#         user.save()

#         messages.add_message(request, messages.SUCCESS, "Email activated succesfully!, You may login.")

#         return redirect(reverse('login'))
    
#     return render(request, 'authentication/activate-failed.html', {'user':user})

    