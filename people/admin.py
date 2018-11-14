from django.contrib import admin
from .models import ORMPerson, ORMAuthToken, ORMConfirmationToken, ORMLoginToken, ORMBlock


class PersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'is_email_confirmed')
    search_fields = ('email', )


admin.site.register(ORMPerson, PersonAdmin)


class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ('person', 'access_token', 'refresh_token')
    search_fields = ('person__username', )


admin.site.register(ORMAuthToken, AuthTokenAdmin)


class ConfirmationTokenAdmin(admin.ModelAdmin):
    list_display = ('person', 'token')
    search_fields = ('person__username', )


admin.site.register(ORMConfirmationToken, ConfirmationTokenAdmin)


class LoginTokenAdmin(admin.ModelAdmin):
    list_display = ('person', 'token')
    search_fields = ('person__username', )


admin.site.register(ORMLoginToken, LoginTokenAdmin)


class BlockAdmin(admin.ModelAdmin):
    list_display = ('creator', 'target')
    search_fields = ('creator__username', 'target__username')


admin.site.register(ORMBlock, BlockAdmin)
