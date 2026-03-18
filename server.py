"""Growth Marketing Toolkit - FastAPI Server."""
import os
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

sys.path.insert(0, str(Path(__file__).parent.parent))

from analytics import AnalyticsClient, add_tracking_event, check_events, AnalyticsProvider
from seo import SEOClient, create_keyword_universe, optimize_existing_page, create_new_page
from indexing import IndexingAnalyzer
from pagespeed import PagespeedAnalyzer

app = FastAPI(title="Growth Marketing Toolkit")

BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "frontend" / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "frontend" / "templates"))


class TrackEventRequest(BaseModel):
    event_name: str
    properties: Optional[Dict[str, Any]] = None


class KeywordUniverseRequest(BaseModel):
    keywords: List[str]


class OptimizePageRequest(BaseModel):
    url: str
    keywords: List[str]


class PagespeedRequest(BaseModel):
    url: str
    optimize: bool = False


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/analytics/track")
async def api_track_event(req: TrackEventRequest):
    try:
        result = add_tracking_event(req.event_name, req.properties)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analytics/check")
async def api_check_events(events: List[str]):
    try:
        result = check_events(events)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analytics/report")
async def api_analytics_report(query: str):
    try:
        client = AnalyticsClient()
        result = client.report_metrics(AnalyticsProvider.POSTHOG, query)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/seo/universe")
async def api_keyword_universe(req: KeywordUniverseRequest):
    try:
        result = create_keyword_universe(req.keywords)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/seo/optimize")
async def api_optimize_page(req: OptimizePageRequest):
    try:
        result = optimize_existing_page(req.url, req.keywords)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/seo/create-page")
async def api_create_page(keyword: str, competitors: List[str]):
    try:
        result = create_new_page(keyword, competitors)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/indexing/analyze")
async def api_analyze_indexing(sitemap_path: Optional[str] = None, gsc_path: Optional[str] = None):
    try:
        analyzer = IndexingAnalyzer()
        result = analyzer.generate_report(sitemap_path, gsc_path)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pagespeed/analyze")
async def api_pagespeed(req: PagespeedRequest):
    try:
        analyzer = PagespeedAnalyzer()
        if req.optimize:
            result = analyzer.run_lighthouse(req.url)
            if result.get("status") == "success":
                plan = analyzer.generate_optimization_plan(result.get("data", {}))
                return {"success": True, "data": plan}
            return result
        else:
            result = analyzer.run_lighthouse(req.url)
            if result.get("status") == "success":
                scores = analyzer.analyze_scores(result.get("data", {}))
                opportunities = analyzer.get_opportunities(result.get("data", {}))
                return {"success": True, "data": {"scores": scores.__dict__, "opportunities": opportunities}}
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
