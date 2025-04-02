from django.contrib import admin
from . import models



@admin.register(models.Todo)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'start_date', 'end_date', 'completed', 'created_at'] 