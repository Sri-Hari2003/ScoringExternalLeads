import feedparser
import json
import time
from datetime import datetime
from urllib.parse import quote_plus
# Add import for KnowledgeBase
try:
    from config.KnowledgeBase import get_knowledge_base
except ImportError:
    get_knowledge_base = None

class EnhancedGoogleNewsCollector:
    def __init__(self, knowledge_base=None):
        self.results = []
        # Use provided knowledge_base or get global if available
        if knowledge_base is not None:
            self.knowledge_base = knowledge_base
        elif get_knowledge_base is not None:
            self.knowledge_base = get_knowledge_base()
        else:
            self.knowledge_base = None

    def _score_and_context(self, title, description):
        title_lower = title.lower()
        context = ""
        strength = 5
        confidence = 0.6
        priority = "Medium"
        # Use knowledge base if available
        if self.knowledge_base:
            patterns = self.knowledge_base.match_patterns(title_lower + " " + description.lower())
            if patterns['positive_score'] > 0.5:
                strength = 9
                confidence = 0.9
                priority = "High"
                context = "Funding/Growth Event"
            elif patterns['pain_score'] > 0.5:
                strength = 7
                confidence = 0.8
                priority = "High"
                context = "Pain Point/Growth Signal"
            elif patterns['buying_intent_score'] > 0.3:
                strength = 6
                confidence = 0.7
                priority = "Medium"
                context = "Business Development"
        else:
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
        return strength, confidence, priority, context

    def search_company_news(self, companies, keywords, days_back=7):
        """
        Search Google News RSS feeds for recent articles related to the companies and keywords.
        Returns a list of structured signal dictionaries (JSON-serializable).
        """
        self.results = []
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
                            title = entry.title
                            description = entry.get('summary', '')
                            strength, confidence, priority, context = self._score_and_context(title, description)

                            engagement_score = len(title) + len(description) // 10

                            positive_words = ['success', 'growth', 'expansion', 'achievement', 'breakthrough']
                            negative_words = ['decline', 'loss', 'problem', 'issue', 'challenge']
                            sentiment = sum(1 for word in positive_words if word in title.lower()) - sum(1 for word in negative_words if word in title.lower())
                            sentiment_score = max(-1, min(1, sentiment / 5))

                            signal_data = {
                                'signal_type': "Topic Research Surge",
                                'company_name': company,
                                'signal_strength': strength,
                                'source': "Google News",
                                'source_type': "News Media",
                                'description': title,
                                'url': entry.link,
                                'keyword': keyword,
                                'search_term': search_term,
                                'content_snippet': description[:500],
                                'publication_date': entry.published,
                                'engagement_score': engagement_score,
                                'sentiment_score': sentiment_score,
                                'relevance_score': strength,
                                'signal_context': context,
                                'confidence_level': confidence,
                                'follow_up_required': strength >= 8,
                                'priority_level': priority,
                                'raw_data': json.dumps({
                                    'title': title,
                                    'summary': description,
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

                            self.results.append(signal_data)

                    time.sleep(1)

                except Exception as e:
                    print(f"❌ Error fetching news for {company} + {keyword}: {e}")

        return self.results
