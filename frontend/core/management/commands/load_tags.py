import json
from pathlib import Path
from django.core.management.base import BaseCommand
from core.models import Category, Tag

class Command(BaseCommand):
    help = "Load placeholder categories and tags into PostgreSQL"

    def handle(self, *args, **kwargs):
        # Look for tags.json in frontend directory
        tags_file = Path(__file__).resolve().parent.parent.parent.parent / 'tags.json'
        if not tags_file.exists():
            tags_file = Path('tags.json')  # Fallback to current directory
        
        with open(tags_file, 'r', encoding='utf-8') as f:
            data = json.load(f)['categories']

        for key, info in data.items():
            cat, _ = Category.objects.get_or_create(
                key=key,
                display_name=info['display_name']
            )
            for tag_name in info['tags']:
                Tag.objects.get_or_create(category=cat, name=tag_name)

        self.stdout.write(self.style.SUCCESS("Tags loaded successfully!"))
