# Main Agentic Intent Signal Analysis Execution
# Enhanced with AI-powered analysis and automated decision-making

import pandas as pd
import matplotlib.pyplot as plt
from agentic.analyzer import AgenticIntentAnalyzer
from agentic.processor import AgenticProcessor, AgenticReportGenerator
from agentic.decision_engine import DecisionEngine
from DataCollectors.GoogleNewsCollector import EnhancedGoogleNewsCollector
from DataCollectors.RedditCollector import EnhancedRedditCollector
from DataCollectors.JobPostingCollector import EnhancedJobPostingCollector
from DataCollectors.BuiltWithCollector import BuiltWithCollector
from config.KnowledgeBase import get_knowledge_base

def collect_all_signals():
    kb = get_knowledge_base()
    signals = []
    # Google News
    news_collector = EnhancedGoogleNewsCollector(knowledge_base=kb)
    signals.extend(news_collector.search_company_news(['OpenAI', 'Google'], ['AI', 'cloud']))
    # Reddit
    reddit_collector = EnhancedRedditCollector(knowledge_base=kb)
    signals.extend(reddit_collector.search_reddit_mentions(['OpenAI', 'Google'], ['AI', 'cloud']))
    # Job Postings
    job_collector = EnhancedJobPostingCollector(knowledge_base=kb)
    signals.extend(job_collector.search_job_postings(['San Francisco', 'New York'], ['AI', 'cloud']))
    # BuiltWith (requires API key)
    # builtwith_collector = BuiltWithCollector(api_key='YOUR_API_KEY')
    # signals.extend(builtwith_collector.collect_builtwith_signals([...]))
    return signals

def run_agentic_analysis(collector=None):
    """
    Main agentic analysis function
    """
    print("🚀 Starting Agentic Intent Signal Analysis...")
    print("="*60)

    # Check if we have collected signals
    if not collector or not hasattr(collector, 'detailed_signals') or not collector.detailed_signals:
        print("❌ No signals found. Please run the data collection pipeline first.")
        return None, None

    # Initialize agentic components
    print("🤖 Initializing AI-powered analysis components...")
    agentic_analyzer = AgenticIntentAnalyzer(collector)
    agentic_processor = AgenticProcessor(agentic_analyzer)

    # Process each signal with AI
    print(f"🔄 Processing {len(collector.detailed_signals)} signals with AI...")

    for i, signal in enumerate(collector.detailed_signals):
        print(f"  Processing signal {i+1}/{len(collector.detailed_signals)}: {signal.get('company_name', 'Unknown')}")

        # AI analysis
        enhanced_signal = agentic_processor.analyze_signal_with_ai(signal)

        # Autonomous decision making
        decisions = agentic_processor.make_autonomous_decisions(enhanced_signal)
        enhanced_signal['autonomous_decisions'] = decisions

        # Store processed signal
        agentic_processor.processed_signals.append(enhanced_signal)

    print(f"✅ AI analysis complete! Processed {len(agentic_processor.processed_signals)} signals")

    # Generate AI insights report
    report_generator = AgenticReportGenerator(agentic_processor)
    recommendations = report_generator.generate_ai_insights_report()

    # Export AI-enhanced data
    export_ai_enhanced_data(agentic_processor.processed_signals)

    return agentic_processor, recommendations

