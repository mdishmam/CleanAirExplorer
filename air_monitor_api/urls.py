from django.urls import path
from . import views

urlpatterns = [
    path('best-districts/', views.BestDistricts.as_view(), name='best_districts'),
    path('travel-recommendation/', views.TravelRecommendation.as_view(), name='travel_recommendation'),
]
