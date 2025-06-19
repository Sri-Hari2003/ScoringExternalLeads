import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
from dataclasses import dataclass
from urllib.parse import urlparse
import re
from config.KnowledgeBase import get_knowledge_base

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TechSignal:
    """Data class for technology signals"""
    signal_type: str
    technology: str
    category: str
    first_detected: Optional[str]
    last_detected: Optional[str]
    confidence: float
    signal_strength: int
    metadata: Dict[str, Any]

class BuiltWithCollector:
    """BuiltWith API client for collecting technographic signals"""
    
    def __init__(self, api_key: str, rate_limit_delay: float = 1.0):
        self.api_key = api_key
        self.rate_limit_delay = rate_limit_delay
        self.base_url = "https://api.builtwith.com"
        self.session = requests.Session()
        
        # Use knowledge base for technology categories and intent patterns
        kb = get_knowledge_base()
        self.tech_categories = kb.get_builtwith_tech_categories()
        self.intent_patterns = kb.get_builtwith_intent_patterns()
    
    def normalize_domain(self, domain: str) -> str:
        """Normalize domain format for API calls"""
        if not domain:
            return ""
        
        # Remove protocol if present
        domain = re.sub(r'^https?://', '', domain)
        # Remove www. prefix
        domain = re.sub(r'^www\.', '', domain)
        # Remove trailing slash and path
        domain = domain.split('/')[0]
        # Remove port numbers
        domain = domain.split(':')[0]
        
        return domain.lower().strip()
    
    def call_builtwith_api(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make API call to BuiltWith with error handling"""
        try:
            params['KEY'] = self.api_key
            url = f"{self.base_url}/{endpoint}"
            
            logger.info(f"Calling BuiltWith API: {endpoint} for {params.get('LOOKUP', 'unknown')}")
            
            response = self.session.get(url, params=params, timeout=30)
            
            # Handle rate limiting
            if response.status_code == 429:
                logger.warning("Rate limit hit, waiting...")
                time.sleep(self.rate_limit_delay * 2)
                response = self.session.get(url, params=params, timeout=30)
            
            response.raise_for_status()
            data = response.json()
            
            # Add delay to respect rate limits
            time.sleep(self.rate_limit_delay)
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {params.get('LOOKUP', 'unknown')}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse API response: {e}")
            return None
    
    def get_domain_info(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive domain technology information"""
        normalized_domain = self.normalize_domain(domain)
        if not normalized_domain:
            return None
        
        # Get current technologies
        current_tech = self.call_builtwith_api(
            "v21/api.json",
            {"LOOKUP": normalized_domain}
        )
        
        # Get technology history (if available in your plan)
        history_tech = self.call_builtwith_api(
            "v15/api.json", 
            {"LOOKUP": normalized_domain}
        )
        
        # Get relationships/similar sites (if available)
        relationships = self.call_builtwith_api(
            "v17/api.json",
            {"LOOKUP": normalized_domain}
        )
        
        return {
            'domain': normalized_domain,
            'current_technologies': current_tech,
            'technology_history': history_tech,
            'relationships': relationships,
            'collected_at': datetime.now().isoformat()
        }
    
    def extract_technology_signals(self, domain_data: Dict[str, Any]) -> List[TechSignal]:
        """Extract intent signals from BuiltWith data"""
        signals = []
        
        if not domain_data or not domain_data.get('current_technologies'):
            return signals
        
        current_tech = domain_data['current_technologies']
        history_tech = domain_data.get('technology_history', {})
        
        # Extract current technology signals
        if 'Results' in current_tech:
            for result in current_tech['Results']:
                if 'Result' in result and 'Paths' in result['Result']:
                    for path in result['Result']['Paths']:
                        if 'Technologies' in path:
                            for tech in path['Technologies']:
                                signal = self.create_tech_signal(tech, 'current_usage')
                                if signal:
                                    signals.append(signal)
        
        # Extract historical change signals (if available)
        if history_tech and 'Results' in history_tech:
            historical_signals = self.analyze_technology_changes(history_tech)
            signals.extend(historical_signals)
        
        return signals
    
    def create_tech_signal(self, tech_data: Dict[str, Any], signal_type: str) -> Optional[TechSignal]:
        """Create a TechSignal from BuiltWith technology data"""
        try:
            tech_name = tech_data.get('Name', '').lower()
            tech_tag = tech_data.get('Tag', '').lower()
            
            # Determine category
            category = self.categorize_technology(tech_name, tech_tag)
            
            # Calculate confidence and signal strength
            confidence = self.calculate_confidence(tech_data)
            signal_strength = self.calculate_signal_strength(tech_data, signal_type)
            
            return TechSignal(
                signal_type=signal_type,
                technology=tech_data.get('Name', ''),
                category=category,
                first_detected=tech_data.get('FirstDetected'),
                last_detected=tech_data.get('LastDetected'),
                confidence=confidence,
                signal_strength=signal_strength,
                metadata={
                    'tag': tech_data.get('Tag', ''),
                    'description': tech_data.get('Description', ''),
                    'website': tech_data.get('Website', ''),
                    'categories': tech_data.get('Categories', [])
                }
            )
        except Exception as e:
            logger.error(f"Error creating tech signal: {e}")
            return None
    
    def categorize_technology(self, tech_name: str, tech_tag: str) -> str:
        """Categorize technology based on name and tag"""
        for category, keywords in self.tech_categories.items():
            if any(keyword in tech_name or keyword in tech_tag for keyword in keywords):
                return category
        return 'other'
    
    def calculate_confidence(self, tech_data: Dict[str, Any]) -> float:
        """Calculate confidence score for technology detection"""
        base_confidence = 0.7
        
        # Increase confidence if we have recent detection
        if tech_data.get('LastDetected'):
            try:
                last_detected = datetime.fromisoformat(tech_data['LastDetected'].replace('Z', '+00:00'))
                days_ago = (datetime.now() - last_detected.replace(tzinfo=None)).days
                if days_ago < 30:
                    base_confidence += 0.2
                elif days_ago < 180:
                    base_confidence += 0.1
            except:
                pass
        
        # Increase confidence if technology has detailed metadata
        if tech_data.get('Categories'):
            base_confidence += 0.1
        
        return min(1.0, base_confidence)
    
    def calculate_signal_strength(self, tech_data: Dict[str, Any], signal_type: str) -> int:
        """Calculate signal strength (1-10 scale)"""
        base_strength = 5
        
        # Adjust based on signal type
        strength_modifiers = {
            'current_usage': 0,
            'new_implementation': 3,
            'technology_change': 4,
            'category_expansion': 2,
            'stack_consolidation': 2
        }
        
        base_strength += strength_modifiers.get(signal_type, 0)
        
        # Adjust based on technology category (business-critical = higher strength)
        critical_categories = ['crm', 'ecommerce', 'analytics', 'security']
        category = self.categorize_technology(
            tech_data.get('Name', '').lower(), 
            tech_data.get('Tag', '').lower()
        )
        
        if category in critical_categories:
            base_strength += 1
        
        return min(10, max(1, base_strength))
    
    def analyze_technology_changes(self, history_data: Dict[str, Any]) -> List[TechSignal]:
        """Analyze historical technology changes for intent signals"""
        signals = []
        
        # This would analyze historical data to detect:
        # - Recent technology additions (expansion intent)
        # - Technology replacements (migration intent)
        # - Category changes (modernization intent)
        
        # Note: Implementation depends on your BuiltWith plan and available historical data
        # This is a placeholder for the logic
        
        return signals
    
    def analyze_company_signals(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze signals for a single company"""
        company_name = company.get('name', 'Unknown')
        domain = company.get('domain', '')
        
        logger.info(f"Analyzing signals for {company_name} ({domain})")
        
        # Get BuiltWith data
        domain_data = self.get_domain_info(domain)
        
        if not domain_data:
            return {
                'company_name': company_name,
                'domain': domain,
                'status': 'failed',
                'error': 'Could not retrieve domain data',
                'signals': [],
                'summary': {}
            }
        
        # Extract technology signals
        tech_signals = self.extract_technology_signals(domain_data)
        
        # Generate summary
        summary = self.generate_signal_summary(tech_signals)
        
        # Detect intent patterns
        intent_analysis = self.analyze_intent_patterns(tech_signals)
        
        return {
            'company_name': company_name,
            'domain': self.normalize_domain(domain),
            'status': 'success',
            'signals': [
                {
                    'signal_type': signal.signal_type,
                    'technology': signal.technology,
                    'category': signal.category,
                    'first_detected': signal.first_detected,
                    'last_detected': signal.last_detected,
                    'confidence': signal.confidence,
                    'signal_strength': signal.signal_strength,
                    'metadata': signal.metadata
                }
                for signal in tech_signals
            ],
            'summary': summary,
            'intent_analysis': intent_analysis,
            'collected_at': datetime.now().isoformat(),
            'raw_data': domain_data  # Include raw data for further analysis
        }
    
    def generate_signal_summary(self, signals: List[TechSignal]) -> Dict[str, Any]:
        """Generate summary statistics for signals"""
        if not signals:
            return {'total_signals': 0}
        
        category_counts = {}
        signal_type_counts = {}
        avg_confidence = sum(s.confidence for s in signals) / len(signals)
        avg_strength = sum(s.signal_strength for s in signals) / len(signals)
        
        for signal in signals:
            category_counts[signal.category] = category_counts.get(signal.category, 0) + 1
            signal_type_counts[signal.signal_type] = signal_type_counts.get(signal.signal_type, 0) + 1
        
        return {
            'total_signals': len(signals),
            'category_breakdown': category_counts,
            'signal_type_breakdown': signal_type_counts,
            'average_confidence': round(avg_confidence, 3),
            'average_signal_strength': round(avg_strength, 1),
            'top_category': max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else None
        }
    
    def analyze_intent_patterns(self, signals: List[TechSignal]) -> Dict[str, Any]:
        """Analyze signals for buying intent patterns"""
        intent_scores = {
            'migration_intent': 0.0,
            'expansion_intent': 0.0,
            'optimization_intent': 0.0,
            'modernization_intent': 0.0
        }
        
        # Analyze technology diversity (expansion intent)
        categories = set(signal.category for signal in signals)
        if len(categories) > 5:
            intent_scores['expansion_intent'] += 0.3
        
        # Analyze recent changes (migration intent)
        recent_signals = [s for s in signals if s.signal_type in ['new_implementation', 'technology_change']]
        if recent_signals:
            intent_scores['migration_intent'] += min(0.8, len(recent_signals) * 0.2)
        
        # Analyze redundant technologies (optimization intent)
        category_counts = {}
        for signal in signals:
            category_counts[signal.category] = category_counts.get(signal.category, 0) + 1
        
        redundant_categories = [cat for cat, count in category_counts.items() if count > 2]
        if redundant_categories:
            intent_scores['optimization_intent'] += min(0.7, len(redundant_categories) * 0.2)
        
        return {
            'intent_scores': intent_scores,
            'primary_intent': max(intent_scores.items(), key=lambda x: x[1])[0],
            'intent_confidence': max(intent_scores.values()),
            'detected_patterns': self.detect_specific_patterns(signals)
        }
    
    def detect_specific_patterns(self, signals: List[TechSignal]) -> List[str]:
        """Detect specific buying intent patterns"""
        patterns = []
        
        # Check for common migration patterns
        cms_signals = [s for s in signals if s.category == 'cms']
        if len(cms_signals) > 1:
            patterns.append('multiple_cms_detected')
        
        # Check for analytics stack complexity
        analytics_signals = [s for s in signals if s.category == 'analytics']
        if len(analytics_signals) > 3:
            patterns.append('complex_analytics_stack')
        
        # Check for recent technology additions
        recent_signals = [s for s in signals if s.signal_type == 'new_implementation']
        if len(recent_signals) > 2:
            patterns.append('rapid_technology_adoption')
        
        return patterns

def collect_builtwith_signals(companies: List[Dict[str, Any]], 
                            api_key: str, 
                            rate_limit_delay: float = 1.0,
                            max_retries: int = 3) -> Dict[str, Any]:
    """
    Main function to collect BuiltWith signals for a list of companies
    
    Args:
        companies: List of company dictionaries with 'name' and 'domain' keys
        api_key: BuiltWith API key
        rate_limit_delay: Delay between API calls in seconds
        max_retries: Maximum number of retries for failed requests
    
    Returns:
        Dictionary containing collected signals and metadata
    """
    
    if not companies:
        return {
            'status': 'error',
            'message': 'No companies provided',
            'results': []
        }
    
    if not api_key:
        return {
            'status': 'error', 
            'message': 'API key required',
            'results': []
        }
    
    # Initialize collector
    collector = BuiltWithCollector(api_key, rate_limit_delay)
    
    # Collect signals for each company
    results = []
    successful_collections = 0
    failed_collections = 0
    
    logger.info(f"Starting signal collection for {len(companies)} companies")
    
    for i, company in enumerate(companies, 1):
        logger.info(f"Processing company {i}/{len(companies)}: {company.get('name', 'Unknown')}")
        
        retries = 0
        while retries < max_retries:
            try:
                result = collector.analyze_company_signals(company)
                results.append(result)
                
                if result['status'] == 'success':
                    successful_collections += 1
                    logger.info(f"✅ Successfully collected {len(result['signals'])} signals")
                else:
                    failed_collections += 1
                    logger.warning(f"❌ Failed to collect signals: {result.get('error', 'Unknown error')}")
                
                break  # Success, exit retry loop
                
            except Exception as e:
                retries += 1
                logger.error(f"Attempt {retries} failed for {company.get('name', 'Unknown')}: {e}")
                
                if retries < max_retries:
                    time.sleep(rate_limit_delay * retries)  # Exponential backoff
                else:
                    # Final failure
                    results.append({
                        'company_name': company.get('name', 'Unknown'),
                        'domain': company.get('domain', ''),
                        'status': 'failed',
                        'error': f'Failed after {max_retries} retries: {str(e)}',
                        'signals': []
                    })
                    failed_collections += 1
    
    # Generate overall summary
    all_signals = []
    for result in results:
        all_signals.extend(result.get('signals', []))
    
    overall_summary = {
        'total_companies_processed': len(companies),
        'successful_collections': successful_collections,
        'failed_collections': failed_collections,
        'total_signals_collected': len(all_signals),
        'collection_date': datetime.now().isoformat()
    }
    
    # Category analysis across all companies
    if all_signals:
        category_analysis = {}
        for signal in all_signals:
            category = signal.get('category', 'unknown')
            category_analysis[category] = category_analysis.get(category, 0) + 1
        
        overall_summary['category_distribution'] = category_analysis
        overall_summary['top_technology_category'] = max(category_analysis.items(), key=lambda x: x[1])[0]
    
    logger.info(f"✅ Signal collection completed: {successful_collections} successful, {failed_collections} failed")
    
    return {
        'status': 'completed',
        'summary': overall_summary,
        'results': results,
        'metadata': {
            'collection_parameters': {
                'rate_limit_delay': rate_limit_delay,
                'max_retries': max_retries,
                'companies_count': len(companies)
            },
            'api_info': {
                'service': 'BuiltWith',
                'version': 'v21'
            }
        }
    }


    # # Example usage
    # sample_companies = [
    #     {'name': 'Shopify', 'domain': 'shopify.com'},
    #     {'name': 'Stripe', 'domain': 'stripe.com'},
    #     {'name': 'Airbnb', 'domain': 'airbnb.com'}
    # ]
    
    # # Replace with your actual BuiltWith API key
    # API_KEY = "your_builtwith_api_key_here"
    
    # if API_KEY != "your_builtwith_api_key_here":
    #     # Collect signals
    #     results = collect_builtwith_signals(
    #         companies=sample_companies,
    #         api_key=API_KEY,
    #         rate_limit_delay=1.0
    #     )
        
    #     # Print results
    #     print(json.dumps(results, indent=2))
        
    #     # Save to file
    #     with open('builtwith_signals.json', 'w') as f:
    #         json.dump(results, f, indent=2)
        
    #     print(f"\n✅ Results saved to builtwith_signals.json")
    # else:
    #     print("❌ Please set your BuiltWith API key before running")
    #     print("Get your API key from: https://builtwith.com/api")