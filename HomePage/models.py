from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)  # Yeni bir alan: Beğeni sayısı
    slug = models.SlugField(blank=True, max_length=100, unique=True, db_index=True, editable=False)
    topic = models.CharField(max_length=50, blank=True)  # Konu alanı

    def save(self, *args, **kwargs):
        if not self.slug or Post.objects.filter(slug=self.slug).exclude(id=self.id).exists():
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            while Post.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

        # İçerik kaydedildikten sonra konuyu tahmin et
        if not self.topic:
            # Metin sınıflandırma modelini yükleme
            tokenizer = AutoTokenizer.from_pretrained("savasy/bert-turkish-text-classification")
            model = AutoModelForSequenceClassification.from_pretrained("savasy/bert-turkish-text-classification")
            nlp = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

            # Metni sınıflandırma
            result = nlp(self.content)

            # Tahmin edilen konuyu al
            if result:
                label_key = result[0]['label']
                code_to_label = {
                    'world': 'dünya',
                    'economy': 'ekonomi',
                    'culture': 'kültür',
                    'health': 'sağlık',
                    'politics': 'siyaset',
                    'sport': 'spor',
                    'technology': 'teknoloji'
                }
                predicted_label = code_to_label.get(label_key, 'Bilinmeyen')
                self.topic = predicted_label
                self.save()  # Konuyu kaydetmek için tekrar kaydetme


    def __str__(self):
        return self.title
