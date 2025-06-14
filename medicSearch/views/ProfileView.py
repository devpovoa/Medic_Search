from django.http import HttpResponse


def list_profile_view(request, _id=None):
    if _id is None and request.user.is_authenticated:
        _id = request.user.id
    elif not request.user.is_authenticated:
        _id = 0
    return HttpResponse('<h1>Usuário de id %s!</h1>' % _id)
