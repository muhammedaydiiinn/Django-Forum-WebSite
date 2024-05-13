import json
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from .models import Post
from .forms import NewContentForm
from django.http import JsonResponse
from Content.models import Like
from django.utils import timezone


def home_view(request):
    # Sorguyu al
    queryset = Post.objects.all()

    # En popüler 8 gönderiyi al
    popular_posts = queryset.order_by('-likes')[:8]

    # En yeni 8 gönderiyi al
    newest_posts_page = queryset.order_by('-created_at')[:8]
    newest_posts = queryset.order_by('-created_at')[:5]

    # Zamanı biçimlendir ve JSON'a dönüştür
    post_list = list(newest_posts.values('id', 'author__username', 'title', 'content', 'slug', 'likes', 'created_at'))
    for post in post_list:
        post['created_at'] = timezone.localtime(post['created_at']).strftime('%Y-%m-%d %H:%M:%S')

    # JSON verisini ana bağlama ekleyin
    context = {
        'popular_posts': popular_posts,
        'newest_posts': newest_posts_page,
        'qs_json': json.dumps(post_list)
    }

    # Arama sonuçlarını kontrol et
    searched_posts = None
    if 'searched_posts' in request.session:
        searched_posts = request.session.pop('searched_posts')

    # Arama sonuçlarını ana bağlama ekleyin
    context['searched_posts'] = searched_posts

    # render fonksiyonu ile template'i döndür
    return render(request, "Home/Home_Page.html", context)


class PostListView(ListView):
    model = Post
    template_name = 'Home/Home_Page.html'
    context_object_name = 'post_list'  # Eğer istenirse, kullanıcı tarafından belirtilen bağlama adını değiştirir

    def get_queryset(self):
        return Post.objects.all()


def create_topic(request):
    if request.method == 'POST':
        forms = NewContentForm(request.POST)
        if forms.is_valid():
            topic_title = forms.cleaned_data['topic_title']
            topic_content = forms.cleaned_data['topic_content']
            new_topic = Post(title=topic_title, content=topic_content, author=request.user)
            new_topic.save()
            return redirect('post_detail', author=request.user.username, slug=new_topic.slug)
    else:
        forms = NewContentForm()
    return render(request, 'create_topic.html', {'form': forms})


def increase_likes(request, author, slug):
    post = get_object_or_404(Post, author__username=author, slug=slug)
    user = request.user
    liked = False
    try:
        # Eğer kullanıcı bu gönderiyi zaten beğenmişse, beğeniyi sil
        like = Like.objects.get(user=user, post=post)
        like.delete()
    except Like.DoesNotExist:
        # Eğer kullanıcı bu gönderiyi daha önce beğenmemişse, beğeni oluştur
        like = Like(user=user, post=post)
        like.save()
        liked = True

    # Post modelindeki beğeni sayısını güncelle
    post.likes = post.like_set.count()
    post.save()

    return JsonResponse({'liked': liked, 'likes': post.likes})


def check_like_status(request, author, slug):
    # Gönderiyi al
    post = get_object_or_404(Post, author__username=author, slug=slug)

    # Eğer kullanıcı kimlik doğrulaması yapılmışsa
    if request.user.is_authenticated:
        # Kullanıcının belirli bir gönderiyi beğenip beğenmediğini kontrol et
        liked = Like.objects.filter(user=request.user, post=post).exists()
    else:
        liked = False

    return JsonResponse({'liked': liked})


def profile_image_view(request):
    profile_image_url = request.user.profile.profile_pic.url
    return JsonResponse({'profile_pic_url': profile_image_url})


def search_view(request):
    queryset = Post.objects.all()
    newest_posts = queryset.order_by('-created_at')[:5]
    post_list = list(newest_posts.values('id', 'author__username', 'title', 'content', 'slug', 'likes', 'created_at'))
    for post in post_list:
        post['created_at'] = timezone.localtime(post['created_at']).strftime('%Y-%m-%d %H:%M:%S')

    searched = request.POST.get('searched', '')
    # Kelimeye göre gönderileri filtrele
    searched_posts = Post.objects.filter(title__icontains=searched) | Post.objects.filter(content__icontains=searched)

    # JSON verisini de döndür
    context = {'searched_posts': searched_posts, 'searched': searched, 'qs_json': json.dumps(post_list)}
    return render(request, 'Home/searchPage.html', context)
