from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
from django.urls import reverse
import pytz
from .models import PasswordReset
from django.views.decorators.csrf import csrf_exempt
#from .models import Event
#from .forms import EventForm
from .models import *
from django.urls import reverse
#from .forms import EventForm
from django.shortcuts import get_object_or_404




@login_required
def Home(request):
    return render(request, 'index.html')

def Register(request):

    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        user_data_has_error = False

        if User.objects.filter(username=username).exists():
            user_data_has_error = True
            messages.error(request, "Username already exists")

        if User.objects.filter(email=email).exists():
            user_data_has_error = True
            messages.error(request, "Email already exists")

        if len(password) < 5:
            user_data_has_error = True
            messages.error(request, "Password must be at least 5 characters")

        if password != confirm_password:
            user_data_has_error = True
            messages.error(request, "Password do not match")

        if user_data_has_error:
            return redirect('register')
        else:
            new_user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email, 
                username=username,
                password=password
            )            
            messages.success(request, "Account created. Login now")

            email_body = f"Thank you for opening an account with EventVibe.\nWe're thrilled to have you as part of our growing community!"
            email_message = EmailMessage(
                " Welcome to EventVibes - We're Excited to Have You!",  
                email_body,
                settings.EMAIL_HOST_USER, 
                [email] 
            )

            email_message.fail_silently = True
            email_message.send()

            return redirect('login')

    return render(request, 'register.html')

def LoginView(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            return redirect('home')
        
        else:
            messages.error(request, "Invalid login credentials")
            return redirect('login')

    return render(request, 'login.html')

def LoginView(request):
    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid login credentials!")
            return redirect('login')

    return render(request, 'login.html')

def LogoutView(request):
    logout(request)
    return redirect ('login')



def ForgetPassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        users = User.objects.filter(email=email)
        if users.exists():
            for user in users:
                # Create a PasswordReset instance for each user
                reset_instance = PasswordReset(user=user)
                reset_instance.save()
                # Send a password reset email to each user (replace with your email logic)
                send_password_reset_email(user)
            return render(request, 'password_reset_sent.html')
        else:
            return render(request, 'forget_password.html', {'error': 'No user with that email found.'})
    return render(request, 'forget_password.html')

def send_password_reset_email(user):
    # Your email sending logic here
    pass


#def ForgetPassword(request):

#    if request.method == "POST":
 #       email = request.POST.get('email')

  #      try:
   #         password_reset_url = reverse('reset-password', kwargs={'reset_id': new_password_reset.reset_id})
            ##full_password_reset_url = f'{request.get_scheme()}://{request.get_host()}{password_reset_url}'
       #     full_password_reset_url = f'{request.scheme}://{request.get_host()}{password_reset_url}'
            #email_body = f'Reset your password using the link below:\n\n\n{full_password_reset_url}'
            #email_message = EmailMessage(
             #   'Reset your password',  
              #  email_body,
               # settings.EMAIL_HOST_USER, 
               # [email] 
      #      )

            #email_message.fail_silently = True
            #email_message.send()

            #return redirect('password-reset-sent', reset_id=new_password_reset.reset_id)

        #except User.DoesNotExist:
         #   messages.error(request, f"No user with email '{email}' found")
          #  return redirect('forget-password')
        
   # return render(request, 'forget_password.html')#

def PasswordResetSent(request, reset_id):
    if PasswordReset.objects.filter(reset_id=reset_id).exists():
        return render(request, 'password_reset_sent.html')
    else:
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')
    
def ResetPassword(request, reset_id):
    try:
        password_reset = PasswordReset.objects.get(reset_id=reset_id)  # Fetching the PasswordReset object

        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            passwords_have_error = False

            if password != confirm_password:
                passwords_have_error = True
                messages.error(request, 'Passwords do not match')

            if len(password) < 6:
                passwords_have_error = True
                messages.error(request, 'Password must be at least 6 characters')

            expiration_time = password_reset.created_when + timezone.timedelta(minutes=10)
            if timezone.now() > expiration_time:
                passwords_have_error = True
                messages.error(request, 'Reset link has expired')
                password_reset.delete()
            if not passwords_have_error:
                user = password_reset.user
                user.set_password(password)
                user.save()

                password_reset.delete()

                messages.success(request, 'Password reset successfully. Please login.')
                return redirect('login')

            return redirect('reset-password', reset_id=reset_id)

    except PasswordReset.DoesNotExist:
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')

    return render(request, 'reset_password.html')

def dashboard(request):
    return render(request, 'dashboard.html')