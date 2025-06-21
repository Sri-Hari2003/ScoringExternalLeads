import requests
import time
from datetime import datetime
import json
from .enhanced_intent_signal_collector import EnhancedIntentSignalCollector

class EnhancedRedditCollector:
    def __init__(self, collector: EnhancedIntentSignalCollector):
        self.collector = collector
        self.base_url = "https://www.reddit.com/search.json"

    def search_reddit_mentions(self, companies, keywords, subreddits=None):
        """Enhanced Reddit search with comprehensive data capture"""
        print("🔍 Collecting Enhanced Reddit signals...")

        if not subreddits:
            subreddits = ['entrepreneur', 'startups', 'business', 'technology', 'SaaS', 'marketing', 'sales']

        headers = {'User-Agent': 'IntentSignalBot/1.0'}

        for company in companies:
            for keyword in keywords:
                try:
                    for subreddit in subreddits:
                        query = f'"{company}" "{keyword}" subreddit:{subreddit}'
                        params = {
                            'q': query,
                            'sort': 'new',
                            't': 'week',
                            'limit': 10
                        }
                        response = requests.get(self.base_url, params=params, headers=headers)
                        if response.status_code == 200:
                            data = response.json()
                            for post in data.get('data', {}).get('children', []):
                                post_data = post.get('data', {})
                                score = post_data.get('score', 0)
                                comments = post_data.get('num_comments', 0)
                                upvote_ratio = post_data.get('upvote_ratio', 0.5)
                                engagement_score = score + (comments * 2)
                                strength = min(8, max(3, engagement_score // 10))
                                title_lower = post_data.get('title', '').lower()
                                priority = "High" if engagement_score > 50 else "Medium" if engagement_score > 20 else "Low"
                                context = ""
                                if any(word in title_lower for word in ['recommendation', 'advice', 'help']):
                                    context = "Seeking Solutions"
                                elif any(word in title_lower for word in ['review', 'experience', 'thoughts']):
                                    context = "Product Evaluation"
                                elif any(word in title_lower for word in ['problem', 'issue', 'challenge']):
                                    context = "Pain Point Discussion"
                                signal_data = {
                                    'signal_type': "Forum or Social Chatter",
                                    'company_name': company,
                                    'signal_strength': strength,
                                    'source': f"Reddit - r/{subreddit}",
                                    'source_type': "Social Media",
                                    'description': post_data.get('title', ''),
                                    'url': f"https://reddit.com{post_data.get('permalink', '')}",
                                    'keyword': keyword,
                                    'search_term': f"{company} {keyword}",
                                    'content_snippet': post_data.get('selftext', '')[:500],
                                    'author': post_data.get('author', ''),
                                    'publication_date': datetime.fromtimestamp(post_data.get('created_utc', 0)).isoformat() if post_data.get('created_utc') else '',
                                    'engagement_score': engagement_score,
                                    'sentiment_score': (upvote_ratio - 0.5) * 2,
                                    'relevance_score': strength,
                                    'signal_context': context,
                                    'confidence_level': min(0.9, 0.5 + (engagement_score / 100)),
                                    'follow_up_required': engagement_score > 30,
                                    'priority_level': priority,
                                    'raw_data': json.dumps(post_data),
                                    'processing_notes': f"Reddit post from r/{subreddit} with {score} upvotes and {comments} comments",
                                    'metadata': {
                                        'subreddit': subreddit,
                                        'score': score,
                                        'comments': comments,
                                        'upvote_ratio': upvote_ratio,
                                        'post_id': post_data.get('id', ''),
                                        'flair': post_data.get('link_flair_text', ''),
                                        'gilded': post_data.get('gilded', 0),
                                        'over_18': post_data.get('over_18', False)
                                    }
                                }
                                self.collector.save_enhanced_signal(signal_data)
                        time.sleep(2)
                except Exception as e:
                    print(f"❌ Error fetching Reddit data for {company} + {keyword}: {e}") 