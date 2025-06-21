import numpy as np
import pandas as pd
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
from collections import defaultdict, Counter
import warnings
import os
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
        print("🤖 Initializing AI models...")
        try:
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                truncation=True,
                max_length=512
            )
            self.intent_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.ner_pipeline = pipeline(
                "ner",
                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                aggregation_strategy="simple"
            )
            self.vader = SentimentIntensityAnalyzer()
            print("✅ AI models loaded successfully")
        except Exception as e:
            print(f"⚠️ Error loading some AI models: {e}")
            self.setup_fallback_models()

    def setup_fallback_models(self):
        try:
            self.sentiment_analyzer = pipeline("sentiment-analysis")
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.vader = SentimentIntensityAnalyzer()
            print("✅ Fallback models loaded")
        except Exception as e:
            print(f"❌ Critical error loading models: {e}")

    def build_knowledge_base(self):
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

class DecisionEngine:
    """
    Autonomous decision-making engine for intent signals
    """
    def __init__(self):
        self.decision_rules = self.setup_decision_rules()
        self.action_templates = self.setup_action_templates()

    def setup_decision_rules(self):
        return {
            'immediate_action': {
                'conditions': ['signal_strength >= 8', 'urgency_score > 0.7', 'buying_intent_score > 0.8'],
                'action': 'schedule_immediate_outreach'
            },
            'high_priority': {
                'conditions': ['signal_strength >= 6', 'company_fit_score > 0.7'],
                'action': 'add_to_priority_queue'
            },
            'nurture': {
                'conditions': ['signal_strength >= 4', 'engagement_potential > 0.5'],
                'action': 'add_to_nurture_campaign'
            },
            'research_needed': {
                'conditions': ['confidence_level < 0.6', 'entity_clarity < 0.5'],
                'action': 'schedule_research_task'
            }
        }

    def setup_action_templates(self):
        return {
            'email_outreach': {
                'subject_templates': [
                    "Saw your {signal_context} - here's how we can help",
                    "Quick question about your {technology} implementation",
                    "{company_name} + {our_solution} = potential partnership?"
                ],
                'personalization_points': [
                    'recent_signal', 'company_stage', 'tech_stack', 'pain_points'
                ]
            },
            'content_recommendation': {
                'case_studies': 'based on similar company profiles',
                'whitepapers': 'matching technology interests',
                'demos': 'relevant to identified use cases'
            },
            'follow_up_cadence': {
                'immediate': [1, 3, 7],
                'high_priority': [3, 7, 14],
                'nurture': [7, 14, 30]
            }
        }

