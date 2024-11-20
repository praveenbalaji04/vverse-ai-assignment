from django.db import models
# from django.contrib.auth.models import User


class Video(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="videos/")  # not a recommended way, use s3 or other storage and save URL here
    # user = models.OneToOneField(, on_delete=models.CASCADE)  # not using user for now
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file.name

    class Meta:
        db_table = "video"
