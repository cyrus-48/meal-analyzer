from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DetailView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.views import LogoutView
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse
from django.db.models import Q
from .models import FoodAnalysis, Profile, Comment
from .forms import (
    CustomUserCreationForm, ProfileUpdateForm, 
    FoodAnalysisForm, CommentForm
)
from recommendations.models import FoodRecommendation
import base64
import json
import requests
from django.conf import settings
from .tasks import analyze_food_image

def extract_json_from_content(content):
    """Extract and parse JSON from API response content"""
    try:
        if "```json" in content:
            parts = content.split("```json")
            if len(parts) > 1:
                content = parts[1].split("```")[0]
        elif "```" in content:
            parts = content.split("```")
            if len(parts) > 1:
                content = parts[1]
        
        content = content.strip()
        return json.loads(content)
    except Exception as e:
        print(f"JSON extraction error: {str(e)}")
        return None

class HomeView(ListView):
    model = FoodAnalysis
    context_object_name = 'analyses'
    paginate_by = 12
    
    def get_template_names(self):
        if self.request.user.is_authenticated:
            return ['analyzer/home.html']
        return ['analyzer/landing.html']

    def get_queryset(self):
        return FoodAnalysis.objects.filter(is_public=True).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user_analyses'] = FoodAnalysis.objects.filter(
                user=self.request.user
            ).order_by('-created_at')[:5]
        return context
 

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'analyzer/registration/signup.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        """Handle successful form submission"""
        try:
            response = super().form_valid(form)
            login(self.request, self.object)
            messages.success(self.request, "Welcome to FoodAI! Your account has been created successfully.")
            return response
        except Exception as e:
            messages.error(self.request, "An error occurred during registration. Please try again.")
            return self.form_invalid(form)

class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'analyzer/profile.html'
    context_object_name = 'profile'

    def get_object(self):
        return get_object_or_404(Profile, user__username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object().user
        context['analyses'] = FoodAnalysis.objects.filter(user=user).order_by('-created_at')
        context['recommendations'] = FoodRecommendation.objects.filter(user=user).order_by('-created_at')
        return context

class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'analyzer/profile_update.html'

    def test_func(self):
        profile = self.get_object()
        return self.request.user == profile.user

    def get_success_url(self):
        return reverse('profile', kwargs={'username': self.request.user.username})

class AnalysisCreateView(LoginRequiredMixin, CreateView):
    model = FoodAnalysis
    form_class = FoodAnalysisForm
    template_name = 'analyzer/analysis_form.html'

    def form_valid(self, form):
        """Handle form submission and queue analysis task"""
        try:
            # Set initial status
            form.instance.user = self.request.user
            form.instance.status = 'pending'
            self.object = form.save()

            # Queue the analysis task
            analyze_food_image.delay(self.object.id)
            
            
            
            # Show success message
            messages.success(
                self.request, 
                "Your food image has been uploaded and is being analyzed. " 
            )
            
            return HttpResponseRedirect(self.get_success_url())

        except Exception as e:
            print(f"Error queueing analysis task: {str(e)}")
            messages.error(
                self.request, 
                "An error occurred while processing your request. Please try again."
            )
            return self.form_invalid(form)

    def form_invalid(self, form):
        for error in form.errors.values():
            messages.error(self.request, error)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('analysis-detail', kwargs={'pk': self.object.pk})

class AnalysisDetailView(DetailView):
    model = FoodAnalysis
    template_name = 'analyzer/analysis.html'
    context_object_name = 'analysis'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['comments'] = self.object.comments.all()
        return context

class ExploreView(ListView):
    model = FoodAnalysis
    template_name = 'analyzer/explore.html'
    context_object_name = 'analyses'
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return FoodAnalysis.objects.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query) |
                Q(user__username__icontains=query),
                is_public=True
            ).order_by('-created_at')
        return FoodAnalysis.objects.filter(is_public=True).order_by('-created_at')

@login_required
def like_analysis(request, pk):
    analysis = get_object_or_404(FoodAnalysis, pk=pk)
    if request.user in analysis.likes.all():
        analysis.likes.remove(request.user)
        liked = False
    else:
        analysis.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': analysis.total_likes()})

@login_required
def add_comment(request, pk):
    analysis = get_object_or_404(FoodAnalysis, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.analysis = analysis
            comment.user = request.user
            comment.save()
            return JsonResponse({
                'status': 'success',
                'comment': {
                    'text': comment.text,
                    'user': comment.user.username,
                    'date': comment.created_at.strftime('%B %d, %Y %H:%M')
                }
            })
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def toggle_analysis_privacy(request, pk):
    analysis = get_object_or_404(FoodAnalysis, pk=pk)
    if request.user == analysis.user:
        analysis.is_public = not analysis.is_public
        analysis.save()
    return HttpResponseRedirect(reverse('analysis-detail', kwargs={'pk': pk}))

def about_view(request):
    return render(request, 'analyzer/about.html')

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')
    
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        messages.success(request, "You have been successfully logged out.")
        return response

def help_page(request):
    """Render the help page with instructions on using FoodAI."""
    return render(request, 'analyzer/help.html')

from django.http import JsonResponse
from django.core.exceptions import PermissionDenied

@login_required
def check_analysis_status(request, pk):
    """Check the status of an analysis via AJAX"""
    try:
        analysis = get_object_or_404(FoodAnalysis, pk=pk)
        
        # Check if user has permission to view this analysis
        if not analysis.is_public and analysis.user != request.user:
            raise PermissionDenied
        
        return JsonResponse({
            'status': analysis.status,
            'error_message': analysis.error_message,
            'completed': analysis.status == 'completed',
            'progress': {
                'has_ingredients': bool(analysis.ingredients),
                'has_calories': bool(analysis.calories),
                'has_nutrients': bool(analysis.nutrients)
            }
        })
        
    except PermissionDenied:
        return JsonResponse({
            'status': 'error',
            'error_message': 'You do not have permission to view this analysis'
        }, status=403)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error_message': str(e)
        }, status=500)