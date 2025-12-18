from django.core.management.base import BaseCommand
from core.models import ContentSource

class Command(BaseCommand):
    help = 'Seed default content sources (podcasts, news, memes)'

    def handle(self, *args, **options):
        sources = [
            # ========== PODCASTS ==========
            
            # Podcasts - News & Politics
            {
                'name': 'NPR News Now',
                'type': 'podcast',
                'feed_url': 'https://feeds.npr.org/500005/podcast.xml',
                'policy': 'cache_allowed'
            },
            {
                'name': 'The Daily (NYT)',
                'type': 'podcast',
                'feed_url': 'https://feeds.simplecast.com/54nAGcIl',
                'policy': 'cache_allowed'
            },
            {
                'name': 'BBC Global News',
                'type': 'podcast',
                'feed_url': 'https://podcasts.files.bbci.co.uk/p02nq0gn.rss',
                'policy': 'cache_allowed'
            },
            {
                'name': 'Up First (NPR)',
                'type': 'podcast',
                'feed_url': 'https://feeds.npr.org/510318/podcast.xml',
                'policy': 'cache_allowed'
            },
            {
                'name': 'Today, Explained',
                'type': 'podcast',
                'feed_url': 'https://feeds.megaphone.fm/VMP5705694065',
                'policy': 'cache_allowed'
            },
            {
                'name': 'Pod Save America',
                'type': 'podcast',
                'feed_url': 'https://feeds.simplecast.com/AciORVLR',
                'policy': 'cache_allowed'
            },
            {
                'name': 'The Economist Radio',
                'type': 'podcast',
                'feed_url': 'https://rss.acast.com/theeconomistradio',
                'policy': 'cache_allowed'
            },
            {
                'name': 'FiveThirtyEight Politics',
                'type': 'podcast',
                'feed_url': 'https://feeds.megaphone.fm/ESP8429020194',
                'policy': 'cache_allowed'
            },
            
            # Podcasts - Education & Science
            {
                'name': 'TED Talks Daily',
                'type': 'podcast', 
                'feed_url': 'https://feeds.feedburner.com/tedtalks_audio',
                'policy': 'cache_allowed'
            },
            {
                'name': 'Radiolab',
                'type': 'podcast',
                'feed_url': 'http://feeds.wnyc.org/radiolab',
                'policy': 'cache_allowed'
            },
            {
                'name': 'Science Vs',
                'type': 'podcast',
                'feed_url': 'https://feeds.megaphone.fm/sciencevs',
                'policy': 'cache_allowed'
            },
            {
                'name': 'Stuff You Should Know',
                'type': 'podcast',
                'feed_url': 'https://feeds.megaphone.fm/stuffyoushouldknow',
                'policy': 'cache_allowed'
            },
            {
                'name': 'Short Wave (NPR)',
                'type': 'podcast',
                'feed_url': 'https://feeds.npr.org/510351/podcast.xml',
                'policy': 'cache_allowed'
            },
            {
                'name': 'StarTalk Radio',
                'type': 'podcast',
                'feed_url': 'https://feeds.soundcloud.com/users/soundcloud:users:38128127/sounds.rss',
                'policy': 'cache_allowed'
            },
            {
                'name': 'Hidden Brain',
                'type': 'podcast',
                'feed_url': 'https://feeds.npr.org/510308/podcast.xml',
                'policy': 'cache_allowed'
            },
            {
                'name': 'Ologies',
                'type': 'podcast',
                'feed_url': 'https://feeds.simplecast.com/4T39_jAj',
                'policy': 'cache_allowed'
            },
            {
                'name': 'Daniel and Jorge Explain the Universe',
                'type': 'podcast',
                'feed_url': 'https://feeds.simplecast.com/4T39_jAj',
                'policy': 'cache_allowed'
            },
            
            # Podcasts - Tech & Business
            {
                'name': 'Planet Money',
                'type': 'podcast',
                'feed_url': 'https://feeds.npr.org/510289/podcast.xml',
                'policy': 'cache_allowed'
            },
            {
                'name': 'Freakonomics Radio',
                'type': 'podcast',
                'feed_url': 'https://feeds.simplecast.com/Y8lFbOT4',
                'policy': 'cache_allowed'
            },
            {
                'name': 'How I Built This',
                'type': 'podcast',
                'feed_url': 'https://feeds.npr.org/510313/podcast.xml',
                'policy': 'cache_allowed'
            },
            {
                'name': 'Reply All',
                'type': 'podcast',
                'feed_url': 'https://feeds.megaphone.fm/replyall',
                'policy': 'cache_allowed'
            },
            {
                'name': 'Acquired',
                'type': 'podcast',
                'feed_url': 'https://feeds.simplecast.com/F66xvR1p',
                'policy': 'cache_allowed'
            },
            {
                'name': 'The Vergecast',
                'type': 'podcast',
                'feed_url': 'https://feeds.megaphone.fm/vergecast',
                'policy': 'cache_allowed'
            },
            {
                'name': 'Pivot (Kara Swisher)',
                'type': 'podcast',
                'feed_url': 'https://feeds.megaphone.fm/pivot',
                'policy': 'cache_allowed'
            },
            {
                'name': 'Masters of Scale',
                'type': 'podcast',
                'feed_url': 'https://feeds.simplecast.com/3SVE8VjK',
                'policy': 'cache_allowed'
            },
            {
                'name': 'The Tim Ferriss Show',
                'type': 'podcast',
                'feed_url': 'https://rss.art19.com/tim-ferriss-show',
                'policy': 'cache_allowed'
            },
            {
                'name': 'WorkLife with Adam Grant',
                'type': 'podcast',
                'feed_url': 'https://feeds.simplecast.com/LpvezHsg',
                'policy': 'cache_allowed'
            },
            {
                'name': 'Marketplace (APM)',
                'type': 'podcast',
                'feed_url': 'https://www.marketplace.org/feed/podcast/marketplace',
                'policy': 'cache_allowed'
            },
            
            # Podcasts - True Crime & Mystery
            {
                'name': 'Serial',
                'type': 'podcast',
                'feed_url': 'https://feeds.simplecast.com/xl36XBC2',
                'policy': 'cache_allowed'
            },
            {
                'name': 'Crime Junkie',
                'type': 'podcast',
                'feed_url': 'https://feeds.simplecast.com/qm_9xx0g',
                'policy': 'cache_allowed'
            },
            {
                'name': 'My Favorite Murder',
                'type': 'podcast',
                'feed_url': 'https://feeds.simplecast.com/qI0dOePz',
                'policy': 'cache_allowed'
            },
            {
                'name': 'Dateline NBC',
                'type': 'podcast',
                'feed_url': 'https://podcastfeeds.nbcnews.com/dateline-nbc',
                'policy': 'cache_allowed'
            },
            
            # Podcasts - Comedy & Entertainment
            {
                'name': 'Conan O\'Brien Needs A Friend',
                'type': 'podcast',
                'feed_url': 'https://feeds.simplecast.com/dHoohVNH',
                'policy': 'cache_allowed'
            },
            {
                'name': 'SmartLess',
                'type': 'podcast',
                'feed_url': 'https://rss.art19.com/smartless',
                'policy': 'cache_allowed'
            },
            {
                'name': 'Wait Wait... Don\'t Tell Me!',
                'type': 'podcast',
                'feed_url': 'https://feeds.npr.org/344098539/podcast.xml',
                'policy': 'cache_allowed'
            },
            {
                'name': 'This American Life',
                'type': 'podcast',
                'feed_url': 'https://feeds.thisamericanlife.org/talpodcast',
                'policy': 'cache_allowed'
            },
            
            # Podcasts - Health & Wellness
            {
                'name': 'Huberman Lab',
                'type': 'podcast',
                'feed_url': 'https://feeds.megaphone.fm/hubermanlab',
                'policy': 'cache_allowed'
            },
            {
                'name': 'The Peter Attia Drive',
                'type': 'podcast',
                'feed_url': 'https://feeds.megaphone.fm/peterattiamd',
                'policy': 'cache_allowed'
            },
            {
                'name': 'ZOE Science & Nutrition',
                'type': 'podcast',
                'feed_url': 'https://feeds.acast.com/public/shows/zoe-science-nutrition',
                'policy': 'cache_allowed'
            },
            
            # Podcasts - History & Culture
            {
                'name': 'Hardcore History',
                'type': 'podcast',
                'feed_url': 'https://feeds.feedburner.com/dancarlin/history',
                'policy': 'cache_allowed'
            },
            {
                'name': 'Throughline (NPR)',
                'type': 'podcast',
                'feed_url': 'https://feeds.npr.org/510333/podcast.xml',
                'policy': 'cache_allowed'
            },
            {
                'name': '99% Invisible',
                'type': 'podcast',
                'feed_url': 'https://feeds.99percentinvisible.org/99percentinvisible',
                'policy': 'cache_allowed'
            },
            {
                'name': 'Revisionist History',
                'type': 'podcast',
                'feed_url': 'https://feeds.megaphone.fm/revisionisthistory',
                'policy': 'cache_allowed'
            },
            
            # Podcasts - Sports
            {
                'name': 'The Bill Simmons Podcast',
                'type': 'podcast',
                'feed_url': 'https://feeds.megaphone.fm/billsimmons',
                'policy': 'cache_allowed'
            },
            {
                'name': 'Pardon My Take',
                'type': 'podcast',
                'feed_url': 'https://feeds.megaphone.fm/ESP1388245279',
                'policy': 'cache_allowed'
            },
            
            # ========== NEWS (NewsAPI) ==========
            {
                'name': 'Tech News',
                'type': 'news',
                'feed_url': 'technology',
                'policy': 'cache_allowed',
            },
            {
                'name': 'AI & Machine Learning News',
                'type': 'news',
                'feed_url': 'artificial intelligence OR machine learning',
                'policy': 'cache_allowed',
            },
            {
                'name': 'Science News',
                'type': 'news',
                'feed_url': 'science discovery research',
                'policy': 'cache_allowed',
            },
            {
                'name': 'Business News',
                'type': 'news',
                'feed_url': 'business finance stocks',
                'policy': 'cache_allowed',
            },
            {
                'name': 'World News',
                'type': 'news',
                'feed_url': 'world news international',
                'policy': 'cache_allowed',
            },
            {
                'name': 'Entertainment News',
                'type': 'news',
                'feed_url': 'entertainment movies music celebrity',
                'policy': 'cache_allowed',
            },
            {
                'name': 'Sports News',
                'type': 'news',
                'feed_url': 'sports NFL NBA MLB soccer',
                'policy': 'cache_allowed',
            },
            {
                'name': 'Health News',
                'type': 'news',
                'feed_url': 'health medicine wellness',
                'policy': 'cache_allowed',
            },
            
            # ========== MEMES (Reddit) ==========
            {
                'name': 'Wholesome Memes',
                'type': 'meme',
                'feed_url': 'https://reddit.com/r/wholesomememes',
                'policy': 'cache_allowed',
            },
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
                    self.style.SUCCESS(f'✓ Created: {source.name} ({source_data["type"]})')
                )
            else:
                # Update existing source
                for key, value in source_data.items():
                    if key != 'name':
                        setattr(source, key, value)
                source.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Updated: {source.name}')
                )
        
        # Delete article sources (metadata_only)
        deleted_count, _ = ContentSource.objects.filter(type='article').delete()
        if deleted_count:
            self.stdout.write(
                self.style.WARNING(f'🗑 Deleted {deleted_count} article sources')
            )
        
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Seeding complete: {created_count} created, {updated_count} updated, {deleted_count} deleted'
            )
        )
        self.stdout.write('')
        self.stdout.write('Content types seeded:')
        self.stdout.write(f'  📻 Podcasts: {len([s for s in sources if s["type"] == "podcast"])}')
        self.stdout.write(f'  📰 News: {len([s for s in sources if s["type"] == "news"])}')
        self.stdout.write(f'  😂 Memes: {len([s for s in sources if s["type"] == "meme"])}')
