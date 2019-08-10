from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
# from django.db import models

class CustomUser(AbstractUser):
    pass

    def __str__(self):
        return self.email
    # add additional fields in here


class custom_verification_code(models.Model):
    email = models.EmailField(max_length=70,blank=True, null= True, unique= True)
    code = models.IntegerField(null= False, unique= True)
