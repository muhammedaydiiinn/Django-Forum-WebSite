from django.contrib import admin
from .models import Post
from .forms import PostForm  # Özel formunuzu içe aktarın

class PostAdmin(admin.ModelAdmin):
    form = PostForm  # Özel formu belirtin
    list_display = ('title', 'author', 'created_at', 'likes', 'slug')  # Görüntülenen sütunlar
    list_filter = ('author', 'created_at')  # Filtreleme için kullanılacak alanlar
    search_fields = ('title', 'content')  # Arama yapılacak alanlar
    prepopulated_fields = {'slug': ('title',)}  # Otomatik slug oluşturma

admin.site.register(Post, PostAdmin)
