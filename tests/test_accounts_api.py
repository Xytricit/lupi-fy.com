import json
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

User = get_user_model()


class RegisterApiTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_api_creates_user(self):
        payload = {
            "username": "newuser123",
            "email": "newuser123@example.com",
            "password1": "StrongPass#1",
            "password2": "StrongPass#1",
        }
        response = self.client.post(
            reverse("register_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertIn("redirect_url", data)
        self.assertTrue(User.objects.filter(username=payload["username"]).exists())
        auth_user_id = self.client.session.get("_auth_user_id")
        self.assertIsNotNone(auth_user_id)
        self.assertEqual(
            str(User.objects.get(username=payload["username"]).id), auth_user_id
        )

    def test_register_api_rejects_duplicate_email(self):
        User.objects.create_user(
            username="existinguser",
            email="duplicate@example.com",
            password="Existing123!",
        )
        payload = {
            "username": "anotheruser",
            "email": "duplicate@example.com",
            "password1": "StrongPass#2",
            "password2": "StrongPass#2",
        }
        response = self.client.post(
            reverse("register_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data.get("success", True))
        self.assertIn("errors", data)
        self.assertIn("email", data["errors"])


class AvailabilityApiTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_check_username_available_for_new_value(self):
        response = self.client.get(
            reverse("check_username_api"),
            {"username": "brandnewuser"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("available"))
        self.assertEqual(data.get("message"), "Username available")

    def test_check_username_taken_is_case_insensitive(self):
        User.objects.create_user(
            username="TakenUser",
            email="taken@example.com",
            password="Pass123!",
        )
        response = self.client.get(
            reverse("check_username_api"),
            {"username": "takenuser"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data.get("available"))
        self.assertEqual(data.get("message"), "Username taken")

    def test_check_username_empty_returns_error(self):
        response = self.client.get(reverse("check_username_api"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data.get("available"))
        self.assertEqual(data.get("message"), "Username cannot be empty")

    def test_check_email_available_for_new_value(self):
        response = self.client.get(
            reverse("check_email_api"),
            {"email": "new-email@example.com"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("available"))
        self.assertEqual(data.get("message"), "Email available")

    def test_check_email_taken_is_case_insensitive(self):
        User.objects.create_user(
            username="user2",
            email="TakenEmail@example.com",
            password="Pass123!",
        )
        response = self.client.get(
            reverse("check_email_api"),
            {"email": "takenemail@example.com"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data.get("available"))
        self.assertEqual(data.get("message"), "Email taken")

    def test_check_email_invalid_format_returns_error(self):
        response = self.client.get(
            reverse("check_email_api"),
            {"email": "not-an-email"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data.get("available"))
        self.assertEqual(data.get("message"), "Invalid email format")


class LoginApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="loginuser",
            email="loginuser@example.com",
            password="Password123!",
        )
        self.user.is_email_verified = True
        self.user.save()

    def post_login(self, identifier, password, remember_me=False):
        return self.client.post(
            reverse("login_api"),
            data=json.dumps(
                {
                    "identifier": identifier,
                    "password": password,
                    "remember_me": remember_me,
                }
            ),
            content_type="application/json",
        )

    def test_login_api_succeeds_with_username(self):
        response = self.post_login(self.user.username, "Password123!")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("redirect_url"), reverse("dashboard_home"))
        self.assertEqual(str(self.user.id), self.client.session.get("_auth_user_id"))

    def test_login_api_succeeds_with_email(self):
        response = self.post_login(self.user.email, "Password123!")
        data = response.json()
        self.assertTrue(data.get("success"))

    def test_login_api_user_not_found(self):
        response = self.post_login("ghost@example.com", "Password123!")
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data.get("success"))
        self.assertEqual(data.get("error_code"), "user_not_found")

    def test_login_api_incorrect_password(self):
        response = self.post_login(self.user.username, "WrongPass!")
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data.get("error_code"), "incorrect_password")

    def test_login_api_account_locked(self):
        self.user.suspended_until = timezone.now() + timedelta(hours=2)
        self.user.save()
        response = self.post_login(self.user.username, "Password123!")
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data.get("error_code"), "account_locked")

    def test_login_api_account_inactive(self):
        self.user.is_active = False
        self.user.save()
        response = self.post_login(self.user.username, "Password123!")
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data.get("error_code"), "account_inactive")
