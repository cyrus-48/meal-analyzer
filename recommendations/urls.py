from django.urls import path
from .views import FoodRecommendationView, RecommendationDetailView
from . import views

urlpatterns = [
    path('recommend/', FoodRecommendationView.as_view(), name='recommend'),
    path('recommendation/<int:pk>/', RecommendationDetailView.as_view(), name='recommendation-detail'),
    path(
        '<int:pk>/status/',
        views.check_recommendation_status,
        name='recommendation-status'
    ),
]