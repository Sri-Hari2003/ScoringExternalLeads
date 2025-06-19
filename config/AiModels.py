# ai_models.py
"""
AI Models Utility Module
Handles initialization and management of AI models for intent analysis
"""

import warnings
from transformers import pipeline, AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk

warnings.filterwarnings('ignore')

class AIModels:
    """Singleton class to manage AI models"""
    
    _instance = None
    _models_loaded = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIModels, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._models_loaded:
            self.setup_models()
            self._models_loaded = True
    
    def setup_models(self):
        """Initialize all AI models"""
        print("🤖 Initializing AI models...")
        
        # Download NLTK data
        self._download_nltk_data()
        
        try:
            # Sentiment analysis
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis", 
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                truncation=True,
                max_length=512
            )
            
            # Intent classification
            self.intent_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
            
            # Sentence embeddings
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Named Entity Recognition
            self.ner_pipeline = pipeline(
                "ner",
                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                aggregation_strategy="simple"
            )
            
            # VADER sentiment
            self.vader = SentimentIntensityAnalyzer()
            
            print("✅ AI models loaded successfully")
            
        except Exception as e:
            print(f"⚠️ Error loading models: {e}")
            self._setup_fallback_models()
    
    def _download_nltk_data(self):
        """Download required NLTK data"""
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('vader_lexicon', quiet=True)
        except:
            pass
    
    def _setup_fallback_models(self):
        """Setup basic models if advanced ones fail"""
        try:
            self.sentiment_analyzer = pipeline("sentiment-analysis")
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.vader = SentimentIntensityAnalyzer()
            print("✅ Fallback models loaded")
        except Exception as e:
            print(f"❌ Critical error loading models: {e}")
            raise

# Global instance
ai_models = AIModels()

def get_ai_models():
    """Get the global AI models instance"""
    return ai_models