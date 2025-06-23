# Streamlit Dashboard for AI Intent Signals with Real-time Collection
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from collections import Counter
import os
import time
import threading
from datetime import datetime
import sys
import io

# Import our modules
from main import run_enhanced_intent_signal_collection
from data_collectors.agentic_intent_analyzer import run_agentic_analysis, create_ai_dashboard

# Configure page
st.set_page_config(
    page_title="🤖 AI Intent Signals Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .section-header {
        background: #2c3e50;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        font-weight: bold;
    }
    .urgent-alert {
        background: #e74c3c;
        color: white;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 5px solid #c0392b;
    }
    .priority-item {
        background: #f39c12;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        border-left: 3px solid #d68910;
    }
    .research-item {
        background: #3498db;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        border-left: 3px solid #2980b9;
    }
    .intent-item {
        background: #34495e;
        color: white;
        padding: 0.8rem;
        border-radius: 4px;
        margin: 0.3rem 0;
        display: flex;
        justify-content: space-between;
    }
    .tech-trend {
        background: #9b59b6;
        color: white;
        padding: 0.8rem;
        border-radius: 4px;
        margin: 0.3rem 0;
        display: flex;
        justify-content: space-between;
    }
    .action-recommendation {
        background: #27ae60;
        color: white;
        padding: 0.8rem;
        border-radius: 4px;
        margin: 0.3rem 0;
        display: flex;
        justify-content: space-between;
    }
    .signal-item {
        background: #ecf0f1;
        color: #2c3e50;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        border-left: 4px solid #3498db;
    }
    .progress-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

# Session state for storing data
if 'collector' not in st.session_state:
    st.session_state.collector = None
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = None
if 'comprehensive_df' not in st.session_state:
    st.session_state.comprehensive_df = None
if 'ai_processor' not in st.session_state:
    st.session_state.ai_processor = None
if 'ai_recommendations' not in st.session_state:
    st.session_state.ai_recommendations = None
if 'signals_collected' not in st.session_state:
    st.session_state.signals_collected = []
if 'collection_complete' not in st.session_state:
    st.session_state.collection_complete = False

def create_main_header():
    """Create main dashboard header"""
    st.markdown("""
    <div class="main-header">
        <h1>🤖 External Intent Signal Insights </h1>
        <p>Comprehensive analysis of intent signals with AI-powered recommendations</p>
    </div>
    """, unsafe_allow_html=True)

def create_company_input_section():
    """Create company input section"""
    st.markdown('<div class="section-header">🏢 COMPANY SELECTION</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        company_input = st.text_area(
            "Enter company names (one per line):",
            height=150,
            placeholder="Enter company names here...\nExample:\nShopify\nStripe\nHubSpot\nSalesforce"
        )
    
    with col2:
        st.markdown("### 📋 Quick Add")
        if st.button("Add Sample Companies"):
            sample_companies = [
                "Shopify", "Stripe", "HubSpot", "Salesforce", "Slack",
                "Zoom", "Atlassian", "Asana", "Monday.com", "Notion"
            ]
            st.session_state.sample_companies = "\n".join(sample_companies)
            st.rerun()
        
        if st.button("Clear All"):
            st.session_state.sample_companies = ""
            st.rerun()
    
    # Parse companies
    if company_input:
        companies = [company.strip() for company in company_input.split('\n') if company.strip()]
        return companies
    return []

def run_signal_collection(companies):
    """Run signal collection with real-time progress"""
    if not companies:
        st.error("Please enter at least one company name.")
        return
    
    st.markdown('<div class="section-header">🔄 SIGNAL COLLECTION IN PROGRESS</div>', unsafe_allow_html=True)
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Run the collection pipeline
        status_text.text("Initializing collectors...")
        progress_bar.progress(10)
        
        # Run the main collection
        collector, analyzer, comprehensive_df = run_enhanced_intent_signal_collection(companies)
        
        # Store results in session state
        st.session_state.collector = collector
        st.session_state.analyzer = analyzer
        st.session_state.comprehensive_df = comprehensive_df
        st.session_state.collection_complete = True
        
        progress_bar.progress(100)
        status_text.text("✅ Signal collection completed!")
        
        # Display collected signals
        if comprehensive_df is not None:
            st.success(f"🎉 Successfully collected {len(comprehensive_df)} signals!")
            
            # Show sample of collected signals
            st.markdown("### 📊 Sample of Collected Signals")
            sample_signals = comprehensive_df[['company_name', 'signal_type', 'source', 'description', 'signal_strength']].head(10)
            st.dataframe(sample_signals, use_container_width=True)
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error during signal collection: {e}")
        return False

