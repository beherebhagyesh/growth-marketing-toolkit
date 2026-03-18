"""Indexing analysis tools for sitemap.xml and Google Search Console data."""
import os
import xml.etree.ElementTree as ET
import requests
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict
import csv
import re


@dataclass
class URLStatus:
    url: str
    status: str
    last_modified: Optional[datetime]
    priority: float
    change_frequency: Optional[str]


@dataclass
class IndexingIssue:
    url: str
    issue_type: str
    severity: str
    recommendation: str


class IndexingAnalyzer:
    def __init__(self):
        self.sitemap_url = os.getenv("TARGET_SITEMAP_URL")
        self.target_domain = os.getenv("TARGET_DOMAIN")

    def parse_sitemap(self, sitemap_path: Optional[str] = None) -> List[URLStatus]:
        """Parse a sitemap.xml file and extract URL information."""
        urls = []
        
        if sitemap_path:
            with open(sitemap_path, "r", encoding="utf-8") as f:
                content = f.read()
        elif self.sitemap_url:
            response = requests.get(self.sitemap_url)
            content = response.text
        else:
            return []

        try:
            root = ET.fromstring(content)
            
            if root.tag.endswith("}sitemapindex"):
                for sitemap in root.findall(".//{*}loc"):
                    pass
            elif root.tag.endswith("}urlset"):
                for url_elem in root.findall(".//{*}url"):
                    url = url_elem.find("{*}loc")
                    if url is None:
                        continue
                    
                    last_mod = url_elem.find("{*}lastmod")
                    priority = url_elem.find("{*}priority")
                    changefreq = url_elem.find("{*}changefreq")
                    
                    last_mod_dt = None
                    if last_mod is not None and last_mod.text:
                        try:
                            last_mod_dt = datetime.fromisoformat(last_mod.text.replace("Z", "+00:00"))
                        except:
                            pass
                    
                    urls.append(URLStatus(
                        url=url.text,
                        status="indexed",
                        last_modified=last_mod_dt,
                        priority=float(priority.text) if priority is not None else 0.5,
                        change_frequency=changefreq.text if changefreq is not None else None,
                    ))
        except ET.ParseError:
            pass
        
        return urls

    def parse_gsc_export(self, gsc_file: str) -> Dict[str, Any]:
        """Parse Google Search Console CSV export."""
        urls_by_status = defaultdict(list)
        
        with open(gsc_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row.get("URL", "")
                status = row.get("Indexing status", "unknown")
                status_reason = row.get("Status reason", "")
                
                urls_by_status[status].append({
                    "url": url,
                    "reason": status_reason,
                })
        
        return dict(urls_by_status)

    def compare_sitemap_vs_gsc(
        self,
        sitemap_urls: List[str],
        gsc_indexed: List[str],
    ) -> Dict:
        """Compare sitemap URLs with GSC indexed URLs."""
        sitemap_set = set(sitemap_urls)
        gsc_set = set(gsc_indexed)
        
        indexed_in_both = sitemap_set & gsc_set
        in_sitemap_not_gsc = sitemap_set - gsc_set
        in_gsc_not_sitemap = gsc_set - sitemap_set
        
        return {
            "indexed_in_both": list(indexed_in_both),
            "in_sitemap_not_indexed": list(in_sitemap_not_gsc),
            "indexed_not_in_sitemap": list(in_gsc_not_sitemap),
            "summary": {
                "total_in_sitemap": len(sitemap_set),
                "total_indexed_gsc": len(gsc_set),
                "indexed_count": len(indexed_in_both),
                "not_indexed_count": len(in_sitemap_not_gsc),
            },
        }

    def analyze_indexing_issues(self, urls: List[URLStatus], gsc_data: Dict) -> List[IndexingIssue]:
        """Analyze and identify indexing issues."""
        issues = []
        
        for status_list in gsc_data.values():
            for item in status_list:
                url = item["url"]
                reason = item["reason"]
                
                if "discovered" in reason.lower() or "not indexed" in reason.lower():
                    issues.append(IndexingIssue(
                        url=url,
                        issue_type="not_indexed",
                        severity="high",
                        recommendation="Check for noindex tags, canonical issues, or content quality problems",
                    ))
                elif "crawl" in reason.lower():
                    issues.append(IndexingIssue(
                        url=url,
                        issue_type="crawl_issue",
                        severity="medium",
                        recommendation="Check robots.txt, server errors, or improve internal linking",
                    ))
        
        for url in urls:
            if url.priority == 0:
                issues.append(IndexingIssue(
                    url=url.url,
                    issue_type="no_priority",
                    severity="low",
                    recommendation="Consider adding priority to important pages",
                ))
        
        return issues

    def fix_indexing_issues(
        self,
        issues: List[IndexingIssue],
    ) -> Dict:
        """Generate fix recommendations for indexing issues."""
        fix_plan = {
            "issues_found": len(issues),
            "fixes": [],
        }
        
        issue_groups = defaultdict(list)
        for issue in issues:
            issue_groups[issue.issue_type].append(issue)
        
        for issue_type, issue_list in issue_groups.items():
            if issue_type == "not_indexed":
                fix_plan["fixes"].append({
                    "issue_type": issue_type,
                    "action": "Check and remove noindex meta tags",
                    "affected_urls": [i.url for i in issue_list[:10]],
                    "code_change": """<!-- Add to <head> if missing -->
<meta name="robots" content="index, follow">""",
                })
            elif issue_type == "crawl_issue":
                fix_plan["fixes"].append({
                    "issue_type": issue_type,
                    "action": "Review robots.txt and fix crawl errors",
                    "affected_urls": [i.url for i in issue_list[:10]],
                    "code_change": """# Add to robots.txt
Allow: /""",
                })
            elif issue_type == "no_priority":
                fix_plan["fixes"].append({
                    "issue_type": issue_type,
                    "action": "Add priority attribute to sitemap",
                    "affected_urls": [i.url for i in issue_list[:10]],
                    "code_change": """<url>
  <loc>https://example.com/important-page</loc>
  <priority>1.0</priority>
  <changefreq>weekly</changefreq>
</url>""",
                })
        
        return fix_plan

    def generate_report(
        self,
        sitemap_path: Optional[str] = None,
        gsc_file: Optional[str] = None,
    ) -> Dict:
        """Generate a comprehensive indexing report."""
        urls = self.parse_sitemap(sitemap_path)
        sitemap_urls = [u.url for u in urls]
        
        gsc_data = {}
        gsc_indexed = []
        if gsc_data:
            gsc_data = self.parse_gsc_export(gsc_file)
            gsc_indexed = [item["url"] for items in gsc_data.values() for item in items]
        
        comparison = self.compare_sitemap_vs_gsc(sitemap_urls, gsc_indexed)
        issues = self.analyze_indexing_issues(urls, gsc_data)
        fixes = self.fix_indexing_issues(issues)
        
        return {
            "sitemap_stats": {
                "total_urls": len(urls),
                "urls": sitemap_urls[:100],
            },
            "gsc_stats": {
                "indexed_count": len(gsc_indexed),
                "status_breakdown": {k: len(v) for k, v in gsc_data.items()},
            },
            "comparison": comparison,
            "issues": [
                {"url": i.url, "type": i.issue_type, "severity": i.severity}
                for i in issues[:50]
            ],
            "fixes": fixes,
        }


def analyze_sitemap(sitemap_path: str) -> Dict:
    """Convenience function to analyze a sitemap."""
    analyzer = IndexingAnalyzer()
    return analyzer.parse_sitemap(sitemap_path)


def fix_indexing(sitemap_path: str, gsc_file: str) -> Dict:
    """Convenience function to analyze and fix indexing issues."""
    analyzer = IndexingAnalyzer()
    return analyzer.generate_report(sitemap_path, gsc_file)
