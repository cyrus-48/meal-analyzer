from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile, FoodAnalysis, Comment


WIDGET_CLASS  = 'block w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:ring-2 focus:ring-primary/20 focus:border-primary focus:outline-none transition-all duration-200'
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': WIDGET_CLASS,
            'placeholder': 'Enter your email'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': WIDGET_CLASS,
            'placeholder': 'Choose a username'
        })
        
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': WIDGET_CLASS,
            'placeholder': 'Create a password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': WIDGET_CLASS,
            'placeholder': 'Confirm password'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': WIDGET_CLASS,
            'placeholder': 'Enter your username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': WIDGET_CLASS,
            'placeholder': 'Enter your password'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'password')

class ProfileUpdateForm(forms.ModelForm):
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': WIDGET_CLASS,
            'rows': 4,
            'placeholder': 'Tell us about yourself...'
        })
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': WIDGET_CLASS,
            'placeholder': 'Where are you from?'
        })
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'sr-only',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = Profile
        fields = ('bio', 'location', 'avatar')

class FoodAnalysisForm(forms.ModelForm):
    title = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': WIDGET_CLASS,
            'placeholder': 'Give your analysis a title'
        })
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': WIDGET_CLASS,
            'rows': 3,
            'placeholder': 'Add some details about your food...'
        })
    )
    image = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'sr-only',
            'accept': 'image/*'
        })
    )
    is_public = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary'
        })
    )

    class Meta:
        model = FoodAnalysis
        fields = ('image', 'title', 'description', 'is_public')

class CommentForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': WIDGET_CLASS,
            'rows': 3,
            'placeholder': 'Share your thoughts...'
        })
    )

    class Meta:
        model = Comment
        fields = ('text',)

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text.strip()) < 2:
            raise forms.ValidationError('Comment must be at least 2 characters long.')
        return text