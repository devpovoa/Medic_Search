from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from datetime import date, time
from medicSearch.models import Profile, Speciality, Address
from medicSearch.admin import ProfileAdmin


class ProfileAdminTest(TestCase):
    def setUp(self):
        # Cria usuário (gera Profile automaticamente pelo sinal)
        self.user = User.objects.create_user(
            username="testuser",
            password="12345",
            is_active=True
        )

        # Reutiliza o Profile criado automaticamente
        self.profile = self.user.profile
        self.profile.role = 2  # Médico
        self.profile.birthday = date(1990, 1, 1)
        self.profile.save()

        # Cria objetos para ManyToMany
        self.spec1 = Speciality.objects.create(name="Cardiology")
        self.spec2 = Speciality.objects.create(name="Dermatology")
        # Cria objetos para ManyToMany com latitude/longitude obrigatórios
        self.addr1 = Address.objects.create(
            name="Main Street 123",
            latitude=-22.12345,
            longitude=-43.98765,
            opening_time=time(8, 0),
            closing_time=time(18, 0)
        )
        self.addr2 = Address.objects.create(
            name="Second Avenue 456",
            latitude=-22.54321,
            longitude=-43.12345,
            opening_time=time(9, 0),
            closing_time=time(17, 0)
        )


        # Instancia o Admin
        self.site = AdminSite()
        self.admin = ProfileAdmin(Profile, self.site)

    # ========================
    # user_status
    # ========================
    def test_user_status_active(self):
        """Deve retornar True se o usuário está ativo"""
        self.assertTrue(self.admin.user_status(self.profile))

    def test_user_status_inactive(self):
        """Deve retornar False se o usuário está inativo"""
        self.user.is_active = False
        self.user.save()
        self.assertFalse(self.admin.user_status(self.profile))

    # ========================
    # birth
    # ========================
    def test_birth_with_date(self):
        """Deve formatar a data corretamente"""
        self.assertEqual(self.admin.birth(self.profile), "01/01/1990")

    def test_birth_without_date(self):
        """Deve retornar placeholder se não tiver data"""
        self.profile.birthday = None
        self.profile.save()
        self.assertEqual(self.admin.birth(self.profile), "___/___/_____")

    # ========================
    # specialtiesList
    # ========================
    def test_specialties_list_with_items(self):
        """Deve retornar nomes das especialidades separados por vírgula"""
        self.profile.specialties.add(self.spec1, self.spec2)
        result = self.admin.specialtiesList(self.profile)
        self.assertIn("Cardiology", result)
        self.assertIn("Dermatology", result)
        self.assertEqual(result, "Cardiology, Dermatology")

    def test_specialties_list_empty(self):
        """Deve retornar string vazia se não houver especialidades"""
        result = self.admin.specialtiesList(self.profile)
        self.assertEqual(result, "")

    # ========================
    # addressesList
    # ========================
    def test_addresses_list_with_items(self):
        """Deve retornar endereços separados por vírgula"""
        self.profile.addresses.add(self.addr1, self.addr2)
        result = self.admin.addressesList(self.profile)
        self.assertIn("Main Street 123", result)
        self.assertIn("Second Avenue 456", result)
        self.assertEqual(result, "Main Street 123, Second Avenue 456")

    def test_addresses_list_empty(self):
        """Deve retornar string vazia se não houver endereços"""
        result = self.admin.addressesList(self.profile)
        self.assertEqual(result, "")
