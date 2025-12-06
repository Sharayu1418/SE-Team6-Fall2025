"""
Management command to create UserPreference for users that don't have one.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserPreference


class Command(BaseCommand):
    help = 'Create default UserPreference for all users that do not have one'

    def handle(self, *args, **options):
        users_without_prefs = User.objects.filter(userpreference__isnull=True)
        count = 0
        
        for user in users_without_prefs:
            UserPreference.objects.create(
                user=user,
                topics=[],
                max_daily_items=10,
                max_storage_mb=500
            )
            self.stdout.write(f'Created preferences for: {user.username}')
            count += 1
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('All users already have preferences!'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Created preferences for {count} user(s)'))

