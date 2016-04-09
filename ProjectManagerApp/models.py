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
    PROJECT_STATUS_OPEN = 'O'
    PROJECT_STATUS_OPEN_LABEL = 'Open'
    PROJECT_STATUS_CLOSED = 'C'
    PROJECT_STATUS_CLOSED_LABEL = 'Closed'
    PROJECT_STATUS = (
         (PROJECT_STATUS_OPEN, PROJECT_STATUS_OPEN_LABEL),
         (PROJECT_STATUS_CLOSED, PROJECT_STATUS_CLOSED_LABEL)
     )

    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    status = models.CharField(max_length=1, choices=PROJECT_STATUS)
    assigned_team = models.OneToOneField(Team, null=True, on_delete=models.SET_NULL)
    author = models.ForeignKey(Teacher, null=False, related_name="author", on_delete=models.CASCADE)
