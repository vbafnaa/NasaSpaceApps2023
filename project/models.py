from django.db import models

# Create your models here.

class Audio(models.Model):
    au_file=models.FileField(upload_to='audios/',null=False,blank=False)

class VideoAudio(models.Model):
    auvi_file=models.FileField(upload_to='videoaudio/',null=False,blank=False)

class Video(models.Model):
    vi_file=models.FileField(upload_to='videos/',null=False,blank=False)