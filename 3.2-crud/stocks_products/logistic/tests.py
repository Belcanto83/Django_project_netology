from unittest import TestCase
from rest_framework.test import APIClient


class TestSomething(TestCase):
    def test_sample_view(self):
        client = APIClient()
        response = client.get('/test_cicd/')
        self.assertEqual(response.status_code, 200)
