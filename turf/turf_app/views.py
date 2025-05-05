from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings
import random
from datetime import datetime, timedelta
from .models import *
from .models import Turf, Slot, Booking
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone


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
            
            # Redirect to 'adminindex' if the user is an admin, otherwise redirect to 'index'
            if user.is_superuser:
                return redirect('adminindex')  # Redirect to admin index page
            else:
                return redirect('index')  # Redirect to normal user index page
        else:
            messages.error(request, "Invalid credentials.")
    
    return render(request, 'login.html')


def adminindex(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access this page.")
        return redirect('login_view')
    return render(request, 'adminindex.html')

# def index(request): 
#     if request.user.is_authenticated:
#         return render(request, "home.html")
#     return render(request, "index.html")

 
def logoutuser(request):
    logout(request)
    request.session.flush()
    return redirect('index')

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
    if request.POST:
        otp = request.POST.get('otp')
        otp1 = request.session.get('otp')
        otp_time_str = request.session.get('otp_time') 

    
        if otp_time_str:
            otp_time = datetime.fromisoformat(otp_time_str)
            otp_expiry_time = otp_time + timedelta(minutes=5)
            if datetime.now() > otp_expiry_time:
                messages.error(request, 'OTP has expired. Please request a new one.')
                del request.session['otp']
                del request.session['otp_time']
                return redirect('verifyotp')

        if otp == otp1:
            del request.session['otp']
            del request.session['otp_time']
            return redirect('passwordreset')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    
    otp = ''.join(random.choices('123456789', k=6))
    request.session['otp'] = otp
    request.session['otp_time'] = datetime.now().isoformat()
    message = f'Your email verification code is: {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [request.session.get('email')]
    send_mail('Email Verification', message, email_from, recipient_list)

    return render(request, "otp.html")



def passwordreset(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confpassword')

    
        if confirmpassword != password:
            messages.error(request, "Passwords do not match.")
        else:
            email = request.session.get('email')
            try:
                user = User.objects.get(email=email)

                user.set_password(password)
                user.save()

                del request.session['email']
                messages.success(request, "Your password has been reset successfully.")
                
                user = authenticate(username=user.username, password=password)
                if user is not None:
                    login(request, user)

                return redirect('loginuser')
            except User.DoesNotExist:
                messages.error(request, "No user found with that email address.")
                return redirect('getusername')

    return render(request, "passwordreset.html")


def index(request): 
    if request.user.is_authenticated:
        return render(request, "home.html")
    return render(request, "index.html")





################################




def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def admin_index(request):
    turfs = Turf.objects.all()
    return render(request, 'adminindex.html', {'turfs': turfs})





def admin_upload(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        location = request.POST.get('location')
        sport_type = request.POST.get('sport_type')
        open_time = request.POST.get('open_time')
        close_time = request.POST.get('close_time')
        image = request.FILES.get('image')

        # Convert open_time and close_time from 12-hour format (if provided) to 24-hour format
        try:
            open_time_24hr = datetime.strptime(open_time, "%I:%M %p").strftime("%H:%M")
            close_time_24hr = datetime.strptime(close_time, "%I:%M %p").strftime("%H:%M")
        except ValueError:
            # Handle invalid time format (e.g., if the input doesn't match expected format)
            messages.error(request, "Invalid time format. Please use HH:MM AM/PM.")
            return redirect('adminupload')

        # Create the Turf object with the 24-hour format times
        Turf.objects.create(
            name=name,
            location=location,
            sport_types=sport_type,
            open_time=open_time_24hr,  # Save as 24-hour format
            close_time=close_time_24hr,  # Save as 24-hour format
            images=image
        )
        messages.success(request, "Turf uploaded successfully.")
        return redirect('home')

    return render(request, 'adminupload.html')



    return render(request, 'adminupload.html')
def home(request):
    turfs = Turf.objects.all()
    return render(request, 'home.html', {'turfs': turfs})






def turf_detail(request, turf_id):
    turf = get_object_or_404(Turf, pk=turf_id)
    
    # Get all slots for the turf for the next 2 weeks
    current_date = timezone.now().date()
    end_date = current_date + timezone.timedelta(weeks=2)
    slots = Slot.objects.filter(turf=turf, date__range=[current_date, end_date]).order_by('date', 'start_time')

    # Check if a slot is already booked
    booked_slots = Booking.objects.filter(slot__in=slots).values_list('slot', flat=True)
    available_slots = [slot for slot in slots if slot.id not in booked_slots]

    context = {
        'turf': turf,
        'available_slots': available_slots,
    }
    
    return render(request, 'turf_detail.html', context)








def book_slot(request, slot_id):
    slot = get_object_or_404(Slot, pk=slot_id)
    
    # Check if the slot is already booked
    if slot.is_booked:
        return redirect('turf_detail', turf_id=slot.turf.id)

    # Create a booking if the slot is available
    if request.user.is_authenticated:
        Booking.objects.create(user=request.user, slot=slot, sport=slot.turf.sport_types, players=6)
        slot.is_booked = True  # Mark slot as booked
        slot.save()

        # Redirect back to turf details page
        return redirect('turf_detail', turf_id=slot.turf.id)
    else:
        return redirect('login')  # Redirect to login if the user is not logged in
