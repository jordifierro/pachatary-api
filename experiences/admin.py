from django.contrib import admin
from .models import ORMExperience, ORMSave, ORMFlag
from scenes.factories import create_index_experiences_interactor


class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'saves_count', 'share_id', 'is_deleted')
    search_fields = ('title', 'description')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        create_index_experiences_interactor().set_params(obj.id, obj.id).execute()


admin.site.register(ORMExperience, ExperienceAdmin)


class SaveAdmin(admin.ModelAdmin):
    list_display = ('person', 'experience')
    search_fields = ('person', 'experience')


admin.site.register(ORMSave, SaveAdmin)


class FlagAdmin(admin.ModelAdmin):
    list_display = ('person', 'experience', 'reason', 'is_solved')
    search_fields = ('person', 'experience')


admin.site.register(ORMFlag, FlagAdmin)
