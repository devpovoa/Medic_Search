from django.shortcuts import render, redirect, get_object_or_404
from medicSearch.models.Profile import Profile
from django.core.paginator import Paginator
from medicSearch.forms.UserProfileForm import UserProfileForm, UserForm
from django.contrib.auth.decorators import login_required

def list_profile_view(request, id=None):
    profile = None

    # Seleciona o perfil
    if id is None and request.user.is_authenticated:
        profile = Profile.objects.filter(user=request.user).first()
    elif id is not None:
        profile = Profile.objects.filter(user__id=id).first()
    elif not request.user.is_authenticated:
        return redirect("/")

    # Se não encontrou perfil → redireciona
    if not profile:
        return redirect("/")

    # Helper para funcionar com QuerySet real ou lista mockada
    def has_results(data):
        if hasattr(data, "exists"):  # é QuerySet
            return data.exists()
        return bool(data)  # é lista mockada nos testes

    # Carrega favoritos
    favorites_raw = profile.show_favorites()
    if has_results(favorites_raw):
        paginator = Paginator(favorites_raw, 8)
        favorites = paginator.get_page(request.GET.get("page"))
    else:
        favorites = favorites_raw

    # Carrega avaliações
    ratings_raw = profile.show_ratings()
    if has_results(ratings_raw):
        paginator = Paginator(ratings_raw, 8)
        ratings = paginator.get_page(request.GET.get("page"))
    else:
        ratings = ratings_raw

    context = {
        "profile": profile,
        "favorites": favorites,
        "ratings": ratings,
    }
    return render(request, "profile/profile.html", context=context, status=200)


@login_required
def edit_profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    message = None

    if request.method == 'POST':
        profileForm = UserProfileForm(request.POST, request.FILES, instance=profile)
        userForm = UserForm(request.POST, instance=request.user)

        # Verifica se o e-mail já está em uso por outro usuário
        verifyEmail = Profile.objects.filter(user__email=request.POST['email']).exclude(user=request.user).first()
        emailUnused = verifyEmail is None

        if profileForm.is_valid() and userForm.is_valid() and emailUnused:
            profileForm.save()
            userForm.save()
            message = {'type': 'success', 'text': 'Dados atualizados com sucesso!'}
        else:
            
            if not emailUnused:
                message = {'type': 'warning', 'text': 'E-mail já se encontra em uso por outro usuário.'}
            else:
                message = {'type': 'danger', 'text': 'Dados inválidos.'}
    else:
        profileForm = UserProfileForm(instance=profile)
        userForm = UserForm(instance=request.user)

    context = {
        'profileForm': profileForm,
        'userForm': userForm,
        'message': message,
    }
    return render(request, template_name='user/profile.html', context=context, status=200)

