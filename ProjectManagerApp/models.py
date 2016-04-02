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


class Teacher(UserBase):
    pass


class Student(UserBase):
    student_no = models.IntegerField()


class Team(models.Model):
    first_teammate = models.ForeignKey(Student, null=True, related_name="first_student", on_delete=models.SET_NULL)
    second_teammate = models.ForeignKey(Student, null=True, related_name="second_student", on_delete=models.SET_NULL)


# class Project(models.Model):
#     PROJECT_STATUS = (
#         ('O', 'Open'),
#         ('C', 'Closed')
#     )
#     project_name = models.CharField(max_length=30)
#     project_description = models.CharField(max_length=200)
#     status = models.CharField(max_length=1, choices=PROJECT_STATUS)
#     assigned_team = models.OneToOneField(Team, null=True, on_delete=models.SET_NULL)