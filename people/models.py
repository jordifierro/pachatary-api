import uuid

from django.db import models


class ORMPerson(models.Model):
    email = models.CharField(max_length=64, blank=True, null=True, unique=True)
    is_email_confirmed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Person'
        verbose_name_plural = 'People'

    def __str__(self):
        if self.email is not None:
            return self.email
        else:
            return "anonymous_{}".format(self.id)


class ORMAuthToken(models.Model):
    person = models.ForeignKey('ORMPerson', on_delete=models.CASCADE)
    access_token = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)
    refresh_token = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Auth token'
        verbose_name_plural = 'Auth tokens'

    def __str__(self):
        return str(self.access_token)


class ORMConfirmationToken(models.Model):
    person = models.ForeignKey('ORMPerson', db_index=True, on_delete=models.CASCADE)
    token = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Confirmation token'
        verbose_name_plural = 'Confirmation tokens'

    def __str__(self):
        return str(self.token)


class ORMLoginToken(models.Model):
    person = models.ForeignKey('ORMPerson', db_index=True, on_delete=models.CASCADE)
    token = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Login token'
        verbose_name_plural = 'Login tokens'

    def __str__(self):
        return str(self.token)


class ORMBlock(models.Model):
    creator = models.ForeignKey('ORMPerson', related_name='creator_person',
                                db_index=True, on_delete=models.CASCADE)
    target = models.ForeignKey('ORMPerson', related_name='target_person',
                               db_index=True, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Block'
        verbose_name_plural = 'Blocks'

    def __str__(self):
        return '{} -> {}'.format(self.author, self.target)
