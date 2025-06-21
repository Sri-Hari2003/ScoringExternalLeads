import json
from datetime import datetime

class EnhancedIntentSignalCollector:
    def __init__(self):
        self.signals = []
        self.detailed_signals = []  # For comprehensive CSV export

    def save_enhanced_signal(self, signal_data):
        """Save comprehensive signal data to memory only (no database)"""
        # Set defaults for missing fields
        defaults = {
            'signal_type': 'Unknown',
            'company_name': '',
            'signal_strength': 5,
            'source': '',
            'source_type': '',
            'description': '',
            'url': '',
            'timestamp': datetime.now().isoformat(),
            'collection_date': datetime.now().strftime('%Y-%m-%d'),
            'keyword': '',
            'search_term': '',
            'content_snippet': '',
            'author': '',
            'publication_date': '',
            'engagement_score': 0,
            'sentiment_score': 0.0,
            'relevance_score': 5,
            'geographic_location': '',
            'industry_category': '',
            'signal_context': '',
            'raw_data': '',
            'processing_notes': '',
            'confidence_level': 0.7,
            'follow_up_required': False,
            'priority_level': 'Medium',
            'metadata': {}
        }

        # Merge provided data with defaults
        signal = {**defaults, **signal_data}

        # Add to memory storage
        self.detailed_signals.append(signal)
        self.signals.append({  # Backward compatibility
            'signal_type': signal['signal_type'],
            'company_name': signal['company_name'],
            'signal_strength': signal['signal_strength'],
            'source': signal['source'],
            'description': signal['description'],
            'url': signal['url'],
            'timestamp': signal['timestamp'],
            'metadata': signal['metadata']
        })

        print(f"✅ Enhanced signal saved: {signal['signal_type']} - {signal['company_name']} (Strength: {signal['signal_strength']})") 