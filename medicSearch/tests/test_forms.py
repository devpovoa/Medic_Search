from django.test import TestCase
from django.contrib.auth.models import User
from medicSearch.models import Profile
from medicSearch.forms.UserProfileForm import UserProfileForm, UserForm 
from datetime import date


class UserProfileFormTest(TestCase):
    def setUp(self):
        # Cria usuário
        self.user = User.objects.create_user(username="testuser", password="12345")
        
        # Recupera o Profile gerado pelo sinal
        self.profile_admin = self.user.profile
        self.profile_admin.role = 1  # Admin
        self.profile_admin.birthday = date(1990, 1, 1)
        self.profile_admin.save()

        # Outro Profile como Médico (role=2)
        self.user_medic = User.objects.create_user(username="medicuser", password="12345")
        self.profile_medic = self.user_medic.profile
        self.profile_medic.role = 2  # Médico
        self.profile_medic.save()

    def test_role_field_visible_for_admin(self):
        """Se role == 1 (Admin), o campo 'role' deve estar presente no formulário"""
        form = UserProfileForm(instance=self.profile_admin)
        self.assertIn('role', form.fields)

    def test_role_field_removed_for_non_admin(self):
        """Se role != 1, o campo 'role' deve ser removido do formulário"""
        form = UserProfileForm(instance=self.profile_medic)
        self.assertNotIn('role', form.fields)

    def test_widgets_applied_correctly(self):
        """Widgets definidos na Meta devem estar corretos"""
        form = UserProfileForm(instance=self.profile_admin)

        # Verifica se os widgets possuem as classes corretas
        self.assertIsInstance(form.fields['birthday'].widget, type(form.Meta.widgets['birthday']))
        self.assertIn('class', form.fields['birthday'].widget.attrs)
        self.assertIn('form-control', form.fields['birthday'].widget.attrs['class'])

        self.assertIsInstance(form.fields['image'].widget, type(form.Meta.widgets['image']))
        self.assertIn('form-control', form.fields['image'].widget.attrs['class'])


class UserFormTest(TestCase):
    def test_user_form_widgets_and_validation(self):
        """UserForm deve ter widgets corretos e ser válido com dados válidos"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User'
        }
        form = UserForm(data=form_data)

        # Deve ser válido com dados corretos
        self.assertTrue(form.is_valid())

        # Verifica widgets
        self.assertIsInstance(form.fields['username'].widget, type(form.Meta.widgets['username']))
        self.assertIn('form-control', form.fields['username'].widget.attrs['class'])

        self.assertIsInstance(form.fields['email'].widget, type(form.Meta.widgets['email']))
        self.assertIn('form-control', form.fields['email'].widget.attrs['class'])

        self.assertIsInstance(form.fields['first_name'].widget, type(form.Meta.widgets['first_name']))
        self.assertIn('form-control', form.fields['first_name'].widget.attrs['class'])

        self.assertIsInstance(form.fields['last_name'].widget, type(form.Meta.widgets['last_name']))
        self.assertIn('form-control', form.fields['last_name'].widget.attrs['class'])
