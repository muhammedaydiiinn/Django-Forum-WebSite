from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)  # Yeni bir alan: Beğeni sayısı
    slug = models.SlugField(blank=True, max_length=100, unique=True, db_index=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.slug or Post.objects.filter(slug=self.slug).exclude(id=self.id).exists():
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            while Post.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
