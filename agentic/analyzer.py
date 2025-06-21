# Agentic Intent Signal Analysis Module
# Enhanced with AI-powered analysis and automated decision-making

import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
except:
    pass

class AgenticIntentAnalyzer:
    """
    AI-powered agentic module for intelligent intent signal analysis
    """

    def __init__(self, collector):
        self.collector = collector
        self.setup_ai_models()
        self.knowledge_base = self.build_knowledge_base()
        self.decision_engine = DecisionEngine()
        self.autonomous_actions = []

    def setup_ai_models(self):
        """Initialize pre-trained AI models for analysis"""
        print("🤖 Initializing AI models...")

        try:
            # Sentiment analysis pipeline
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                truncation=True,
                max_length=512
            )

            # Text classification for intent detection
            self.intent_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )

            # Sentence embeddings for similarity analysis
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

            # Named Entity Recognition
            self.ner_pipeline = pipeline(
                "ner",
                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                aggregation_strategy="simple"
            )

            # VADER sentiment for backup
            self.vader = SentimentIntensityAnalyzer()

            print("✅ AI models loaded successfully")

        except Exception as e:
            print(f"⚠️ Error loading some AI models: {e}")
            # Fallback to basic models
            self.setup_fallback_models()

    def setup_fallback_models(self):
        """Setup basic models if advanced ones fail"""
        try:
            self.sentiment_analyzer = pipeline("sentiment-analysis")
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.vader = SentimentIntensityAnalyzer()
            print("✅ Fallback models loaded")
        except Exception as e:
            print(f"❌ Critical error loading models: {e}")

    def build_knowledge_base(self):
        """Build knowledge base of company and technology patterns"""
        return {
            'buying_signals': [
                'looking for', 'need help with', 'recommendation', 'comparison',
                'evaluation', 'budget', 'procurement', 'vendor selection',
                'implementation', 'migration', 'upgrade', 'replace'
            ],
            'pain_points': [
                'problem', 'issue', 'challenge', 'struggling', 'difficult',
                'frustrated', 'broken', 'not working', 'slow', 'expensive'
            ],
            'positive_indicators': [
                'funding', 'investment', 'growth', 'expansion', 'hiring',
                'success', 'achievement', 'breakthrough', 'launch', 'partnership'
            ],
            'urgency_indicators': [
                'urgent', 'asap', 'immediately', 'deadline', 'critical',
                'emergency', 'priority', 'time-sensitive', 'soon'
            ],
            'company_stages': {
                'startup': ['seed', 'series a', 'early stage', 'founding', 'mvp'],
                'growth': ['series b', 'series c', 'scaling', 'expansion', 'growing'],
                'enterprise': ['established', 'fortune', 'large', 'enterprise', 'corporate']
            },
            'tech_categories': {
                'crm': ['salesforce', 'hubspot', 'pipedrive', 'customer relationship'],
                'marketing': ['mailchimp', 'marketo', 'automation', 'campaign'],
                'productivity': ['slack', 'asana', 'monday', 'workflow', 'collaboration'],
                'development': ['github', 'jira', 'devops', 'api', 'integration'],
                'analytics': ['tableau', 'looker', 'dashboard', 'reporting', 'metrics']
            }
        }

    def analyze_signal(self, signal):
        """Analyze a single signal with AI and knowledge base"""
        enhanced_signal = signal.copy()
        text_content = f"{signal.get('description', '')} {signal.get('content_snippet', '')}"
        try:
            # Sentiment analysis
            sentiment_result = self.sentiment_analyzer(text_content[:512])
            enhanced_signal['ai_sentiment'] = sentiment_result[0]['label']
            enhanced_signal['ai_sentiment_score'] = sentiment_result[0]['score']
            # VADER sentiment
            vader_scores = self.vader.polarity_scores(text_content)
            enhanced_signal['vader_sentiment'] = vader_scores
            # Intent classification
            intent_labels = [
                'buying intent', 'research intent', 'comparison shopping',
                'problem solving', 'vendor evaluation', 'technology adoption'
            ]
            intent_result = self.intent_classifier(text_content[:512], intent_labels)
            enhanced_signal['primary_intent'] = intent_result['labels'][0]
            enhanced_signal['intent_confidence'] = intent_result['scores'][0]
            # NER
            entities = self.ner_pipeline(text_content[:512])
            enhanced_signal['entities'] = [
                {'text': ent['word'], 'label': ent['entity_group'], 'confidence': ent['score']}
                for ent in entities if ent['score'] > 0.7
            ]
            # Knowledge base pattern matching
            enhanced_signal.update(self.knowledge_base.match_patterns(text_content))
        except Exception as e:
            enhanced_signal['ai_error'] = str(e)
        return enhanced_signal 