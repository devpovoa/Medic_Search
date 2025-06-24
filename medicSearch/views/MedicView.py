from django.shortcuts import render
from medicSearch.models import Profile
from django.db.models import Q
from django.core.paginator import Paginator


def list_medics_view(request):
    name = request.GET.get("name")
    speciality = request.GET.get("speciality")
    neighborhood = request.GET.get("neighborhood")
    city = request.GET.get("city")
    state = request.GET.get("state")

    medics = Profile.objects

    # Aqui aplicamos uma consulta SQL.
    if name is not None and name != '':
        medics = medics.filter(Q(user__first_name__contains=name) | Q(
            user__username__contains=name))

    if speciality is not None:
        medics = medics.filter(specialties__id=speciality)

    if neighborhood is not None:
        medics = medics.filter(addresses__neighborhood__id=neighborhood)
    else:
        if city is not None:
            medics = medics.filter(addresses__neighborhood__city__id=city)
        elif state is not None:
            medics = medics.filter(addresses__neighborhood__city__state__id=state)

    if len(medics) > 0:
        paginator = Paginator(medics, 8)
        page = request.GET.get("page")
        medics = paginator.get_page(page)

    get_copy = request.GET.copy()
    parameters = get_copy.pop("page", True) and get_copy.urlencode()

    context = {
        'medics': medics,
        'parameters': parameters,
    }

    return render(request, template_name='medic/medics.html', context=context, status=200)
