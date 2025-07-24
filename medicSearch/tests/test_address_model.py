from django.test import TestCase
from medicSearch.models import Address, Neighborhood
from datetime import time


class AddressModelTest(TestCase):
    def setUp(self):
        # Cria um Neighborhood fake para satisfazer FK
        self.neighborhood = Neighborhood.objects.create(name="Centro")

        self.address = Address.objects.create(
            neighborhood=self.neighborhood,
            name="Clínica Teste",
            address="Rua Principal, 123",
            latitude=-22.1234567,
            longitude=-43.7654321,
            opening_time=time(8, 0),
            closing_time=time(18, 0),
            phone="(21) 99999-9999",
            status=True
        )

    def test_str_returns_name(self):
        """O método __str__ deve retornar o nome do endereço"""
        self.assertEqual(str(self.address), "Clínica Teste")
