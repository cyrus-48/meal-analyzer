from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import CustomLogoutView

urlpatterns = [
    # Main pages
    path('', views.HomeView.as_view(), name='home'),
    path('explore/', views.ExploreView.as_view(), name='explore'),
    path('about/', views.about_view, name='about'),
    
    # Authentication
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='analyzer/registration/login.html'), 
         name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='analyzer/registration/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='analyzer/registration/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='analyzer/registration/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='analyzer/registration/password_reset_complete.html'),
         name='password_reset_complete'),
    
    # Profile
    path('profile/<str:username>/', views.ProfileView.as_view(), name='profile'),
    path('profile/<str:username>/edit/', views.ProfileUpdateView.as_view(), name='profile-update'),
    
    # Food Analysis
    path('analysis/new/', views.AnalysisCreateView.as_view(), name='analysis-create'),
    path('analysis/<int:pk>/', views.AnalysisDetailView.as_view(), name='analysis-detail'),
    path('analysis/<int:pk>/privacy/', views.toggle_analysis_privacy, name='analysis-privacy'), 
    path('analysis/<int:pk>/status/', views.check_analysis_status, name='analysis-status'),
    
    # Social Features
    path('analysis/<int:pk>/like/', views.like_analysis, name='analysis-like'),
    path('analysis/<int:pk>/comment/', views.add_comment, name='analysis-comment'),
]