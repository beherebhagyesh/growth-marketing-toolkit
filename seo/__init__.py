"""SEO module with DataForSEO integration for keyword research and optimization."""
import os
import requests
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class KeywordData:
    keyword: str
    volume: int
    cpc: float
    competition: float
    difficulty: int
    trends: Optional[Dict] = None


class SEOClient:
    def __init__(self):
        self.login = os.getenv("DATAFORSEO_LOGIN")
        self.password = os.getenv("DATAFORSEO_PASSWORD")
        self.target_domain = os.getenv("TARGET_DOMAIN")
        self.base_url = "https://api.dataforseo.com/v3"
        
    def _auth(self) -> tuple:
        return (self.login, self.password) if self.login and self.password else (None, None)
    
    def _headers(self) -> Dict:
        return {"Content-Type": "application/json"}

    def create_keyword_universe(
        self,
        seed_keywords: List[str],
        location_code: int = 2840,
        language_code: str = "en",
    ) -> Dict:
        """Create a keyword universe from seed keywords."""
        if not self.login or not self.password:
            return {"error": "DataForSEO credentials not configured"}

        url = f"{self.base_url}/keywords_data/google/keywords_for_site/live"
        tasks = []
        
        for keyword in seed_keywords:
            tasks.append({
                "keyword": keyword,
                "location_code": location_code,
                "language_code": language_code,
                "include_subdomains": True,
                "include_suggestions": True,
            })

        response = requests.post(
            url,
            json=tasks,
            auth=self._auth(),
            headers=self._headers(),
        )
        
        if response.status_code == 200:
            result = response.json()
            return {"status": "success", "tasks": result.get("tasks", [])}
        return {"error": response.text}

    def get_keyword_data(
        self,
        keywords: List[str],
        location_code: int = 2840,
        language_code: str = "en",
    ) -> List[KeywordData]:
        """Get keyword metrics (volume, CPC, competition, difficulty)."""
        if not self.login or not self.password:
            return []

        url = f"{self.base_url}/keywords_data/google/keywords_for_keywords/live"
        tasks = [
            {
                "keyword": kw,
                "location_code": location_code,
                "language_code": language_code,
            }
            for kw in keywords
        ]

        response = requests.post(url, json=tasks, auth=self._auth(), headers=self._headers())
        
        if response.status_code == 200:
            results = response.json()
            keyword_data = []
            for task in results.get("tasks", []):
                for result in task.get("result", []):
                    keyword_data.append(KeywordData(
                        keyword=result.get("keyword", ""),
                        volume=result.get("search_volume", 0),
                        cpc=result.get("cpc", 0),
                        competition=result.get("competition", 0),
                        difficulty=result.get("keyword_difficulty", 0),
                    ))
            return keyword_data
        return []

    def analyze_page_keywords(self, url: str) -> Dict:
        """Analyze what keywords a page is ranking for."""
        if not self.login or not self.password:
            return {"error": "DataForSEO credentials not configured"}

        url_endpoint = f"{self.base_url}/keywords_data/google/organic/live"
        response = requests.post(
            url_endpoint,
            json=[{"url": url, "limit": 100}],
            auth=self._auth(),
            headers=self._headers(),
        )
        
        if response.status_code == 200:
            return {"status": "success", "data": response.json()}
        return {"error": response.text}

    def get_serp_data(self, keyword: str, location_code: int = 2840) -> Dict:
        """Get SERP data for a keyword."""
        if not self.login or not self.password:
            return {"error": "DataForSEO credentials not configured"}

        url = f"{self.base_url}/serp/google/organic/live"
        response = requests.post(
            url,
            json=[{"keyword": keyword, "location_code": location_code}],
            auth=self._auth(),
            headers=self._headers(),
        )
        
        if response.status_code == 200:
            return {"status": "success", "data": response.json()}
        return {"error": response.text}

    def optimize_page(
        self,
        url: str,
        target_keywords: List[str],
    ) -> Dict:
        """Generate optimization recommendations for a page."""
        page_data = self.analyze_page_keywords(url)
        keyword_data = self.get_keyword_data(target_keywords)
        
        recommendations = {
            "url": url,
            "target_keywords": target_keywords,
            "recommendations": [],
        }
        
        for kw in keyword_data:
            if kw.volume > 100:
                recommendations["recommendations"].append({
                    "keyword": kw.keyword,
                    "priority": "high" if kw.volume > 1000 else "medium",
                    "search_volume": kw.volume,
                    "difficulty": kw.difficulty,
                    "suggestion": f"Target keyword '{kw.keyword}' (volume: {kw.volume}, difficulty: {kw.difficulty})",
                })
        
        return recommendations

    def generate_page_content(
        self,
        keyword: str,
        competitor_urls: List[str],
    ) -> Dict:
        """Generate content recommendations based on competitor analysis."""
        competitors_content = []
        for url in competitor_urls:
            data = self.analyze_page_keywords(url)
            competitors_content.append({"url": url, "data": data})
        
        keyword_metrics = self.get_keyword_data([keyword])
        
        return {
            "target_keyword": keyword,
            "keyword_metrics": [
                {"keyword": k.keyword, "volume": k.volume, "difficulty": k.difficulty}
                for k in keyword_metrics
            ],
            "competitor_analysis": competitors_content,
            "content_recommendations": {
                "title": f"{keyword.title()} - Your Complete Guide",
                "meta_description": f"Learn everything about {keyword}. Our comprehensive guide covers {keyword} in detail.",
                "headings": [f"What is {keyword}?", f"Top {keyword} Strategies", f"{keyword} Best Practices"],
            },
        }


def create_keyword_universe(seed_keywords: List[str]) -> Dict:
    """Convenience function to create keyword universe."""
    client = SEOClient()
    return client.create_keyword_universe(seed_keywords)


def optimize_existing_page(url: str, keywords: List[str]) -> Dict:
    """Convenience function to optimize a page."""
    client = SEOClient()
    return client.optimize_page(url, keywords)


def create_new_page(keyword: str, competitors: List[str]) -> Dict:
    """Convenience function to generate new page content."""
    client = SEOClient()
    return client.generate_page_content(keyword, competitors)
