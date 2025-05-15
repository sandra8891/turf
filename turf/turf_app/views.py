from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings
import random
from datetime import datetime, timedelta, time
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
            
            if user.is_superuser:
                return redirect('admin_index')
            else:
                return redirect('index')
        else:
            messages.error(request, "Invalid credentials.")
    
    return render(request, 'login.html')

# def adminindex(request):
#     if not request.user.is_authenticated:
#         messages.error(request, "You need to be logged in to access this page.")
#         return redirect('login_view')
#     return render(request, 'adminindex.html')

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
        turfs = Turf.objects.all()
        return render(request, "home.html", {'turfs': turfs})
    return render(request, "index.html")


def is_admin(user):
    return user.is_superuser

def admin_index(request):
    # Get the recent bookings and turfs
    bookings = Booking.objects.select_related('slot').order_by('-slot__date')[:5]  # Sort by Slot's date field
    turfs = Turf.objects.all()  # Get all turfs

    # Calculate active users (users who have made at least one booking)
    active_users = User.objects.filter(booking__isnull=False).distinct().count()

    context = {
        'bookings': bookings,
        'turfs': turfs,
        'active_users': active_users,  # Add active users to context
    }

    return render(request, 'adminindex.html', context)

def admin_upload(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        location = request.POST.get('location')
        sport_type = request.POST.get('sport_type')
        open_time = request.POST.get('open_time')
        close_time = request.POST.get('close_time')
        image = request.FILES.get('image')

        try:
            open_time_24hr = datetime.strptime(open_time, "%I:%M %p").strftime("%H:%M")
            close_time_24hr = datetime.strptime(close_time, "%I:%M %p").strftime("%H:%M")
        except ValueError:
            messages.error(request, "Invalid time format. Please use HH:MM AM/PM.")
            return redirect('adminupload')

        Turf.objects.create(
            name=name,
            location=location,
            sport_types=sport_type,
            open_time=open_time_24hr,
            close_time=close_time_24hr,
            images=image
        )
        messages.success(request, "Turf uploaded successfully.")
        return redirect('admin_index')  # Redirect to admin_index page after upload

    return render(request, 'adminupload.html')

def home(request):
    turfs = Turf.objects.all()
    return render(request, 'home.html', {'turfs': turfs})

def turf_detail(request, turf_id):
    turf = get_object_or_404(Turf, pk=turf_id)
    context = {'turf': turf}
    return render(request, 'turf_detail.html', context)

def booking(request, turf_id):
    turf = get_object_or_404(Turf, pk=turf_id)
    
    # Get the selected date from query parameters or default to today
    selected_date_str = request.GET.get('date', timezone.now().date().isoformat())
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = timezone.now().date()

    # Ensure selected date is within the next 2 weeks
    today = timezone.now().date()
    max_date = today + timedelta(weeks=2)
    if selected_date < today:
        selected_date = today
    elif selected_date > max_date:
        selected_date = max_date

    # Generate a list of dates for the date selector (5 days at a time, within 2 weeks)
    dates = []
    start_date = max(today, selected_date - timedelta(days=2))  # Show 2 days before if possible
    for i in range(5):
        current_date = start_date + timedelta(days=i)
        if current_date > max_date:
            break
        dates.append({
            'date': current_date,
            'day': current_date.day,
            'month': current_date.strftime('%b').upper(),
            'weekday': current_date.strftime('%a').upper()
        })

    # Calculate previous and next dates for navigation (within 2 weeks)
    prev_date = selected_date - timedelta(days=5)
    if prev_date < today:
        prev_date = today
    next_date = selected_date + timedelta(days=5)
    if next_date > max_date:
        next_date = max_date

    # Get the first and last dates for disabling arrows
    first_date = dates[0]['date'] if dates else today
    last_date = dates[-1]['date'] if dates else max_date

    # Generate or fetch slots for the selected date
    slots = Slot.objects.filter(turf=turf, date=selected_date).order_by('start_time')
    
    # If no slots exist for the date, generate them for the full range between open_time and close_time
    if not slots.exists():
        open_time = datetime.strptime(str(turf.open_time), '%H:%M:%S').time()
        close_time = datetime.strptime(str(turf.close_time), '%H:%M:%S').time()
        current_time = datetime.combine(selected_date, open_time)
        close_datetime = datetime.combine(selected_date, close_time)

        while current_time < close_datetime:
            end_time = (current_time + timedelta(hours=1)).time()
            # Only create the slot if the end_time is before or equal to close_time
            if end_time <= close_time:
                Slot.objects.create(
                    turf=turf,
                    date=selected_date,
                    start_time=current_time.time(),
                    end_time=end_time,
                    is_booked=False
                )
            current_time += timedelta(hours=1)

        slots = Slot.objects.filter(turf=turf, date=selected_date).order_by('start_time')

    # Filter available slots
    booked_slots = Booking.objects.filter(slot__in=slots).values_list('slot', flat=True)
    available_slots = [slot for slot in slots if slot.id not in booked_slots]

    context = {
        'turf': turf,
        'dates': dates,
        'selected_date': selected_date,
        'available_slots': available_slots,
        'prev_date': prev_date,
        'next_date': next_date,
        'first_date': first_date,
        'last_date': last_date,
    }
    return render(request, 'booking.html', context)

def book_slot(request, slot_id):
    slot = get_object_or_404(Slot, pk=slot_id)
    
    if slot.is_booked:
        return redirect('turf_detail', turf_id=slot.turf.id)

    if request.user.is_authenticated:
        Booking.objects.create(user=request.user, slot=slot, sport=slot.turf.sport_types, players=6)
        slot.is_booked = True
        slot.save()
        return redirect('turf_detail', turf_id=slot.turf.id)
    else:
        return redirect('login')
    
    
@login_required
def booking_details(request, slot_id):
    slot = get_object_or_404(Slot, pk=slot_id)

    # Redirect if slot is already booked
    if slot.is_booked:
        return redirect('turf_detail', turf_id=slot.turf.id)

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')

        # Basic validation
        if not username or not email or not phone_number:
            messages.error(request, 'Please provide all required fields.')
            return render(request, 'booking_details.html', {'slot': slot})

        # Optional: Validate phone number format (e.g., 10 digits)
        if not phone_number.isdigit() or len(phone_number) < 10:
            messages.error(request, 'Please enter a valid phone number.')
            return render(request, 'booking_details.html', {'slot': slot})

        # Create a booking and mark the slot as booked
        booking = Booking.objects.create(
            user=request.user,
            slot=slot,
            address=username,  # Storing username in address field
            email=email,       # Assuming Booking model has an email field
            phone_number=phone_number,
            sport=slot.turf.sport_types,
            players=6
        )

        slot.is_booked = True
        slot.save()

        return redirect('payment', booking_id=booking.id)

    return render(request, 'booking_details.html', {'slot': slot})






def recent_bookings(request):
    bookings = Booking.objects.select_related('slot').order_by('-slot__date')[:10]

    return render(request, 'recent_bookings.html', {'bookings': bookings})


def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def edit_turf(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id)

    if request.method == 'POST':
        # Retrieve form data
        turf.name = request.POST.get('name')
        turf.location = request.POST.get('location')
        turf.sport_types = request.POST.get('sport_type')
        open_time = request.POST.get('open_time')
        close_time = request.POST.get('close_time')

        # Validate required fields
        if not all([turf.name, turf.location, turf.sport_types, open_time, close_time]):
            messages.error(request, "All fields are required.")
            return render(request, 'edit_turf.html', {'turf': turf})

        # Handle time fields
        try:
            # If using <input type="time">, the format is typically HH:MM (24-hour)
            turf.open_time = datetime.strptime(open_time, "%H:%M").time()
            turf.close_time = datetime.strptime(close_time, "%H:%M").time()
        except ValueError:
            messages.error(request, "Invalid time format. Please use HH:MM (e.g., 14:30).")
            return render(request, 'edit_turf.html', {'turf': turf})

        # Handle image upload
        if request.FILES.get('image'):
            turf.images = request.FILES['image']

        # Save the updated turf
        try:
            turf.save()
            messages.success(request, "Turf updated successfully.")
            return redirect('admin_index')
        except Exception as e:
            messages.error(request, f"Error saving turf: {str(e)}")
            return render(request, 'edit_turf.html', {'turf': turf})

    return render(request, 'edit_turf.html', {'turf': turf})

@user_passes_test(is_admin)
def delete_turf(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id)
    turf.delete()
    messages.success(request, "Turf deleted successfully.")
    return redirect('admin_index')




def list_turfs(request):
    turfs = Turf.objects.all()
    return render(request, 'list_turfs.html', {'turfs': turfs})





from django.db.models import Q

def search_turfs(request):
    query = request.GET.get('q', '')  # Get the search query from the input field
    turfs = Turf.objects.all()

    if query:
        # Filter turfs by name or location (case-insensitive)
        turfs = turfs.filter(
            Q(name__icontains=query) | Q(location__icontains=query)
        )

    context = {
        'turfs': turfs,
        'query': query,  # Pass the query to display in the template
    }
    return render(request, 'list_turfs.html', context)\
        
        
        
        
@login_required
def profile(request):
    user = request.user
    # Get the latest booking for phone number (if exists)
    latest_booking = Booking.objects.filter(user=user).order_by('-created_at').first()
    
    context = {
        'username': user.username,
        'email': user.email,
        'phone_number': latest_booking.phone_number if latest_booking else "Not provided",
    }
    return render(request, 'profile.html', context)