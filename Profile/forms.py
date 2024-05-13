from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User


class PasswordChangingForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}), label='Eski Şifre')
    new_password1 = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}), label='Yeni Şifre')
    new_password2 = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}), label='Yeni Şifre(Tekrar)')

    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']

