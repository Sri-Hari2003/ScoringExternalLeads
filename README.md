# 🤖 AI-Powered Intent Signal Analysis System

A comprehensive system for collecting, analyzing, and generating AI-powered insights from intent signals across multiple data sources including Google News, Reddit, and job boards.

## 🚀 **What to Run - Quick Commands**

### **Step 1: Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 2: Choose Your Run Method**

#### **🎯 RECOMMENDED: Streamlit Dashboard**
```bash
# If streamlit is not found, install it first:
pip install streamlit

# Then run the dashboard:
streamlit run streamlit_dashboard.py
```
**What it does:**
- Opens web interface at `http://localhost:8501`
- Lets you enter company names interactively
- Shows real-time signal collection progress
- Displays AI analysis with interactive charts
- **Best for: Interactive use, real-time monitoring**

#### **⚡ FAST: Basic Signal Collection**
```bash
python main.py
```
**What it does:**
- Collects signals from Google News, Reddit, and job boards
- Uses default sample companies (Shopify, Stripe, etc.)
- Generates CSV reports in timestamped folders
- **Best for: Quick testing, batch processing**

#### **🤖 COMPLETE: Full AI Analysis**
```bash
python agentic_main.py
```
**What it does:**
- Runs signal collection + AI analysis
- Generates AI-enhanced insights and recommendations
- Creates autonomous decision recommendations
- **Best for: Complete analysis, AI insights**

## 📊 **System Overview**

```
User Input (Companies) → Data Collection → Signal Processing → AI Analysis → Insights & Recommendations
```

## 🏗️ **Architecture**

### **Data Collection Pipeline**

#### **1. Signal Sources**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Google News   │    │     Reddit      │    │   Job Boards    │
│                 │    │                 │    │                 │
│ • RSS Feeds     │    │ • Subreddits    │    │ • Indeed.com    │
│ • News Search   │    │ • API Search    │    │ • Job Postings  │
│ • Recent News   │    │ • User Posts    │    │ • Tech Keywords │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### **2. Collection Tools & Libraries**
- **`feedparser`** - Google News RSS feeds
- **`requests`** - Reddit API calls, web scraping
- **`beautifulsoup4`** - HTML parsing (job boards)
- **`newspaper3k`** - Article extraction
- **Rate limiting** - Respectful API usage

#### **3. Data Collection Process**
```python
# For each company + keyword combination:
1. Google News: RSS feed search → Parse articles → Extract metadata
2. Reddit: API search → Parse posts → Extract engagement metrics  
3. Job Boards: Web scraping → Parse job listings → Extract tech requirements
```

### **Signal Processing Pipeline**

#### **1. Signal Enhancement**
```python
# Each raw signal gets enhanced with:
{
    'signal_type': "Topic Research Surge",
    'signal_strength': 5-10,           # Calculated based on keywords/engagement
    'confidence_level': 0.0-1.0,       # Based on source reliability
    'engagement_score': 0-100,         # Reddit upvotes, comments, etc.
    'sentiment_score': -1.0 to 1.0,    # Basic keyword-based sentiment
    'relevance_score': 1-10,           # How relevant to buying intent
    'follow_up_required': True/False,  # Based on strength thresholds
    'priority_level': "High/Medium/Low" # Based on multiple factors
}
```

#### **2. Signal Strength Calculation**
```python
# Google News Signals:
- Funding/Investment keywords: +4 points
- Hiring/Growth keywords: +2 points  
- Partnership/Launch keywords: +1 point

# Reddit Signals:
- High engagement (upvotes + comments): +3 points
- Seeking advice/recommendations: +2 points
- Product evaluation: +1 point

# Job Postings:
- Senior/Lead roles: +2 points
- Specific tech stack: +1 point
- Remote/Hybrid: +1 point
```

### **AI Analysis Pipeline**

