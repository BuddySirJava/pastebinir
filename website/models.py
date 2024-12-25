from django.db import models


class Language(models.Model):
    displayname = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    def __str__(self):
        return self.displayname

class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    def __str__(self):
            return self.username
    class Meta:
            ordering = ['username']

    def __str__(self):
        return self.name


class Paste(models.Model):
    id = models.AutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField(blank=True, null=True)
    lang = models.ForeignKey(Language, on_delete=models.CASCADE, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, default=None)
    salt = models.CharField(max_length=24, blank=True, null=True, default=None)
    iv = models.CharField(max_length=24, blank=True, null=True, default=None)
    ciphertext = models.TextField()
    def __str__(self):
        return f"Paste {self.id}"
    class Meta:
        ordering = ['-created']
