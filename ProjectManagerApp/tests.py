from django.test import TestCase
from .models import User, Student, Teacher, Team, Project
from .services import *
from django.core.urlresolvers import reverse

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

    project_name = "test_project_name"
    project_descripton = "test_project_descrption"

    def test_create_project_as_student(self):
        user = Student()
        # project_name = "test_project_name"
        # project_descripton = "test_project_descrption"

        with self.assertRaisesMessage(MustBeTeacher, ""):
            user_create_project(user, self.project_name, self.project_descripton)

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

    def test_create_project(self):
        user = Teacher()
        user.save()
        project = user_create_project(user, self.project_name, self.project_descripton)

        self.assertIsInstance(project, Project)
        self.assertEqual(project.name, self.project_name)
        self.assertEqual(project.description, self.project_descripton)
        self.assertEqual(project.status, Project.PROJECT_STATUS_OPEN)
        self.assertEqual(project.assigned_team, None)
        self.assertEqual(project.author, user)


class ViewsTests(TestCase):

    #unlogged user - should be redirected to login view
    def test_unlogged_user_get_index(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/account/login/?next=/')

    def test_unlogged_user_get_projects(self):
        response = self.client.get('/projects/')
        self.assertRedirects(response, '/account/login/?next=/projects/')

    def test_unlogged_user_get_teams(self):
        response = self.client.get('/teams/')
        self.assertRedirects(response, '/account/login/?next=/teams/')
