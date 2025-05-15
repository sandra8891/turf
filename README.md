# turf
the sports ground booking website is proposed for booking the turf in an easy and efficient way



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .models import Turf, Booking

def home(request):
turfs = Turf.objects.filter(availability=True)
return render(request, 'home.html', {'turfs': turfs})

def about(request):
return render(request, 'about.html')

def contact(request):
return render(request, 'contact.html')

def login_view(request):
if request.method == 'POST':
username = request.POST['username']
password = request.POST['password']
user = authenticate(request, username=username, password=password)
if user is not None:
login(request, user)
return redirect('admin_page')
else:
messages.error(request, 'Invalid credentials')
return render(request, 'login.html')

def logout_view(request):
logout(request)
return redirect('home')

@login_required
def change_password(request):
if request.method == 'POST':
form = PasswordChangeForm(user=request.user, data=request.POST)
if form.is_valid():
form.save()
messages.success(request, 'Password changed successfully')
return redirect('admin_page')
else:
messages.error(request, 'Please correct the errors below')
else:
form = PasswordChangeForm(user=request.user)
return render(request, 'change_password.html', {'form': form})

@login_required
def admin_page(request):
turf_count = Turf.objects.count()
booking_count = Booking.objects.count()
return render(request, 'admin_page.html', {'turf_count': turf_count, 'booking_count': booking_count})

@login_required
def dashboard(request):
return render(request, 'dashboard.html')

@login_required
def turf_list(request):
turfs = Turf.objects.all()
return render(request, 'turf_list.html', {'turfs': turfs})

def turf_detail(request, turf_id):
turf = get_object_or_404(Turf, id=turf_id)
return render(request, 'turf_detail.html', {'turf': turf})

@login_required
def add_turf(request):
if request.method == 'POST':
name = request.POST['name']
location = request.POST['location']
price = request.POST['price']
Turf.objects.create(name=name, location=location, price_per_hour=price)
return redirect('turf_list')
return render(request, 'turf_form.html')

@login_required
def edit_turf(request, turf_id):
turf = get_object_or_404(Turf, id=turf_id)
if request.method == 'POST':
turf.name = request.POST['name']
turf.location = request.POST['location']
turf.price_per_hour = request.POST['price']
turf.save()
return redirect('turf_list')
return render(request, 'turf_form.html', {'turf': turf})

@login_required
def delete_turf(request, turf_id):
turf = get_object_or_404(Turf, id=turf_id)
turf.delete()
return redirect('turf_list')

@login_required
def booking_list(request):
bookings = Booking.objects.all()
return render(request, 'booking_list.html', {'bookings': bookings})

def booking_detail(request, booking_id):
booking = get_object_or_404(Booking, id=booking_id)
return render(request, 'booking_detail.html', {'booking': booking})

@login_required
def add_booking(request):
if request.method == 'POST':
turf_id = request.POST['turf']
customer_name = request.POST['customer_name']
booking_date = request.POST['booking_date']
booking_time = request.POST['booking_time']
duration = request.POST['duration']
turf = get_object_or_404(Turf, id=turf_id)
Booking.objects.create(
turf=turf,
customer_name=customer_name,
booking_date=booking_date,
booking_time=booking_time,
duration=duration
)
return redirect('booking_list')
turfs = Turf.objects.filter(availability=True)
return render(request, 'booking_form.html', {'turfs': turfs})

@login_required
def edit_booking(request, booking_id):
booking = get_object_or_404(Booking, id=booking_id)
if request.method == 'POST':
booking.turf = get_object_or_404(Turf, id=request.POST['turf'])
booking.customer_name = request.POST['customer_name']
booking.booking_date = request.POST['booking_date']
booking.booking_time = request.POST['booking_time']
booking.duration = request.POST['duration']
booking.save()
return redirect('booking_list')
turfs = Turf.objects.filter(availability=True)
return render(request, 'booking_form.html', {'booking': booking, 'turfs': turfs})

@login_required
def delete_booking(request, booking_id):
booking = get_object_or_404(Booking, id=booking_id)
booking.delete()
return redirect('booking_list')

@login_required
def report_turfs(request):
turfs = Turf.objects.all()
return render(request, 'report_turfs.html', {'turfs': turfs})

@login_required
def report_bookings(request):
bookings = Booking.objects.all()
return render(request, 'report_bookings.html', {'bookings': bookings})

5. urls.py (turf_app)
Defining app-level URL routing
from django.urls import path
from . import views

urlpatterns = [
path('', views.home, name='home'),
path('about/', views.about, name='about'),
path('contact/', views.contact, name='contact'),
path('login/', views.login_view, name='login'),
path('logout/', views.logout_view, name='logout'),
path('change-password/', views.change_password, name='change_password'),
path('admin-page/', views.admin_page, name='admin_page'),
path('dashboard/', views.dashboard, name='dashboard'),
path('turfs/', views.turf_list, name='turf_list'),
path('turfs/int:turf_id/', views.turf_detail, name='turf_detail'),
path('turfs/add/', views.add_turf, name='add_turf'),
path('turfs/edit/int:turf_id/', views.edit_turf, name='edit_turf'),
path('turfs/delete/int:turf_id/', views.delete_turf, name='delete_turf'),
path('bookings/', views.booking_list, name='booking_list'),
path('bookings/int:booking_id/', views.booking_detail, name='booking_detail'),
path('bookings/add/', views.add_booking, name='add_booking'),
path('bookings/edit/int:booking_id/', views.edit_booking, name='edit_booking'),
path('bookings/delete/int:booking_id/', views.delete_booking, name='delete_booking'),
path('reports/turfs/', views.report_turfs, name='report_turfs'),
path('reports/bookings/', views.report_bookings, name='report_bookings'),
]

