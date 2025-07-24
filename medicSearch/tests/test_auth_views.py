from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from medicSearch.models import Profile
from unittest.mock import patch
from django.utils.crypto import get_random_string


class AuthViewsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="123456"
        )
        self.profile = self.user.profile
        self.profile.save()

    # =======================
    # LOGIN
    # =======================
    def test_login_view_get(self):
        """GET deve retornar 200 e exibir formulário"""
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login")

    def test_login_authenticated_redirects(self):
        """Se já está logado deve redirecionar para '/'"""
        self.client.login(username="testuser", password="123456")
        response = self.client.get("/login/")
        self.assertRedirects(response, "/")

    def test_login_valid_credentials(self):
        """POST com credenciais válidas deve logar e redirecionar"""
        response = self.client.post(
            "/login/",
            {"username": "testuser", "password": "123456"},
        )
        self.assertEqual(response.status_code, 302)  # redireciona
        self.assertEqual(response.url, "/")

    def test_login_invalid_credentials(self):
        """POST com senha errada deve mostrar mensagem de erro"""
        response = self.client.post(
            "/login/",
            {"username": "testuser", "password": "wrongpass"},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dados de usuário incorretos")

    # =======================
    # LOGOUT
    # =======================
    def test_logout_view_redirects_to_login(self):
        """Logout deve redirecionar para login"""
        self.client.login(username="testuser", password="123456")
        response = self.client.get("/logout/")
        self.assertRedirects(response, "/login/")

    # =======================
    # REGISTER
    # =======================
    def test_register_view_get(self):
        """GET deve retornar 200"""
        response = self.client.get("/register/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Registrar")

    def test_register_user_already_exists(self):
        """Se username já existe deve mostrar erro"""
        response = self.client.post(
            "/register/",
            {
                "username": "testuser",
                "email": "new@example.com",
                "password": "123456",
            },
            follow=True,
        )
        self.assertContains(response, "Já existe um usuário com este username")

    def test_register_email_already_exists(self):
        """Se email já existe deve mostrar erro"""
        response = self.client.post(
            "/register/",
            {
                "username": "newuser",
                "email": "test@example.com",
                "password": "123456",
            },
            follow=True,
        )
        self.assertContains(response, "Já existe um usuário com este email")

    def test_register_new_user_success(self):
        """Se username e email são novos deve criar usuário"""
        response = self.client.post(
            "/register/",
            {
                "username": "newuser",
                "email": "new@example.com",
                "password": "123456",
            },
            follow=True,
        )
        self.assertContains(response, "Conta criada com sucesso")

    # =======================
    # RECOVERY
    # =======================
    def test_recover_view_get(self):
        """GET deve retornar 200"""
        response = self.client.get("/recovery/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recuperar senha")

    def test_recover_view_invalid_form(self):
        """Se enviar form vazio deve retornar erro"""
        response = self.client.post("/recovery/", {}, follow=True)
        self.assertContains(response, "Formulário inválido")

    def test_recover_view_invalid_email(self):
        """Se email não existe deve retornar erro"""
        response = self.client.post(
            "/recovery/", {"email": "wrong@example.com"}, follow=True
        )
        self.assertContains(response, "E-mail inexistente.")

    @patch("medicSearch.views.AuthView.send_mail", return_value=1)
    def test_recover_view_valid_email(self, mock_send_mail):
        # Garante que email está salvo
        self.user.email = "test@example.com"
        self.user.save()

        response = self.client.post("/recovery/", {"email": "test@example.com"}, follow=True)

        # Deve mostrar mensagem de sucesso
        self.assertContains(response, "Um e-mail foi enviado para sua caixa de entrada.")
        # Deve ter chamado send_mail
        self.assertTrue(mock_send_mail.called)



    # =======================
    # CHANGE PASSWORD
    # =======================
    def test_change_password_invalid_token(self):
        """Se token inválido deve mostrar mensagem"""
        response = self.client.get("/change-password/invalidtoken/", follow=True)
        self.assertContains(response, "Token inválido")

    def test_change_password_with_valid_token(self):
        """Se token válido e senha correta deve alterar senha"""
        self.profile.token = "validtoken"
        self.profile.save()

        response = self.client.post(
            "/change-password/validtoken/",
            {"password": "newpass123"},
            follow=True,
        )

        self.assertContains(response, "Senha alterada com sucesso!")
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpass123"))


    def test_change_password_invalid_form(self):
        """Token válido mas form inválido (sem senha)"""
        self.profile.token = "validtoken2"
        self.profile.save()
        response = self.client.post(
            "/change-password/validtoken2/", {}, follow=True
        )
        # Não deve quebrar, mas deve continuar renderizando a página
        self.assertIn(response.status_code, [200, 302])
