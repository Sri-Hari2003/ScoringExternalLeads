"""
Knowledge Base Utility Module
Contains domain-specific patterns and matching logic for intent analysis
"""

from collections import defaultdict
import re

class KnowledgeBase:
    """Knowledge base for intent signal patterns"""
    
    def __init__(self):
        self.patterns = self._build_patterns()
    
    def _build_patterns(self):
        """Build knowledge base patterns"""
        return {
            'buying_signals': list(set([
                'looking for', 'need help with', 'recommendation', 'comparison',
                'evaluation', 'budget', 'procurement', 'vendor selection',
                'implementation', 'migration', 'upgrade', 'replace', 'purchase',
                'buy', 'pricing', 'quote', 'proposal', 'demo', 'trial'
            ])),
            'pain_points': list(set([
                'problem', 'issue', 'challenge', 'struggling', 'difficult',
                'frustrated', 'broken', 'not working', 'slow', 'expensive',
                'inefficient', 'outdated', 'manual', 'error-prone', 'complex'
            ])),
            'positive_indicators': list(set([
                'funding', 'investment', 'growth', 'expansion', 'hiring',
                'success', 'achievement', 'breakthrough', 'launch', 'partnership',
                'revenue', 'profit', 'scale', 'opportunity', 'innovation'
            ])),
            'urgency_indicators': list(set([
                'urgent', 'asap', 'immediately', 'deadline', 'critical',
                'emergency', 'priority', 'time-sensitive', 'soon', 'quickly',
                'rush', 'fast', 'now', 'today', 'this week'
            ])),
            'company_stages': {
                'startup': list(set(['seed', 'series a', 'early stage', 'founding', 'mvp', 'pre-seed'])),
                'growth': list(set(['series b', 'series c', 'scaling', 'expansion', 'growing', 'mature'])),
                'enterprise': list(set(['established', 'fortune', 'large', 'enterprise', 'corporate', 'global']))
            },
            'tech_categories': {
                'crm': list(set(['salesforce', 'hubspot', 'pipedrive', 'customer relationship', 'lead management'])),
                'marketing': list(set(['mailchimp', 'marketo', 'automation', 'campaign', 'email marketing'])),
                'productivity': list(set(['slack', 'asana', 'monday', 'workflow', 'collaboration', 'project management'])),
                'development': list(set(['github', 'jira', 'devops', 'api', 'integration', 'software development'])),
                'analytics': list(set(['tableau', 'looker', 'dashboard', 'reporting', 'metrics', 'business intelligence'])),
                'security': list(set(['cybersecurity', 'firewall', 'compliance', 'data protection', 'authentication'])),
                'cloud': list(set(['aws', 'azure', 'gcp', 'cloud', 'infrastructure', 'hosting'])),
                'ai_ml': list(set(['artificial intelligence', 'machine learning', 'ai', 'ml', 'automation', 'chatbot']))
            }
        }
    
    def match_patterns(self, text):
        """Match text against knowledge base patterns"""
        text_lower = text.lower()
        results = {}
        
        # Buying signals
        buying_matches = [signal for signal in self.patterns['buying_signals'] if signal in text_lower]
        results['buying_intent_score'] = min(1.0, len(buying_matches) / 3)
        results['buying_signals_found'] = buying_matches
        
        # Pain points
        pain_matches = [point for point in self.patterns['pain_points'] if point in text_lower]
        results['pain_score'] = min(1.0, len(pain_matches) / 2)
        results['pain_points_found'] = pain_matches
        
        # Positive indicators
        positive_matches = [ind for ind in self.patterns['positive_indicators'] if ind in text_lower]
        results['positive_score'] = min(1.0, len(positive_matches) / 2)
        results['positive_indicators_found'] = positive_matches
        
        # Urgency
        urgency_matches = [ind for ind in self.patterns['urgency_indicators'] if ind in text_lower]
        results['urgency_score'] = min(1.0, len(urgency_matches) / 2)
        results['urgency_indicators_found'] = urgency_matches
        
        # Company stage
        detected_stage = 'unknown'
        stage_confidence = 0.0
        for stage, keywords in self.patterns['company_stages'].items():
            matches = [kw for kw in keywords if kw in text_lower]
            if matches:
                detected_stage = stage
                stage_confidence = len(matches) / len(keywords)
                break
        
        results['detected_company_stage'] = detected_stage
        results['stage_confidence'] = stage_confidence
        
        # Technology interests
        tech_interests = []
        tech_scores = {}
        for category, keywords in self.patterns['tech_categories'].items():
            matches = [kw for kw in keywords if kw in text_lower]
            if matches:
                tech_interests.append(category)
                tech_scores[category] = len(matches) / len(keywords)
        
        results['technology_interests'] = tech_interests
        results['tech_interest_scores'] = tech_scores
        
        return results
    
    def get_intent_labels(self):
        """Get predefined intent labels for classification"""
        return [
            'buying intent', 'research intent', 'comparison shopping',
            'problem solving', 'vendor evaluation', 'technology adoption',
            'feature request', 'support inquiry', 'partnership interest'
        ]

    def get_builtwith_tech_categories(self):
        """Return BuiltWith-specific technology categories"""
        return {
            'analytics': ['google-analytics', 'adobe-analytics', 'mixpanel', 'segment', 'hotjar'],
            'advertising': ['google-ads', 'facebook-ads', 'linkedin-ads', 'twitter-ads'],
            'ecommerce': ['shopify', 'woocommerce', 'magento', 'bigcommerce', 'stripe'],
            'cms': ['wordpress', 'drupal', 'joomla', 'contentful', 'strapi'],
            'crm': ['salesforce', 'hubspot', 'pipedrive', 'zoho-crm', 'freshsales'],
            'marketing': ['mailchimp', 'sendgrid', 'marketo', 'pardot', 'constant-contact'],
            'hosting': ['aws', 'azure', 'gcp', 'cloudflare', 'digitalocean'],
            'development': ['react', 'angular', 'vue', 'node-js', 'python'],
            'security': ['cloudflare', 'sucuri', 'wordfence', 'ssl-certificates'],
            'communication': ['intercom', 'zendesk', 'drift', 'crisp', 'freshchat']
        }

    def get_builtwith_intent_patterns(self):
        """Return BuiltWith-specific intent signal patterns"""
        return {
            'migration_intent': [
                'recently_changed', 'new_implementation', 'technology_change'
            ],
            'expansion_intent': [
                'new_categories', 'additional_tools', 'tech_stack_growth'
            ],
            'optimization_intent': [
                'multiple_similar_tools', 'redundant_technologies'
            ],
            'modernization_intent': [
                'legacy_technologies', 'outdated_versions'
            ]
        }

# Global knowledge base instance
knowledge_base = KnowledgeBase()

def get_knowledge_base():
    """Get the global knowledge base instance"""
    return knowledge_base

def match_knowledge_patterns(text):
    """Convenience function to match patterns"""
    return knowledge_base.match_patterns(text)