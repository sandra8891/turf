from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .import views

urlpatterns = [
    path('',views.index,name='index'),
    # path('index',views.index,name="index"), 
    path('login_view', views.login_view, name='login'),
    path('adminindex', views.admin_index, name='admin_index'), 
    path('usersignup', views.signup, name='signup'),
    path('forgotpassword',views.getusername,name='forgotpassword'),
    path('verifyotp',views.verifyotp,name='verifyotp'),
    path('passwordreset',views.passwordreset,name='passwordreset'),
    path('logout', views.logoutuser, name="logoutuser"),
    path('adminlogout/', views.logoutadmin, name='adminlogout'),
    path('home', views.home, name='home'),
    # path('adminindex/', views.admin_index, name='adminindex'),
    path('adminupload/', views.admin_upload, name='adminupload'),
    path('turf/<int:turf_id>/', views.turf_detail, name='turf_detail'),
    path('booking/<int:turf_id>/', views.booking, name='booking'),
    path('book_slot/<int:slot_id>/', views.book_slot, name='book_slot'),
    path('booking-details/<int:slot_id>/', views.booking_details, name='booking_details'),
    path('recent_bookings/', views.recent_bookings, name='recent_bookings'),
    path('edit/<int:turf_id>/', views.edit_turf, name='edit_turf'),
    path('delete/<int:turf_id>/', views.delete_turf, name='delete_turf'),
    path('list-turfs/', views.list_turfs, name='list_turfs'), 
    path('search-turfs/', views.search_turfs, name='search_turfs'),
    path('profile/', views.profile, name='profile'),
    path('payment/<int:booking_id>/', views.order_payment, name='order_payment'),
    path('payment/callback/', views.razorpay_callback, name='razorpay_callback'),
    path('recent-bookings/', views.recent_bookings, name='recent_bookings'),
    path('booking-history/', views.booking_history, name='booking_history'),
    
]
    
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

