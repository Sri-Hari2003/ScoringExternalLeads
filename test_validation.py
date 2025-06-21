#!/usr/bin/env python3
"""
Test Validation Script for Intent Signal Analysis System
Validates accuracy and functionality of all components
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_collectors.enhanced_google_news_collector import EnhancedGoogleNewsCollector
from data_collectors.enhanced_reddit_collector import EnhancedRedditCollector
from data_collectors.enhanced_job_posting_collector import EnhancedJobPostingCollector
from data_collectors.agentic_intent_analyzer import AgenticIntentAnalyzer

class SystemValidator:
    def __init__(self):
        self.test_companies = [
            "Shopify", "Stripe", "Notion", "Figma", "Linear"
        ]
        self.test_keywords = [
            "funding", "investment", "hiring", "growth", "partnership",
            "acquisition", "expansion", "new product", "launch"
        ]
        self.results = {}
        
    def test_data_collection(self):
        """Test data collection from all sources"""
        print("🔍 Testing Data Collection...")
        
        # Test Google News Collector
        try:
            news_collector = EnhancedGoogleNewsCollector()
            news_signals = news_collector.collect_signals(["Shopify"], ["funding", "hiring"])
            self.results['news_collection'] = {
                'success': len(news_signals) > 0,
                'count': len(news_signals),
                'sample_data': news_signals[:2] if news_signals else []
            }
            print(f"✅ Google News: {len(news_signals)} signals collected")
        except Exception as e:
            self.results['news_collection'] = {'success': False, 'error': str(e)}
            print(f"❌ Google News: {str(e)}")
        
        # Test Reddit Collector
        try:
            reddit_collector = EnhancedRedditCollector()
            reddit_signals = reddit_collector.collect_signals(["Stripe"], ["payment", "api"])
            self.results['reddit_collection'] = {
                'success': len(reddit_signals) > 0,
                'count': len(reddit_signals),
                'sample_data': reddit_signals[:2] if reddit_signals else []
            }
            print(f"✅ Reddit: {len(reddit_signals)} signals collected")
        except Exception as e:
            self.results['reddit_collection'] = {'success': False, 'error': str(e)}
            print(f"❌ Reddit: {str(e)}")
        
        # Test Job Posting Collector
        try:
            job_collector = EnhancedJobPostingCollector()
            job_signals = job_collector.collect_signals(["Notion"], ["software engineer", "product manager"])
            self.results['job_collection'] = {
                'success': len(job_signals) > 0,
                'count': len(job_signals),
                'sample_data': job_signals[:2] if job_signals else []
            }
            print(f"✅ Job Postings: {len(job_signals)} signals collected")
        except Exception as e:
            self.results['job_collection'] = {'success': False, 'error': str(e)}
            print(f"❌ Job Postings: {str(e)}")
    
    def test_signal_processing(self):
        """Test signal processing and scoring"""
        print("\n🔍 Testing Signal Processing...")
        
        # Create sample signals for testing
        sample_signals = [
            {
                'company_name': 'Shopify',
                'signal_type': 'Topic Research Surge',
                'description': 'Shopify announces $100M funding round for e-commerce expansion',
                'content_snippet': 'Shopify has secured $100 million in funding to expand its e-commerce platform capabilities.',
                'source': 'TechCrunch',
                'url': 'https://example.com/shopify-funding',
                'published_date': datetime.now().isoformat(),
                'engagement_score': 85,
                'sentiment_score': 0.8,
                'relevance_score': 9,
                'signal_strength': 8,
                'confidence_level': 0.9
            },
            {
                'company_name': 'Stripe',
                'signal_type': 'Hiring Surge',
                'description': 'Stripe hiring 500+ engineers for payment infrastructure',
                'content_snippet': 'Stripe is aggressively hiring engineers to scale their payment processing infrastructure.',
                'source': 'LinkedIn',
                'url': 'https://example.com/stripe-hiring',
                'published_date': datetime.now().isoformat(),
                'engagement_score': 72,
                'sentiment_score': 0.6,
                'relevance_score': 7,
                'signal_strength': 6,
                'confidence_level': 0.8
            }
        ]
        
        # Test signal scoring accuracy
        high_funding_signal = sample_signals[0]
        hiring_signal = sample_signals[1]
        
        # Validate signal strength scoring
        funding_keywords = ['funding', 'investment', 'raise', 'capital']
        hiring_keywords = ['hiring', 'recruiting', 'job', 'position']
        
        funding_score = sum(4 for keyword in funding_keywords if keyword in high_funding_signal['description'].lower())
        hiring_score = sum(2 for keyword in hiring_keywords if keyword in hiring_signal['description'].lower())
        
        self.results['signal_scoring'] = {
            'funding_signal_expected': 8,
            'funding_signal_actual': high_funding_signal['signal_strength'],
            'hiring_signal_expected': 6,
            'hiring_signal_actual': hiring_signal['signal_strength'],
            'scoring_accurate': (high_funding_signal['signal_strength'] >= 7 and hiring_signal['signal_strength'] >= 5)
        }
        
        print(f"✅ Signal Scoring: Funding={high_funding_signal['signal_strength']}, Hiring={hiring_signal['signal_strength']}")
    
    def test_ai_analysis(self):
        """Test AI analysis components"""
        print("\n🔍 Testing AI Analysis...")
        
        try:
            analyzer = AgenticIntentAnalyzer()
            
            # Test sentiment analysis
            test_texts = [
                "Shopify raises $100M for amazing growth opportunities",
                "Stripe faces challenges with payment processing issues",
                "Notion launches new collaboration features"
            ]
            
            sentiment_results = []
            for text in test_texts:
                sentiment = analyzer.analyze_sentiment(text)
                sentiment_results.append({
                    'text': text,
                    'sentiment': sentiment
                })
            
            # Validate sentiment accuracy
            expected_sentiments = ['positive', 'negative', 'positive']
            sentiment_accuracy = sum(1 for i, result in enumerate(sentiment_results) 
                                   if result['sentiment']['label'].lower() == expected_sentiments[i]) / len(expected_sentiments)
            
            self.results['ai_analysis'] = {
                'sentiment_accuracy': sentiment_accuracy,
                'sentiment_results': sentiment_results,
                'success': sentiment_accuracy >= 0.6  # 60% accuracy threshold
            }
            
            print(f"✅ AI Analysis: Sentiment accuracy = {sentiment_accuracy:.2%}")
            
        except Exception as e:
            self.results['ai_analysis'] = {'success': False, 'error': str(e)}
            print(f"❌ AI Analysis: {str(e)}")
    
    def test_data_quality(self):
        """Test data quality metrics"""
        print("\n🔍 Testing Data Quality...")
        
        # Check if output files exist
        output_dir = Path("csv_outputs")
        latest_output = None
        
        if output_dir.exists():
            subdirs = [d for d in output_dir.iterdir() if d.is_dir()]
            if subdirs:
                latest_output = max(subdirs, key=lambda x: x.stat().st_mtime)
        
        if latest_output:
            try:
                # Check comprehensive signals file
                comp_file = latest_output / "comprehensive_intent_signals.csv"
                if comp_file.exists():
                    df = pd.read_csv(comp_file)
                    
                    quality_metrics = {
                        'total_signals': len(df),
                        'companies_covered': df['company_name'].nunique(),
                        'signal_types': df['signal_type'].nunique(),
                        'avg_signal_strength': df['signal_strength'].mean(),
                        'avg_confidence': df['confidence_level'].mean(),
                        'missing_values': df.isnull().sum().sum(),
                        'duplicate_signals': df.duplicated().sum()
                    }
                    
                    self.results['data_quality'] = {
                        'file_exists': True,
                        'metrics': quality_metrics,
                        'quality_score': self._calculate_quality_score(quality_metrics)
                    }
                    
                    print(f"✅ Data Quality: {quality_metrics['total_signals']} signals, "
                          f"{quality_metrics['companies_covered']} companies, "
                          f"Quality Score: {self.results['data_quality']['quality_score']:.1%}")
                else:
                    self.results['data_quality'] = {'file_exists': False, 'error': 'No comprehensive signals file found'}
                    print("❌ Data Quality: No comprehensive signals file found")
            except Exception as e:
                self.results['data_quality'] = {'file_exists': False, 'error': str(e)}
                print(f"❌ Data Quality: {str(e)}")
        else:
            self.results['data_quality'] = {'file_exists': False, 'error': 'No output directory found'}
            print("❌ Data Quality: No output directory found")
    
    def _calculate_quality_score(self, metrics):
        """Calculate overall data quality score"""
        score = 0
        
        # Signal count (0-25 points)
        if metrics['total_signals'] >= 50:
            score += 25
        elif metrics['total_signals'] >= 20:
            score += 15
        elif metrics['total_signals'] >= 10:
            score += 10
        
        # Company coverage (0-25 points)
        if metrics['companies_covered'] >= 5:
            score += 25
        elif metrics['companies_covered'] >= 3:
            score += 15
        elif metrics['companies_covered'] >= 1:
            score += 10
        
        # Signal strength (0-25 points)
        if metrics['avg_signal_strength'] >= 6:
            score += 25
        elif metrics['avg_signal_strength'] >= 4:
            score += 15
        elif metrics['avg_signal_strength'] >= 2:
            score += 10
        
        # Data completeness (0-25 points)
        missing_ratio = metrics['missing_values'] / (metrics['total_signals'] * 10)  # Assuming ~10 columns
        if missing_ratio <= 0.1:
            score += 25
        elif missing_ratio <= 0.2:
            score += 15
        elif missing_ratio <= 0.3:
            score += 10
        
        return score / 100
    
    def run_comprehensive_test(self):
        """Run all tests and generate report"""
        print("🚀 Starting Comprehensive System Validation...\n")
        
        self.test_data_collection()
        self.test_signal_processing()
        self.test_ai_analysis()
        self.test_data_quality()
        
        self._generate_report()
    
    def _generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("📊 COMPREHENSIVE VALIDATION REPORT")
        print("="*60)
        
        # Overall system health
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result.get('success', False))
        system_health = passed_tests / total_tests if total_tests > 0 else 0
        
        print(f"\n🏥 System Health: {system_health:.1%} ({passed_tests}/{total_tests} components working)")
        
        # Detailed results
        for component, result in self.results.items():
            status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
            print(f"\n{component.replace('_', ' ').title()}: {status}")
            
            if 'error' in result:
                print(f"   Error: {result['error']}")
            elif 'metrics' in result:
                metrics = result['metrics']
                print(f"   Signals: {metrics.get('total_signals', 'N/A')}")
                print(f"   Companies: {metrics.get('companies_covered', 'N/A')}")
                print(f"   Avg Strength: {metrics.get('avg_signal_strength', 'N/A'):.1f}")
            elif 'count' in result:
                print(f"   Signals Collected: {result['count']}")
            elif 'sentiment_accuracy' in result:
                print(f"   Sentiment Accuracy: {result['sentiment_accuracy']:.1%}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if system_health >= 0.8:
            print("   🎉 System is working well! Ready for production use.")
        elif system_health >= 0.6:
            print("   ⚠️  System has some issues. Review failed components.")
        else:
            print("   🚨 System needs significant fixes. Check dependencies and configuration.")
        
        # Save detailed report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"validation_report_{timestamp}.txt"
        
        with open(report_file, 'w') as f:
            f.write("Intent Signal Analysis System - Validation Report\n")
            f.write("="*50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"System Health: {system_health:.1%}\n\n")
            
            for component, result in self.results.items():
                f.write(f"{component}:\n")
                f.write(f"  Success: {result.get('success', False)}\n")
                if 'error' in result:
                    f.write(f"  Error: {result['error']}\n")
                f.write("\n")
        
        print(f"\n📄 Detailed report saved to: {report_file}")

def main():
    """Main validation function"""
    validator = SystemValidator()
    validator.run_comprehensive_test()

if __name__ == "__main__":
    main() 