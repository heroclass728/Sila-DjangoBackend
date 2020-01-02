from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
from tinymce import HTMLField

class templates(models.Model):
    name = models.CharField(max_length=120,unique=True,blank=False,null=False)
    description = models.TextField(max_length=250,null=True,blank=True)
    temp = HTMLField('Content')
#    draft = models.BooleanField(default=False)

    def __str__(self):
        return self.name
# class content(models.Model):
#     name = models.ForeignKey(templates, on_delete=models.PROTECT)
#     text = models.TextField(max_length=250,null=True)
# #    draft = models.BooleanField(default=False)

    def __str__(self):
        return self.name
