from django.contrib import admin
from .models import ORMProfile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('person', 'username', 'bio')
    search_fields = ('person', 'username')


admin.site.register(ORMProfile, ProfileAdmin)
