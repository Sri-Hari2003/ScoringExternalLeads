import feedparser
import time
from datetime import datetime
from urllib.parse import quote_plus
import json
from .enhanced_intent_signal_collector import EnhancedIntentSignalCollector

class EnhancedGoogleNewsCollector:
    def __init__(self, collector: EnhancedIntentSignalCollector):
        self.collector = collector

    def search_company_news(self, companies, keywords, days_back=7):
        """Enhanced Google News search with comprehensive data capture"""
        print("🔍 Collecting Enhanced Google News signals...")

        for company in companies:
            for keyword in keywords:
                try:
                    query = f'"{company}" AND "{keyword}"'
                    search_term = f"{company} {keyword}"
                    url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en&gl=US&ceid=US:en"

                    feed = feedparser.parse(url)

                    for entry in feed.entries[:5]:
                        pub_date = datetime(*entry.published_parsed[:6])
                        if (datetime.now() - pub_date).days <= days_back:
                            title_lower = entry.title.lower()
                            description_lower = entry.get('summary', '').lower()
                            strength = 5
                            confidence = 0.6
                            priority = "Medium"
                            context = ""
                            if any(word in title_lower for word in ['funding', 'raised', 'investment', 'series', 'venture']):
                                strength = 9
                                confidence = 0.9
                                priority = "High"
                                context = "Funding Event"
                            elif any(word in title_lower for word in ['hiring', 'expands', 'growth', 'acquisition']):
                                strength = 7
                                confidence = 0.8
                                priority = "High"
                                context = "Growth Signal"
                            elif any(word in title_lower for word in ['partnership', 'announces', 'launches']):
                                strength = 6
                                confidence = 0.7
                                priority = "Medium"
                                context = "Business Development"
                            engagement_score = len(entry.title) + len(entry.get('summary', '')) // 10
                            positive_words = ['success', 'growth', 'expansion', 'achievement', 'breakthrough']
                            negative_words = ['decline', 'loss', 'problem', 'issue', 'challenge']
                            sentiment = sum(1 for word in positive_words if word in title_lower) - sum(1 for word in negative_words if word in title_lower)
                            sentiment_score = max(-1, min(1, sentiment / 5))
                            signal_data = {
                                'signal_type': "Topic Research Surge",
                                'company_name': company,
                                'signal_strength': strength,
                                'source': "Google News",
                                'source_type': "News Media",
                                'description': entry.title,
                                'url': entry.link,
                                'keyword': keyword,
                                'search_term': search_term,
                                'content_snippet': entry.get('summary', '')[:500],
                                'publication_date': entry.published,
                                'engagement_score': engagement_score,
                                'sentiment_score': sentiment_score,
                                'relevance_score': strength,
                                'signal_context': context,
                                'confidence_level': confidence,
                                'follow_up_required': strength >= 8,
                                'priority_level': priority,
                                'raw_data': json.dumps({
                                    'title': entry.title,
                                    'summary': entry.get('summary', ''),
                                    'published': entry.published,
                                    'link': entry.link
                                }),
                                'processing_notes': f"Auto-processed from Google News RSS feed on {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                                'metadata': {
                                    'feed_source': 'google_news_rss',
                                    'search_query': query,
                                    'days_back': days_back,
                                    'entry_id': entry.get('id', ''),
                                    'tags': entry.get('tags', [])
                                }
                            }
                            self.collector.save_enhanced_signal(signal_data)
                    time.sleep(1)
                except Exception as e:
                    print(f"❌ Error fetching news for {company} + {keyword}: {e}") 