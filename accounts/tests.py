import json
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.test import Client, TestCase
from django.urls import reverse
from unittest.mock import MagicMock, patch

from PIL import Image

from .models import ChatRateLimit, UserSettings

User = get_user_model()


class SettingsModuleTests(TestCase):
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

        response = self.client.post(
            reverse('settings'),
            {
                'section': 'profile',
                'username': 'tester2',
                'first_name': 'Updated',
                'last_name': 'Name',
                'email': 'updated@example.com',
                'full_name': 'Updated Name',
                'mobile': '1234567890',
                'bio': 'A short bio',
                'organization': 'OCAP',
                'profile_picture': image_file,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'tester2')
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')
        self.assertEqual(self.user.email, 'updated@example.com')
        self.assertEqual(self.user.bio, 'A short bio')
        self.assertEqual(self.user.organization, 'OCAP')
        self.assertTrue(self.user.profile_picture)

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

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPass123!'))

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