def run_ai_analysis():
    """Run AI analysis on collected signals"""
    if not st.session_state.collection_complete or st.session_state.analyzer is None:
        st.error("Please run signal collection first.")
        return
    
    st.markdown('<div class="section-header">🤖 AI ANALYSIS IN PROGRESS</div>', unsafe_allow_html=True)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("Initializing AI models...")
        progress_bar.progress(20)
        
        # Run AI analysis
        ai_processor, ai_recommendations = run_agentic_analysis(
            st.session_state.collector, 
            st.session_state.analyzer.output_dir
        )
        
        st.session_state.ai_processor = ai_processor
        st.session_state.ai_recommendations = ai_recommendations
        
        progress_bar.progress(100)
        status_text.text("✅ AI analysis completed!")
        
        st.success("🎉 AI analysis completed successfully!")
        return True
        
    except Exception as e:
        st.error(f"❌ Error during AI analysis: {e}")
        return False

@st.cache_data
def load_ai_data(output_dir):
    """Load processed AI signals data"""
    try:
        ai_csv = os.path.join(output_dir, "ai_enhanced_intent_signals.csv")
        if os.path.exists(ai_csv):
            df = pd.read_csv(ai_csv)
            return df
        else:
            return None
    except Exception as e:
        st.error(f"Error loading AI data: {e}")
        return None

