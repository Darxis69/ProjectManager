from django.db import models
from django.contrib.auth.models import User


class UserBase(User):
    pass


class Teacher(UserBase):
    pass


class Student(UserBase):
    student_no = models.IntegerField()


class Team(models.Model):
    first_teammate = models.ForeignKey(Student, null=True, related_name="first_student", on_delete=models.SET_NULL)
    second_teammate = models.ForeignKey(Student, null=True, related_name="second_student", on_delete=models.SET_NULL)

class Project(models.Model):
    PROJECT_STATUS = (
         ('O', 'Open'),
         ('C', 'Closed')
     )

    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    status = models.CharField(max_length=1, choices=PROJECT_STATUS)
    assigned_team = models.OneToOneField(Team, null=True, on_delete=models.SET_NULL)