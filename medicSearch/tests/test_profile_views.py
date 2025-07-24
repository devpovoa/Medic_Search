from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from medicSearch.models import Profile
from unittest.mock import patch

class ProfileViewsTest(TestCase):
    def setUp(self):
        # Usuário autenticado
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="123456"
        )
        self.profile = self.user.profile

        # Outro usuário para simular acesso via id
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="123456"
        )
        self.other_profile = self.other_user.profile

    # =======================
    # LIST PROFILE VIEW
    # =======================
    def test_list_profile_view_authenticated_own_profile(self):
        """Usuário logado sem id deve ver seu próprio perfil"""
        self.client.login(username="testuser", password="123456")
        response = self.client.get(reverse("profile_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.profile.user.username)

    def test_list_profile_view_with_specific_id(self):
        """Com id na URL deve mostrar o perfil do outro usuário"""
        self.client.login(username="testuser", password="123456")
        response = self.client.get(reverse("profile_list", args=[self.other_user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.other_profile.user.username)

    def test_list_profile_view_redirect_if_not_authenticated(self):
        """Se não logado e sem id deve redirecionar para /"""
        response = self.client.get(reverse("profile_list"))
        self.assertRedirects(response, "/")

    @patch("medicSearch.models.Profile.Profile.show_favorites", return_value=["fav1", "fav2"])
    @patch("medicSearch.models.Profile.Profile.show_ratings", return_value=["rate1", "rate2"])
    def test_list_profile_view_with_favorites_and_ratings(self, mock_ratings, mock_favs):
        """Se perfil tem favoritos e ratings deve paginar"""
        self.client.login(username="testuser", password="123456")
        response = self.client.get(reverse("profile_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.profile.user.username)
        self.assertTrue(mock_favs.called)
        self.assertTrue(mock_ratings.called)

    # =======================
    # EDIT PROFILE VIEW
    # =======================
    def test_edit_profile_view_get(self):
        """GET deve carregar os formulários com dados do usuário"""
        self.client.login(username="testuser", password="123456")
        response = self.client.get(reverse("edit_profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testuser")
        self.assertContains(response, "test@example.com")

    def test_edit_profile_view_post_valid(self):
        """POST com dados válidos deve atualizar perfil"""
        self.client.login(username="testuser", password="123456")
        response = self.client.post(reverse("edit_profile"), {
            "username": "newname",
            "email": "new@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "role": self.profile.role,
            "birthday": "1990-01-01"
        }, follow=True)
        self.assertContains(response, "Dados atualizados com sucesso!")
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "newname")
        self.assertEqual(self.user.email, "new@example.com")

    def test_edit_profile_view_post_email_in_use(self):
        """POST com email duplicado deve mostrar warning"""
        # Outro usuário já tem esse email
        self.other_user.email = "duplicate@example.com"
        self.other_user.save()

        self.client.login(username="testuser", password="123456")
        response = self.client.post(reverse("edit_profile"), {
            "username": "testuser",
            "email": "duplicate@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "role": self.profile.role,
            "birthday": "1990-01-01"
        }, follow=True)
        self.assertContains(response, "E-mail já se encontra em uso por outro usuário.")

    def test_edit_profile_view_post_invalid(self):
        """POST inválido deve mostrar erro"""
        self.client.login(username="testuser", password="123456")
        # Envia sem username
        response = self.client.post(reverse("edit_profile"), {
            "username": "",
            "email": "",
            "first_name": "",
            "last_name": "",
        }, follow=True)
        self.assertContains(response, "Dados inválidos.")
