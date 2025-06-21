from data_collectors.enhanced_intent_signal_collector import EnhancedIntentSignalCollector
from data_collectors.enhanced_google_news_collector import EnhancedGoogleNewsCollector
from data_collectors.enhanced_reddit_collector import EnhancedRedditCollector
from data_collectors.enhanced_job_posting_collector import EnhancedJobPostingCollector
from data_collectors.enhanced_signal_analyzer import EnhancedSignalAnalyzer
import pandas as pd
from datetime import datetime
import os

def analyze_signal_trends(df):
    if df is None or df.empty:
        return
    print("\n📈 SIGNAL TRENDS ANALYSIS:")
    df['timestamp_dt'] = pd.to_datetime(df['timestamp'])
    df['collection_day'] = df['timestamp_dt'].dt.date
    daily_counts = df.groupby('collection_day').size()
    print(f"Daily Signal Counts:")
    for date, count in daily_counts.items():
        print(f"  {date}: {count} signals")
    company_trends = df.groupby(['company_name', 'collection_day'])['signal_strength'].mean().unstack(fill_value=0)
    if len(company_trends.columns) > 1:
        for company in company_trends.index:
            values = company_trends.loc[company].values
            if len(values) > 1 and values[-1] > values[0]:
                trend = (values[-1] - values[0]) / len(values)
                if trend > 0.5:
                    print(f"📈 Trending UP: {company} (trend: +{trend:.1f})")

def generate_action_items(df):
    if df is None or df.empty:
        return
    print("\n🎯 RECOMMENDED ACTION ITEMS:")
    immediate_actions = df[df['needs_immediate_action'] == True].sort_values('signal_strength', ascending=False)
    if not immediate_actions.empty:
        print(f"\n🚨 IMMEDIATE ACTIONS REQUIRED ({len(immediate_actions)} items):")
        for _, signal in immediate_actions.head(10).iterrows():
            print(f"  • {signal['company_name']}: {signal['description'][:80]}...")
            print(f"    Strength: {signal['signal_strength']}/10, Source: {signal['source']}")
            print(f"    Action: {signal['signal_context']}")
    company_signal_counts = df.groupby('company_name').size().sort_values(ascending=False)
    hot_prospects = company_signal_counts[company_signal_counts >= 3].head(10)
    if not hot_prospects.empty:
        print(f"\n🔥 HOT PROSPECTS (Multiple Signals):")
        for company, count in hot_prospects.items():
            avg_strength = df[df['company_name'] == company]['signal_strength'].mean()
            latest_signal = df[df['company_name'] == company].sort_values('timestamp').iloc[-1]
            print(f"  • {company}: {count} signals, avg strength {avg_strength:.1f}")
            print(f"    Latest: {latest_signal['description'][:60]}...")
    keyword_analysis = df.groupby('keyword').agg({
        'signal_strength': 'mean',
        'company_name': 'nunique'
    }).sort_values('signal_strength', ascending=False)
    print(f"\n🔍 TRENDING KEYWORDS/TOPICS:")
    for keyword, data in keyword_analysis.head(10).iterrows():
        if keyword:
            print(f"  • {keyword}: {data['company_name']} companies, avg strength {data['signal_strength']:.1f}")

def export_executive_summary(df, output_dir, filename="executive_summary.csv"):
    if df is None or df.empty:
        return
    summary_data = []
    for company in df['company_name'].unique():
        company_df = df[df['company_name'] == company]
        summary = {
            'company_name': company,
            'total_signals': len(company_df),
            'avg_signal_strength': company_df['signal_strength'].mean(),
            'max_signal_strength': company_df['signal_strength'].max(),
            'high_priority_signals': len(company_df[company_df['priority_level'] == 'High']),
            'follow_up_required': len(company_df[company_df['follow_up_required'] == True]),
            'avg_confidence': company_df['confidence_level'].mean(),
            'primary_signal_types': ', '.join(company_df['signal_type'].value_counts().head(3).index.tolist()),
            'latest_signal_date': company_df['timestamp'].max(),
            'latest_signal_description': company_df.sort_values('timestamp').iloc[-1]['description'][:100],
            'recommendation': 'IMMEDIATE ACTION' if len(company_df[company_df['needs_immediate_action'] == True]) > 0
                           else 'HIGH PRIORITY' if company_df['signal_strength'].mean() >= 7
                           else 'MONITOR'
        }
        summary_data.append(summary)
    summary_df = pd.DataFrame(summary_data)
    summary_df = summary_df.sort_values('avg_signal_strength', ascending=False)
    out_path = os.path.join(output_dir, filename)
    summary_df.to_csv(out_path, index=False)
    print(f"✅ Executive summary exported to {out_path}")
    return summary_df

