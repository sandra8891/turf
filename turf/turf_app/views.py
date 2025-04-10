from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings
import random
from datetime import datetime, timedelta
from .models import *

def signup(request):
    if request.POST:
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confpassword')

        if not username or not email or not password or not confirmpassword:
            messages.error(request, 'All fields are required.')
        elif confirmpassword != password:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, "Signup successful! You can now log in.")
            return redirect('login')

    return render(request, "signup.html")

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            request.session['username'] = username
            messages.success(request, "User logged in successfully!")
            if user.is_superuser:
                return redirect('adminindex')
            else:
                return redirect('index')
        else:
            messages.error(request, "Invalid credentials.")
    
    return render(request, 'login.html')

def adminindex(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access this page.")
        return redirect('login_view')
    return render(request, 'adminindex.html')

def index(request): 
    return render(request, "index.html")

def logoutuser(request):
    logout(request)
    request.session.flush()
    return redirect('login_view')

def logoutadmin(request):
    logout(request)
    request.session.flush()
    return redirect('index')

def getusername(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            request.session['email'] = user.email
            return redirect('verifyotp')
        except User.DoesNotExist:
            messages.error(request, "Username does not exist.")
            return redirect('forgotpassword')

    return render(request, 'getusername.html')



def verifyotp(request):
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        actual_otp = request.session.get('otp')
        otp_time = request.session.get('otp_time')

        if not actual_otp or not otp_time:
            messages.error(request, "OTP session expired. Please try again.")
            return redirect('forgotpassword')

        # Check if OTP has expired (5 minutes)
        if datetime.now() > datetime.strptime(otp_time, '%Y-%m-%d %H:%M:%S') + timedelta(minutes=5):
            messages.error(request, "OTP expired. Please try again.")
            return redirect('forgotpassword')

        if otp_entered == str(actual_otp):
            messages.success(request, "OTP verified. You can now reset your password.")
            return redirect('passwordreset')
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    else:
        # Generate and send OTP
        otp = random.randint(100000, 999999)
        email = request.session.get('email')
        if email:
            request.session['otp'] = otp
            request.session['otp_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            send_mail(
                'Your OTP Code',
                f'Your OTP code is {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
        else:
            messages.error(request, "Session expired or email missing. Please try again.")
            return redirect('forgotpassword')

    return render(request, 'verifyotp.html')




def passwordreset(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confpassword = request.POST.get('confpassword')

        if password != confpassword:
            messages.error(request, "Passwords do not match.")
            return redirect('passwordreset')

        email = request.session.get('email')
        if not email:
            messages.error(request, "Session expired or email not found.")
            return redirect('forgotpassword')

        try:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            messages.success(request, "Password reset successful. You can now log in.")
            return redirect('login_view')
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('forgotpassword')

    return render(request, 'passwordreset.html')