#### **1. AI Models Used**
```python
# Sentiment Analysis
- Model: "cardiffnlp/twitter-roberta-base-sentiment-latest"
- Purpose: Analyze text sentiment (POSITIVE/NEGATIVE/NEUTRAL)

# Intent Classification  
- Model: "facebook/bart-large-mnli"
- Purpose: Zero-shot classification of buying intent

# Named Entity Recognition
- Model: "dbmdz/bert-large-cased-finetuned-conll03-english"
- Purpose: Extract company names, technologies, locations

# Sentence Embeddings
- Model: "all-MiniLM-L6-v2"
- Purpose: Text similarity and clustering
```

#### **2. AI Processing Steps**
```python
# For each signal:
1. Text Extraction: Combine description + content_snippet
2. Sentiment Analysis: Get sentiment label and confidence score
3. Intent Classification: Classify as buying/research/comparison intent
4. Entity Recognition: Extract companies, technologies, locations
5. Knowledge Base Matching: Match against buying signals, pain points
6. Score Calculation: Company fit, engagement potential, urgency
7. Decision Making: Apply autonomous decision rules
```

#### **3. AI Decision Engine**
```python
# Decision Rules:
{
    'immediate_action': {
        'conditions': ['signal_strength >= 8', 'urgency_score > 0.7'],
        'action': 'schedule_immediate_outreach'
    },
    'high_priority': {
        'conditions': ['signal_strength >= 6', 'company_fit_score > 0.7'],
        'action': 'add_to_priority_queue'
    },
    'nurture': {
        'conditions': ['signal_strength >= 4', 'engagement_potential > 0.5'],
        'action': 'add_to_nurture_campaign'
    }
}
```

## 🛠️ **Key Technologies & Libraries**

### **Data Collection:**
- **`requests`** - HTTP requests for APIs
- **`feedparser`** - RSS feed parsing
- **`beautifulsoup4`** - HTML parsing
- **`newspaper3k`** - Article extraction

### **AI/ML Processing:**
- **`transformers`** - Hugging Face models
- **`torch`** - PyTorch backend
- **`sentence-transformers`** - Text embeddings
- **`scikit-learn`** - Machine learning utilities
- **`nltk`** - Natural language processing
- **`textblob`** - Text processing
- **`vaderSentiment`** - Sentiment analysis

### **Data Processing:**
- **`pandas`** - Data manipulation
- **`numpy`** - Numerical computing
- **`matplotlib`** - Static visualizations
- **`plotly`** - Interactive visualizations

### **Web Interface:**
- **`streamlit`** - Web dashboard
- **`seaborn`** - Statistical visualizations

## 📈 **Signal Quality Metrics**

### **Signal Strength (1-10):**
- **9-10:** High funding/investment news
- **7-8:** Hiring, growth, partnerships
- **5-6:** General business news
- **3-4:** Social media mentions
- **1-2:** Low engagement content

### **Confidence Level (0.0-1.0):**
- **0.9+:** Verified news sources
- **0.7-0.8:** Social media with engagement
- **0.5-0.6:** User-generated content
- **<0.5:** Unverified sources

### **Engagement Potential:**
- **High:** Seeking recommendations, comparing solutions
- **Medium:** General research, product evaluation
- **Low:** News consumption, casual mentions

## 🚀 **Quick Start Guide**

### **1. Installation**

```bash
# Clone the repository
git clone <repository-url>
cd ScoringExternalLeads

# Install dependencies
pip install -r requirements.txt
```

### **2. Choose Your Run Method**

#### **Option A: Streamlit Dashboard (Recommended)**
```bash
streamlit run streamlit_dashboard.py
```
- Opens web interface at `http://localhost:8501`
- Enter company names interactively
- See real-time signal collection progress
- View AI analysis results with beautiful visualizations

#### **Option B: Command Line - Basic Pipeline**
```bash
python main.py
```
- Runs with default sample companies
- Collects signals and generates CSV reports
- Creates timestamped output folders

#### **Option C: Command Line - AI Analysis Only**
```bash
python agentic_main.py
```
- Runs the full pipeline + AI analysis
- Generates AI-enhanced insights and recommendations

