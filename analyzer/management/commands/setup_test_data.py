from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files import File
from pathlib import Path
import shutil
import os
from analyzer.models import FoodAnalysis, Profile

class Command(BaseCommand):
    help = 'Sets up test data for the FoodAI application'

    def handle(self, *args, **kwargs):
        self.stdout.write('Setting up test data...')

        # Create test user if it doesn't exist
        test_user, created = User.objects.get_or_create(
            username='testuser',
            email='test@example.com'
        )
        
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            Profile.objects.get_or_create(user=test_user)
            self.stdout.write(self.style.SUCCESS('Created test user: testuser'))

        # Create test food analysis
        sample_data = {
            'ingredients': ['rice', 'chicken', 'vegetables', 'sauce'],
            'calories': {
                'total': 450,
                'breakdown': {
                    'protein': 120,
                    'carbohydrates': 200,
                    'fats': 130
                }
            },
            'nutrients': {
                'protein': '25g',
                'carbohydrates': '50g',
                'fat': '15g',
                'fiber': '5g',
                'vitamins': {
                    'A': '15%',
                    'C': '20%',
                    'D': '10%'
                },
                'minerals': {
                    'calcium': '8%',
                    'iron': '12%'
                }
            }
        }

        # Path to sample images in your project
        sample_images_dir = Path(__file__).resolve().parent.parent.parent / 'sample_images'
        
        if not sample_images_dir.exists():
            sample_images_dir.mkdir(parents=True)
            self.stdout.write('Created sample_images directory')

        # Create sample food analysis
        for i in range(1, 4):
            title = f'Test Food Analysis {i}'
            description = f'This is a test food analysis {i} with sample data'
            
            # Create sample image if it doesn't exist
            sample_image_path = sample_images_dir / f'sample_food_{i}.jpg'
            if not sample_image_path.exists():
                # Copy default image if available
                default_image_path = Path(__file__).resolve().parent.parent.parent / 'static' / 'images' / 'default_food.jpg'
                if default_image_path.exists():
                    shutil.copy(default_image_path, sample_image_path)
                    self.stdout.write(f'Created sample image: {sample_image_path}')

            if sample_image_path.exists():
                analysis, created = FoodAnalysis.objects.get_or_create(
                    user=test_user,
                    title=title,
                    defaults={
                        'description': description,
                        'ingredients': sample_data['ingredients'],
                        'calories': sample_data['calories'],
                        'nutrients': sample_data['nutrients'],
                        'is_public': True
                    }
                )

                if created:
                    # Set the image
                    with open(sample_image_path, 'rb') as img_file:
                        analysis.image.save(
                            f'sample_food_{i}.jpg',
                            File(img_file),
                            save=True
                        )
                    self.stdout.write(self.style.SUCCESS(f'Created food analysis: {title}'))
                else:
                    self.stdout.write(f'Food analysis already exists: {title}')

        self.stdout.write(self.style.SUCCESS('Test data setup complete!'))
        self.stdout.write('''
Test user credentials:
Username: testuser
Password: testpass123
        ''')