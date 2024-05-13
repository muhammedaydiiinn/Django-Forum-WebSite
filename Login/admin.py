from django.contrib import admin
from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_pic')  # Görüntülenen sütunlar


admin.site.register(Profile, ProfileAdmin)
