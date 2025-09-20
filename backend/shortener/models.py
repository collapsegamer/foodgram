from django.db import models


class ShortLink(models.Model):
    code = models.CharField(max_length=16, unique=True)
    target_path = models.CharField(max_length=256)

    def __str__(self):
        return self.code
