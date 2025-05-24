from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import random
from django.urls import reverse
from django.core.mail import send_mail
import razorpay
from datetime import datetime, timedelta, time
from .models import Turf, Slot, Booking,PaymentStatus,TurfImage
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
    # Get recent bookings and turfs
    bookings = Booking.objects.select_related('slot').order_by('-created_at')[:5]
    turfs = Turf.objects.all()
    
    # Calculate active users
    active_users = User.objects.filter(booking__isnull=False).distinct().count()
    
    # Count bookings from the last 7 days
    recent_bookings_count = Booking.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()

    context = {
        'bookings': bookings,
        'turfs': turfs,
        'active_users': active_users,
        'recent_bookings_count': recent_bookings_count,
    }
    return render(request, 'adminindex.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def admin_upload(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        location = request.POST.get('location')
        sport_types = request.POST.get('sport_types')
        open_time = request.POST.get('open_time')
        close_time = request.POST.get('close_time')
        price = request.POST.get('price')
        images = request.FILES.getlist('images')  # Get list of uploaded images

        # Validate required fields
        if not all([name, location, sport_types, open_time, close_time, price]):
            messages.error(request, "All fields are required.")
            return redirect('admin_upload')

        # Validate number of images
        if not images:
            messages.error(request, "At least one image is required.")
            return redirect('admin_upload')
        if len(images) > 5:
            messages.error(request, "You can upload a maximum of 5 images.")
            return redirect('admin_upload')

        # Validate time format
        try:
            open_time_24hr = datetime.strptime(open_time, "%I:%M %p").strftime("%H:%M")
            close_time_24hr = datetime.strptime(close_time, "%I:%M %p").strftime("%H:%M")
        except (ValueError, TypeError):
            messages.error(request, "Invalid time format. Please use HH:MM AM/PM (e.g., 06:00 AM).")
            return redirect('admin_upload')

        # Validate price
        try:
            price = float(price)
            if price < 0:
                messages.error(request, "Price cannot be negative.")
                return redirect('admin_upload')
        except (ValueError, TypeError):
            messages.error(request, "Invalid price format. Please enter a valid number.")
            return redirect('admin_upload')

        # Save turf
        turf = Turf.objects.create(
            name=name,
            location=location,
            sport_types=sport_types,
            open_time=open_time_24hr,
            close_time=close_time_24hr,
            price=price
        )

        # Save images with additional logging
        for image in images:
            if image.content_type.startswith('image'):
                TurfImage.objects.create(turf=turf, image=image)
                print(f"Saved image: {image.name} for turf {turf.name} (ID: {turf.id})")
            else:
                messages.warning(request, f"Skipped {image.name}: Not a valid image file.")

        messages.success(request, "Turf uploaded successfully with images.")
        return redirect('admin_index')

    return render(request, 'adminupload.html')
def home(request):
    turfs = Turf.objects.all()
    return render(request, 'home.html', {'turfs': turfs})

def turf_detail(request, turf_id):
    turf = get_object_or_404(Turf, pk=turf_id)
    images = turf.images.all()  # Get all images for the turf
    context = {'turf': turf, 'images': images}
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
        messages.error(request, 'This slot is already booked.')
        return redirect('turf_detail', turf_id=slot.turf.id)

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')

        # Basic validation
        if not username or not email or not phone_number:
            messages.error(request, 'Please provide all required fields.')
            return render(request, 'booking_details.html', {'slot': slot})

        # Validate phone number format (e.g., 10 digits)
        if not phone_number.isdigit() or len(phone_number) < 10:
            messages.error(request, 'Please enter a valid phone number.')
            return render(request, 'booking_details.html', {'slot': slot})

        # Create a booking (do not mark slot as booked yet)
        booking = Booking.objects.create(
            user=request.user,
            slot=slot,
            address=username,  # Storing username in address field
            email=email,
            phone_number=phone_number,
            sport=slot.turf.sport_types,
            players=6,
            total_amount=slot.turf.price,  # Set total_amount from turf price
            status=PaymentStatus.PENDING  # Explicitly set status
        )

        return redirect('order_payment', booking_id=booking.id)

    return render(request, 'booking_details.html', {'slot': slot})



def recent_bookings(request):
    if request.user.is_superuser:
        # Admins see all bookings with related slot and turf data
        bookings = Booking.objects.select_related('slot__turf').order_by('-created_at')[:10]
    else:
        # Regular users see only their bookings
        bookings = Booking.objects.filter(user=request.user).select_related('slot__turf').order_by('-created_at')[:10]
    
    context = {
        'bookings': bookings,
        'is_admin': request.user.is_superuser,
    }
    return render(request, 'recent_bookings.html', context)

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def edit_turf(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id)

    if request.method == 'POST':
        # Retrieve form data
        turf.name = request.POST.get('name')
        turf.location = request.POST.get('location')
        turf.sport_types = request.POST.get('sport_types')
        open_time = request.POST.get('open_time')
        close_time = request.POST.get('close_time')
        price = request.POST.get('price')
        images = request.FILES.getlist('images')  # Get list of uploaded images

        # Validate required fields
        if not all([turf.name, turf.location, turf.sport_types, open_time, close_time, price]):
            messages.error(request, "All fields are required.")
            return render(request, 'edit_turf.html', {'turf': turf})

        # Handle time fields
        try:
            turf.open_time = datetime.strptime(open_time, "%H:%M").time()
            turf.close_time = datetime.strptime(close_time, "%H:%M").time()
        except ValueError:
            messages.error(request, "Invalid time format. Please use HH:MM (e.g., 14:30).")
            return render(request, 'edit_turf.html', {'turf': turf})

        # Handle price field
        try:
            turf.price = float(price)
            if turf.price < 0:
                messages.error(request, "Price cannot be negative.")
                return render(request, 'edit_turf.html', {'turf': turf})
        except (ValueError, TypeError):
            messages.error(request, "Invalid price format. Please enter a valid number.")
            return render(request, 'edit_turf.html', {'turf': turf})

        # Handle image uploads (append new images instead of deleting existing ones)
        if images:
            existing_images_count = turf.images.count()
            new_images_count = len(images)
            if existing_images_count + new_images_count > 5:
                messages.error(request, "Total images cannot exceed 5.")
                return render(request, 'edit_turf.html', {'turf': turf})
            for image in images:
                if image.content_type.startswith('image'):
                    TurfImage.objects.create(turf=turf, image=image)
                    print(f"Added image: {image.name} to turf {turf.name} (ID: {turf.id})")
                else:
                    messages.warning(request, f"Skipped {image.name}: Not a valid image file.")

        # Save the updated turf
        try:
            turf.save()
            messages.success(request, "Turf updated successfully.")
            return redirect('admin_index')
        except Exception as e:
            messages.error(request, f"Error saving turf: {str(e)}")
            return render(request, 'edit_turf.html', {'turf': turf})

    images = turf.images.all()  # Pass current images to template
    return render(request, 'edit_turf.html', {'turf': turf, 'images': images})

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

@login_required
def booking_history(request):
    # Fetch bookings for the logged-in user, ordered by most recent
    bookings = Booking.objects.filter(user=request.user).select_related('slot').order_by('-created_at')
    context = {
        'bookings': bookings,
    }
    return render(request, 'booking_history.html', context)


@login_required
def order_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

    # Create Razorpay order
    try:
        razorpay_order = client.order.create({
            'amount': int(booking.total_amount * 100),  # Amount in paise
            'currency': 'INR',
            'payment_capture': '1'  # Auto-capture payment
        })

        # Save Razorpay order ID to booking
        booking.provider_order_id = razorpay_order['id']
        booking.save()

        # Build callback URL
        callback_url = request.build_absolute_uri(reverse('razorpay_callback'))

        return render(request, 'payment.html', {
            'booking': booking,
            'razorpay_key': settings.RAZOR_KEY_ID,
            'razorpay_order_id': razorpay_order['id'],
            'amount': int(booking.total_amount * 100),
            'currency': 'INR',
            'callback_url': callback_url,
            'name': booking.user.username,
            'description': f'Payment for booking {booking.id}',
            'prefill': {
                'name': booking.user.username,
                'email': booking.email,
                'contact': booking.phone_number,
            }
        })
    except Exception as e:
        messages.error(request, f'Error creating payment order: {str(e)}')
        return redirect('booking_details', slot_id=booking.slot.id)



@csrf_exempt
def razorpay_callback(request):
    client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
    if "razorpay_signature" in request.POST:
        payment_id = request.POST.get('razorpay_payment_id', '')
        provider_order_id = request.POST.get('razorpay_order_id', '')
        signature_id = request.POST.get('razorpay_signature', '')
        try:
            booking = Booking.objects.get(provider_order_id=provider_order_id)
            booking.payment_id = payment_id
            booking.signature_id = signature_id
            params_dict = {
                'razorpay_order_id': provider_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature_id
            }
            try:
                client.utility.verify_payment_signature(params_dict)
                booking.status = PaymentStatus.COMPLETED
                booking.slot.is_booked = True  # Mark slot as booked
                booking.slot.save()
                booking.save()
                # Send confirmation email
                send_mail(
                    subject='Booking Confirmation',
                    message=(
                        f'Dear {booking.user.username},\n\n'
                        f'Your booking for {booking.slot.turf.name} on {booking.slot.date} '
                        f'from {booking.slot.start_time.strftime("%I:%M %p")} to '
                        f'{booking.slot.end_time.strftime("%I:%M %p")} has been confirmed.\n'
                        f'Total Amount: ₹{booking.total_amount}\n\n'
                        f'Thank you for using PlaySpots!'
                    ),
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[booking.email],
                    fail_silently=True,
                )
                messages.success(request, 'Payment successful! Your booking is confirmed.')
                return redirect('booking_history')  # Redirect to booking_history instead
            except razorpay.errors.SignatureVerificationError:
                booking.status = PaymentStatus.CANCELLED
                booking.slot.is_booked = False
                booking.slot.save()
                booking.save()
                messages.error(request, 'Payment verification failed.')
                return redirect('booking_history')
        except Booking.DoesNotExist:
            messages.error(request, 'Booking not found.')
            return redirect('booking_history')
    else:
        # Handle failed payment
        error_metadata = request.POST.get('error[metadata]', '{}')
        try:
            import json
            error_metadata = json.loads(error_metadata)
            provider_order_id = error_metadata.get('order_id', '')
            booking = Booking.objects.get(provider_order_id=provider_order_id)
            booking.status = PaymentStatus.CANCELLED
            booking.slot.is_booked = False
            booking.slot.save()
            booking.save()
            messages.error(request, 'Payment failed. Please try again.')
            return redirect('booking_history')
        except (Booking.DoesNotExist, ValueError):
            messages.error(request, 'Booking not found or invalid error metadata.')
            return redirect('booking_history')