def run_enhanced_intent_signal_collection(target_companies=None):
    print("🚀 Starting Enhanced Intent Signal Collection Pipeline")
    print("=" * 60)
    collector = EnhancedIntentSignalCollector()
    
    # Default companies if none provided
    if target_companies is None:
        target_companies = [
            "Shopify", "Stripe", "HubSpot", "Salesforce", "Slack",
            "Zoom", "Atlassian", "Asana", "Monday.com", "Notion",
            "Zendesk", "Intercom", "Mailchimp", "Canva", "Figma"
        ]
    
    KEYWORDS = [
        "CRM", "automation", "API", "integration", "analytics",
        "machine learning", "AI", "workflow", "productivity", "SaaS",
        "customer success", "sales enablement", "marketing automation"
    ]
    TECH_KEYWORDS = [
        "Python", "React", "Node.js", "AWS", "API", "GraphQL",
        "microservices", "DevOps", "machine learning", "data science",
        "Kubernetes", "Docker", "TypeScript", "MongoDB", "PostgreSQL"
    ]
    enhanced_google_news = EnhancedGoogleNewsCollector(collector)
    enhanced_reddit = EnhancedRedditCollector(collector)
    enhanced_jobs = EnhancedJobPostingCollector(collector)
    print("\n🔄 Running enhanced data collection...")
    enhanced_google_news.search_company_news(target_companies[:5], KEYWORDS[:5], days_back=14)
    enhanced_reddit.search_reddit_mentions(target_companies[:4], KEYWORDS[:4])
    enhanced_jobs.search_job_postings(target_companies[:3], TECH_KEYWORDS[:5])
    print(f"\n✅ Enhanced collection complete! Found {len(collector.detailed_signals)} comprehensive signals")
    analyzer = EnhancedSignalAnalyzer(collector)
    comprehensive_df = analyzer.export_comprehensive_csv("comprehensive_intent_signals.csv")
    analyzer.generate_enhanced_report()
    analyzer.create_enhanced_visualizations()
    if comprehensive_df is not None:
        high_priority = comprehensive_df[comprehensive_df['needs_immediate_action'] == True]
        if not high_priority.empty:
            high_priority.to_csv(os.path.join(analyzer.output_dir, "high_priority_signals.csv"), index=False)
            print(f"✅ High priority signals exported to {os.path.join(analyzer.output_dir, 'high_priority_signals.csv')} ({len(high_priority)} records)")
        for source_type in comprehensive_df['source_type'].unique():
            source_df = comprehensive_df[comprehensive_df['source_type'] == source_type]
            filename = f"signals_{source_type.lower().replace(' ', '_')}.csv"
            source_df.to_csv(os.path.join(analyzer.output_dir, filename), index=False)
            print(f"✅ {source_type} signals exported to {os.path.join(analyzer.output_dir, filename)} ({len(source_df)} records)")
        top_companies = comprehensive_df['company_name'].value_counts().head(5).index
        for company in top_companies:
            company_df = comprehensive_df[comprehensive_df['company_name'] == company]
            filename = f"signals_{company.lower().replace(' ', '_').replace('.', '')}.csv"
            company_df.to_csv(os.path.join(analyzer.output_dir, filename), index=False)
            print(f"✅ {company} signals exported to {os.path.join(analyzer.output_dir, filename)} ({len(company_df)} records)")
    return collector, analyzer, comprehensive_df

if __name__ == "__main__":
    collector, analyzer, comprehensive_df = run_enhanced_intent_signal_collection()
    if comprehensive_df is not None:
        analyze_signal_trends(comprehensive_df)
        generate_action_items(comprehensive_df)
        executive_summary = export_executive_summary(comprehensive_df, analyzer.output_dir)
        print(f"\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        print(f"📁 Files generated in: {analyzer.output_dir}")
        print(f"  • comprehensive_intent_signals.csv - Complete dataset")
        print(f"  • high_priority_signals.csv - Urgent follow-ups")
        print(f"  • executive_summary.csv - Leadership overview")
        print(f"  • Source-specific CSV files")
        print(f"  • Company-specific CSV files")
        print(f"\n💡 Next steps: Review high priority signals and executive summary for immediate actions!") 