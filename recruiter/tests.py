from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from assessments.models import Assessment
from questions.models import Question
from results.models import Result
from submissions.models import Submission

User = get_user_model()


class RecruiterSettingsTests(TestCase):
    def test_recruiter_candidates_page_renders_real_candidate_data(self):
        recruiter = User.objects.create_user(
            username='recruiter_test',
            email='recruiter@example.com',
            password='StrongPass123!',
            is_staff=True,
        )
        candidate = User.objects.create_user(
            username='candidate_test',
            email='candidate@example.com',
            password='StrongPass123!',
            role='candidate',
            full_name='Candidate User',
        )
        assessment = Assessment.objects.create(
            title='Sample Assessment',
            duration=30,
            total_marks=100,
            difficulty='Beginner',
            is_active=True,
        )
        Result.objects.create(
            candidate=candidate,
            assessment=assessment,
            score=88,
            rank=1,
            passed=True,
        )

        self.client.force_login(recruiter)
        response = self.client.get(reverse('recruiter_candidates'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Candidate User')
        self.assertContains(response, 'candidate@example.com')
        self.assertContains(response, '88.0')

    def test_recruiter_candidates_page_renders_modal_details_for_view_action(self):
        recruiter = User.objects.create_user(
            username='recruiter_modal_test',
            email='recruiter_modal@example.com',
            password='StrongPass123!',
            is_staff=True,
        )
        candidate = User.objects.create_user(
            username='candidate_modal_test',
            email='candidate_modal@example.com',
            password='StrongPass123!',
            role='candidate',
            full_name='Modal Candidate',
            mobile='9876543210',
        )
        assessment = Assessment.objects.create(
            title='Sample Assessment',
            duration=30,
            total_marks=100,
            difficulty='Beginner',
            is_active=True,
        )
        question = Question.objects.create(
            assessment=assessment,
            title='Sum of Two Numbers',
            description='Add two numbers',
            difficulty='Easy',
            question_type='coding',
            language='python',
        )
        Result.objects.create(
            candidate=candidate,
            assessment=assessment,
            score=88,
            rank=1,
            passed=True,
        )
        Submission.objects.create(
            user=candidate,
            question=question,
            code='print(1)',
            language='python',
            score=100,
            passed_cases=1,
            total_cases=1,
            result='Accepted',
        )

        self.client.force_login(recruiter)
        response = self.client.get(reverse('recruiter_candidates'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Candidate Details')
        self.assertContains(response, 'Modal Candidate')
        self.assertContains(response, 'candidate_modal_test')
        self.assertContains(response, '9876543210')
        self.assertContains(response, 'Recent Coding Submissions')
        self.assertContains(response, 'Recent Contests')

    def test_recruiter_delete_candidate_removes_candidate_from_database(self):
        recruiter = User.objects.create_user(
            username='recruiter_delete_test',
            email='recruiter_delete@example.com',
            password='StrongPass123!',
            is_staff=True,
        )
        candidate = User.objects.create_user(
            username='candidate_delete_test',
            email='candidate_delete@example.com',
            password='StrongPass123!',
            role='candidate',
            full_name='Delete Candidate',
        )

        self.client.force_login(recruiter)
        response = self.client.post(reverse('recruiter_delete_candidate', args=[candidate.pk]))

        self.assertRedirects(response, reverse('recruiter_candidates'))
        self.assertFalse(User.objects.filter(pk=candidate.pk).exists())

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
