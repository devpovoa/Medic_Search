from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import transaction, IntegrityError

from medicSearch.models import Profile, Rating


class MedicViewFullCoverageTests(TestCase):
    def setUp(self):
        """Cria paciente autenticado e um médico para simular listagem/favoritos/avaliações"""
        try:
            with transaction.atomic():
                # Usuário que será o paciente (logado)
                self.user = User.objects.create_user(
                    username='paciente',
                    password='123456',
                    first_name='João'
                )
                self.profile = Profile.objects.get(user=self.user)
                self.profile.role = 2
                self.profile.save()

                # Outro usuário que será o médico
                self.medic_user = User.objects.create_user(
                    username='dr.maria',
                    password='123456',
                    first_name='Maria'
                )
                self.medic_profile = Profile.objects.get(user=self.medic_user)
                self.medic_profile.role = 2
                self.medic_profile.save()

        except IntegrityError as e:
            print(f"Erro ao criar usuário: {e}")

        self.client = Client(enforce_csrf_checks=False)

    # ---------------------------
    # LISTAGEM DE MÉDICOS
    # ---------------------------
    def test_list_medics_basic(self):
        """Caminho sem filtros"""
        response = self.client.get(reverse('medics'))
        self.assertEqual(response.status_code, 200)
        # Verifica texto que aparece no HTML
        self.assertContains(response, 'Foram encontrados')

    def test_list_medics_with_name_filter(self):
        """Filtro por nome"""
        response = self.client.get(reverse('medics'), {'name': 'Maria'})
        self.assertEqual(response.status_code, 200)

    def test_list_medics_with_speciality(self):
        """Filtro por speciality"""
        response = self.client.get(reverse('medics'), {'speciality': '1'})
        self.assertEqual(response.status_code, 200)

    def test_list_medics_with_neighborhood(self):
        """Filtro por neighborhood"""
        response = self.client.get(reverse('medics'), {'neighborhood': '10'})
        self.assertEqual(response.status_code, 200)

    def test_list_medics_with_city_and_state(self):
        """Força caminhos alternativos city/state"""
        # city
        response = self.client.get(reverse('medics'), {'city': '1'})
        self.assertEqual(response.status_code, 200)
        # state
        response = self.client.get(reverse('medics'), {'state': '2'})
        self.assertEqual(response.status_code, 200)

    def test_list_medics_pagination(self):
        """Força paginação com page=1"""
        # Cria mais médicos para ativar o paginator
        for i in range(10):
            u = User.objects.create_user(username=f'dr{i}', password='123')
            Profile.objects.get(user=u).save()

        response = self.client.get(reverse('medics'), {'page': 2})
        self.assertEqual(response.status_code, 200)

    # ---------------------------
    # ADICIONAR FAVORITO
    # ---------------------------
    def test_add_favorite_success(self):
        """Adiciona médico como favorito com sucesso"""
        self.client.login(username='paciente', password='123456')
        response = self.client.post(reverse('medic-favorite'), {
            'page': 1,
            'id': self.medic_user.id,
            'name': 'Maria',
            'speciality': 'Cardio',
            'neighborhood': '123',
            'city': '456',
            'state': '789'
        })
        self.assertEqual(response.status_code, 302)
        # Corrigido: a view usa ! literal, não %21
        self.assertIn('msg=Favorito%20adicionado%20com%20sucesso!', response.url)
        self.assertIn('type=success', response.url)


    def test_add_favorite_exception(self):
        """Força exceção removendo profile do paciente"""
        self.client.login(username='paciente', password='123456')
        self.profile.delete()  # agora Profile.objects.filter(user=request.user).first() será None
        response = self.client.post(reverse('medic-favorite'), {'id': 999})
        self.assertEqual(response.status_code, 302)
        self.assertIn('erro', response.url.lower())

    # ---------------------------
    # REMOVER FAVORITO
    # ---------------------------
    def test_remove_favorite_success(self):
        """Remove médico favorito"""
        self.client.login(username='paciente', password='123456')
        # Adiciona favorito primeiro
        self.profile.favorites.add(self.medic_user)
        response = self.client.post(reverse('medic-favorite-remove'), {
            'page': 2,
            'id': self.medic_user.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('/profile/?page=2', response.url)

    def test_remove_favorite_exception(self):
        """Força exceção removendo profile antes"""
        self.client.login(username='paciente', password='123456')
        self.profile.delete()
        response = self.client.post(reverse('medic-favorite-remove'), {'id': 999})
        self.assertEqual(response.status_code, 302)
        self.assertIn('erro', response.url.lower())

    # ---------------------------
    # AVALIAR MÉDICO
    # ---------------------------
    def test_rate_medic_get(self):
        """Acessa formulário via GET"""
        self.client.login(username='paciente', password='123456')
        response = self.client.get(reverse('rate-medic', args=[self.medic_user.id]))
        self.assertEqual(response.status_code, 200)
        # Verifica se o campo "value" aparece no HTML
        self.assertContains(response, 'name="value"')

    def test_rate_medic_post_valid(self):
        """POST válido salva avaliação"""
        self.client.login(username='paciente', password='123456')

        response = self.client.post(
            reverse('rate-medic', args=[self.medic_user.id]),
            {
                'user': self.user.id,             # hidden obrigatório
                'user_rated': self.medic_user.id, # hidden obrigatório
                'value': 5,                       # nota
                'opinion': 'Ótimo médico!'        # opinião
            }
        )

        self.assertEqual(response.status_code, 200)
        # Com os 4 campos o form é válido e salva, então gera mensagem de sucesso
        self.assertContains(response, 'Avaliação salva com sucesso')

        # Confirma que realmente salvou no banco
        rating = Rating.objects.filter(user=self.user, user_rated=self.medic_user).first()
        self.assertIsNotNone(rating)

    def test_rate_medic_post_invalid(self):
        """POST inválido gera mensagem de erro"""
        self.client.login(username='paciente', password='123456')
        # Form inválido: value vazio
        response = self.client.post(reverse('rate-medic', args=[self.medic_user.id]), {
            'value': ''  # inválido
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Erro ao salvar avaliação')
