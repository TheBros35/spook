from django.urls import path

from . import views

urlpatterns = [
    path('', views.device_list, name='device_list'),
    path('devices/<int:pk>/wake/', views.device_wake, name='device_wake'),
    path('devices/<int:pk>/delete/', views.device_delete, name='device_delete'),
]
