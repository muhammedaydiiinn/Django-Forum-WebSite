import json
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from .models import Post
from .forms import NewContentForm
from django.http import JsonResponse
from Content.models import Like
from django.utils import timezone
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification


def home_view(request):
    # Sorguyu al
    queryset = Post.objects.all()

    # En popüler 8 gönderiyi al
    popular_posts = queryset.order_by('-likes')[:8]

    # En yeni 8 gönderiyi al
    newest_posts_page = queryset.order_by('-created_at')[:8]
    newest_posts = queryset.order_by('-created_at')[:5]

    # Zamanı biçimlendir ve JSON'a dönüştür
    post_list = list(
        newest_posts.values('id', 'author__username', 'title', 'content', 'slug', 'likes', 'created_at', 'topic'))
    for post in post_list:
        post['created_at'] = timezone.localtime(post['created_at']).strftime('%Y-%m-%d %H:%M:%S')

    # Mevcut konuları alın
    topics = Post.objects.values('topic').distinct()

    # JSON verisini ana bağlama ekleyin
    context = {
        'popular_posts': popular_posts,
        'newest_posts': newest_posts_page,
        'qs_json': json.dumps(post_list),
        'topics': topics,
    }

    # Arama sonuçlarını kontrol et
    searched_posts = None
    if 'searched_posts' in request.session:
        searched_posts = request.session.pop('searched_posts')

    # Arama sonuçlarını ana bağlama ekleyin
    context['searched_posts'] = searched_posts

    # render fonksiyonu ile template'i döndür
    return render(request, "Home/Home_Page.html", context)


class TopicPostsView(ListView):
    model = Post
    template_name = 'Home/TopicContent.html'
    context_object_name = 'posts'

    def get_queryset(self):
        # Konuya göre gönderileri getir
        topic = self.kwargs.get('topic')
        return Post.objects.filter(topic=topic)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Konu adını ve tüm konuları içeren bir bağlam oluştur
        context['topic_name'] = self.kwargs.get('topic')
        context['topics'] = Post.objects.values('topic').distinct()

        # Tüm postların JSON temsili için post_list oluştur
        queryset = self.get_queryset()
        post_list = list(
            queryset.values('id', 'author__username', 'title', 'content', 'slug', 'likes', 'created_at', 'topic'))
        for post_item in post_list:
            post_item['created_at'] = timezone.localtime(post_item['created_at']).strftime('%d-%m-%Y %H:%M:%S')
        context['qs_json'] = json.dumps(post_list)

        return context


def search_view(request):
    queryset = Post.objects.all()
    newest_posts = queryset.order_by('-created_at')[:5]
    post_list = list(newest_posts.values('id', 'author__username', 'title', 'content', 'slug', 'likes', 'created_at'))
    for post in post_list:
        post['created_at'] = timezone.localtime(post['created_at']).strftime('%d-%m-%Y %H:%M:%S')

    searched = request.POST.get('searched', '')
    searched_posts = Post.objects.filter(title__icontains=searched) | Post.objects.filter(content__icontains=searched)

    context = {'searched_posts': searched_posts, 'searched': searched, 'qs_json': json.dumps(post_list)}
    return render(request, 'Home/searchPage.html', context)


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

            # Metin sınıflandırma modellerini yükleme
            tokenizer1 = AutoTokenizer.from_pretrained("gurkan08/bert-turkish-text-classification")
            model1 = AutoModelForSequenceClassification.from_pretrained("gurkan08/bert-turkish-text-classification")
            nlp1 = pipeline("sentiment-analysis", model=model1, tokenizer=tokenizer1)

            tokenizer2 = AutoTokenizer.from_pretrained("savasy/bert-turkish-text-classification")
            model2 = AutoModelForSequenceClassification.from_pretrained("savasy/bert-turkish-text-classification")
            nlp2 = pipeline("sentiment-analysis", model=model2, tokenizer=tokenizer2)

            # Metni sınıflandırma
            result1 = nlp1(topic_content)
            result2 = nlp2(topic_content)

            # Tahmin edilen konuları birleştir
            label_dict1 = {
                'ekonomi': 'economy',
                'spor': 'sport',
                'saglik': 'health',
                'kultur_sanat': 'culture',
                'bilim_teknoloji': 'technology',
                'egitim': 'education'
            }
            label_dict2 = {
                'world': 'dünya',
                'economy': 'ekonomi',
                'culture': 'kültür',
                'health': 'sağlık',
                'politics': 'siyaset',
                'sport': 'spor',
                'technology': 'teknoloji'
            }

            topic_scores = {}
            for result in result1:
                label1 = label_dict1.get(result['label'], 'Bilinmeyen')
                topic_scores[label1] = topic_scores.get(label1, 0) + result['score']

            for result in result2:
                label2 = label_dict2.get(result['label'], 'Bilinmeyen')
                topic_scores[label2] = topic_scores.get(label2, 0) + result['score']

            # En yüksek skora sahip konuyu al
            max_score = max(topic_scores.values())
            predicted_label = [label for label, score in topic_scores.items() if score == max_score][0]

            # Yeni konuyu oluştur
            new_topic = Post(title=topic_title, content=topic_content, author=request.user, topic=predicted_label)
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
