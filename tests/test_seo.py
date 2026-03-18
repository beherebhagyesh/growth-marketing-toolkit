import pytest
from unittest.mock import Mock, patch
from seo import SEOClient, create_keyword_universe, optimize_existing_page


class TestSEOClient:
    def test_init_without_env(self):
        client = SEOClient()
        assert client.login is None
        assert client.password is None

    @patch.dict('os.environ', {'DATAFORSEO_LOGIN': 'test_login', 'DATAFORSEO_PASSWORD': 'test_pass'})
    def test_init_with_env(self):
        client = SEOClient()
        assert client.login == 'test_login'
        assert client.password == 'test_pass'

    def test_auth_returns_none_when_no_credentials(self):
        client = SEOClient()
        assert client._auth() == (None, None)

    def test_auth_returns_credentials(self):
        client = SEOClient()
        client.login = 'user'
        client.password = 'pass'
        assert client._auth() == ('user', 'pass')

    def test_headers_returns_content_type(self):
        client = SEOClient()
        headers = client._headers()
        assert headers == {"Content-Type": "application/json"}

    @patch('seo.requests.post')
    def test_create_keyword_universe_no_credentials(self, mock_post):
        client = SEOClient()
        result = client.create_keyword_universe(['test'])
        assert result == {"error": "DataForSEO credentials not configured"}
        mock_post.assert_not_called()

    @patch('seo.requests.post')
    def test_get_keyword_data_no_credentials(self, mock_post):
        client = SEOClient()
        result = client.get_keyword_data(['test'])
        assert result == []
        mock_post.assert_not_called()


class TestConvenienceFunctions:
    @patch('seo.SEOClient')
    def test_create_keyword_universe(self, mock_client):
        mock_instance = Mock()
        mock_instance.create_keyword_universe.return_value = {'status': 'success'}
        mock_client.return_value = mock_instance
        
        result = create_keyword_universe(['ai', 'marketing'])
        
        assert result == {'status': 'success'}

    @patch('seo.SEOClient')
    def test_optimize_existing_page(self, mock_client):
        mock_instance = Mock()
        mock_instance.optimize_page.return_value = {'recommendations': []}
        mock_client.return_value = mock_instance
        
        result = optimize_existing_page('https://example.com', ['keyword'])
        
        assert 'recommendations' in result
