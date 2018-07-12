from django.db import models
from stdimage.models import StdImageField
from stdimage.utils import UploadToUUID, pre_delete_delete_callback, pre_save_delete_callback

from people.models import ORMPerson


class ORMProfile(models.Model):
    person = models.OneToOneField(ORMPerson, related_name='profile', on_delete=models.CASCADE)
    username = models.CharField(max_length=20, unique=True)
    bio = models.CharField(max_length=140, blank=True)
    picture = StdImageField(upload_to=UploadToUUID(path='profiles'),
                            variations={'medium': (640, 640),
                                        'small': (320, 320),
                                        'tiny': (160, 160)},
                            blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return self.username


models.signals.post_delete.connect(pre_delete_delete_callback, sender=ORMProfile)
models.signals.pre_save.connect(pre_save_delete_callback, sender=ORMProfile)
