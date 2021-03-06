from django.db import models
from stdimage.models import StdImageField
from stdimage.utils import UploadToUUID

from people.models import ORMPerson


class ORMExperience(models.Model):
    title = models.CharField(max_length=80, blank=False)
    description = models.TextField(blank=True)
    picture = StdImageField(upload_to=UploadToUUID(path='experiences'),
                            variations={'large': (1280, 1280),
                                        'medium': (640, 640),
                                        'small': (320, 320)},
                            blank=True)
    author = models.ForeignKey(ORMPerson, on_delete=models.CASCADE)
    share_id = models.CharField(unique=True, max_length=8, null=True, blank=True)

    saves_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Experience'
        verbose_name_plural = 'Experiences'

    def __str__(self):
        return self.title


class ORMSave(models.Model):
    person = models.ForeignKey(ORMPerson, on_delete=models.CASCADE)
    experience = models.ForeignKey(ORMExperience, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Save'
        verbose_name_plural = 'Saves'

    def __str__(self):
        return "{} - {}".format(str(self.person), str(self.experience))


class ORMFlag(models.Model):
    person = models.ForeignKey(ORMPerson, on_delete=models.CASCADE)
    experience = models.ForeignKey(ORMExperience, on_delete=models.CASCADE)
    reason = models.CharField(max_length=80, blank=False)

    is_solved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Flag'
        verbose_name_plural = 'Flags'

    def __str__(self):
        return "{} - {}".format(str(self.person), str(self.experience))