class AgenticProcessor:
    """
    Main agentic processing engine
    """
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.processed_signals = []
        self.autonomous_insights = []

    def analyze_signal_with_ai(self, signal):
        enhanced_signal = signal.copy()
        try:
            text_content = f"{signal.get('description', '')} {signal.get('content_snippet', '')}"
            sentiment_result = self.analyzer.sentiment_analyzer(text_content[:512])
            enhanced_signal['ai_sentiment'] = sentiment_result[0]['label']
            enhanced_signal['ai_sentiment_score'] = sentiment_result[0]['score']
            vader_scores = self.analyzer.vader.polarity_scores(text_content)
            enhanced_signal['vader_sentiment'] = vader_scores
            intent_labels = [
                'buying intent', 'research intent', 'comparison shopping',
                'problem solving', 'vendor evaluation', 'technology adoption'
            ]
            intent_result = self.analyzer.intent_classifier(text_content[:512], intent_labels)
            enhanced_signal['primary_intent'] = intent_result['labels'][0]
            enhanced_signal['intent_confidence'] = intent_result['scores'][0]
            entities = self.analyzer.ner_pipeline(text_content[:512])
            enhanced_signal['entities'] = [
                {'text': ent['word'], 'label': ent['entity_group'], 'confidence': ent['score']}
                for ent in entities if ent['score'] > 0.7
            ]
            enhanced_signal.update(self.match_knowledge_patterns(text_content))
            enhanced_signal.update(self.calculate_ai_scores(enhanced_signal))
            return enhanced_signal
        except Exception as e:
            print(f"⚠️ Error in AI analysis: {e}")
            return enhanced_signal

    def match_knowledge_patterns(self, text):
        text_lower = text.lower()
        kb = self.analyzer.knowledge_base
        buying_signals = sum(1 for signal in kb['buying_signals'] if signal in text_lower)
        buying_intent_score = min(1.0, buying_signals / 3)
        pain_points = [point for point in kb['pain_points'] if point in text_lower]
        pain_score = min(1.0, len(pain_points) / 2)
        urgency_indicators = [ind for ind in kb['urgency_indicators'] if ind in text_lower]
        urgency_score = min(1.0, len(urgency_indicators) / 2)
        detected_stage = 'unknown'
        for stage, keywords in kb['company_stages'].items():
            if any(keyword in text_lower for keyword in keywords):
                detected_stage = stage
                break
        tech_interests = []
        for category, keywords in kb['tech_categories'].items():
            if any(keyword in text_lower for keyword in keywords):
                tech_interests.append(category)
        return {
            'buying_intent_score': buying_intent_score,
            'pain_score': pain_score,
            'urgency_score': urgency_score,
            'detected_company_stage': detected_stage,
            'technology_interests': tech_interests,
            'matched_pain_points': pain_points,
            'urgency_indicators': urgency_indicators
        }

    def calculate_ai_scores(self, signal):
        company_fit_factors = [
            signal.get('buying_intent_score', 0) * 0.3,
            signal.get('intent_confidence', 0) * 0.2,
            signal.get('ai_sentiment_score', 0) * 0.2,
            (1 if signal.get('detected_company_stage') != 'unknown' else 0) * 0.15,
            (len(signal.get('technology_interests', [])) / 5) * 0.15
        ]
        company_fit_score = sum(company_fit_factors)
        engagement_factors = [
            signal.get('urgency_score', 0) * 0.25,
            signal.get('pain_score', 0) * 0.25,
            signal.get('buying_intent_score', 0) * 0.3,
            (signal.get('engagement_score', 0) / 100) * 0.2
        ]
        engagement_potential = sum(engagement_factors)
        entity_clarity = len(signal.get('entities', [])) / 5 if signal.get('entities') else 0.3
        priority_score = (
            signal.get('signal_strength', 5) * 0.3 +
            company_fit_score * 10 * 0.25 +
            engagement_potential * 10 * 0.25 +
            signal.get('confidence_level', 0.5) * 10 * 0.2
        )
        return {
            'company_fit_score': round(company_fit_score, 3),
            'engagement_potential': round(engagement_potential, 3),
            'entity_clarity': round(entity_clarity, 3),
            'ai_priority_score': round(priority_score, 2)
        }

    def make_autonomous_decisions(self, enhanced_signal):
        decisions = []
        rules = self.analyzer.decision_engine.decision_rules
        for rule_name, rule in rules.items():
            if self.evaluate_conditions(enhanced_signal, rule['conditions']):
                decisions.append({
                    'rule': rule_name,
                    'action': rule['action'],
                    'confidence': enhanced_signal.get('ai_priority_score', 5) / 10,
                    'reasoning': self.generate_reasoning(enhanced_signal, rule_name)
                })
        return decisions

    def evaluate_conditions(self, signal, conditions):
        for condition in conditions:
            try:
                parts = condition.replace('>=', '|>=|').replace('>', '|>|').replace('<', '|<|').replace('==', '|==|')
                for op in ['|>=|', '|>|', '|<|', '|==|']:
                    if op in parts:
                        field, operator, value = parts.split(op)
                        field = field.strip()
                        value = float(value.strip())
                        signal_value = signal.get(field, 0)
                        if operator == '|>=|' and signal_value >= value:
                            continue
                        elif operator == '|>|' and signal_value > value:
                            continue
                        elif operator == '|<|' and signal_value < value:
                            continue
                        elif operator == '|==|' and signal_value == value:
                            continue
                        else:
                            return False
            except:
                continue
        return True

    def generate_reasoning(self, signal, rule_name):
        reasoning_templates = {
            'immediate_action': f"High signal strength ({signal.get('signal_strength', 0)}) with strong buying intent ({signal.get('buying_intent_score', 0):.2f}) and urgency indicators detected.",
            'high_priority': f"Good company fit ({signal.get('company_fit_score', 0):.2f}) with solid signal strength ({signal.get('signal_strength', 0)}).",
            'nurture': f"Moderate engagement potential ({signal.get('engagement_potential', 0):.2f}) suggests nurturing opportunity.",
            'research_needed': f"Low confidence ({signal.get('confidence_level', 0):.2f}) requires additional research before action."
        }
        return reasoning_templates.get(rule_name, "Standard processing rule applied.")

