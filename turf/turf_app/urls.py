from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .import views

urlpatterns = [
    path('login_view', views.login_view, name='login'),
    path('adminindex', views.adminindex, name='adminindex'), 
    path('usersignup', views.signup, name='signup'),
    path('forgotpassword',views.getusername,name='forgotpassword'),
    path('verifyotp',views.verifyotp,name='verifyotp'),
    path('passwordreset',views.passwordreset,name='passwordreset'),
    path('',views.index,name="index"), 
    path('logout', views.logoutuser, name="logoutuser"),

    
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

