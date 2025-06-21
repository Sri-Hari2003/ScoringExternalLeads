import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlencode
import re
import json
from .enhanced_intent_signal_collector import EnhancedIntentSignalCollector

class EnhancedJobPostingCollector:
    def __init__(self, collector: EnhancedIntentSignalCollector):
        self.collector = collector

    def search_job_postings(self, companies, tech_keywords):
        """Enhanced job posting search with comprehensive data capture"""
        print("🔍 Collecting Enhanced Job Posting signals...")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

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
                    response = requests.get(search_url, headers=headers)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        job_cards = soup.find_all('div', {'class': re.compile('job_seen_beacon')})
                        if job_cards:
                            for job_card in job_cards[:3]:
                                title_elem = job_card.find('h2', {'class': 'jobTitle'})
                                company_elem = job_card.find('span', {'class': 'companyName'})
                                location_elem = job_card.find('div', {'class': 'companyLocation'})
                                salary_elem = job_card.find('span', {'class': 'salaryText'})
                                if title_elem and company_elem:
                                    job_title = title_elem.get_text(strip=True)
                                    job_company = company_elem.get_text(strip=True)
                                    location = location_elem.get_text(strip=True) if location_elem else ''
                                    salary = salary_elem.get_text(strip=True) if salary_elem else ''
                                    title_lower = job_title.lower()
                                    strength = 6
                                    priority = "Medium"
                                    context = "Standard Hiring"
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
                                    engagement_score = 10
                                    if salary:
                                        engagement_score += 5
                                    if any(word in title_lower for word in ['remote', 'hybrid']):
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
                                    self.collector.save_enhanced_signal(signal_data)
                    time.sleep(3)
                except Exception as e:
                    print(f"❌ Error fetching job postings for {company} + {keyword}: {e}") 