class AgenticReportGenerator:
    """
    Generate intelligent reports with AI insights
    """
    def __init__(self, processor):
        self.processor = processor

    def generate_ai_insights_report(self):
        signals = self.processor.processed_signals
        if not signals:
            print("❌ No processed signals available for AI insights")
            return
        print("\n" + "="*80)
        print("🤖 AI-POWERED INTENT SIGNAL INSIGHTS REPORT")
        print("="*80)
        total_signals = len(signals)
        high_intent_signals = len([s for s in signals if s.get('buying_intent_score', 0) > 0.6])
        urgent_signals = len([s for s in signals if s.get('urgency_score', 0) > 0.5])
        print(f"\n🧠 AI ANALYSIS OVERVIEW:")
        print(f"Total Analyzed Signals: {total_signals}")
        print(f"High Buying Intent: {high_intent_signals} ({high_intent_signals/total_signals*100:.1f}%)")
        print(f"Urgent Signals: {urgent_signals} ({urgent_signals/total_signals*100:.1f}%)")
        intent_distribution = defaultdict(int)
        for signal in signals:
            intent = signal.get('primary_intent', 'unknown')
            intent_distribution[intent] += 1
        print(f"\n🎯 INTENT DISTRIBUTION:")
        for intent, count in sorted(intent_distribution.items(), key=lambda x: x[1], reverse=True):
            percentage = count/total_signals*100
            print(f"  {intent}: {count} signals ({percentage:.1f}%)")
        sentiment_scores = [s.get('ai_sentiment_score', 0.5) for s in signals]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        positive_sentiment = len([s for s in signals if s.get('ai_sentiment') == 'POSITIVE'])
        print(f"\n😊 SENTIMENT ANALYSIS:")
        print(f"Average Sentiment Score: {avg_sentiment:.3f}")
        print(f"Positive Sentiment: {positive_sentiment} signals ({positive_sentiment/total_signals*100:.1f}%)")
        fit_scores = [s.get('company_fit_score', 0) for s in signals]
        high_fit_companies = [s for s in signals if s.get('company_fit_score', 0) > 0.7]
        print(f"\n🏢 COMPANY FIT ANALYSIS:")
        print(f"Average Company Fit Score: {sum(fit_scores)/len(fit_scores):.3f}")
        print(f"High-Fit Companies: {len(high_fit_companies)}")
        all_decisions = []
        for signal in signals:
            if 'autonomous_decisions' in signal:
                all_decisions.extend(signal['autonomous_decisions'])
        if all_decisions:
            action_counts = defaultdict(int)
            for decision in all_decisions:
                action_counts[decision['action']] += 1
            print(f"\n🤖 TOP AI-RECOMMENDED ACTIONS:")
            for action, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  {action}: {count} recommendations")
        all_tech_interests = []
        for signal in signals:
            all_tech_interests.extend(signal.get('technology_interests', []))
        if all_tech_interests:
            tech_counter = Counter(all_tech_interests)
            print(f"\n💻 TRENDING TECHNOLOGY INTERESTS:")
            for tech, count in tech_counter.most_common(5):
                print(f"  {tech}: {count} mentions")
        return self.generate_actionable_recommendations(signals)

    def generate_actionable_recommendations(self, signals):
        print(f"\n🎯 AI-GENERATED ACTIONABLE RECOMMENDATIONS:")
        immediate_actions = []
        high_priority_items = []
        research_items = []
        for signal in signals:
            decisions = signal.get('autonomous_decisions', [])
            for decision in decisions:
                item = {
                    'company': signal.get('company_name', 'Unknown'),
                    'description': signal.get('description', '')[:60] + '...',
                    'action': decision['action'],
                    'confidence': decision['confidence'],
                    'reasoning': decision['reasoning']
                }
                if decision['action'] == 'schedule_immediate_outreach':
                    immediate_actions.append(item)
                elif decision['action'] == 'add_to_priority_queue':
                    high_priority_items.append(item)
                elif decision['action'] == 'schedule_research_task':
                    research_items.append(item)
        if immediate_actions:
            print(f"\n🚨 IMMEDIATE ACTIONS ({len(immediate_actions)} items):")
            for item in sorted(immediate_actions, key=lambda x: x['confidence'], reverse=True)[:5]:
                print(f"  • {item['company']}: {item['description']}")
                print(f"    Action: {item['action']} (Confidence: {item['confidence']:.2f})")
                print(f"    Reasoning: {item['reasoning']}")
        if high_priority_items:
            print(f"\n⭐ HIGH PRIORITY QUEUE ({len(high_priority_items)} items):")
            for item in sorted(high_priority_items, key=lambda x: x['confidence'], reverse=True)[:5]:
                print(f"  • {item['company']}: {item['description']}")
        if research_items:
            print(f"\n🔍 RESEARCH REQUIRED ({len(research_items)} items):")
            for item in research_items[:3]:
                print(f"  • {item['company']}: {item['description']}")
        return {
            'immediate_actions': immediate_actions,
            'high_priority': high_priority_items,
            'research_needed': research_items
        }

