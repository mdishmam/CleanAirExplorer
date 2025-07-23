from django.urls import path
from . import views

urlpatterns = [
    path('best-districts/', views.best_districts, name='best_districts'),
    path('travel-recommendation/', views.travel_recommendation, name='travel_recommendation'),
]