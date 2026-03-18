"""Growth Marketing Toolkit CLI."""
import argparse
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from analytics import AnalyticsClient, add_tracking_event, check_events, AnalyticsProvider
from seo import create_keyword_universe, optimize_existing_page, create_new_page
from indexing import analyze_sitemap, fix_indexing
from pagespeed import run_pagespeed, optimize_to_90


def main():
    parser = argparse.ArgumentParser(
        description="Growth Marketing Toolkit - Claude Code as your data analyst"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Analytics commands
    analytics_parser = subparsers.add_parser("analytics", help="Analytics commands")
    analytics_sub = analytics_parser.add_subparsers(dest="analytics_command")
    
    track_parser = analytics_sub.add_parser("track", help="Track an event")
    track_parser.add_argument("event_name", help="Event name to track")
    track_parser.add_argument("--properties", "-p", help="Event properties as JSON")
    
    check_parser = analytics_sub.add_parser("check", help="Check if events are tracked")
    check_parser.add_argument("events", nargs="+", help="Event names to check")
    
    report_parser = analytics_sub.add_parser("report", help="Generate metrics report")
    report_parser.add_argument("query", help="Query in natural language")
    
    # SEO commands
    seo_parser = subparsers.add_parser("seo", help="SEO commands")
    seo_sub = seo_parser.add_subparsers(dest="seo_command")
    
    universe_parser = seo_sub.add_parser("universe", help="Create keyword universe")
    universe_parser.add_argument("keywords", nargs="+", help="Seed keywords")
    
    optimize_parser = seo_sub.add_parser("optimize", help="Optimize a page")
    optimize_parser.add_argument("url", help="URL to optimize")
    optimize_parser.add_argument("keywords", nargs="+", help="Target keywords")
    
    create_parser = seo_sub.add_parser("create", help="Create new page content")
    create_parser.add_argument("keyword", help="Target keyword")
    create_parser.add_argument("competitors", nargs="+", help="Competitor URLs")
    
    # Indexing commands
    indexing_parser = subparsers.add_parser("indexing", help="Indexing commands")
    indexing_parser.add_argument("--sitemap", "-s", help="Path to sitemap.xml")
    indexing_parser.add_argument("--gsc", "-g", help="Path to GSC export CSV")
    
    # Pagespeed commands
    pagespeed_parser = subparsers.add_parser("pagespeed", help="Pagespeed commands")
    pagespeed_parser.add_argument("url", help="URL to analyze")
    pagespeed_parser.add_argument("--optimize", "-o", action="store_true", help="Generate optimization plan")
    
    args = parser.parse_args()
    
    if args.command == "analytics":
        if args.analytics_command == "track":
            import json
            props = json.loads(args.properties) if args.properties else {}
            result = add_tracking_event(args.event_name, props)
            print(f"Tracked event: {result}")
        elif args.analytics_command == "check":
            result = check_events(args.events)
            print(f"Found: {result['found']}")
            print(f"Missing: {result['missing']}")
        elif args.analytics_command == "report":
            client = AnalyticsClient()
            result = client.report_metrics(AnalyticsProvider.POSTHOG, args.query)
            print(result)
    
    elif args.command == "seo":
        if args.seo_command == "universe":
            result = create_keyword_universe(args.keywords)
            print(result)
        elif args.seo_command == "optimize":
            result = optimize_existing_page(args.url, args.keywords)
            print(result)
        elif args.seo_command == "create":
            result = create_new_page(args.keyword, args.competitors)
            print(result)
    
    elif args.command == "indexing":
        result = fix_indexing(args.sitemap, args.gsc) if args.sitemap or args.gsc else {}
        print(result)
    
    elif args.command == "pagespeed":
        if args.optimize:
            result = optimize_to_90(args.url)
        else:
            result = run_pagespeed(args.url)
        print(result)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
