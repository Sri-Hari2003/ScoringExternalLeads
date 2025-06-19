class AgenticProcessor:
    """
    Main agentic processing engine
    """
    def __init__(self, analyzer, decision_engine):
        self.analyzer = analyzer
        self.decision_engine = decision_engine
        self.processed_signals = []

    def process_signals(self, signals):
        for signal in signals:
            enhanced_signal = self.analyzer.analyze_signal(signal)
            enhanced_signal.update(self.calculate_ai_scores(enhanced_signal))
            enhanced_signal['autonomous_decisions'] = self.make_autonomous_decisions(enhanced_signal)
            self.processed_signals.append(enhanced_signal)
        return self.processed_signals

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
        rules = self.decision_engine.decision_rules
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