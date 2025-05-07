from django import forms

class RecommendationForm(forms.Form):
    MEAL_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]
    
    WIDGET_CLASS =  'block w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:ring-2 focus:ring-primary/20 focus:border-primary focus:outline-none transition-all duration-200'

    meal_type = forms.ChoiceField(
        choices=MEAL_CHOICES,
        widget=forms.Select(attrs={
            'class': WIDGET_CLASS
        })
    )

    family_size = forms.IntegerField(
        min_value=1,
        max_value=20,
        widget=forms.NumberInput(attrs={
            'class': WIDGET_CLASS,
            'placeholder': 'Number of people'
        })
    )

    age_ranges = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full rounded-xl border-gray-300 focus:border-primary focus:ring-2 focus:ring-primary/20 bg-gray-50 shadow-sm resize-none h-24',
            'placeholder': 'Enter age ranges (e.g., 2 children: 5-7, 3 adults: 30-45)'
        })
    )

    region = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class':  WIDGET_CLASS,
            'placeholder': 'Your region or location'
        })
    )

    dietary_restrictions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full rounded-xl border-gray-300 focus:border-primary focus:ring-2 focus:ring-primary/20 bg-gray-50 shadow-sm resize-none h-24',
            'placeholder': 'Any dietary restrictions or allergies?'
        })
    )

    cultural_preferences = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': WIDGET_CLASS,
            'placeholder': 'E.g., Traditional African, Modern fusion, etc.'
        })
    )