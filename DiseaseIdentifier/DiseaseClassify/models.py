from django.db import models

# Create your models here.

class UploadImage(models.Model):
    name = models.CharField(max_length=30)
    predict_image=models.FileField(upload_to='predict_image/', blank=True, null=True)
    prediction = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return self.name