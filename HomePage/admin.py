from django.contrib import admin
from .models import Post


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'likes')  # Görüntülenen sütunlar
    list_filter = ('author', 'created_at')  # Filtreleme için kullanılacak alanlar
    search_fields = ('title', 'content')  # Arama yapılacak alanlar
    prepopulated_fields = {'slug': ('title',)}  # Otomatik slug oluşturma


admin.site.register(Post, PostAdmin)
