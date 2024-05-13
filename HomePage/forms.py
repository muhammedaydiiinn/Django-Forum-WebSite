from django import forms
from HomePage.models import Post


class NewContentForm(forms.Form):
    topic_title = forms.CharField(max_length=100)
    topic_content = forms.CharField(widget=forms.Textarea(attrs={'rows': 7}))

    class Meta:
        model = Post
        fields = ['title', 'content']