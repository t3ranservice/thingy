from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path('process-data/', views.process_data_plain),
    path('process-data-table/', views.process_data_table),
    path('test-endpoint', views.test_endpoint)
]
