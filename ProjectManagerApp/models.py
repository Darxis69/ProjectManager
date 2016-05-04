from django.db import models
from django.contrib.auth.models import User


class UserBase(User):
    pass


class Teacher(UserBase):
    pass


class Student(UserBase):
    STUDENT_STATUS_UNASSIGNED = 'U'
    STUDENT_STATUS_UNASSIGNED_LABEL = 'Unassigned'
    STUDENT_STATUS_ASSIGNED = 'A'
    STUDENT_STATUS_ASSIGNED_LABEL = 'Assigned'
    STUDENT_STATUS = (
         (STUDENT_STATUS_UNASSIGNED, STUDENT_STATUS_UNASSIGNED_LABEL),
         (STUDENT_STATUS_ASSIGNED, STUDENT_STATUS_ASSIGNED_LABEL)
     )

    student_no = models.IntegerField(unique=True)
    team = models.ForeignKey('Team', null=True, related_name='+', on_delete=models.SET_NULL, unique=False)
    status = models.CharField(max_length=1, choices=STUDENT_STATUS)
    

class Team(models.Model):
    name = models.CharField(max_length=50)
    first_teammate = models.OneToOneField(Student, null=True, related_name='+', on_delete=models.SET_NULL, unique=True)
    second_teammate = models.OneToOneField(Student, null=True, related_name='+', on_delete=models.SET_NULL, unique=True)


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
    assigned_team = models.OneToOneField(Team, null=True, related_name="project", on_delete=models.SET_NULL)
    all_teams = models.ManyToManyField(Team, related_name="+")
    author = models.ForeignKey(Teacher, null=False, related_name="+", on_delete=models.CASCADE)
