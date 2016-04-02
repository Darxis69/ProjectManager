from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)

    #TODO powinno byc chyba tylko wolny/zajety
    status = models.CharField(max_length=10)

    #TODO
    #team = models.OneToOneField(Team,unique=True)


class UserBase(User):
    pass


class Teacher(models.Model):
    pass


class Student(models.Model):
    student_no = models.IntegerField()


# class Team(models.Model):
#     first_teammate = models.ForeignKey(Student, on_delete=models.CASCADE)
#     second_teammate = models.ForeignKey(Student, on_delete=models.CASCADE)

# class Project(models.Model):
#     PROJECT_STATUS = (
#         ('O', 'Open'),
#         ('C', 'Closed')
#     )
#     project_name = models.CharField(max_length=30)
#     project_description = models.CharField(max_length=200)
#     status = models.CharField(max_length=1, choices=PROJECT_STATUS)
#     assigned_team = models.ForeignKey(Team, on_delete=models.CASCADE)