def create_ai_analysis_overview(df):
    """Create AI Analysis Overview section"""
    st.markdown('<div class="section-header">🧠 AI ANALYSIS OVERVIEW</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_signals = len(df)
    high_intent = len(df[df['buying_intent_score'] > 0.6]) if 'buying_intent_score' in df.columns else 0
    urgent_signals = len(df[df['urgency_score'] > 0.5]) if 'urgency_score' in df.columns else 0
    high_intent_pct = (high_intent / total_signals * 100) if total_signals > 0 else 0
    urgent_pct = (urgent_signals / total_signals * 100) if total_signals > 0 else 0
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{total_signals}</h2>
            <p><strong>Total Analyzed Signals</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{high_intent}</h2>
            <p><strong>High Buying Intent</strong></p>
            <small>({high_intent_pct:.1f}%)</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{urgent_signals}</h2>
            <p><strong>Urgent Signals</strong></p>
            <small>({urgent_pct:.1f}%)</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_sentiment = df['ai_sentiment_score'].mean() if 'ai_sentiment_score' in df.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <h2>{avg_sentiment:.3f}</h2>
            <p><strong>Avg Sentiment Score</strong></p>
        </div>
        """, unsafe_allow_html=True)

def create_intent_distribution(df):
    """Create Intent Distribution section"""
    st.markdown('<div class="section-header">🎯 INTENT DISTRIBUTION</div>', unsafe_allow_html=True)
    
    if 'primary_intent' in df.columns:
        intent_counts = df['primary_intent'].value_counts()
        total = len(df)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            for intent, count in intent_counts.items():
                percentage = (count / total * 100)
                st.markdown(f"""
                <div class="intent-item">
                    <span><strong>{intent}</strong></span>
                    <span>{count} signals ({percentage:.1f}%)</span>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            fig = px.pie(
                values=intent_counts.values,
                names=intent_counts.index,
                title="Intent Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

def create_sentiment_analysis(df):
    """Create Sentiment Analysis section"""
    st.markdown('<div class="section-header">😊 SENTIMENT ANALYSIS</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if 'ai_sentiment_score' in df.columns:
            avg_sentiment = df['ai_sentiment_score'].mean()
            st.markdown(f"**Average Sentiment Score:** {avg_sentiment:.3f}")
        
        if 'ai_sentiment' in df.columns:
            positive_count = len(df[df['ai_sentiment'] == 'POSITIVE'])
            total = len(df)
            positive_pct = (positive_count / total * 100) if total > 0 else 0
            st.markdown(f"**Positive Sentiment:** {positive_count} signals ({positive_pct:.1f}%)")
    
    with col2:
        if 'ai_sentiment' in df.columns:
            sentiment_counts = df['ai_sentiment'].value_counts()
            fig = px.bar(
                x=sentiment_counts.index,
                y=sentiment_counts.values,
                title="Sentiment Distribution",
                color=sentiment_counts.values,
                color_continuous_scale="viridis"
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

def create_company_fit_analysis(df):
    """Create Company Fit Analysis section"""
    st.markdown('<div class="section-header">🏢 COMPANY FIT ANALYSIS</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if 'company_fit_score' in df.columns:
            avg_fit = df['company_fit_score'].mean()
            high_fit = len(df[df['company_fit_score'] > 0.7])
            st.markdown(f"**Average Company Fit Score:** {avg_fit:.3f}")
            st.markdown(f"**High-Fit Companies:** {high_fit}")
    
    with col2:
        if 'company_fit_score' in df.columns:
            fig = px.histogram(
                df,
                x='company_fit_score',
                nbins=20,
                title="Company Fit Score Distribution",
                color_discrete_sequence=['#3498db']
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

def create_ai_recommendations(df):
    """Create AI Recommendations section"""
    st.markdown('<div class="section-header">🤖 TOP AI-RECOMMENDED ACTIONS</div>', unsafe_allow_html=True)
    
    if 'recommended_actions' in df.columns:
        # Count all actions
        all_actions = []
        for actions in df['recommended_actions'].dropna():
            all_actions.extend(actions.split(', '))
        
        action_counts = Counter(all_actions)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            for action, count in action_counts.most_common():
                st.markdown(f"""
                <div class="action-recommendation">
                    <span><strong>{action.replace('_', ' ').title()}</strong></span>
                    <span>{count} recommendations</span>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            fig = px.bar(
                x=list(action_counts.values()),
                y=list(action_counts.keys()),
                orientation='h',
                title="Recommended Actions",
                color=list(action_counts.values()),
                color_continuous_scale="plasma"
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

def create_technology_trends(df):
    """Create Technology Trends section"""
    st.markdown('<div class="section-header">💻 TRENDING TECHNOLOGY INTERESTS</div>', unsafe_allow_html=True)
    
    if 'technology_interests' in df.columns:
        all_tech = []
        for tech_list in df['technology_interests'].dropna():
            if isinstance(tech_list, str) and tech_list.strip():
                all_tech.extend([t.strip() for t in tech_list.split(',') if t.strip()])
        
        if all_tech:
            tech_counts = Counter(all_tech)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                for tech, count in tech_counts.most_common(5):
                    st.markdown(f"""
                    <div class="tech-trend">
                        <span><strong>{tech}</strong></span>
                        <span>{count} mentions</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                top_5 = dict(tech_counts.most_common(5))
                fig = px.bar(
                    x=list(top_5.keys()),
                    y=list(top_5.values()),
                    title="Top Technology Interests",
                    color=list(top_5.values()),
                    color_continuous_scale="viridis"
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)

def create_actionable_recommendations(df):
    """Create Actionable Recommendations section"""
    st.markdown('<div class="section-header">🎯 AI-GENERATED ACTIONABLE RECOMMENDATIONS</div>', unsafe_allow_html=True)
    
    # Immediate Actions
    if 'recommended_actions' in df.columns:
        immediate_df = df[df['recommended_actions'].str.contains('immediate_outreach', na=False)]
        
        if not immediate_df.empty:
            st.markdown(f"""
            <div class="urgent-alert">
                <h3>🚨 IMMEDIATE ACTIONS ({len(immediate_df)} items)</h3>
                <p>Companies with high buying intent and urgency detected</p>
            </div>
            """, unsafe_allow_html=True)
            
            for _, row in immediate_df.head(5).iterrows():
                company = row.get('company_name', 'Unknown')
                description = str(row.get('description', ''))[:60] + '...' if len(str(row.get('description', ''))) > 60 else str(row.get('description', ''))
                confidence = row.get('recommendation_confidence', 0)
                reasoning = row.get('ai_reasoning', 'No reasoning available')
                
                st.markdown(f"""
                <div class="priority-item">
                    <strong>• {company}</strong>: {description}<br>
                    <small>Action: schedule_immediate_outreach (Confidence: {confidence:.2f})</small><br>
                    <small>Reasoning: {reasoning}</small>
                </div>
                """, unsafe_allow_html=True)
        
        # High Priority Queue
        priority_df = df[df['recommended_actions'].str.contains('priority_queue', na=False)]
        
        if not priority_df.empty:
            st.markdown(f"""
            <div class="section-header">⭐ HIGH PRIORITY QUEUE ({len(priority_df)} items)</div>
            """, unsafe_allow_html=True)
            
            for _, row in priority_df.head(5).iterrows():
                company = row.get('company_name', 'Unknown')
                description = str(row.get('description', ''))[:60] + '...' if len(str(row.get('description', ''))) > 60 else str(row.get('description', ''))
                
                st.markdown(f"""
                <div class="priority-item">
                    <strong>• {company}</strong>: {description}
                </div>
                """, unsafe_allow_html=True)
        
        # Research Required
        research_df = df[df['recommended_actions'].str.contains('research_task', na=False)]
        
        if not research_df.empty:
            st.markdown(f"""
            <div class="section-header">🔍 RESEARCH REQUIRED ({len(research_df)} items)</div>
            """, unsafe_allow_html=True)
            
            for _, row in research_df.head(3).iterrows():
                company = row.get('company_name', 'Unknown')
                description = str(row.get('description', ''))[:60] + '...' if len(str(row.get('description', ''))) > 60 else str(row.get('description', ''))
                
                st.markdown(f"""
                <div class="research-item">
                    <strong>• {company}</strong>: {description}
                </div>
                """, unsafe_allow_html=True)

def main():
    """Main dashboard function"""
    # Main header
    create_main_header()
    
    # Sidebar
    st.sidebar.markdown("### 🎛️ Dashboard Controls")
    
    # Company input section
    companies = create_company_input_section()
    
    # Collection controls
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Start Signal Collection", type="primary"):
            if companies:
                success = run_signal_collection(companies)
                if success:
                    st.rerun()
            else:
                st.error("Please enter company names first.")
    
    with col2:
        if st.button("🤖 Run AI Analysis"):
            if st.session_state.collection_complete:
                success = run_ai_analysis()
                if success:
                    st.rerun()
            else:
                st.error("Please run signal collection first.")
    
    # Display results if available
    if st.session_state.collection_complete and st.session_state.comprehensive_df is not None:
        st.markdown("---")
        st.markdown("### 📊 Basic Signal Analysis")
        
        df = st.session_state.comprehensive_df
        
        # Basic metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Signals", len(df))
        with col2:
            st.metric("Unique Companies", df['company_name'].nunique())
        with col3:
            st.metric("Avg Signal Strength", f"{df['signal_strength'].mean():.1f}")
        with col4:
            st.metric("High Priority", len(df[df['follow_up_required'] == True]))
        
        # Signal breakdown by source
        st.markdown("### 📡 Signals by Source")
        source_counts = df['source_type'].value_counts()
        fig = px.pie(values=source_counts.values, names=source_counts.index, title="Signal Distribution by Source")
        st.plotly_chart(fig, use_container_width=True)
        
        # Recent signals table
        st.markdown("### 📋 Recent Signals")
        recent_signals = df[['company_name', 'signal_type', 'source', 'description', 'signal_strength', 'timestamp']].head(10)
        st.dataframe(recent_signals, use_container_width=True)
    
    # AI Analysis Results
    if st.session_state.ai_processor is not None and st.session_state.analyzer is not None:
        st.markdown("---")
        st.markdown("### 🤖 AI Analysis Results")
        
        # Load AI enhanced data
        ai_df = load_ai_data(st.session_state.analyzer.output_dir)
        
        if ai_df is not None:
            create_ai_analysis_overview(ai_df)
            st.markdown("---")
            
            create_intent_distribution(ai_df)
            st.markdown("---")
            
            create_sentiment_analysis(ai_df)
            st.markdown("---")
            
            create_company_fit_analysis(ai_df)
            st.markdown("---")
            
            create_ai_recommendations(ai_df)
            st.markdown("---")
            
            create_technology_trends(ai_df)
            st.markdown("---")
            
            create_actionable_recommendations(ai_df)
    
    # Sidebar info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Status Info")
    
    if st.session_state.collection_complete:
        st.sidebar.success("✅ Signal Collection Complete")
        if st.session_state.comprehensive_df is not None:
            st.sidebar.markdown(f"**Signals Collected**: {len(st.session_state.comprehensive_df)}")
            st.sidebar.markdown(f"**Companies**: {st.session_state.comprehensive_df['company_name'].nunique()}")
    
    if st.session_state.ai_processor is not None:
        st.sidebar.success("✅ AI Analysis Complete")
    
    st.sidebar.markdown(f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if st.sidebar.button("🔄 Refresh All"):
        st.cache_data.clear()
        st.rerun()

if __name__ == "__main__":
    main() 