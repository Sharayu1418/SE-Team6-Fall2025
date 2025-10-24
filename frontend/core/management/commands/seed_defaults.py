from django.core.management.base import BaseCommand
from core.models import ContentSource

class Command(BaseCommand):
    help = 'Seed default content sources'

    def handle(self, *args, **options):
        sources = [
            {
                'name': 'NPR News Now',
                'type': 'podcast',
                'feed_url': 'https://feeds.npr.org/500005/podcast.xml',
                'policy': 'cache_allowed'
            },
            {
                'name': 'TED Talks Daily',
                'type': 'podcast', 
                'feed_url': 'https://feeds.feedburner.com/tedtalks_audio',
                'policy': 'cache_allowed'
            },
            {
                'name': 'NASA Breaking News',
                'type': 'article',
                'feed_url': 'https://www.nasa.gov/news/releases/latest/index.html',
                'policy': 'metadata_only'
            },
            {
                'name': 'BBC World',
                'type': 'article',
                'feed_url': 'https://feeds.bbci.co.uk/news/world/rss.xml',
                'policy': 'metadata_only'
            },
            {
                'name': 'Hacker News Frontpage',
                'type': 'article',
                'feed_url': 'https://hnrss.org/frontpage',
                'policy': 'metadata_only'
            },
            {
                'name': 'Reddit API',
                'type': 'article',
                'feed_url': 'https://api.reddit.com/r/worldnews/hot.json',
                'policy': 'metadata_only'
            },
            {
                'name': 'Substack Crawler',
                'type': 'article',
                'feed_url': 'https://example.com/substack-placeholder',
                'policy': 'metadata_only'
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for source_data in sources:
            source, created = ContentSource.objects.get_or_create(
                name=source_data['name'],
                defaults=source_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {source.name}')
                )
            else:
                # Update existing source
                for key, value in source_data.items():
                    if key != 'name':
                        setattr(source, key, value)
                source.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated: {source.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Seeding complete: {created_count} created, {updated_count} updated'
            )
        )