import json
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from accounts.models import ChatRateLimit

User = get_user_model()

@override_settings(GROQ_API_KEY='test-valid-groq-key')
class ChatbotTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = "settings_user"
        self.password = "Pass12345!"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            role="candidate",
            email="tester@example.com",
            first_name="Test",
            last_name="User",
            full_name="Test User",
        )

    def test_candidate_login_requires_the_correct_password_for_existing_users(self):
        response = self.client.post('/accounts/login/', {
            'username': self.username,
            'password': 'WrongPassword123!',
            'panel': 'candidate',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid credentials.')
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_recruiter_login_normalizes_the_recruiter_account(self):
        recruiter_user = User.objects.create_user(
            username='recruiter',
            password='Pass12345!',
            role='candidate',
            full_name='',
        )

        response = self.client.post('/accounts/login/', {
            'username': 'recruiter',
            'password': 'Recruiter@1234',
            'panel': 'recruiter',
        })

        self.assertEqual(response.status_code, 302)
        recruiter_user.refresh_from_db()
        self.assertTrue(recruiter_user.is_staff)
        self.assertEqual(recruiter_user.role, 'examiner')
        self.assertEqual(recruiter_user.full_name, 'Recruiter')

    def test_editor_language_selection_is_rendered_from_saved_settings(self):
        self.user.settings.default_language = 'cpp'
        self.user.settings.save(update_fields=['default_language'])

        self.client.force_login(self.user)
        response = self.client.get(reverse('settings'), {'tab': 'editor'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="cpp" selected')

    def test_profile_settings_update_profile_fields_and_picture(self):
        self.client.force_login(self.user)

        image_buffer = BytesIO()
        Image.new('RGB', (1, 1), color=(255, 0, 0)).save(image_buffer, format='PNG')
        image_file = ContentFile(image_buffer.getvalue(), name='avatar.png')
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
        # Mock successful Groq API response
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "Hello, how can I help you debug today?"
                }
            }]
        }).encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        self.client.login(username=self.username, password=self.password)

    def test_password_change_requires_correct_current_password_and_updates_password(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('settings'),
            {
                'section': 'password',
                'current_password': 'wrong-pass',
                'new_password': 'NewPass123!',
                'confirm_password': 'NewPass123!',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('Pass12345!'))
        self.assertFalse(self.user.check_password('NewPass123!'))

        response = self.client.post(
            reverse('settings'),
            {
                'section': 'password',
                'current_password': 'Pass12345!',
                'new_password': 'NewPass123!',
                'confirm_password': 'NewPass123!',
            },
        )
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
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "Response"
                }
            }]
        }).encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

    def test_notification_and_privacy_toggles_save_false_when_unchecked(self):
        self.client.force_login(self.user)

        settings_obj = self.user.settings
        settings_obj.email_notifications = True
        settings_obj.public_profile = True
        settings_obj.save()

        response = self.client.post(
            reverse('settings'),
            {
                'section': 'notifications',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        settings_obj.refresh_from_db()
        self.assertFalse(settings_obj.email_notifications)
        self.assertFalse(settings_obj.contest_notifications)
        self.assertFalse(settings_obj.course_update_notifications)
        self.assertFalse(settings_obj.submission_result_notifications)
        self.assertFalse(settings_obj.team_member_notifications)
        self.assertFalse(settings_obj.spam_filtering)

        response = self.client.post(
            reverse('settings'),
            {
                'section': 'privacy',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        settings_obj.refresh_from_db()
        self.assertFalse(settings_obj.public_profile)
        self.assertFalse(settings_obj.show_solved_problems)
        self.assertFalse(settings_obj.show_contest_ranking)
        self.assertFalse(settings_obj.show_activity)



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


class RegistrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')

    def test_registration_page_get(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')

    def test_registration_successful_post(self):
        payload = {
            'username': 'newcoder',
            'email': 'newcoder@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newcoder').exists())

    def test_registration_mismatched_passwords(self):
        payload = {
            'username': 'newcoder',
            'email': 'newcoder@example.com',
            'password': 'password123',
            'confirm_password': 'password124'
        }
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Passwords do not match.')

    def test_registration_short_password(self):
        payload = {
            'username': 'newcoder',
            'email': 'newcoder@example.com',
            'password': '123',
            'confirm_password': '123'
        }
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Password must be at least 8 characters long.')

