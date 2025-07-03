from django.urls import path
from medicSearch.views.ProfileView import list_profile_view, edit_profile_view

urlpatterns = [
    path("", list_profile_view),
    path("<int:id>", list_profile_view, name='profile'),
    path("edit", edit_profile_view, name='edit_profile'),
]
