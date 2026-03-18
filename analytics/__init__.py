"""Analytics integration module for PostHog, Google Analytics, and Mixpanel."""
import os
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class AnalyticsProvider(Enum):
    POSTHOG = "posthog"
    GOOGLE_ANALYTICS = "ga"
    MIXPANEL = "mixpanel"


@dataclass
class Event:
    name: str
    properties: Dict[str, Any]
    timestamp: Optional[datetime] = None


class AnalyticsClient:
    def __init__(self):
        self.posthog_api_key = os.getenv("POSTHOG_API_KEY")
        self.posthog_project_id = os.getenv("POSTHOG_PROJECT_ID")
        self.ga_measurement_id = os.getenv("GOOGLE_ANALYTICS_MEASUREMENT_ID")
        self.ga_api_secret = os.getenv("GOOGLE_ANALYTICS_API_SECRET")
        self.mixpanel_api_key = os.getenv("MIXPANEL_API_KEY")
        self.mixpanel_api_secret = os.getenv("MIXPANEL_API_SECRET")

    def track_event(
        self,
        event_name: str,
        properties: Optional[Dict[str, Any]] = None,
        provider: Optional[AnalyticsProvider] = None,
    ) -> Dict[str, Any]:
        """Track an event to all configured providers or a specific one."""
        results = {}
        properties = properties or {}

        if provider is None or provider == AnalyticsProvider.POSTHOG:
            if self.posthog_api_key:
                results["posthog"] = self._track_posthog(event_name, properties)

        if provider is None or provider == AnalyticsProvider.GOOGLE_ANALYTICS:
            if self.ga_measurement_id:
                results["ga"] = self._track_ga(event_name, properties)

        if provider is None or provider == AnalyticsProvider.MIXPANEL:
            if self.mixpanel_api_key:
                results["mixpanel"] = self._track_mixpanel(event_name, properties)

        return results

    def _track_posthog(self, event_name: str, properties: Dict) -> Dict:
        """Send event to PostHog."""
        url = f"https://app.posthog.com/e"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.posthog_api_key}",
        }
        payload = {
            "event": event_name,
            "properties": properties,
            "timestamp": datetime.utcnow().isoformat(),
        }
        response = requests.post(url, json=payload, headers=headers)
        return {"status": response.status_code, "body": response.text}

    def _track_ga(self, event_name: str, properties: Dict) -> Dict:
        """Send event to Google Analytics 4 via Measurement Protocol."""
        url = f"https://www.google-analytics.com/mp/collect"
        payload = {
            "client_id": properties.get("client_id", "anonymous"),
            "events": [
                {
                    "name": event_name,
                    "params": properties,
                }
            ],
        }
        response = requests.post(
            url,
            params={"measurement_id": self.ga_measurement_id, "api_secret": self.ga_api_secret},
            json=payload,
        )
        return {"status": response.status_code, "body": response.text}

    def _track_mixpanel(self, event_name: str, properties: Dict) -> Dict:
        """Send event to Mixpanel."""
        url = "https://api.mixpanel.com/track"
        payload = {
            "event": event_name,
            "properties": {**properties, "time": int(datetime.utcnow().timestamp())},
        }
        response = requests.post(url, json=[payload])
        return {"status": response.status_code, "body": response.text}

    def get_events(
        self,
        provider: AnalyticsProvider,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """Fetch events from a specific provider."""
        if provider == AnalyticsProvider.POSTHOG:
            return self._get_posthog_events(start_date, end_date, limit)
        elif provider == AnalyticsProvider.MIXPANEL:
            return self._get_mixpanel_events(start_date, end_date, limit)
        return []

    def _get_posthog_events(
        self, start_date: Optional[datetime], end_date: Optional[datetime], limit: int
    ) -> List[Dict]:
        """Fetch events from PostHog."""
        if not self.posthog_api_key:
            return []

        url = f"https://app.posthog.com/api/projects/{self.posthog_project_id}/events/"
        headers = {"Authorization": f"Bearer {self.posthog_api_key}"}
        params = {"limit": limit}
        if start_date:
            params["after"] = start_date.isoformat()
        if end_date:
            params["before"] = end_date.isoformat()

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json().get("results", [])
        return []

    def _get_mixpanel_events(
        self, start_date: Optional[datetime], end_date: Optional[datetime], limit: int
    ) -> List[Dict]:
        """Fetch events from Mixpanel."""
        if not self.mixpanel_api_key:
            return []

        from base64 import b64encode

        url = "https://api.mixpanel.com/funnels"
        auth = b64encode(f"{self.mixpanel_api_key}:{self.mixpanel_api_secret}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}"}
        response = requests.get(url, headers=headers)
        return response.json() if response.status_code == 200 else []

    def create_dashboard(
        self,
        provider: AnalyticsProvider,
        title: str,
        events: List[str],
        metrics: List[str],
    ) -> Dict:
        """Create a new dashboard with specified events and metrics."""
        if provider == AnalyticsProvider.POSTHOG:
            return self._create_posthog_dashboard(title, events, metrics)
        return {"error": "Dashboard creation not implemented for this provider"}

    def _create_posthog_dashboard(self, title: str, events: List[str], metrics: List[str]) -> Dict:
        """Create a dashboard in PostHog."""
        if not self.posthog_api_key:
            return {"error": "PostHog API key not configured"}

        url = f"https://app.posthog.com/api/projects/{self.posthog_project_id}/dashboards/"
        headers = {"Authorization": f"Bearer {self.posthog_api_key}"}
        payload = {
            "name": title,
            "description": f"Auto-generated dashboard tracking: {', '.join(events)}",
            "filters": {},
            "tiles": [
                {"kind": "InsightViz", "layouts": {}, "color": None}
                for _ in events
            ],
        }
        response = requests.post(url, json=payload, headers=headers)
        return {"status": response.status_code, "data": response.json() if response.status_code == 201 else response.text}

    def report_metrics(
        self,
        provider: AnalyticsProvider,
        query: str,
    ) -> Dict:
        """Generate a natural language report on metrics."""
        if provider == AnalyticsProvider.POSTHOG:
            return self._report_posthog_metrics(query)
        return {"error": "Reporting not implemented for this provider"}

    def _report_posthog_metrics(self, query: str) -> Dict:
        """Generate a report from PostHog data."""
        if not self.posthog_api_key:
            return {"error": "PostHog API key not configured"}

        events = self._get_posthog_events(None, None, 1000)
        
        total_events = len(events)
        event_types = {}
        for event in events:
            name = event.get("event", "unknown")
            event_types[name] = event_types.get(name, 0) + 1

        return {
            "query": query,
            "total_events": total_events,
            "event_breakdown": event_types,
            "summary": f"Found {total_events} events. Top events: {', '.join([f'{k}({v})' for k, v in sorted(event_types.items(), key=lambda x: -x[1])[:5]])}",
        }


def add_tracking_event(event_name: str, properties: Optional[Dict] = None) -> Dict:
    """Convenience function to add a new tracking event."""
    client = AnalyticsClient()
    return client.track_event(event_name, properties)


def check_events(events: List[str], provider: AnalyticsProvider = AnalyticsProvider.POSTHOG) -> Dict:
    """Check if specified events exist and are correctly tracked."""
    client = AnalyticsClient()
    tracked_events = client.get_events(provider)
    tracked_event_names = set(e.get("event") for e in tracked_events)
    
    found = [e for e in events if e in tracked_event_names]
    missing = [e for e in events if e not in tracked_event_names]
    
    return {
        "found": found,
        "missing": missing,
        "status": "ok" if not missing else "missing_events",
    }
