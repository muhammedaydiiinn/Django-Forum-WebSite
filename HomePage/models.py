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
    slug = models.SlugField(blank=True, max_length=100, unique=True, db_index=True, editable=True)
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
            tokenizer1 = AutoTokenizer.from_pretrained("gurkan08/bert-turkish-text-classification")
            model1 = AutoModelForSequenceClassification.from_pretrained("gurkan08/bert-turkish-text-classification")
            nlp1 = pipeline("sentiment-analysis", model=model1, tokenizer=tokenizer1)

            tokenizer2 = AutoTokenizer.from_pretrained("savasy/bert-turkish-text-classification")
            model2 = AutoModelForSequenceClassification.from_pretrained("savasy/bert-turkish-text-classification")
            nlp2 = pipeline("sentiment-analysis", model=model2, tokenizer=tokenizer2)

            # Metni sınıflandırma
            result1 = nlp1(self.content)
            result2 = nlp2(self.content)

            # En yüksek skorlu çıktıyı seç
            if result1[0]['score'] > result2[0]['score']:
                combined_label = result1[0]['label']
            else:
                combined_label = result2[0]['label']

            # Etiketlerin daha açıklayıcı karşılıkları
            label_dict1 = {
                'ekonomi': 'economy',
                'spor': 'sport',
                'saglik': 'health',
                'kultur_sanat': 'culture',
                'bilim_teknoloji': 'technology',
                'egitim': 'education'
            }

            label_dict2 = {
                'LABEL_0': 'world',
                'LABEL_1': 'economy',
                'LABEL_2': 'culture',
                'LABEL_3': 'health',
                'LABEL_4': 'politics',
                'LABEL_5': 'sport',
                'LABEL_6': 'technology',
                'LABEL_7': 'education'
            }

            # Etiketleri uygun hale getir
            if combined_label in label_dict1:
                self.topic = label_dict1[combined_label]
            elif combined_label in label_dict2:
                self.topic = label_dict2[combined_label]
            else:
                self.topic = 'Bilinmeyen'

            self.save()  # Konuyu kaydetmek için tekrar kaydetme

    def __str__(self):
        return self.title
