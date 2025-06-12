from django.contrib import admin
from .models import Profile, Address, City, DayWeek, Speciality, Neighborhood, Rating, State


class ProfileAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ('user', 'user_status', 'role', 'birth',
                    'specialtiesList', 'addressesList', )
    list_display_links = ('user', 'role',)
    list_filter = ('user__is_active', 'role',)
    # fields = ('user', ('role',), 'image', 'birthday',
    #           'specialties', 'addresses',)
    exclude = ('favorites', 'created_at', 'updated_at',)
    # readonly_fields = ('user',)
    search_fields = ('user__username',)

    fieldsets = (
        ('Usuário', {
         'fields': ('user', 'birthday', 'image',)
         }),
        ('Função', {
         'fields': ('role',)
         }),
        ('Extras', {
         'fields': ('specialties', 'addresses')
         }),
    )

    def user_status(self, obj):
        return obj.user.is_active
    user_status.boolean = True
    user_status.short_description = 'Status'

    def birth(self, obj):
        # if obj.birthday:
        return obj.birthday.strftime("%d/%m/%Y") if obj.birthday else "___/___/_____"
    # birth.empty_value_display = '___/___/_____'

    def specialtiesList(self, obj):
        return ", ".join([i.name for i in obj.specialties.all()])
    specialtiesList.short_description = 'Specialties'

    def addressesList(self, obj):
        return ", ".join([i.name for i in obj.addresses.all()])
    addressesList.short_description = 'Addresses'

    class Media:
        css = {
            "all": ("css/custom.css",)
        }
        js = ("js/custom.js",)


admin_models = [Address, City, DayWeek,
                Speciality, Neighborhood, Rating, State]

admin.site.register(Profile, ProfileAdmin)
admin.site.register(admin_models)
