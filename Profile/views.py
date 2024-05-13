from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from Content.models import Comment, Like
from HomePage.models import Post
from .forms import PasswordChangingForm


# Create your views here.
def view_profile(request):
    if request.user.is_authenticated:
        is_profile_page = request.path.startswith('/profile/')
        user = request.user
        form = PasswordChangingForm(user=user)
        if request.method == 'POST':
            form = PasswordChangingForm(user=request.user, data=request.POST)
            if form.is_valid():
                form.save()
                # Form başarıyla kaydedildi, ancak çıkış yapmayacağız
                return JsonResponse({'success': True})
        return render(request, 'base_profile.html', {'form': form})
    else:
        return HttpResponseRedirect(reverse('login'))


def update_profile_picture(request):
    if request.user.is_authenticated:
        if request.method == 'POST' and request.FILES.get('profile_pic'):
            profile = request.user.profile
            profile.profile_pic = request.FILES['profile_pic']
            profile.save()
            return JsonResponse({'message': 'Profil resmi güncellendi.'})
        else:
            return JsonResponse({'error': 'Profil resmi güncelleme işlemi başarısız.'}, status=400)
    else:
        return redirect('login')


def update_profile(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            # Formdan gelen verileri al
            username = request.POST.get('username')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')

            # Kullanıcı bilgilerini güncelle
            request.user.username = username
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.email = email
            request.user.save()

            # Başarı mesajı gönder
            return JsonResponse({'message': 'Profil bilgileriniz başarıyla güncellendi.'})

        else:
            # POST request gelmezse hata mesajı gönder
            return JsonResponse({'error': 'POST request bekleniyor.'}, status=400)
    else:
        return redirect('login')


def my_topics(request):
    if request.user.is_authenticated:
        # Oturum açmış kullanıcının gönderilerini çek
        posts = Post.objects.filter(author=request.user)

        # Oturum açmış kullanıcının yorumlarını çek ve her yorumun hangi gönderiye ait olduğunu döndür
        comments_with_posts = [(comment, comment.post) for comment in Comment.objects.filter(author=request.user)]

        likes_with_posts = [(like, like.post) for like in Like.objects.filter(user=request.user)]

        return render(request, 'my_topic.html', {'posts': posts, 'comments_with_posts': comments_with_posts,
                                                 'likes_with_posts': likes_with_posts})
    else:
        return redirect('login')