def run_agentic_analysis(collector, output_dir):
    print("🚀 Starting Agentic Intent Signal Analysis...")
    print("="*60)
    if not hasattr(collector, 'detailed_signals') or not collector.detailed_signals:
        print("❌ No signals found. Please run the data collection pipeline first.")
        return None, None
    print("🤖 Initializing AI-powered analysis components...")
    agentic_analyzer = AgenticIntentAnalyzer(collector)
    agentic_processor = AgenticProcessor(agentic_analyzer)
    print(f"🔄 Processing {len(collector.detailed_signals)} signals with AI...")
    for i, signal in enumerate(collector.detailed_signals):
        print(f"  Processing signal {i+1}/{len(collector.detailed_signals)}: {signal.get('company_name', 'Unknown')}")
        enhanced_signal = agentic_processor.analyze_signal_with_ai(signal)
        decisions = agentic_processor.make_autonomous_decisions(enhanced_signal)
        enhanced_signal['autonomous_decisions'] = decisions
        agentic_processor.processed_signals.append(enhanced_signal)
    print(f"✅ AI analysis complete! Processed {len(agentic_processor.processed_signals)} signals")
    report_generator = AgenticReportGenerator(agentic_processor)
    recommendations = report_generator.generate_ai_insights_report()
    export_ai_enhanced_data(agentic_processor.processed_signals, output_dir)
    return agentic_processor, recommendations

