from django.core.management.base import BaseCommand
from core.models import ContentSource

class Command(BaseCommand):
    help = 'Seed default content sources'

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
            
            # ========== ARTICLES ==========
            
            # Articles - News (US & World)
            {
                'name': 'BBC World News',
                'type': 'article',
                'feed_url': 'https://feeds.bbci.co.uk/news/world/rss.xml',
                'policy': 'metadata_only'
            },
            {
                'name': 'Reuters Top News',
                'type': 'article',
                'feed_url': 'https://www.reutersagency.com/feed/',
                'policy': 'metadata_only'
            },
            {
                'name': 'The Guardian World',
                'type': 'article',
                'feed_url': 'https://www.theguardian.com/world/rss',
                'policy': 'metadata_only'
            },
            {
                'name': 'NPR News',
                'type': 'article',
                'feed_url': 'https://feeds.npr.org/1001/rss.xml',
                'policy': 'metadata_only'
            },
            {
                'name': 'The New York Times World',
                'type': 'article',
                'feed_url': 'https://rss.nytimes.com/services/xml/rss/nyt/World.xml',
                'policy': 'metadata_only'
            },
            {
                'name': 'Washington Post World News',
                'type': 'article',
                'feed_url': 'https://feeds.washingtonpost.com/rss/world',
                'policy': 'metadata_only'
            },
            {
                'name': 'CNN Top Stories',
                'type': 'article',
                'feed_url': 'http://rss.cnn.com/rss/cnn_topstories.rss',
                'policy': 'metadata_only'
            },
            {
                'name': 'Associated Press News',
                'type': 'article',
                'feed_url': 'https://rssnews.in/feed/apnews/',
                'policy': 'metadata_only'
            },
            {
                'name': 'Al Jazeera English',
                'type': 'article',
                'feed_url': 'https://www.aljazeera.com/xml/rss/all.xml',
                'policy': 'metadata_only'
            },
            {
                'name': 'The Economist',
                'type': 'article',
                'feed_url': 'https://www.economist.com/rss',
                'policy': 'metadata_only'
            },
            
            # Articles - Tech & Startups
            {
                'name': 'Hacker News Frontpage',
                'type': 'article',
                'feed_url': 'https://hnrss.org/frontpage',
                'policy': 'metadata_only'
            },
            {
                'name': 'Ars Technica',
                'type': 'article',
                'feed_url': 'https://feeds.arstechnica.com/arstechnica/index',
                'policy': 'metadata_only'
            },
            {
                'name': 'TechCrunch',
                'type': 'article',
                'feed_url': 'https://techcrunch.com/feed/',
                'policy': 'metadata_only'
            },
            {
                'name': 'Wired',
                'type': 'article',
                'feed_url': 'https://www.wired.com/feed/rss',
                'policy': 'metadata_only'
            },
            {
                'name': 'The Verge',
                'type': 'article',
                'feed_url': 'https://www.theverge.com/rss/index.xml',
                'policy': 'metadata_only'
            },
            {
                'name': 'Engadget',
                'type': 'article',
                'feed_url': 'https://www.engadget.com/rss.xml',
                'policy': 'metadata_only'
            },
            {
                'name': 'MIT Technology Review',
                'type': 'article',
                'feed_url': 'https://www.technologyreview.com/feed/',
                'policy': 'metadata_only'
            },
            {
                'name': 'VentureBeat',
                'type': 'article',
                'feed_url': 'https://venturebeat.com/feed/',
                'policy': 'metadata_only'
            },
            {
                'name': 'CNET',
                'type': 'article',
                'feed_url': 'https://www.cnet.com/rss/news/',
                'policy': 'metadata_only'
            },
            {
                'name': 'Mashable Tech',
                'type': 'article',
                'feed_url': 'https://mashable.com/feeds/rss/tech',
                'policy': 'metadata_only'
            },
            {
                'name': 'Hacker News Best',
                'type': 'article',
                'feed_url': 'https://hnrss.org/best',
                'policy': 'metadata_only'
            },
            
            # Articles - Science & Space
            {
                'name': 'NASA Breaking News',
                'type': 'article',
                'feed_url': 'https://www.nasa.gov/rss/dyn/breaking_news.rss',
                'policy': 'metadata_only'
            },
            {
                'name': 'Scientific American',
                'type': 'article',
                'feed_url': 'https://www.scientificamerican.com/feed/',
                'policy': 'metadata_only'
            },
            {
                'name': 'Science Daily',
                'type': 'article',
                'feed_url': 'https://www.sciencedaily.com/rss/all.xml',
                'policy': 'metadata_only'
            },
            {
                'name': 'Nature News',
                'type': 'article',
                'feed_url': 'https://www.nature.com/nature.rss',
                'policy': 'metadata_only'
            },
            {
                'name': 'Phys.org',
                'type': 'article',
                'feed_url': 'https://phys.org/rss-feed/',
                'policy': 'metadata_only'
            },
            {
                'name': 'Live Science',
                'type': 'article',
                'feed_url': 'https://www.livescience.com/feeds/all',
                'policy': 'metadata_only'
            },
            {
                'name': 'Space.com',
                'type': 'article',
                'feed_url': 'https://www.space.com/feeds/all',
                'policy': 'metadata_only'
            },
            
            # Articles - Business & Finance
            {
                'name': 'Bloomberg',
                'type': 'article',
                'feed_url': 'https://feeds.bloomberg.com/markets/news.rss',
                'policy': 'metadata_only'
            },
            {
                'name': 'Financial Times',
                'type': 'article',
                'feed_url': 'https://www.ft.com/?format=rss',
                'policy': 'metadata_only'
            },
            {
                'name': 'Forbes',
                'type': 'article',
                'feed_url': 'https://www.forbes.com/real-time/feed2/',
                'policy': 'metadata_only'
            },
            {
                'name': 'Wall Street Journal',
                'type': 'article',
                'feed_url': 'https://feeds.a.dj.com/rss/RSSWorldNews.xml',
                'policy': 'metadata_only'
            },
            {
                'name': 'CNBC Top News',
                'type': 'article',
                'feed_url': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
                'policy': 'metadata_only'
            },
            {
                'name': 'Business Insider',
                'type': 'article',
                'feed_url': 'https://www.businessinsider.com/rss',
                'policy': 'metadata_only'
            },
            {
                'name': 'Harvard Business Review',
                'type': 'article',
                'feed_url': 'https://feeds.hbr.org/harvardbusiness',
                'policy': 'metadata_only'
            },
            
            # Articles - Entertainment & Pop Culture
            {
                'name': 'Entertainment Weekly',
                'type': 'article',
                'feed_url': 'https://ew.com/feed/',
                'policy': 'metadata_only'
            },
            {
                'name': 'Variety',
                'type': 'article',
                'feed_url': 'https://variety.com/feed/',
                'policy': 'metadata_only'
            },
            {
                'name': 'The Hollywood Reporter',
                'type': 'article',
                'feed_url': 'https://www.hollywoodreporter.com/feed/',
                'policy': 'metadata_only'
            },
            {
                'name': 'IndieWire',
                'type': 'article',
                'feed_url': 'https://www.indiewire.com/feed/',
                'policy': 'metadata_only'
            },
            {
                'name': 'Polygon',
                'type': 'article',
                'feed_url': 'https://www.polygon.com/rss/index.xml',
                'policy': 'metadata_only'
            },
            
            # Articles - Sports
            {
                'name': 'ESPN Top Headlines',
                'type': 'article',
                'feed_url': 'https://www.espn.com/espn/rss/news',
                'policy': 'metadata_only'
            },
            {
                'name': 'Bleacher Report',
                'type': 'article',
                'feed_url': 'https://bleacherreport.com/articles/feed',
                'policy': 'metadata_only'
            },
            {
                'name': 'The Athletic',
                'type': 'article',
                'feed_url': 'https://theathletic.com/feed/',
                'policy': 'metadata_only'
            },
            {
                'name': 'Sports Illustrated',
                'type': 'article',
                'feed_url': 'https://www.si.com/.rss/si/all',
                'policy': 'metadata_only'
            },
            
            # Articles - Health & Medicine
            {
                'name': 'Medical News Today',
                'type': 'article',
                'feed_url': 'https://www.medicalnewstoday.com/rss',
                'policy': 'metadata_only'
            },
            {
                'name': 'WebMD Health News',
                'type': 'article',
                'feed_url': 'https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC',
                'policy': 'metadata_only'
            },
            {
                'name': 'Healthline',
                'type': 'article',
                'feed_url': 'https://www.healthline.com/rss',
                'policy': 'metadata_only'
            },
            
            # Articles - Environment & Climate
            {
                'name': 'Inside Climate News',
                'type': 'article',
                'feed_url': 'https://insideclimatenews.org/feed/',
                'policy': 'metadata_only'
            },
            {
                'name': 'Grist',
                'type': 'article',
                'feed_url': 'https://grist.org/feed/',
                'policy': 'metadata_only'
            },
            {
                'name': 'National Geographic',
                'type': 'article',
                'feed_url': 'https://www.nationalgeographic.com/rss/',
                'policy': 'metadata_only'
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