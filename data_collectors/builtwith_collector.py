import os
import requests
from datetime import datetime
from transformers import pipeline

class BuiltWithCollector:
    """
    Collector for BuiltWith technology stack data, with intent scoring using HuggingFace zero-shot classification.
    """
    def __init__(self):
        self.api_key = '35cfbb42-c949-46e7-8aaf-2af211cdc8d2'
        self.base_url = 'https://api.builtwith.com/v21/api.json'
        if not self.api_key:
            raise ValueError("BUILTWITH_API_KEY environment variable not set.")
        # Load zero-shot classifier
        self.intent_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

    def score_intent(self, techs, domain):
        """
        Use zero-shot classification to score intent based on the technology stack.
        Returns a dict with intent_label and intent_scores.
        """
        if not techs:
            return {'intent_label': 'no intent', 'intent_scores': {}}
        text = f"This company ({domain}) uses the following technologies: {', '.join(techs)}."
        candidate_labels = ['buying intent', 'modern stack', 'legacy stack', 'no intent']
        result = self.intent_classifier(text, candidate_labels)
        return {
            'intent_label': result['labels'][0],
            'intent_scores': dict(zip(result['labels'], result['scores']))
        }

    def collect_builtwith_data(self, domains):
        """
        Collect technology stack data for a list of domains using the BuiltWith API.
        Returns a list of signal dicts, each with intent analysis.
        """
        signals = []
        for domain in domains:
            try:
                params = {
                    'KEY': self.api_key,
                    'LOOKUP': domain
                }
                response = requests.get(self.base_url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    techs = []
                    for result in data.get('Results', []):
                        for path in result.get('Result', {}).get('Paths', []):
                            for tech in path.get('Technologies', []):
                                techs.append(tech.get('Name'))
                    techs = list(set(techs))
                    # Score intent using zero-shot classifier
                    intent_info = self.score_intent(techs, domain)
                    signals.append({
                        'company_name': domain.split('.')[0].capitalize(),
                        'domain': domain,
                        'technologies': ', '.join(techs),
                        'signal_type': 'Technology Stack',
                        'source': 'BuiltWith',
                        'source_type': 'Web Technology',
                        'description': f"Detected technologies for {domain}: {', '.join(techs[:5])}..." if techs else f"No technologies detected for {domain}",
                        'confidence_level': 0.9 if techs else 0.5,
                        'intent_label': intent_info['intent_label'],
                        'intent_scores': intent_info['intent_scores'],
                        'timestamp': datetime.now().isoformat(),
                        'collection_date': datetime.now().strftime('%Y-%m-%d'),
                    })
                else:
                    signals.append({
                        'company_name': domain.split('.')[0].capitalize(),
                        'domain': domain,
                        'technologies': '',
                        'signal_type': 'Technology Stack',
                        'source': 'BuiltWith',
                        'source_type': 'Web Technology',
                        'description': f"Failed to fetch BuiltWith data for {domain} (status {response.status_code})",
                        'confidence_level': 0.2,
                        'intent_label': 'no intent',
                        'intent_scores': {},
                        'timestamp': datetime.now().isoformat(),
                        'collection_date': datetime.now().strftime('%Y-%m-%d'),
                    })
            except Exception as e:
                signals.append({
                    'company_name': domain.split('.')[0].capitalize(),
                    'domain': domain,
                    'technologies': '',
                    'signal_type': 'Technology Stack',
                    'source': 'BuiltWith',
                    'source_type': 'Web Technology',
                    'description': f"Error fetching BuiltWith data for {domain}: {e}",
                    'confidence_level': 0.1,
                    'intent_label': 'no intent',
                    'intent_scores': {},
                    'timestamp': datetime.now().isoformat(),
                    'collection_date': datetime.now().strftime('%Y-%m-%d'),
                })
        return signals 