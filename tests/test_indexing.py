import pytest
from unittest.mock import Mock, patch, mock_open
from indexing import IndexingAnalyzer, URLStatus, analyze_sitemap, fix_indexing


class TestIndexingAnalyzer:
    def test_init_without_env(self):
        analyzer = IndexingAnalyzer()
        assert analyzer.sitemap_url is None
        assert analyzer.target_domain is None

    @patch.dict('os.environ', {'TARGET_SITEMAP_URL': 'https://example.com/sitemap.xml'})
    def test_init_with_env(self):
        analyzer = IndexingAnalyzer()
        assert analyzer.sitemap_url == 'https://example.com/sitemap.xml'

    def test_parse_sitemap_empty(self):
        analyzer = IndexingAnalyzer()
        result = analyzer.parse_sitemap()
        assert result == []

    @patch('indexing.open', new_callable=mock_open, read_data='''<?xml version="1.0"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/page1</loc>
    <lastmod>2024-01-01</lastmod>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://example.com/page2</loc>
    <priority>0.8</priority>
  </url>
</urlset>''')
    def test_parse_sitemap(self, mock_file):
        analyzer = IndexingAnalyzer()
        result = analyzer.parse_sitemap('sitemap.xml')
        
        assert len(result) == 2
        assert result[0].url == 'https://example.com/page1'
        assert result[0].priority == 1.0
        assert result[1].url == 'https://example.com/page2'

    def test_parse_gsc_export(self):
        analyzer = IndexingAnalyzer()
        
        with patch('indexing.open', new_callable=mock_open, read_data='''URL,Indexing status,Status reason
https://example.com/page1,Indexed,/indexed
https://example.com/page2,Discovered,/discovered'''):
            result = analyzer.parse_gsc_export('gsc.csv')
            
        assert 'Indexed' in result
        assert 'Discovered' in result

    def test_compare_sitemap_vs_gsc(self):
        analyzer = IndexingAnalyzer()
        
        sitemap = ['https://example.com/a', 'https://example.com/b', 'https://example.com/c']
        gsc = ['https://example.com/a', 'https://example.com/c', 'https://example.com/d']
        
        result = analyzer.compare_sitemap_vs_gsc(sitemap, gsc)
        
        assert len(result['indexed_in_both']) == 2
        assert 'https://example.com/b' in result['in_sitemap_not_indexed']
        assert 'https://example.com/d' in result['indexed_not_in_sitemap']

    def test_analyze_indexing_issues(self):
        analyzer = IndexingAnalyzer()
        
        urls = [
            URLStatus('https://example.com/a', 'indexed', None, 1.0, None),
            URLStatus('https://example.com/b', 'indexed', None, 0.0, None),
        ]
        gsc_data = {
            'Not indexed': [{'url': 'https://example.com/c', 'reason': 'Not indexed - noindex'}]
        }
        
        issues = analyzer.analyze_indexing_issues(urls, gsc_data)
        
        assert len(issues) > 0

    def test_fix_indexing_issues(self):
        analyzer = IndexingAnalyzer()
        
        from indexing import IndexingIssue
        issues = [
            IndexingIssue('https://example.com/a', 'not_indexed', 'high', 'Remove noindex'),
            IndexingIssue('https://example.com/b', 'no_priority', 'low', 'Add priority'),
        ]
        
        fix_plan = analyzer.fix_indexing_issues(issues)
        
        assert fix_plan['issues_found'] == 2
        assert len(fix_plan['fixes']) > 0


class TestConvenienceFunctions:
    @patch('indexing.IndexingAnalyzer')
    def test_analyze_sitemap(self, mock_analyzer):
        mock_instance = Mock()
        mock_instance.parse_sitemap.return_value = []
        mock_analyzer.return_value = mock_instance
        
        result = analyze_sitemap('sitemap.xml')
        
        assert isinstance(result, list)
