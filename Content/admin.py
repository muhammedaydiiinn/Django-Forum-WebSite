from django.contrib import admin
from .models import Comment, Like


class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at')  # Görüntülenen sütunlar
    search_fields = ('author__username', 'post__title', 'content')  # Arama yapılacak alanlar
    list_filter = ('created_at',)  # Filtreleme için kullanılacak alanlar


class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'liked_at')  # Görüntülenen sütunlar
    search_fields = ('user__username', 'post__title')  # Arama yapılacak alanlar
    list_filter = ('liked_at',)  # Filtreleme için kullanılacak alanlar


admin.site.register(Comment, CommentAdmin)
admin.site.register(Like, LikeAdmin)
