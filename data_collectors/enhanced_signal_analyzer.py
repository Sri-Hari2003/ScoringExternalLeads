import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

class EnhancedSignalAnalyzer:
    def __init__(self, collector):
        self.collector = collector
        # Create a timestamped output folder for this run
        self.timestamp_folder = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.output_dir = os.path.join('csv_outputs', self.timestamp_folder)
        os.makedirs(self.output_dir, exist_ok=True)

    def export_comprehensive_csv(self, filename="comprehensive_intent_signals.csv"):
        """Export all collected data to a comprehensive CSV file in the timestamped folder"""
        if not self.collector.detailed_signals:
            print("❌ No detailed signals to export")
            return
        df = pd.DataFrame(self.collector.detailed_signals)
        df['days_since_collection'] = (datetime.now() - pd.to_datetime(df['timestamp'])).dt.days
        df['signal_priority_score'] = df['signal_strength'] * df['confidence_level']
        df['needs_immediate_action'] = (df['signal_strength'] >= 8) & (df['follow_up_required'] == True)
        column_order = [
            'collection_date', 'timestamp', 'signal_type', 'company_name',
            'signal_strength', 'priority_level', 'confidence_level',
            'follow_up_required', 'needs_immediate_action',
            'source', 'source_type', 'description', 'url',
            'keyword', 'search_term', 'content_snippet',
            'author', 'publication_date', 'engagement_score',
            'sentiment_score', 'relevance_score',
            'geographic_location', 'industry_category', 'signal_context',
            'processing_notes', 'signal_priority_score', 'days_since_collection',
            'raw_data', 'metadata'
        ]
        existing_columns = [col for col in column_order if col in df.columns]
        remaining_columns = [col for col in df.columns if col not in column_order]
        final_columns = existing_columns + remaining_columns
        df = df[final_columns]
        out_path = os.path.join(self.output_dir, filename)
        df.to_csv(out_path, index=False, encoding='utf-8')
        print(f"✅ Comprehensive data exported to {out_path}")
        print(f"📊 Total records: {len(df)}")
        print(f"📈 Columns included: {len(df.columns)}")
        print(f"🚨 High priority signals: {len(df[df['needs_immediate_action'] == True])}")
        print(f"\n📋 Sample of exported data:")
        print(df[['company_name', 'signal_type', 'signal_strength', 'priority_level', 'description']].head())
        return df

    def generate_enhanced_report(self):
        if not self.collector.detailed_signals:
            print("❌ No signals collected yet!")
            return
        df = pd.DataFrame(self.collector.detailed_signals)
        print("\n" + "="*80)
        print("🎯 COMPREHENSIVE INTENT SIGNAL ANALYSIS REPORT")
        print("="*80)
        total_signals = len(df)
        unique_companies = df['company_name'].nunique()
        avg_strength = df['signal_strength'].mean()
        avg_confidence = df['confidence_level'].mean()
        high_priority_count = len(df[df['follow_up_required'] == True])
        print(f"\n📊 OVERVIEW:")
        print(f"Total Signals Collected: {total_signals}")
        print(f"Unique Companies: {unique_companies}")
        print(f"Average Signal Strength: {avg_strength:.1f}/10")
        print(f"Average Confidence Level: {avg_confidence:.2f}")
        print(f"High Priority Signals: {high_priority_count} ({high_priority_count/total_signals*100:.1f}%)")
        print(f"\n🎯 PRIORITY BREAKDOWN:")
        priority_counts = df['priority_level'].value_counts()
        for priority, count in priority_counts.items():
            percentage = count/total_signals*100
            print(f"  {priority}: {count} signals ({percentage:.1f}%)")
        print(f"\n📡 SOURCE ANALYSIS:")
        source_counts = df['source_type'].value_counts()
        for source, count in source_counts.items():
            avg_strength = df[df['source_type'] == source]['signal_strength'].mean()
            print(f"  {source}: {count} signals (avg strength: {avg_strength:.1f})")
        print(f"\n🏢 TOP COMPANIES BY SIGNAL STRENGTH:")
        company_performance = df.groupby('company_name').agg({
            'signal_strength': 'mean',
            'confidence_level': 'mean',
            'follow_up_required': 'sum'
        }).round(2).sort_values('signal_strength', ascending=False).head(10)
        for company, data in company_performance.iterrows():
            print(f"  {company}: Strength {data['signal_strength']:.1f}, Confidence {data['confidence_level']:.2f}, Follow-ups: {int(data['follow_up_required'])}")

    def create_enhanced_visualizations(self):
        if not self.collector.detailed_signals:
            print("❌ No signals to visualize")
            return
        df = pd.DataFrame(self.collector.detailed_signals)
        fig, axes = plt.subplots(3, 2, figsize=(18, 15))
        axes[0,0].scatter(df['signal_strength'], df['confidence_level'], alpha=0.6, c=df['signal_strength'], cmap='viridis')
        axes[0,0].set_xlabel('Signal Strength')
        axes[0,0].set_ylabel('Confidence Level')
        axes[0,0].set_title('Signal Strength vs Confidence Level')
        priority_counts = df['priority_level'].value_counts()
        axes[0,1].pie(priority_counts.values, labels=priority_counts.index, autopct='%1.1f%%')
        axes[0,1].set_title('Signal Priority Distribution')
        source_performance = df.groupby('source_type')['signal_strength'].mean().sort_values(ascending=True)
        axes[1,0].barh(range(len(source_performance)), source_performance.values)
        axes[1,0].set_yticks(range(len(source_performance)))
        axes[1,0].set_yticklabels(source_performance.index)
        axes[1,0].set_title('Average Signal Strength by Source Type')
        axes[1,0].set_xlabel('Average Signal Strength')
        axes[1,1].hist(df['engagement_score'], bins=20, alpha=0.7, color='orange')
        axes[1,1].set_xlabel('Engagement Score')
        axes[1,1].set_ylabel('Frequency')
        axes[1,1].set_title('Engagement Score Distribution')
        axes[2,0].hist(df['sentiment_score'], bins=15, alpha=0.7, color='green')
        axes[2,0].set_xlabel('Sentiment Score (-1 to 1)')
        axes[2,0].set_ylabel('Frequency')
        axes[2,0].set_title('Sentiment Score Distribution')
        axes[2,0].axvline(x=0, color='red', linestyle='--', alpha=0.5)
        followup_by_type = df.groupby('signal_type')['follow_up_required'].sum().sort_values(ascending=False)
        axes[2,1].bar(range(len(followup_by_type)), followup_by_type.values)
        axes[2,1].set_xticks(range(len(followup_by_type)))
        axes[2,1].set_xticklabels(followup_by_type.index, rotation=45, ha='right')
        axes[2,1].set_title('Follow-up Required by Signal Type')
        axes[2,1].set_ylabel('Count')
        plt.tight_layout()
        plt.show() 