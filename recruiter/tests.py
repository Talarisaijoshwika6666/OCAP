from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class RecruiterSettingsTests(TestCase):
    def test_recruiter_settings_route_uses_existing_settings_view(self):
        user = User.objects.create_user(
            username='recruiter_test',
            email='recruiter@example.com',
            password='StrongPass123!',
            is_staff=True,
        )
        self.client.force_login(user)

        response = self.client.get(reverse('recruiter_settings'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Profile Information')

    def test_recruiter_all_submissions_route_renders_page(self):
        user = User.objects.create_user(
            username='recruiter_submissions',
            email='recruiter_submissions@example.com',
            password='StrongPass123!',
            is_staff=True,
        )
        self.client.force_login(user)

        response = self.client.get(reverse('recruiter_all_submissions'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'All Submissions')

    def test_recruiter_candidates_route_renders_page(self):
        user = User.objects.create_user(
            username='recruiter_candidates',
            email='recruiter_candidates@example.com',
            password='StrongPass123!',
            is_staff=True,
        )
        self.client.force_login(user)

        response = self.client.get(reverse('recruiter_candidates'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Candidates')

    def test_recruiter_reports_route_renders_page(self):
        user = User.objects.create_user(
            username='recruiter_reports',
            email='recruiter_reports@example.com',
            password='StrongPass123!',
            is_staff=True,
        )
        self.client.force_login(user)

        response = self.client.get(reverse('recruiter_reports'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reports')

    def test_recruiter_contest_results_route_renders_page(self):
        user = User.objects.create_user(
            username='recruiter_contest_results',
            email='recruiter_contest_results@example.com',
            password='StrongPass123!',
            is_staff=True,
        )
        self.client.force_login(user)

        response = self.client.get(reverse('recruiter_contest_results'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contest Results')