### **3. Usage Workflow**

#### **Streamlit Dashboard:**
1. **Enter Company Names** - One per line in the text area
2. **Start Signal Collection** - Click the button to begin data gathering
3. **Run AI Analysis** - Click to get AI-powered insights
4. **Review Results** - Explore visualizations and recommendations

#### **Command Line:**
1. **Edit companies** in `main.py` if needed
2. **Run the script** - `python main.py`
3. **Check outputs** in `csv_outputs/` folder

## 📁 **Output Structure**

```
csv_outputs/
└── YYYYMMDD_HHMMSS/          # Timestamped folder
    ├── comprehensive_intent_signals.csv      # Complete dataset
    ├── high_priority_signals.csv             # Urgent follow-ups
    ├── executive_summary.csv                 # Leadership overview
    ├── ai_enhanced_intent_signals.csv        # AI analysis results
    ├── immediate_action_signals.csv          # Urgent actions
    ├── high_priority_queue.csv               # Priority prospects
    ├── signals_news_media.csv                # News signals
    ├── signals_social_media.csv              # Social media signals
    ├── signals_job_board.csv                 # Job posting signals
    └── signals_[company_name].csv            # Company-specific files
```

## 📊 **What You'll Get**

### **Data Collection Results:**
- **Real-time signals** from Google News, Reddit, and job boards
- **Signal strength scoring** based on relevance and engagement
- **Source categorization** and metadata extraction
- **Timestamped data** for trend analysis

### **AI Analysis Results:**
- **Sentiment analysis** of all collected content
- **Intent classification** (buying, research, comparison)
- **Entity recognition** (companies, technologies, locations)
- **Company fit scoring** for prospect prioritization
- **Autonomous recommendations** for follow-up actions

### **Visualizations:**
- **Interactive dashboards** with Plotly charts
- **Signal distribution** by source and type
- **Trend analysis** over time
- **Priority heatmaps** for action planning

## 🔧 **Configuration**

### **Customizing Keywords:**
Edit the keyword lists in the collector files:
- `data_collectors/enhanced_google_news_collector.py`
- `data_collectors/enhanced_reddit_collector.py`
- `data_collectors/enhanced_job_posting_collector.py`

### **Adjusting Signal Strength:**
Modify scoring algorithms in the collector files to match your business needs.

### **AI Model Configuration:**
Update model parameters in `data_collectors/agentic_intent_analyzer.py` for different analysis approaches.

## 🐛 **Troubleshooting**

### **Common Issues:**

1. **Installation Errors:**
   ```bash
   # Ensure Python 3.8+ is installed
   python --version
   
   # Upgrade pip if needed
   pip install --upgrade pip
   ```

2. **Streamlit Not Found:**
   ```bash
   # Install streamlit separately
   pip install streamlit
   
   # Use python -m to avoid PATH issues
   python -m streamlit run streamlit_dashboard.py
   
   # Alternative: Find streamlit location
   python -c "import streamlit; print(streamlit.__file__)"
   ```

3. **Memory Issues:**
   - AI models require 2-4GB RAM
   - Close other applications if needed
   - Consider using smaller models for testing

4. **API Rate Limits:**
   - Built-in delays prevent rate limiting
   - Increase sleep times if needed
   - Check API status if errors persist

5. **Data Not Loading:**
   - Ensure CSV files exist in output directory
   - Check file permissions
   - Verify data collection completed successfully

### **Performance Tips:**
- Use fewer companies for faster testing
- Reduce keyword lists for quicker collection
- Run AI analysis separately for large datasets

## 📈 **System Requirements**

- **Python:** 3.8 or higher
- **RAM:** 4GB minimum (8GB recommended)
- **Storage:** 2GB free space for models and data
- **Internet:** Required for data collection
- **OS:** Windows, macOS, or Linux

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

**Happy Signal Hunting! 🎯** 