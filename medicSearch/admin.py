from django.contrib import admin
from .models import Profile, Address, City, DayWeek, Speciality, Neighborhood, Rating, State

models = [Profile, Address, City, DayWeek,
          Speciality, Neighborhood, Rating, State]
admin.site.register(models)
