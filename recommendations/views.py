from django.shortcuts import render, redirect
from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from .models import FoodRecommendation
from .forms import RecommendationForm
from .tasks import generate_food_recommendation

class FoodRecommendationView(LoginRequiredMixin, FormView):
    template_name = 'recommendations/recommend.html'
    form_class = RecommendationForm

    def form_valid(self, form):
        try:
            # Create recommendation with pending status
            recommendation = FoodRecommendation.objects.create(
                user=self.request.user,
                status='pending',
                meal_type=form.cleaned_data['meal_type'],
                family_size=form.cleaned_data['family_size'],
                age_ranges=form.cleaned_data['age_ranges'],
                region=form.cleaned_data['region'],
                dietary_restrictions=form.cleaned_data['dietary_restrictions'],
                cultural_preferences=form.cleaned_data['cultural_preferences']
            )

            # Queue the recommendation task
            generate_food_recommendation.delay(recommendation.id)
            
            messages.success(
                self.request, 
                "Your meal recommendation request has been submitted and is being processed. "
                "Please wait a moment..."
            )
            
            return redirect('recommendation-detail', pk=recommendation.id)
            
        except Exception as e:
            messages.error(
                self.request, 
                "An error occurred while processing your request. Please try again."
            )
            return self.form_invalid(form)

class RecommendationDetailView(LoginRequiredMixin, DetailView):
    model = FoodRecommendation
    template_name = 'recommendations/recommendation_detail.html'
    context_object_name = 'recommendation'

    def get_object(self):
        return get_object_or_404(
            FoodRecommendation,
            pk=self.kwargs['pk'],
            user=self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"{self.object.get_meal_type_display()} Recommendations"
        context['is_pending'] = self.object.status == 'pending'
        context['is_failed'] = self.object.status == 'failed'
        context['error_message'] = self.object.error_message
        return context

def check_recommendation_status(request, pk):
    """AJAX endpoint to check recommendation status"""
    try:
        recommendation = get_object_or_404(
            FoodRecommendation, 
            pk=pk,
            user=request.user
        )
        
        return JsonResponse({
            'status': recommendation.status,
            'error_message': recommendation.error_message,
            'completed': recommendation.status == 'completed',
            'has_recommendations': bool(recommendation.recommendations)
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error_message': str(e)
        }, status=500)