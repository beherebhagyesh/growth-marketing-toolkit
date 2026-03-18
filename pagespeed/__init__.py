"""Pagespeed automation using Google Lighthouse."""
import os
import json
import subprocess
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class LighthouseScores:
    performance: float
    accessibility: float
    best_practices: float
    seo: float
    pwa: Optional[float] = None


@dataclass
class LighthouseReport:
    url: str
    scores: LighthouseScores
    metrics: Dict
    opportunities: List[Dict]
    diagnostics: List[Dict]
    timestamp: datetime


class PagespeedAnalyzer:
    def __init__(self):
        self.target_domain = os.getenv("TARGET_DOMAIN")
        self.lhci_token = os.getenv("LHCI_API_TOKEN")

    def run_lighthouse(
        self,
        url: str,
        output_path: Optional[str] = None,
        categories: Optional[List[str]] = None,
    ) -> Dict:
        """Run Lighthouse on a URL."""
        categories = categories or ["performance", "accessibility", "best-practices", "seo"]
        
        cmd = [
            "lighthouse",
            url,
            "--only-categories", *categories,
            "--output", "json",
            "--output-path", output_path or "lighthouse-results.json",
            "--chrome-flags", "--headless",
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
            )
            
            if result.returncode == 0:
                with open(output_path or "lighthouse-results.json", "r") as f:
                    data = json.load(f)
                return {"status": "success", "data": data}
            return {"status": "error", "output": result.stderr}
        except FileNotFoundError:
            return {"status": "error", "message": "Lighthouse CLI not installed. Run: npm install -g lighthouse"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def analyze_scores(self, report: Dict) -> LighthouseScores:
        """Extract scores from Lighthouse report."""
        categories = report.get("categories", {})
        
        return LighthouseScores(
            performance=categories.get("performance", {}).get("score", 0) * 100,
            accessibility=categories.get("accessibility", {}).get("score", 0) * 100,
            best_practices=categories.get("best-practices", {}).get("score", 0) * 100,
            seo=categories.get("seo", {}).get("score", 0) * 100,
            pwa=categories.get("pwa", {}).get("score", 0) * 100 if "pwa" in categories else None,
        )

    def get_opportunities(self, report: Dict) -> List[Dict]:
        """Extract optimization opportunities from Lighthouse report."""
        audits = report.get("audits", {})
        opportunities = []
        
        impact_audits = [
            "render-blocking-resources",
            "unsized-images",
            "efficient-animated-content",
            "unused-css-rules",
            "unused-javascript",
            "server-response-time",
            "main-thread-work",
            "third-party-summary",
        ]
        
        for audit_id in impact_audits:
            if audit_id in audits:
                audit = audits[audit_id]
                if audit.get("score", 1) < 0.9:
                    opportunities.append({
                        "id": audit_id,
                        "title": audit.get("title", audit_id),
                        "description": audit.get("description", "")[:200],
                        "score": audit.get("score", 0) * 100,
                        "impact": "high" if audit.get("score", 1) < 0.5 else "medium",
                    })
        
        return sorted(opportunities, key=lambda x: x["score"])

    def get_diagnostics(self, report: Dict) -> List[Dict]:
        """Extract diagnostic information."""
        audits = report.get("audits", {})
        diagnostics = []
        
        diag_audits = [
            "critical-request-chains",
            "dom-size",
            "duplicate-javascript",
            "font-display",
            "image-alt",
            "link-text",
            "meta-description",
            "document-title",
        ]
        
        for audit_id in diag_audits:
            if audit_id in audits:
                audit = audits[audit_id]
                if audit.get("score", 1) < 1:
                    diagnostics.append({
                        "id": audit_id,
                        "title": audit.get("title", audit_id),
                        "description": audit.get("description", "")[:200],
                        "score": audit.get("score", 0) * 100,
                    })
        
        return diagnostics

    def generate_optimization_plan(self, report: Dict) -> Dict:
        """Generate a plan to optimize scores to 90+."""
        scores = self.analyze_scores(report)
        opportunities = self.get_opportunities(report)
        diagnostics = self.get_diagnostics(report)
        
        plan = {
            "current_scores": {
                "performance": scores.performance,
                "accessibility": scores.accessibility,
                "best_practices": scores.best_practices,
                "seo": scores.seo,
            },
            "target": 90,
            "priority_fixes": [],
        }
        
        if scores.performance < 90:
            high_impact = [o for o in opportunities if o.get("impact") == "high"]
            plan["priority_fixes"].extend([
                self._generate_fix_for_opportunity(o) for o in high_impact[:5]
            ])
        
        if scores.accessibility < 90:
            plan["priority_fixes"].append({
                "category": "accessibility",
                "title": "Fix accessibility issues",
                "recommendations": [d for d in diagnostics if "alt" in d["id"] or "title" in d["id"]],
            })
        
        return plan

    def _generate_fix_for_opportunity(self, opportunity: Dict) -> Dict:
        """Generate specific fix instructions for an opportunity."""
        fix_templates = {
            "render-blocking-resources": {
                "category": "performance",
                "title": "Eliminate render-blocking resources",
                "code_change": """<!-- Add 'defer' or 'async' to scripts -->
<script src="critical.js" defer></script>

<!-- Inline critical CSS -->
<style>
  /* Critical styles here */
</style>""",
            },
            "unsized-images": {
                "category": "performance",
                "title": "Add explicit width and height to images",
                "code_change": """<!-- Add dimensions -->
<img src="image.jpg" width="800" height="600" alt="Description">""",
            },
            "unused-css-rules": {
                "category": "performance",
                "title": "Remove unused CSS",
                "code_change": """<!-- Use PurgeCSS or similar tools to remove unused styles -->""",
            },
            "unused-javascript": {
                "category": "performance",
                "title": "Remove unused JavaScript",
                "code_change": """<!-- Use code splitting and tree shaking -->
<script type="module" src="module.js"></script>""",
            },
            "server-response-time": {
                "category": "performance",
                "title": "Reduce server response time",
                "code_change": """# Add caching headers (.htaccess or nginx)
Cache-Control: max-age=86400

# Consider:
# - CDN (Cloudflare, Fastly)
# - Caching layer (Redis, Varnish)
# - Database optimization""",
            },
        }
        
        return fix_templates.get(opportunity.get("id"), {
            "category": "general",
            "title": opportunity.get("title"),
            "recommendation": opportunity.get("description"),
        })

    def audit_urls(self, urls: List[str]) -> Dict:
        """Run Lighthouse on multiple URLs and generate report."""
        results = []
        
        for url in urls:
            print(f"Running Lighthouse on {url}...")
            result = self.run_lighthouse(url)
            if result.get("status") == "success":
                report_data = result.get("data", {})
                scores = self.analyze_scores(report_data)
                results.append({
                    "url": url,
                    "scores": scores,
                    "passed": scores.performance >= 90 and scores.accessibility >= 90,
                })
        
        return {
            "results": results,
            "summary": {
                "total": len(results),
                "passed": sum(1 for r in results if r.get("passed")),
                "failed": sum(1 for r in results if not r.get("passed")),
            },
        }


def run_pagespeed(url: str) -> Dict:
    """Convenience function to run pagespeed analysis."""
    analyzer = PagespeedAnalyzer()
    return analyzer.run_lighthouse(url)


def optimize_to_90(url: str) -> Dict:
    """Convenience function to get optimization plan to reach 90+ scores."""
    analyzer = PagespeedAnalyzer()
    result = analyzer.run_lighthouse(url)
    if result.get("status") == "success":
        return analyzer.generate_optimization_plan(result.get("data"))
    return result
