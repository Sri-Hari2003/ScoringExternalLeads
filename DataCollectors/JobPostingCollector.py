import requests
import json
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urlencode
# Add import for KnowledgeBase
try:
    from config.KnowledgeBase import get_knowledge_base
except ImportError:
    get_knowledge_base = None

class EnhancedJobPostingCollector:
    def __init__(self, knowledge_base=None):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Use provided knowledge_base or get global if available
        if knowledge_base is not None:
            self.knowledge_base = knowledge_base
        elif get_knowledge_base is not None:
            self.knowledge_base = get_knowledge_base()
        else:
            self.knowledge_base = None

    def _score_and_context(self, job_title, company, location, salary):
        title_lower = job_title.lower()
        context = "Standard Hiring"
        strength = 6
        priority = "Medium"
        # Use knowledge base if available
        if self.knowledge_base:
            patterns = self.knowledge_base.match_patterns(job_title + " " + company + " " + location)
            if patterns['positive_score'] > 0.5:
                strength = 8
                priority = "High"
                context = "Growth/Positive Hiring"
            elif patterns['pain_score'] > 0.5:
                strength = 7
                priority = "High"
                context = "Pain Point/Replacement"
            elif patterns['buying_intent_score'] > 0.3:
                strength = 7
                priority = "Medium"
                context = "Expansion/Buying Intent"
        else:
            if any(word in title_lower for word in ['senior', 'lead', 'principal', 'director', 'head']):
                strength = 8
                priority = "High"
                context = "Senior Role Hiring"
            elif any(word in title_lower for word in ['manager', 'supervisor']):
                strength = 7
                priority = "Medium"
                context = "Management Hiring"
            elif any(word in title_lower for word in ['architect', 'specialist', 'expert']):
                strength = 7
                priority = "High"
                context = "Specialized Role Hiring"
        return strength, priority, context

    def search_job_postings(self, companies, tech_keywords):
        """Fetch and return job posting signals from Indeed"""
        print("🔍 Collecting Enhanced Job Posting signals...")
        results = []

        for company in companies:
            for keyword in tech_keywords:
                try:
                    params = {
                        'q': f'"{keyword}"',
                        'l': company,
                        'fromage': '7',
                        'limit': '10'
                    }
                    search_url = f"https://www.indeed.com/jobs?{urlencode(params)}"
                    response = requests.get(search_url, headers=self.headers)

                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        job_cards = soup.find_all('div', {'class': re.compile('job_seen_beacon')})

                        for job_card in job_cards[:3]:  # Limit to top 3
                            title_elem = job_card.find('h2', {'class': 'jobTitle'})
                            company_elem = job_card.find('span', {'class': 'companyName'})
                            location_elem = job_card.find('div', {'class': 'companyLocation'})
                            salary_elem = job_card.find('span', {'class': 'salaryText'})

                            if title_elem and company_elem:
                                job_title = title_elem.get_text(strip=True)
                                job_company = company_elem.get_text(strip=True)
                                location = location_elem.get_text(strip=True) if location_elem else ''
                                salary = salary_elem.get_text(strip=True) if salary_elem else ''

                                strength, priority, context = self._score_and_context(job_title, job_company, location, salary)

                                engagement_score = 10
                                if salary:
                                    engagement_score += 5
                                if any(word in job_title.lower() for word in ['remote', 'hybrid']):
                                    engagement_score += 3

                                signal_data = {
                                    'signal_type': "Job Postings",
                                    'company_name': job_company,
                                    'signal_strength': strength,
                                    'source': "Indeed",
                                    'source_type': "Job Board",
                                    'description': f"Job posting: {job_title}",
                                    'url': search_url,
                                    'keyword': keyword,
                                    'search_term': f"{keyword} {company}",
                                    'content_snippet': f"Position: {job_title} | Company: {job_company} | Location: {location} | Salary: {salary}",
                                    'geographic_location': location,
                                    'engagement_score': engagement_score,
                                    'relevance_score': strength,
                                    'signal_context': context,
                                    'confidence_level': 0.8,
                                    'follow_up_required': strength >= 8,
                                    'priority_level': priority,
                                    'raw_data': json.dumps({
                                        'job_title': job_title,
                                        'company': job_company,
                                        'location': location,
                                        'salary': salary,
                                        'search_keyword': keyword
                                    }),
                                    'processing_notes': f"Job posting found on Indeed for {keyword} technology",
                                    'metadata': {
                                        'job_title': job_title,
                                        'location': location,
                                        'salary_info': salary,
                                        'search_company': company,
                                        'job_board': 'indeed',
                                        'posting_freshness': '7_days'
                                    }
                                }

                                results.append(signal_data)

                    time.sleep(3)

                except Exception as e:
                    print(f"❌ Error fetching job postings for {company} + {keyword}: {e}")

        return results