def export_ai_enhanced_data(processed_signals):
    """Export AI-enhanced signal data"""
    if not processed_signals:
        return None

    # Create enhanced DataFrame
    enhanced_df = pd.DataFrame(processed_signals)

    # Flatten nested data for CSV export
    for idx, row in enhanced_df.iterrows():
        # Flatten entities
        if 'entities' in row and row['entities']:
            entity_texts = [ent['text'] for ent in row['entities']]
            enhanced_df.at[idx, 'extracted_entities'] = ', '.join(entity_texts)

        # Flatten autonomous decisions
        if 'autonomous_decisions' in row and row['autonomous_decisions']:
            decision_actions = [dec['action'] for dec in row['autonomous_decisions']]
            enhanced_df.at[idx, 'recommended_actions'] = ', '.join(decision_actions)

            # Get highest confidence decision
            best_decision = max(row['autonomous_decisions'], key=lambda x: x['confidence'])
            enhanced_df.at[idx, 'primary_recommendation'] = best_decision['action']
            enhanced_df.at[idx, 'recommendation_confidence'] = best_decision['confidence']
            enhanced_df.at[idx, 'ai_reasoning'] = best_decision['reasoning']

    # Export comprehensive AI-enhanced dataset
    enhanced_df.to_csv("ai_enhanced_intent_signals.csv", index=False, encoding='utf-8')
    print(f"✅ AI-enhanced data exported to ai_enhanced_intent_signals.csv")

    # Export action-specific datasets
    if 'recommended_actions' in enhanced_df.columns:
        immediate_mask = enhanced_df['recommended_actions'].str.contains('immediate_outreach', na=False)
        immediate_actions = enhanced_df[immediate_mask]
        if len(immediate_actions) > 0:
            immediate_actions.to_csv("immediate_action_signals.csv", index=False)
            print(f"✅ Immediate action signals exported ({len(immediate_actions)} records)")

        priority_mask = enhanced_df['recommended_actions'].str.contains('priority_queue', na=False)
        high_priority = enhanced_df[priority_mask]
        if len(high_priority) > 0:
            high_priority.to_csv("high_priority_queue.csv", index=False)
            print(f"✅ High priority queue exported ({len(high_priority)} records)")

    return enhanced_df

def create_ai_dashboard(collector=None):
    """Create interactive AI insights dashboard"""
    if not collector or not hasattr(collector, 'detailed_signals'):
        print("❌ No data available for dashboard")
        return

    # This would create visualizations of AI insights
    print("📊 Creating AI Insights Dashboard...")

    # Load processed data
    try:
        df = pd.read_csv("ai_enhanced_intent_signals.csv")

        # Create enhanced visualizations
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))

        # AI Sentiment Distribution
        sentiment_counts = df['ai_sentiment'].value_counts()
        axes[0,0].pie(sentiment_counts.values, labels=sentiment_counts.index, autopct='%1.1f%%')
        axes[0,0].set_title('AI Sentiment Analysis Distribution')

        # Buying Intent vs Company Fit
        axes[0,1].scatter(df['buying_intent_score'], df['company_fit_score'],
                         alpha=0.6, c=df['ai_priority_score'], cmap='viridis')
        axes[0,1].set_xlabel('Buying Intent Score')
        axes[0,1].set_ylabel('Company Fit Score')
        axes[0,1].set_title('Buying Intent vs Company Fit')

        # Intent Classification Distribution
        intent_counts = df['primary_intent'].value_counts().head(6)
        axes[0,2].bar(range(len(intent_counts)), intent_counts.values)
        axes[0,2].set_xticks(range(len(intent_counts)))
        axes[0,2].set_xticklabels(intent_counts.index, rotation=45, ha='right')
        axes[0,2].set_title('Primary Intent Classification')

        # AI Priority Score Distribution
        axes[1,0].hist(df['ai_priority_score'], bins=20, alpha=0.7, color='purple')
        axes[1,0].set_xlabel('AI Priority Score')
        axes[1,0].set_ylabel('Frequency')
        axes[1,0].set_title('AI Priority Score Distribution')

        # Engagement Potential vs Urgency
        axes[1,1].scatter(df['engagement_potential'], df['urgency_score'],
                         alpha=0.6, s=df['ai_priority_score']*10)
        axes[1,1].set_xlabel('Engagement Potential')
        axes[1,1].set_ylabel('Urgency Score')
        axes[1,1].set_title('Engagement Potential vs Urgency (Size = Priority)')

        # Recommendation Actions Distribution
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

# Main execution
if __name__ == "__main__":
    # Run the agentic analysis
    agentic_processor, ai_recommendations = run_agentic_analysis()

    # Create AI dashboard
    create_ai_dashboard()

    print(f"\n🎉 AGENTIC ANALYSIS COMPLETED!")
    print(f"📁 AI-Enhanced files generated:")
    print(f"  • ai_enhanced_intent_signals.csv - Complete AI analysis")
    print(f"  • immediate_action_signals.csv - Urgent follow-ups")
    print(f"  • high_priority_queue.csv - Priority prospects")
    print(f"\n🤖 The AI agent has analyzed your signals and made autonomous recommendations!")
    print(f"💡 Check the immediate action items for urgent follow-ups!") 