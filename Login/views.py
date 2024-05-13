from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import RegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


# Create your views here.
def login_views(request):
    is_login_page = request.path.startswith('/Login/')  # Kayıt sayfasında mıyız?
    next_url = request.GET.get('next', 'home')
    if request.user.is_authenticated:
        # Kullanıcı zaten giriş yapmışsa, en son kaldığı sayfaya yönlendir.
        return redirect(next_url)
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            # Kullanıcı adı veya şifre boş mu diye kontrol et
            if not username or not password:
                messages.error(request, 'Kullanıcı Adı ve Şifre alanları boş olamaz!')
                return render(request, "Login/Login.html", {})
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(next_url)
            else:
                messages.error(request, 'Kullanıcı Adı veya Şifreniz hatalı!')
        return render(request, "Login/Login.html", {"is_login_page": is_login_page})


def logout_user(request):
    logout(request)
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def sign_views(request):
    is_login_page = request.path.startswith('/Login/')
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = RegisterForm()
        if request.method == "POST":
            form = RegisterForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get("username")
                messages.success(request, user + " için hesap oluşturuldu")
                return redirect('login')  # Kayıt işlemi başarılıysa giriş sayfasına yönlendir
        context = {"form": form, "is_login_page": is_login_page}
        return render(request, "Login/Register.html", context)
