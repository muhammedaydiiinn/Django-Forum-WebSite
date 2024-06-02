from django import forms
from HomePage.models import Post


class NewContentForm(forms.Form):
    topic_title = forms.CharField(max_length=100)
    topic_content = forms.CharField(widget=forms.Textarea(attrs={'rows': 7}))

    class Meta:
        model = Post
        fields = ['title', 'content']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['author', 'title', 'content', 'likes', 'slug', 'topic']  # Tüm alanları dahil edin

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].disabled = True  # slug alanını devre dışı bırakın
