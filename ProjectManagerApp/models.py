from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)

    #TODO powinno byc chyba tylko wolny/zajety
    status = models.CharField(max_length=10)

    #TODO
    #team = models.OneToOneField(Team,unique=True)