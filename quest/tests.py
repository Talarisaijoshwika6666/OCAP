from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class StudyPlanTests(TestCase):
    def test_study_plan_root_route_renders(self):
        user = User.objects.create_user(
            username='study_plan_user',
            email='study_plan@example.com',
            password='StrongPass123!',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('study_plan'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Study Plan')

    def test_study_plan_topic_route_renders(self):
        user = User.objects.create_user(
            username='study_plan_topic_user',
            email='study_plan_topic@example.com',
            password='StrongPass123!',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('study_plan', args=['data-structures']))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Data Structures')
