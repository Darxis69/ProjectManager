from django.test import TestCase
from .models import User, Student, Teacher, Team, Project
from .services import *

# Create your tests here.


class ManageTeamsTests(TestCase):

    def test_create_team_as_teacher(self):
        user = Teacher()
        team_name = "test_team_name"

        with self.assertRaisesMessage(MustBeStudent, ""):
            user_create_team(user, team_name)

    def test_create_team_as_user_already_in_another_team(self):
        user = Student()
        team = Team()
        user.team = team
        team_name = "test_team_name"

        with self.assertRaisesMessage(UserAlreadyInTeam, ""):
            user_create_team(user, team_name)

    def test_leave_team_as_teacher(self):
        user = Teacher()

        with self.assertRaisesMessage(MustBeStudent, ""):
            user_team_leave(user)

    def test_leave_team_as_student_without_team(self):
        user = Student()

        with self.assertRaisesMessage(UserNotInTeam, ""):
            user_team_leave(user)

    def test_add_teacher_to_team(self):
        user = Teacher()
        team = Team()

        with self.assertRaisesMessage(MustBeStudent, ""):
            user_join_team(user, team)

    def test_add_student_with_team_to_another_team(self):
        user = Student()
        team1 = Team()
        team2 = Team()
        user.team = team1

        with self.assertRaisesMessage(UserAlreadyInTeam, ""):
            user_join_team(user, team2)



class ManageProjectsTests(TestCase):

    def test_create_project_as_student(self):
        user = Student()
        project_name = "test_project_name"
        project_descripton = "test_project_descrption"

        with self.assertRaisesMessage(MustBeTeacher, ""):
            user_create_project(user, project_name, project_descripton)

    def test_delete_project_as_student(self):
        user = Student()
        project = Project()

        with self.assertRaisesMessage(MustBeTeacher, ""):
            user_delete_project(user, project)

    def test_delete_project_with_assigned_team(self):
        user = Teacher()
        team = Team()
        project = Project()
        project.assigned_team = team

        with self.assertRaisesMessage(ProjectHasAssignedTeam, ""):
            user_delete_project(user, project)