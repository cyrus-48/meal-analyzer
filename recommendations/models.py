from django.db import models
from django.contrib.auth.models import User

class FoodRecommendation(models.Model):
    MEAL_TYPES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='pending'
    )
    error_message = models.TextField(blank=True, null=True)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    family_size = models.IntegerField()
    age_ranges = models.JSONField()  # Store age ranges as JSON
    region = models.CharField(max_length=100)
    dietary_restrictions = models.TextField(blank=True)
    cultural_preferences = models.CharField(max_length=100)
    recommendations = models.JSONField(null=True, blank=True)  # Store AI recommendations as JSON
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
