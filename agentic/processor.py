from collections import defaultdict, Counter
import pandas as pd
import matplotlib.pyplot as plt

class AgenticProcessor:
    """
    Main agentic processing engine
    """

    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.processed_signals = []
        self.autonomous_insights = []

    def analyze_signal_with_ai(self, signal):
        """Comprehensive AI analysis of a single signal"""
        enhanced_signal = signal.copy()

        try:
            # Extract text for analysis
            text_content = f"{signal.get('description', '')} {signal.get('content_snippet', '')}"

            # AI-powered sentiment analysis
            sentiment_result = self.analyzer.sentiment_analyzer(text_content[:512])
            enhanced_signal['ai_sentiment'] = sentiment_result[0]['label']
            enhanced_signal['ai_sentiment_score'] = sentiment_result[0]['score']

            # VADER sentiment as backup
            vader_scores = self.analyzer.vader.polarity_scores(text_content)
            enhanced_signal['vader_sentiment'] = vader_scores

            # Intent classification
            intent_labels = [
                'buying intent', 'research intent', 'comparison shopping',
                'problem solving', 'vendor evaluation', 'technology adoption'
            ]
            intent_result = self.analyzer.intent_classifier(text_content[:512], intent_labels)
            enhanced_signal['primary_intent'] = intent_result['labels'][0]
            enhanced_signal['intent_confidence'] = intent_result['scores'][0]

            # Named Entity Recognition
            entities = self.analyzer.ner_pipeline(text_content[:512])
            enhanced_signal['entities'] = [
                {'text': ent['word'], 'label': ent['entity_group'], 'confidence': ent['score']}
                for ent in entities if ent['score'] > 0.7
            ]

            # Knowledge base matching
            enhanced_signal.update(self.match_knowledge_patterns(text_content))

            # Calculate AI-driven scores
            enhanced_signal.update(self.calculate_ai_scores(enhanced_signal))

            return enhanced_signal

        except Exception as e:
            print(f"⚠️ Error in AI analysis: {e}")
            return enhanced_signal

    def match_knowledge_patterns(self, text):
        """Match text against knowledge base patterns"""
        text_lower = text.lower()
        kb = self.analyzer.knowledge_base

        # Buying signals detection
        buying_signals = sum(1 for signal in kb['buying_signals'] if signal in text_lower)
        buying_intent_score = min(1.0, buying_signals / 3)

        # Pain points detection
        pain_points = [point for point in kb['pain_points'] if point in text_lower]
        pain_score = min(1.0, len(pain_points) / 2)

        # Urgency detection
        urgency_indicators = [ind for ind in kb['urgency_indicators'] if ind in text_lower]
        urgency_score = min(1.0, len(urgency_indicators) / 2)

        # Company stage detection
        detected_stage = 'unknown'
        for stage, keywords in kb['company_stages'].items():
            if any(keyword in text_lower for keyword in keywords):
                detected_stage = stage
                break

        # Technology category detection
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
        """Calculate comprehensive AI-driven scores"""
        # Company fit score (based on multiple factors)
        company_fit_factors = [
            signal.get('buying_intent_score', 0) * 0.3,
            signal.get('intent_confidence', 0) * 0.2,
            signal.get('ai_sentiment_score', 0) * 0.2,
            (1 if signal.get('detected_company_stage') != 'unknown' else 0) * 0.15,
            (len(signal.get('technology_interests', [])) / 5) * 0.15
        ]
        company_fit_score = sum(company_fit_factors)

        # Engagement potential (likelihood of positive response)
        engagement_factors = [
            signal.get('urgency_score', 0) * 0.25,
            signal.get('pain_score', 0) * 0.25,
            signal.get('buying_intent_score', 0) * 0.3,
            (signal.get('engagement_score', 0) / 100) * 0.2
        ]
        engagement_potential = sum(engagement_factors)

        # Entity clarity (how well we understand the signal)
        entity_clarity = len(signal.get('entities', [])) / 5 if signal.get('entities') else 0.3

        # Composite priority score
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
        """Make autonomous decisions based on AI analysis"""
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
        """Evaluate rule conditions against signal data"""
        for condition in conditions:
            try:
                # Parse condition (e.g., 'signal_strength >= 8')
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
        """Generate human-readable reasoning for decisions"""
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
        """Generate comprehensive AI-powered insights report"""
        signals = self.processor.processed_signals

        if not signals:
            print("❌ No processed signals available for AI insights")
            return

        print("\n" + "="*80)
        print("🤖 AI-POWERED INTENT SIGNAL INSIGHTS REPORT")
        print("="*80)

        # AI Analysis Overview
        total_signals = len(signals)
        high_intent_signals = len([s for s in signals if s.get('buying_intent_score', 0) > 0.6])
        urgent_signals = len([s for s in signals if s.get('urgency_score', 0) > 0.5])

        print(f"\n🧠 AI ANALYSIS OVERVIEW:")
        print(f"Total Analyzed Signals: {total_signals}")
        print(f"High Buying Intent: {high_intent_signals} ({high_intent_signals/total_signals*100:.1f}%)")
        print(f"Urgent Signals: {urgent_signals} ({urgent_signals/total_signals*100:.1f}%)")

        # Intent Distribution
        intent_distribution = defaultdict(int)
        for signal in signals:
            intent = signal.get('primary_intent', 'unknown')
            intent_distribution[intent] += 1

        print(f"\n🎯 INTENT DISTRIBUTION:")
        for intent, count in sorted(intent_distribution.items(), key=lambda x: x[1], reverse=True):
            percentage = count/total_signals*100
            print(f"  {intent}: {count} signals ({percentage:.1f}%)")

        # Sentiment Analysis
        sentiment_scores = [s.get('ai_sentiment_score', 0.5) for s in signals]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        positive_sentiment = len([s for s in signals if s.get('ai_sentiment') == 'POSITIVE'])

        print(f"\n😊 SENTIMENT ANALYSIS:")
        print(f"Average Sentiment Score: {avg_sentiment:.3f}")
        print(f"Positive Sentiment: {positive_sentiment} signals ({positive_sentiment/total_signals*100:.1f}%)")

        # Company Fit Analysis
        fit_scores = [s.get('company_fit_score', 0) for s in signals]
        high_fit_companies = [s for s in signals if s.get('company_fit_score', 0) > 0.7]

        print(f"\n🏢 COMPANY FIT ANALYSIS:")
        print(f"Average Company Fit Score: {sum(fit_scores)/len(fit_scores):.3f}")
        print(f"High-Fit Companies: {len(high_fit_companies)}")

        # Top AI-Recommended Actions
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

        # Technology Interest Trends
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
        """Generate specific actionable recommendations"""
        print(f"\n🎯 AI-GENERATED ACTIONABLE RECOMMENDATIONS:")

        # Immediate action items
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

        # Display recommendations
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