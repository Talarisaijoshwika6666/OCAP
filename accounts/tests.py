import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from accounts.models import ChatRateLimit

User = get_user_model()

class ChatbotTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = "testcoder"
        self.password = "pass12345"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            role="candidate"
        )
        self.api_url = reverse('chatbot_api')

    def test_chatbot_endpoint_requires_login(self):
        response = self.client.post(self.api_url, json.dumps({'message': 'Hi'}), content_type='application/json')
        self.assertEqual(response.status_code, 302) # Redirects to login page

    @patch('urllib.request.urlopen')
    def test_chatbot_successful_interaction(self, mock_urlopen):
        # Mock successful Gemini API response
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "candidates": [{
                "content": {
                    "parts": [{"text": "Hello, how can I help you debug today?"}]
                }
            }]
        }).encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        self.client.login(username=self.username, password=self.password)

        payload = {'message': 'Help me with binary search', 'history': []}
        response = self.client.post(self.api_url, json.dumps(payload), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['response'], "Hello, how can I help you debug today?")
        self.assertEqual(data['remaining_minute_limit'], 4) # 5 total - 1 used

        # Verify rate limit log was written to database
        self.assertEqual(ChatRateLimit.objects.filter(user=self.user).count(), 1)

    @patch('urllib.request.urlopen')
    def test_chatbot_rate_limiter_trigger(self, mock_urlopen):
        # Mock response
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "candidates": [{"content": {"parts": [{"text": "Response"}]}}]
        }).encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        self.client.login(username=self.username, password=self.password)

        # Make 5 successful requests (under the 5 per minute rate limit)
        for i in range(5):
            response = self.client.post(self.api_url, json.dumps({'message': f'Msg {i}'}), content_type='application/json')
            self.assertEqual(response.status_code, 200)

        # The 6th request should trigger rate limit (429 Too Many Requests)
        response = self.client.post(self.api_url, json.dumps({'message': 'Msg 6'}), content_type='application/json')
        self.assertEqual(response.status_code, 429)
        data = response.json()
        self.assertIn("Rate limit exceeded", data['error'])