def export_ai_enhanced_data(processed_signals, output_dir):
    if not processed_signals:
        return
    enhanced_df = pd.DataFrame(processed_signals)
    for idx, row in enhanced_df.iterrows():
        if 'entities' in row and row['entities']:
            entity_texts = [ent['text'] for ent in row['entities']]
            enhanced_df.at[idx, 'extracted_entities'] = ', '.join(entity_texts)
        if 'autonomous_decisions' in row and row['autonomous_decisions']:
            decision_actions = [dec['action'] for dec in row['autonomous_decisions']]
            enhanced_df.at[idx, 'recommended_actions'] = ', '.join(decision_actions)
            best_decision = max(row['autonomous_decisions'], key=lambda x: x['confidence'])
            enhanced_df.at[idx, 'primary_recommendation'] = best_decision['action']
            enhanced_df.at[idx, 'recommendation_confidence'] = best_decision['confidence']
            enhanced_df.at[idx, 'ai_reasoning'] = best_decision['reasoning']
    ai_csv = os.path.join(output_dir, "ai_enhanced_intent_signals.csv")
    enhanced_df.to_csv(ai_csv, index=False, encoding='utf-8')
    print(f"✅ AI-enhanced data exported to {ai_csv}")
    immediate_actions = enhanced_df[enhanced_df['recommended_actions'].str.contains('immediate_outreach', na=False)]
    if not immediate_actions.empty:
        immediate_csv = os.path.join(output_dir, "immediate_action_signals.csv")
        immediate_actions.to_csv(immediate_csv, index=False)
        print(f"✅ Immediate action signals exported ({len(immediate_actions)} records)")
    high_priority = enhanced_df[enhanced_df['recommended_actions'].str.contains('priority_queue', na=False)]
    if not high_priority.empty:
        high_priority_csv = os.path.join(output_dir, "high_priority_queue.csv")
        high_priority.to_csv(high_priority_csv, index=False)
        print(f"✅ High priority queue exported ({len(high_priority)} records)")
    return enhanced_df

def create_ai_dashboard(output_dir):
    ai_csv = os.path.join(output_dir, "ai_enhanced_intent_signals.csv")
    if not os.path.exists(ai_csv):
        print("❌ No data available for dashboard")
        return
    print("📊 Creating AI Insights Dashboard...")
    try:
        df = pd.read_csv(ai_csv)
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        sentiment_counts = df['ai_sentiment'].value_counts()
        axes[0,0].pie(sentiment_counts.values, labels=sentiment_counts.index, autopct='%1.1f%%')
        axes[0,0].set_title('AI Sentiment Analysis Distribution')
        axes[0,1].scatter(df['buying_intent_score'], df['company_fit_score'],
                         alpha=0.6, c=df['ai_priority_score'], cmap='viridis')
        axes[0,1].set_xlabel('Buying Intent Score')
        axes[0,1].set_ylabel('Company Fit Score')
        axes[0,1].set_title('Buying Intent vs Company Fit')
        intent_counts = df['primary_intent'].value_counts().head(6)
        axes[0,2].bar(range(len(intent_counts)), intent_counts.values)
        axes[0,2].set_xticks(range(len(intent_counts)))
        axes[0,2].set_xticklabels(intent_counts.index, rotation=45, ha='right')
        axes[0,2].set_title('Primary Intent Classification')
        axes[1,0].hist(df['ai_priority_score'], bins=20, alpha=0.7, color='purple')
        axes[1,0].set_xlabel('AI Priority Score')
        axes[1,0].set_ylabel('Frequency')
        axes[1,0].set_title('AI Priority Score Distribution')
        axes[1,1].scatter(df['engagement_potential'], df['urgency_score'],
                         alpha=0.6, s=df['ai_priority_score']*10)
        axes[1,1].set_xlabel('Engagement Potential')
        axes[1,1].set_ylabel('Urgency Score')
        axes[1,1].set_title('Engagement Potential vs Urgency (Size = Priority)')
        if 'primary_recommendation' in df.columns:
            rec_counts = df['primary_recommendation'].value_counts()
            axes[1,2].bar(range(len(rec_counts)), rec_counts.values, color='orange')
            axes[1,2].set_xticks(range(len(rec_counts)))
            axes[1,2].set_xticklabels(rec_counts.index, rotation=45, ha='right')
            axes[1,2].set_title('AI Recommended Actions')
        plt.tight_layout()
        plt.show()
        print("✅ AI Dashboard created successfully!")
    except Exception as e:
        print(f"❌ Error creating dashboard: {e}") 