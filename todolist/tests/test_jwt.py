from faker import Faker
from rest_framework.test import APITestCase
from rest_framework import status
from django.shortcuts import reverse
from django.contrib.auth import get_user_model


class TestJWTAuth(APITestCase):
    @classmethod
    def setUpTestData(cls):
        faker = Faker()
        profile = faker.simple_profile()

        cls.user_pass = faker.password(8)

        cls.user = get_user_model().objects.create_user(
            username=profile["username"],
            password=cls.user_pass,
            email=profile["mail"],
        )

    def test_no_data(self):
        resp = self.client.post(reverse("token_obtain_pair"))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        data = resp.json()
        self.assertIn("username", data)
        self.assertIn("password", data)

    def test_with_valid_user_data(self):
        resp = self.client.post(
            reverse("token_obtain_pair"),
            data={
                "username": self.user.username,
                "password": self.user_pass,
            },
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.json()
        self.assertIn("access", data)
        self.assertIn("refresh", data)

    def test_with_invalid_user_data(self):
        resp = self.client.post(
            reverse("token_obtain_pair"),
            data={
                "username": self.user.username,
                "password": "INVALID_PASSWORD",
            },
        )

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertDictEqual(
            resp.json(),
            {
                "detail": "No active account found with the given credentials",
            },
        )

    def test_refresh_token(self):
        resp = self.client.post(
            reverse("token_obtain_pair"),
            data={
                "username": self.user.username,
                "password": self.user_pass,
            },
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        refresh_token = resp.json()["refresh"]

        resp = self.client.post(reverse("token_refresh"), data={"refresh": refresh_token})

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.assertIn("refresh", resp.json())
