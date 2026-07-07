from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from .models import UserSettings

User = get_user_model()


class SettingsModuleTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='OldPass123!',
            first_name='Test',
            last_name='User',
            full_name='Test User',
        )
        self.client.force_login(self.user)

    def test_profile_settings_update_profile_fields_and_picture(self):
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
        self.assertTrue(self.user.check_password('OldPass123!'))
        self.assertFalse(self.user.check_password('NewPass123!'))

        response = self.client.post(
            reverse('settings'),
            {
                'section': 'password',
                'current_password': 'OldPass123!',
                'new_password': 'NewPass123!',
                'confirm_password': 'NewPass123!',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPass123!'))

    def test_notification_and_privacy_toggles_save_false_when_unchecked(self):
        settings = self.user.settings
        settings.email_notifications = True
        settings.public_profile = True
        settings.save()

        response = self.client.post(
            reverse('settings'),
            {
                'section': 'notifications',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        settings.refresh_from_db()
        self.assertFalse(settings.email_notifications)
        self.assertFalse(settings.contest_notifications)
        self.assertFalse(settings.course_update_notifications)
        self.assertFalse(settings.submission_result_notifications)
        self.assertFalse(settings.team_member_notifications)
        self.assertFalse(settings.spam_filtering)

        response = self.client.post(
            reverse('settings'),
            {
                'section': 'privacy',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        settings.refresh_from_db()
        self.assertFalse(settings.public_profile)
        self.assertFalse(settings.show_solved_problems)
        self.assertFalse(settings.show_contest_ranking)
        self.assertFalse(settings.show_activity)
