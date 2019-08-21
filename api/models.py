from django.db import models

# Create your models here.
class settings(models.Model):
    N_symptomps_sent_qa = models.IntegerField(default=5)
    N_symptomps_sent_in_search = models.IntegerField(default=5)

