import json
from datetime import timedelta
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.generic import ListView
from .forms import CommentForm
from HomePage.models import Post
from django.urls import reverse


def post_detail(request, author, slug):
    # PostListView sınıfını kullanarak gönderiyi al
    post_list_view = PostListView()
    queryset = post_list_view.get_queryset()

    # Mevcut gönderiyi al
    post = get_object_or_404(queryset, author__username=author, slug=slug)

    # Gönderiye ait yorumları oluşturulma tarihine göre sırala
    comments = post.comments.all().order_by('-created_at')

    # Formu varsayılan olarak None olarak ayarla
    form = None

    # Kullanıcı kimliği doğrulanmışsa
    if request.user.is_authenticated:
        # İstek POST ise yorumu işle
        if request.method == 'POST':
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()

                # Yorumları güncelleyerek JSON formatında gönder
                comments_data = [{'content': comment.content,
                                  'author': comment.author.username,
                                  'created_at': (comment.created_at + timedelta(hours=3)).strftime("%d/%m/%Y %H:%M:%S")}
                                 for comment in post.comments.all()]
                return JsonResponse({'comments': comments_data, 'topic': post.topic})
        else:
            form = CommentForm()

    # AJAX isteği ile geldiyse, yorumları JSON olarak gönder
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        comments_data = [{'content': comment.content,
                          'author': comment.author.username,
                          'created_at': (comment.created_at + timedelta(hours=3)).strftime("%d/%m/%Y %H:%M:%S")}
                         for comment in comments]
        return JsonResponse({'comments': comments_data, 'topic': post.topic})

    # Diğer durumlarda, gönderiyi ve yorumları render et
    post_list = list(queryset.values('id', 'author__username', 'title', 'content', 'slug', 'likes', 'created_at', 'topic'))
    for post_item in post_list:
        post_item['created_at'] = timezone.localtime(post_item['created_at']).strftime('%d-%m-%Y %H:%M:%S')

    return render(request, 'BaseContent.html',
                  {'post': post, 'comments': comments, 'form': form, 'qs_json': json.dumps(post_list)})


class PostListView(ListView):
    model = Post
    template_name = 'BaseContent.html'
    context_object_name = 'post_list'  # Eğer istenirse, kullanıcı tarafından belirtilen bağlama adını değiştirir

    def get_queryset(self):
        return Post.objects.all()


def create_topic_button(request):
    if request.user.is_authenticated and not request.user.is_superuser:
        return render(request, 'create_topic.html')
    else:
        return redirect('home')


def update_post(request, author, slug):
    # Mevcut gönderiyi al
    post = get_object_or_404(Post, author__username=author, slug=slug)

    if not request.user == post.author:
        return redirect('post_detail', author=author, slug=slug)
    else:
        if request.method == "POST":
            # Form verilerini al
            title = request.POST.get('title')
            content = request.POST.get('content')

            # Gönderiyi güncelle
            post.title = title
            post.content = content
            post.save()

            # Başarı mesajı ekle
            messages.success(request, 'Gönderi başarıyla güncellendi.')

            # Gönderi başarıyla güncellendikten sonra detay sayfasına yönlendir
            return HttpResponseRedirect(reverse('post_detail', args=[author, slug]))

        # POST isteği yoksa, mevcut gönderiyi düzenleme formuyla birlikte göster
        return render(request, 'edit_topic.html', {'post': post})
    