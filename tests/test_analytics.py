import pytest
from unittest.mock import Mock, patch, MagicMock
from analytics import AnalyticsClient, add_tracking_event, check_events, AnalyticsProvider


class TestAnalyticsClient:
    def test_init_without_env(self):
        client = AnalyticsClient()
        assert client.posthog_api_key is None
        assert client.ga_measurement_id is None
        assert client.mixpanel_api_key is None

    @patch.dict('os.environ', {'POSTHOG_API_KEY': 'test_key', 'POSTHOG_PROJECT_ID': 'test_proj'})
    def test_init_with_env(self):
        client = AnalyticsClient()
        assert client.posthog_api_key == 'test_key'
        assert client.posthog_project_id == 'test_proj'

    @patch('analytics.requests.post')
    def test_track_posthog(self, mock_post):
        mock_post.return_value = Mock(status_code=200, text='ok')
        client = AnalyticsClient()
        client.posthog_api_key = 'test_key'
        
        result = client._track_posthog('test_event', {'prop': 'value'})
        
        assert result['status'] == 200
        mock_post.assert_called_once()

    @patch('analytics.requests.post')
    def test_track_ga(self, mock_post):
        mock_post.return_value = Mock(status_code=200, text='ok')
        client = AnalyticsClient()
        client.ga_measurement_id = 'G-TEST123'
        client.ga_api_secret = 'secret'
        
        result = client._track_ga('test_event', {'prop': 'value'})
        
        assert result['status'] == 200

    @patch('analytics.requests.post')
    def test_track_mixpanel(self, mock_post):
        mock_post.return_value = Mock(status_code=200, text='ok')
        client = AnalyticsClient()
        client.mixpanel_api_key = 'test_key'
        
        result = client._track_mixpanel('test_event', {'prop': 'value'})
        
        assert result['status'] == 200

    def test_track_event_no_providers(self):
        client = AnalyticsClient()
        result = client.track_event('test_event')
        assert result == {}

    @patch('analytics.requests.get')
    def test_get_posthog_events(self, mock_get):
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {'results': [{'event': 'test'}]}
        )
        client = AnalyticsClient()
        client.posthog_api_key = 'test_key'
        client.posthog_project_id = 'test_proj'
        
        result = client._get_posthog_events(None, None, 10)
        
        assert len(result) == 1
        assert result[0]['event'] == 'test'

    def test_check_events_empty(self):
        with patch.object(AnalyticsClient, 'get_events', return_value=[]):
            result = check_events(['event1'])
            assert result['found'] == []
            assert result['missing'] == ['event1']


class TestConvenienceFunctions:
    @patch('analytics.AnalyticsClient')
    def test_add_tracking_event(self, mock_client):
        mock_instance = Mock()
        mock_instance.track_event.return_value = {'test': 'result'}
        mock_client.return_value = mock_instance
        
        result = add_tracking_event('test_event', {'prop': 'value'})
        
        assert result == {'test': 'result'}