6. base.html
Base template for all pages
<meta charset="UTF-8"> <meta name="viewport" content="width=device-width, initial-scale=1.0"> <title>Turf Booking System</title> <link rel="stylesheet" href="/static/css/styles.css">
Home About Us Contact Us {% if user.is_authenticated %} Admin Page Logout {% else %} Login {% endif %}
{% block content %} {% endblock %}
7. home.html
Home page template with animated slider
{% extends 'base.html' %}

{% block content %}

Welcome to Turf Booking System
Book your turf easily with us!

Turf 1 - Great for Football
Turf 2 - Perfect for Cricket
Turf 3 - Ideal for Events
Available Turfs
{% for turf in turfs %}
{{ turf.name }}
Location: {{ turf.location }}

Price: ₹{{ turf.price_per_hour }}/hour

View Details
{% empty %}
No turfs available.

{% endfor %}
{% endblock %}
8. about.html
About Us page template
{% extends 'base.html' %}

{% block content %}

About Us
We are a turf booking platform dedicated to providing the best experience for our users.

{% endblock %}
9. contact.html
Contact Us page template
{% extends 'base.html' %}

{% block content %}

Contact Us
Email: support@turfbooking.com

Phone: +91 123-456-7890

{% endblock %}
10. login.html
Login page template
{% extends 'base.html' %}

{% block content %}

Admin Login
<form method="post"> {% csrf_token %} <label for="username">Username:</label> <input type="text" id="username" name="username" required><br> <label for="password">Password:</label> <input type="password" id="password" name="password" required><br> <button type="submit">Login</button> </form> {% if messages %} {% for message in messages %}
{{ message }}

{% endfor %} {% endif %} {% endblock %}
11. change_password.html
Change Password template
{% extends 'base.html' %}

{% block content %}

Change Password
<form method="post"> {% csrf_token %} {{ form.as_p }} <button type="submit">Change Password</button> </form> {% if messages %} {% for message in messages %}
{{ message }}

{% endfor %} {% endif %} {% endblock %}
12. admin_page.html
Admin Page template
{% extends 'base.html' %}

{% block content %}

Admin Page
Total Turfs: {{ turf_count }}

Total Bookings: {{ booking_count }}

Turf Management
Manage Turfs
Add New Turf
Booking Management
View Bookings
Add New Booking
Reports
Turf Report
Booking Report
Account
Change Password
Logout
{% endblock %}
13. dashboard.html
Admin dashboard template (simplified)
{% extends 'base.html' %}

{% block content %}

Admin Dashboard
Welcome to the admin dashboard. Use the Admin Page for all management tasks.

Go to Admin Page {% endblock %}
14. turf_list.html
Turf list template
{% extends 'base.html' %}

{% block content %}

Turf List
Add New Turf {% for turf in turfs %} {% endfor %}

Name	Location	Price/Hour	Availability	Actions
{{ turf.name }}	{{ turf.location }}	₹{{ turf.price_per_hour }}	{{ turf.availability|yesno:"Yes,No" }}	
                    Edit
                    Delete
                
{% endblock %}
15. turf_detail.html
Turf detail template for customers
{% extends 'base.html' %}

{% block content %}

{{ turf.name }}
Location: {{ turf.location }}

Price: ₹{{ turf.price_per_hour }}/hour

Availability: {{ turf.availability|yesno:"Yes,No" }}

{% endblock %}
16. booking_list.html
Booking list template
{% extends 'base.html' %}

{% block content %}

Booking List
Add New Booking {% for booking in bookings %} {% endfor %}

Customer	Turf	Date	Time	Duration	Actions
{{ booking.customer_name }}	{{ booking.turf.name }}	{{ booking.booking_date }}	{{ booking.booking_time }}	{{ booking.duration }} hours	
                    Edit
                    Delete
                
{% endblock %}
17. booking_detail.html
Booking detail template for customers
{% extends 'base.html' %}

{% block content %}

Booking Details
Customer: {{ booking.customer_name }}

Turf: {{ booking.turf.name }}

Date: {{ booking.booking_date }}

Time: {{ booking.booking_time }}

Duration: {{ booking.duration }} hours

{% endblock %}
18. turf_form.html
Turf add/edit form template
{% extends 'base.html' %}

{% block content %}

