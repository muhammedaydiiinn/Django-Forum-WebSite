from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pics', default='profile_pics/avatar.png', blank=True)

    # Diğer profil alanları buraya eklenebilir

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Bir User oluşturulduğunda, bir Profile objesi oluştur.
    """
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Bir User kaydedildiğinde, ilişkili Profile objesini kaydet.
    """
    instance.profile.save()
