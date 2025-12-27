# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register_user'),
    path('login/', views.login_user, name='login_user'),
    path('request-reset/', views.send_reset_otp, name='send_reset_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('store-reading/', views.store_sensor_reading, name='store_sensor_reading'),
    path("soil-summary/", views.soil_summary, name="soil_summary"),
    path('store-daily-summary/', views.store_daily_summary, name='store_daily_summary'),
]