{% if turf %}Edit Turf{% else %}Add Turf{% endif %}
<form method="post"> {% csrf_token %} <label for="name">Name:</label> <input type="text" id="name" name="name" value="{% if turf %}{{ turf.name }}{% endif %}" required><br> <label for="location">Location:</label> <input type="text" id="location" name="location" value="{% if turf %}{{ turf.location }}{% endif %}" required><br> <label for="price">Price/Hour:</label> <input type="number" id="price" name="price" step="0.01" value="{% if turf %}{{ turf.price_per_hour }}{% endif %}" required><br> <button type="submit">Save</button> </form> {% endblock %}
19. booking_form.html
Booking add/edit form template
{% extends 'base.html' %}

{% block content %}

{% if booking %}Edit Booking{% else %}Add Booking{% endif %}
<form method="post"> {% csrf_token %} <label for="turf">Turf:</label> <select id="turf" name="turf" required> {% for turf in turfs %} <option value="{{ turf.id }}" {%="" if="" booking.turf.id="=" turf.id="" %}selected{%="" endif="" %}="">{{ turf.name }}</option> {% endfor %} </select><br> <label for="customer_name">Customer Name:</label> <input type="text" id="customer_name" name="customer_name" value="{% if booking %}{{ booking.customer_name }}{% endif %}" required><br> <label for="booking_date">Booking Date:</label> <input type="date" id="booking_date" name="booking_date" value="{% if booking %}{{ booking.booking_date }}{% endif %}" required><br> <label for="booking_time">Booking Time:</label> <input type="time" id="booking_time" name="booking_time" value="{% if booking %}{{ booking.booking_time }}{% endif %}" required><br> <label for="duration">Duration (hours):</label> <input type="number" id="duration" name="duration" value="{% if booking %}{{ booking.duration }}{% endif %}" required><br> <button type="submit">Save</button> </form> {% endblock %}
20. report_turfs.html
Turf report template
{% extends 'base.html' %}

{% block content %}

Turf Report
{% for turf in turfs %} {% endfor %}

Name	Location	Price/Hour	Availability
{{ turf.name }}	{{ turf.location }}	₹{{ turf.price_per_hour }}	{{ turf.availability|yesno:"Yes,No" }}
{% endblock %}
21. report_bookings.html
Booking report template
{% extends 'base.html' %}

{% block content %}

Booking Report
{% for booking in bookings %} {% endfor %}

Customer	Turf	Date	Time	Duration
{{ booking.customer_name }}	{{ booking.turf.name }}	{{ booking.booking_date }}	{{ booking.booking_time }}	{{ booking.duration }} hours
{% endblock %}
22. styles.css (static/css/styles.css)
CSS styling with animated slider
body {
font-family: Arial, sans-serif;
margin: 0;
padding: 0;
}

nav {
background-color: #333;
padding: 1rem;
}

nav a {
color: white;
margin-right: 1rem;
text-decoration: none;
}

.container {
padding: 2rem;
}

h1 {
color: #333;
}

table {
width: 100%;
border-collapse: collapse;
margin-top: 1rem;
}

th, td {
border: 1px solid #ddd;
padding: 0.5rem;
text-align: left;
}

th {
background-color: #f4f4f4;
}

form {
margin-top: 1rem;
}

form label {
display: block;
margin: 0.5rem 0;
}

form input, form select {
width: 100%;
padding: 0.5rem;
margin-bottom: 1rem;
}

form button {
background-color: #333;
color: white;
padding: 0.5rem 1rem;
border: none;
cursor: pointer;
}

.hero {
text-align: center;
padding: 3rem;
background-color: #f9f9f9;
}

.slider {
width: 100%;
overflow: hidden;
margin: 1rem 0;
}

.slides {
display: flex;
animation: slide 9s infinite;
}

.slide {
min-width: 100%;
padding: 1rem;
background-color: #ddd;
text-align: center;
font-size: 1.2rem;
}

@keyframes slide {
0% {
transform: translateX(0);
}
33% {
transform: translateX(-100%);
}
66% {
transform: translateX(-200%);
}
100% {
transform: translateX(0);
}
}

.turf-list {
display: flex;
flex-wrap: wrap;
gap: 1rem;
}

.turf-card {
border: 1px solid #ddd;
padding: 1rem;
width: 200px;
text-align: center;
}

.admin-stats {
margin-bottom: 2rem;
}

.admin-links h2 {
margin-top: 1rem;
font-size: 1.2rem;
}

.admin-links a {
display: block;
margin: 0.5rem 0;
}

Steps to Run the Project
Create the project directory and set up a virtual environment:
text

Copy
mkdir turf_booking_project
cd turf_booking_project
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install Django:
text

Copy
pip install django
Create the Django project and app:
text

Copy
django-admin startproject turf_booking_project .
python manage.py startapp turf_app
Copy the above files into the respective directories.
Run migrations to set up the database:
text

Copy
python manage.py makemigrations
python manage.py migrate
Create a superuser for admin access:
text

Copy
python manage.py createsuperuser
Run the development server:
text

Copy
python manage.py runserver
Access the application at http://127.0.0.1:8000/. Use the superuser credentials to log in.
This project includes all features from the screenshots (Turf Module, Booking Module, admin page, static pages, reports, etc.) with proper indentation for Python (4 spaces), HTML (4 spaces), and CSS (4 spaces).

Show in sidebar






How can Grok help?