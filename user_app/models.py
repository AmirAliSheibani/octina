from django.db import models

from pricing.models import CustomUser


class UserProfile(models.Model):
    username = models.CharField(max_length=45)
    Email = models.EmailField()
    password = models.CharField(max_length=70)
    password2 = models.CharField(max_length=70)

class EmailCode(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='email_code_user')
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)







