"""Growth Marketing Toolkit.

Usage:
    cp .env.example .env
    # Fill in your API keys

    python -m cli.main analytics track "button_clicked" '{"page": "/home"}'
    python -m cli.main analytics check button_clicked signup submit_form
    python -m cli.main analytics report "show me recent events"

    python -m cli.main seo universe ai marketing growth
    python -m cli.main seo optimize https://example.com ai marketing

    python -m cli.main indexing --sitemap sitemap.xml --gsc gsc_export.csv

    python -m cli.main pagespeed https://example.com
    python -m cli.main pagespeed https://example.com --optimize
"""
