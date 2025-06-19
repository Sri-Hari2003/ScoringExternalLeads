from agentic.analyzer import AgenticAnalyzer
from agentic.processor import AgenticProcessor
from agentic.decision_engine import DecisionEngine
from DataCollectors.GoogleNewsCollector import EnhancedGoogleNewsCollector
from DataCollectors.RedditCollector import EnhancedRedditCollector
from DataCollectors.JobPostingCollector import EnhancedJobPostingCollector
from DataCollectors.BuiltWithCollector import BuiltWithCollector
from config.KnowledgeBase import get_knowledge_base

# Example: Collect signals from all collectors (customize as needed)
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

def main():
    print("\n🚀 Starting Modular Agentic Intent Signal Analysis...")
    signals = collect_all_signals()
    print(f"Collected {len(signals)} signals.")
    analyzer = AgenticAnalyzer()
    decision_engine = DecisionEngine()
    processor = AgenticProcessor(analyzer, decision_engine)
    processed_signals = processor.process_signals(signals)
    print(f"Processed {len(processed_signals)} signals with AI analysis and decision logic.")
    # Print a summary
    for i, signal in enumerate(processed_signals[:5]):
        print(f"\nSignal {i+1}:")
        print(f"  Company: {signal.get('company_name', 'N/A')}")
        print(f"  Description: {signal.get('description', '')[:60]}...")
        print(f"  AI Sentiment: {signal.get('ai_sentiment', 'N/A')} (Score: {signal.get('ai_sentiment_score', 0):.2f})")
        print(f"  Primary Intent: {signal.get('primary_intent', 'N/A')} (Conf: {signal.get('intent_confidence', 0):.2f})")
        print(f"  Decisions: {[d['action'] for d in signal.get('autonomous_decisions', [])]}")
    print("\n🎉 Agentic analysis complete!")

if __name__ == "__main__":
    main() 