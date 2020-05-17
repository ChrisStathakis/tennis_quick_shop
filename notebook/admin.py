from django.contrib import admin

from .models import Tags, NoteBook


@admin.register(Tags)
class TagAdmin(admin.ModelAdmin):
    pass