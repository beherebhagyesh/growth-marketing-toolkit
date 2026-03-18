import pytest
from unittest.mock import Mock, patch
from pagespeed import PagespeedAnalyzer, run_pagespeed, optimize_to_90


class TestPagespeedAnalyzer:
    def test_init_without_env(self):
        analyzer = PagespeedAnalyzer()
        assert analyzer.target_domain is None
        assert analyzer.lhci_token is None

    @patch.dict('os.environ', {'TARGET_DOMAIN': 'https://example.com', 'LHCI_API_TOKEN': 'token123'})
    def test_init_with_env(self):
        analyzer = PagespeedAnalyzer()
        assert analyzer.target_domain == 'https://example.com'
        assert analyzer.lhci_token == 'token123'

    def test_analyze_scores(self):
        analyzer = PagespeedAnalyzer()
        
        report = {
            'categories': {
                'performance': {'score': 0.85},
                'accessibility': {'score': 0.92},
                'best-practices': {'score': 0.88},
                'seo': {'score': 0.95},
            }
        }
        
        scores = analyzer.analyze_scores(report)
        
        assert scores.performance == 85.0
        assert scores.accessibility == 92.0
        assert scores.best_practices == 88.0
        assert scores.seo == 95.0

    def test_analyze_scores_with_pwa(self):
        analyzer = PagespeedAnalyzer()
        
        report = {
            'categories': {
                'performance': {'score': 0.85},
                'accessibility': {'score': 0.92},
                'best-practices': {'score': 0.88},
                'seo': {'score': 0.95},
                'pwa': {'score': 0.75},
            }
        }
        
        scores = analyzer.analyze_scores(report)
        
        assert scores.pwa == 75.0

    def test_get_opportunities(self):
        analyzer = PagespeedAnalyzer()
        
        report = {
            'audits': {
                'render-blocking-resources': {
                    'title': 'Eliminate render-blocking resources',
                    'description': 'Remove unused CSS',
                    'score': 0.4,
                },
                'unsized-images': {
                    'title': 'Image size',
                    'description': 'Add width/height',
                    'score': 0.8,
                },
            }
        }
        
        opportunities = analyzer.get_opportunities(report)
        
        assert len(opportunities) > 0

    def test_get_diagnostics(self):
        analyzer = PagespeedAnalyzer()
        
        report = {
            'audits': {
                'dom-size': {
                    'title': 'DOM size',
                    'description': 'Reduce DOM size',
                    'score': 0.8,
                },
                'image-alt': {
                    'title': 'Image alt text',
                    'description': 'Add alt text',
                    'score': 0.5,
                },
            }
        }
        
        diagnostics = analyzer.get_diagnostics(report)
        
        assert len(diagnostics) > 0

    @patch('pagespeed.subprocess.run')
    def test_run_lighthouse_not_installed(self, mock_run):
        mock_run.side_effect = FileNotFoundError()
        
        analyzer = PagespeedAnalyzer()
        result = analyzer.run_lighthouse('https://example.com')
        
        assert result['status'] == 'error'
        assert 'not installed' in result['message']

    @patch('pagespeed.subprocess.run')
    @patch('pagespeed.open', create=True)
    def test_run_lighthouse_success(self, mock_file, mock_run):
        mock_run.return_value = Mock(returncode=0)
        mock_file.return_value.__enter__.return_value.read.return_value = '{"categories": {"performance": {"score": 0.9}}}'
        
        analyzer = PagespeedAnalyzer()
        result = analyzer.run_lighthouse('https://example.com')
        
        assert result['status'] == 'success'

    def test_generate_optimization_plan(self):
        analyzer = PagespeedAnalyzer()
        
        report = {
            'categories': {
                'performance': {'score': 0.5},
                'accessibility': {'score': 0.95},
                'best-practices': {'score': 0.88},
                'seo': {'score': 0.95},
            },
            'audits': {
                'render-blocking-resources': {
                    'title': 'Eliminate render-blocking',
                    'description': 'Fix this',
                    'score': 0.3,
                },
            }
        }
        
        plan = analyzer.generate_optimization_plan(report)
        
        assert plan['target'] == 90
        assert 'current_scores' in plan
        assert len(plan['priority_fixes']) > 0


class TestConvenienceFunctions:
    @patch('pagespeed.PagespeedAnalyzer')
    def test_run_pagespeed(self, mock_analyzer):
        mock_instance = Mock()
        mock_instance.run_lighthouse.return_value = {'status': 'success', 'data': {}}
        mock_analyzer.return_value = mock_instance
        
        result = run_pagespeed('https://example.com')
        
        assert 'status' in result

    @patch('pagespeed.PagespeedAnalyzer')
    def test_optimize_to_90(self, mock_analyzer):
        mock_instance = Mock()
        mock_instance.run_lighthouse.return_value = {'status': 'success', 'data': {}}
        mock_instance.generate_optimization_plan.return_value = {'target': 90}
        mock_analyzer.return_value = mock_instance
        
        result = optimize_to_90('https://example.com')
        
        assert 'target' in result
