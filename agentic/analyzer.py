from config.AiModels import get_ai_models
from config.KnowledgeBase import get_knowledge_base

class AgenticAnalyzer:
    """
    AI-powered analyzer for intent signals using project AI models and knowledge base
    """
    def __init__(self):
        self.models = get_ai_models()
        self.knowledge_base = get_knowledge_base()

    def analyze_signal(self, signal):
        """Analyze a single signal with AI and knowledge base"""
        enhanced_signal = signal.copy()
        text_content = f"{signal.get('description', '')} {signal.get('content_snippet', '')}"
        try:
            # Sentiment analysis
            sentiment_result = self.models.sentiment_analyzer(text_content[:512])
            enhanced_signal['ai_sentiment'] = sentiment_result[0]['label']
            enhanced_signal['ai_sentiment_score'] = sentiment_result[0]['score']
            # VADER sentiment
            vader_scores = self.models.vader.polarity_scores(text_content)
            enhanced_signal['vader_sentiment'] = vader_scores
            # Intent classification
            intent_labels = [
                'buying intent', 'research intent', 'comparison shopping',
                'problem solving', 'vendor evaluation', 'technology adoption'
            ]
            intent_result = self.models.intent_classifier(text_content[:512], intent_labels)
            enhanced_signal['primary_intent'] = intent_result['labels'][0]
            enhanced_signal['intent_confidence'] = intent_result['scores'][0]
            # NER
            entities = self.models.ner_pipeline(text_content[:512])
            enhanced_signal['entities'] = [
                {'text': ent['word'], 'label': ent['entity_group'], 'confidence': ent['score']}
                for ent in entities if ent['score'] > 0.7
            ]
            # Knowledge base pattern matching
            enhanced_signal.update(self.knowledge_base.match_patterns(text_content))
        except Exception as e:
            enhanced_signal['ai_error'] = str(e)
        return enhanced_signal 