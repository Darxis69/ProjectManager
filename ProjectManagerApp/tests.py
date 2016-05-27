from django.test import TestCase

from .services import *
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from .forms import AccountCreateForm, AccountChangePasswordForm, AccountChangeEmailForm


# SERVICES TESTS

class CreateUsersServicesTests(TestCase):

    def test_create_teacher(self):
        account_create_teacher("test_teacher_username", "test@mail.com", "test_pass")

        self.assertTrue(Teacher.objects.filter(username='test_teacher_username', email='test@mail.com').exists())
        user = Teacher.objects.get(username='test_teacher_username')
        self.assertEqual(user.email, "test@mail.com")

    def test_create_student(self):
        account_create_student("1234", "test_student_username", "test@mail.com", "test_pass")

        self.assertTrue(Student.objects.filter(username='test_student_username', email='test@mail.com').exists())
        user = Student.objects.get(username='test_student_username')
        self.assertEqual(user.student_no, 1234)
        self.assertEqual(user.email, "test@mail.com")

    def test_create_student_with_the_same_student_no(self):
        account_create_student("1234", "test_student_username", "test@mail.com", "test_pass")

        with self.assertRaisesMessage(StudentWithGivenStudentNoAlreadyExists, ""):
            account_create_student("1234", "test_student_username2", "test2@mail.com", "test_pass")

    def test_create_user_with_the_same_username(self):
        account_create_student("1234", "test_student_username", "test1@mail.com", "test_pass")
        account_create_teacher("test_teacher_username", "test2@mail.com", "test_pass")

        with self.assertRaisesMessage(UserWithGivenUsernameAlreadyExists, ""):
            account_create_student("1212", "test_student_username", "test3@mail.com", "test_pass")

        with self.assertRaisesMessage(UserWithGivenUsernameAlreadyExists, ""):
            account_create_student("1212", "test_teacher_username", "test3@mail.com", "test_pass")

        with self.assertRaisesMessage(UserWithGivenUsernameAlreadyExists, ""):
            account_create_teacher("test_teacher_username", "test3@mail.com", "test_pass")

        with self.assertRaisesMessage(UserWithGivenUsernameAlreadyExists, ""):
            account_create_teacher("test_student_username", "test3@mail.com", "test_pass")

    def test_create_user_with_the_same_email(self):
        account_create_student("1234", "test_student_username", "test1@mail.com", "test_pass")
        account_create_teacher("test_teacher_username", "test2@mail.com", "test_pass")

        with self.assertRaisesMessage(UserWithGivenEmailAlreadyExists, ""):
            account_create_student("1212", "test_student_username1", "test1@mail.com", "test_pass")

        with self.assertRaisesMessage(UserWithGivenEmailAlreadyExists, ""):
            account_create_student("1212", "test_teacher_username1", "test2@mail.com", "test_pass")

        with self.assertRaisesMessage(UserWithGivenEmailAlreadyExists, ""):
            account_create_teacher("test_teacher_username1", "test1@mail.com", "test_pass")

        with self.assertRaisesMessage(UserWithGivenEmailAlreadyExists, ""):
            account_create_teacher("test_student_username1", "test2@mail.com", "test_pass")


class ManageUsersServicesTests(TestCase):

    new_password = "new_password"
    new_stud_email = "new_stud@mail.com"
    new_teach_email = "new_teach@mail.com"

    def setUp(self):
        stud = Student(username='student_username', email="student@mail.com", student_no=1111)
        stud.set_password('student_password')
        stud.save()

        teach = Teacher(username='teacher_username', email="teacher@mail.com")
        teach.set_password('teacher_password')
        teach.save()

    def test_user_change_password(self):
        teacher = Teacher.objects.get(username='teacher_username')
        student = Student.objects.get(username='student_username')

        user_change_password(student, "student_password", self.new_password)
        self.assertTrue(student.check_password(self.new_password))

        user_change_password(teacher, "teacher_password", self.new_password)
        self.assertTrue(teacher.check_password(self.new_password))

    def test_user_change_password_wrong_pass(self):
        teacher = Teacher.objects.get(username='teacher_username')
        student = Student.objects.get(username='student_username')

        with self.assertRaisesMessage(InvalidPassword, ""):
            user_change_password(student, "wrong_password", self.new_password)

        with self.assertRaisesMessage(InvalidPassword, ""):
            user_change_password(teacher, "wrong_password", self.new_password)

    def test_user_change_email(self):
        teacher = Teacher.objects.get(username='teacher_username')
        student = Student.objects.get(username='student_username')

        user_change_email(student, self.new_stud_email)
        self.assertEqual(student.email, self.new_stud_email)

        user_change_email(teacher, self.new_teach_email)
        self.assertEqual(teacher.email, self.new_teach_email)

    def test_user_change_email_already_exist(self):
        teacher = Teacher.objects.get(username='teacher_username')
        student = Student.objects.get(username='student_username')

        with self.assertRaisesMessage(UserWithGivenEmailAlreadyExists, ""):
            user_change_email(student, "student@mail.com")

        with self.assertRaisesMessage(UserWithGivenEmailAlreadyExists, ""):
            user_change_email(teacher, "student@mail.com")

    def test_user_delete(self):
        student = Student.objects.get(username='student_username')
        user_delete_account(student)
        self.assertFalse(Student.objects.filter(username='student_username').exists())

    def test_user_delete_already_in_team(self):
        student = Student.objects.get(username='student_username')
        team = Team()
        student.team = team
        with self.assertRaisesMessage(UserAlreadyInTeam, ""):
            user_delete_account(student)
        self.assertTrue(Student.objects.filter(username='student_username').exists())


class ManageTeamsServicesTests(TestCase):

    def setUp(self):
        user = Student(username='test_username', email='test@mail.com', student_no="1234")
        user.save()

        user2 = Student(username='test_username2', email='test2@mail.com', student_no="1212")
        user2.save()

        user3 = Student(username='test_username3', email='test3@mail.com', student_no="12321")
        user3.save()

    def test_create_team(self):
        user = Student.objects.get(username='test_username')

        user_create_team(user, "test_team")

        self.assertTrue(Team.objects.filter(name="test_team").exists())
        team = Team.objects.get(name="test_team")
        self.assertEqual(team.first_teammate, user)
        self.assertEqual(user.team, team)

    def test_create_team_unique_name(self):
        user = Student.objects.get(username='test_username')
        user2 = Student.objects.get(username='test_username2')
        user3 = Student.objects.get(username='test_username3')

        user_create_team(user, "test_team")

        user_create_team(user2, "test_team 2")

        self.assertTrue(Team.objects.filter(name="test_team").exists())
        self.assertTrue(Team.objects.filter(name="test_team 2").exists())

        with self.assertRaisesMessage(TeamWithGivenNameAlreadyExists, ""):
            user_create_team(user3, "test_team")

        with self.assertRaisesMessage(TeamWithGivenNameAlreadyExists, ""):
            user_create_team(user3, "TEST_TEAM")

        with self.assertRaisesMessage(TeamWithGivenNameAlreadyExists, ""):
            user_create_team(user3, "TEST_TEAM 2")

    def test_leave_one_person_team(self):
        user = Student.objects.get(username='test_username')

        user_create_team(user, "test_team")
        self.assertTrue(Team.objects.filter(name="test_team").exists())
        team = Team.objects.get(name="test_team")
        self.assertEqual(user.team, team)

        user_team_leave(user)
        self.assertFalse(Team.objects.filter(name="test_team").exists())
        self.assertEqual(user.team, None)

    def test_leave_first_from_two_persons_team(self):
        user = Student.objects.get(username='test_username')
        user2 = Student.objects.get(username='test_username2')

        user_create_team(user, "test_team")
        self.assertTrue(Team.objects.filter(name="test_team").exists())
        team = Team.objects.get(name="test_team")
        self.assertEqual(user.team, team)

        user_join_team(user2, team)

        user.team.refresh_from_db()

        self.assertEqual(team.second_teammate, user2)
        self.assertEqual(user2.team, team)

        team2 = user.team
        self.assertEqual(team2.second_teammate, user2)

        user_team_leave(user)

        self.assertTrue(Team.objects.filter(name="test_team").exists())

        self.assertTrue(Team.objects.filter(name="test_team").exists())
        team.refresh_from_db()

        self.assertEqual(user.team, None)
        self.assertEqual(user2.team, team)
        self.assertEqual(team.first_teammate, user2)
        self.assertEqual(team.second_teammate, None)

    def test_leave_second_from_two_persons_team(self):
        user = Student.objects.get(username='test_username')
        user2 = Student.objects.get(username='test_username2')

        user_create_team(user, "test_team")
        self.assertTrue(Team.objects.filter(name="test_team").exists())
        team = Team.objects.get(name="test_team")
        self.assertEqual(user.team, team)

        user_join_team(user2, team)

        user.team.refresh_from_db()

        self.assertEqual(team.second_teammate, user2)
        self.assertEqual(user2.team, team)

        user_team_leave(user2)
        self.assertTrue(Team.objects.filter(name="test_team").exists())
        team.refresh_from_db()

        self.assertEqual(user2.team, None)
        self.assertEqual(user.team, team)
        self.assertEqual(team.first_teammate, user)
        self.assertEqual(team.second_teammate, None)

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

    def test_leave_team_with_project_assigned(self):
        user = Student.objects.get(username='test_username')
        user2 = Student.objects.get(username='test_username2')

        user_create_team(user, "test_team")
        self.assertTrue(Team.objects.filter(name="test_team").exists())
        team = Team.objects.get(name="test_team")
        self.assertEqual(user.team, team)

        user_join_team(user2, team)

        user.team.refresh_from_db()
        user.status = Student.STUDENT_STATUS_ASSIGNED

        with self.assertRaisesMessage(UserAssignedToProject, ""):
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

    def test_add_student_to_full_team(self):
        user1 = Student()
        user2 = Student()
        user3 = Student()
        team = Team()
        team.first_teammate = user1
        team.second_teammate = user2

        with self.assertRaisesMessage(TeamIsFull, ""):
            user_join_team(user3, team)


class ManageProjectsServicesTests(TestCase):

    project_name = "test_project_name"
    project_description = "test_project_descrption"

    def test_create_project_as_student(self):
        user = Student()

        with self.assertRaisesMessage(MustBeTeacher, ""):
            user_create_project(user, self.project_name, self.project_description)

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
        project = user_create_project(user, self.project_name, self.project_description)

        self.assertIsInstance(project, Project)
        self.assertEqual(project.name, self.project_name)
        self.assertEqual(project.description, self.project_description)
        self.assertEqual(project.status, Project.PROJECT_STATUS_OPEN)
        self.assertEqual(project.assigned_team, None)
        self.assertEqual(project.author, user)
        self.assertTrue(Project.objects.filter(name=self.project_name).exists())

    def test_create_project_unique_name(self):
        user = Teacher()
        user.save()

        user_create_project(user, "project 1", "description")
        user_create_project(user, "project 2", "description")

        with self.assertRaisesMessage(ProjectWithGivenNameAlreadyExists, ""):
            user_create_project(user, "project 1", "description")

        with self.assertRaisesMessage(ProjectWithGivenNameAlreadyExists, ""):
            user_create_project(user, "PROJECT 2", "description")

    def test_delete_project(self):
        user = Teacher()
        user.save()
        project = user_create_project(user, self.project_name, self.project_description)
        project.save()

        self.assertTrue(Project.objects.filter(name=self.project_name).exists())

        user_delete_project(user, project)

        self.assertFalse(Project.objects.filter(name=self.project_name).exists())

    def test_join_project(self):
        user = Teacher()
        user.save()
        project = user_create_project(user, self.project_name, self.project_description)
        project.save()

        self.assertTrue(Project.objects.filter(name=self.project_name).exists())

        account_create_student("1234", "test_student_username", "test@mail.com", "test_pass")

        self.assertTrue(Student.objects.filter(username='test_student_username', email='test@mail.com').exists())
        user2 = Student.objects.get(username='test_student_username')

        user_create_team(user2, "test_team")

        self.assertTrue(Team.objects.filter(name="test_team").exists())

        user_team_join_project(user2, project)

        self.assertTrue(Project.objects.filter(name=self.project_name).exists())
        project.refresh_from_db()
        self.assertTrue(project.all_teams.filter(name=user2.team.name).exists())

    def test_join_project_as_a_teacher(self):
        user = Teacher()
        user.save()
        project = user_create_project(user, self.project_name, self.project_description)
        project.save()

        self.assertTrue(Project.objects.filter(name=self.project_name).exists())

        with self.assertRaisesMessage(MustBeStudent, ""):
            user_team_join_project(user, project)

    def test_join_project_as_student_without_team(self):
        user = Student()
        project = Project()

        with self.assertRaisesMessage(UserNotInTeam, ""):
            user_team_join_project(user, project)

    def test_join_project_with_project_assigned(self):
        user = Student(username='test_username', email='test@mail.com', student_no="1234")
        user.save()

        user2 = Student(username='test_username2', email='test2@mail.com', student_no="1212")
        user2.save()

        user_create_team(user, "test_team")
        self.assertTrue(Team.objects.filter(name="test_team").exists())
        team = Team.objects.get(name="test_team")
        self.assertEqual(user.team, team)

        user_join_team(user2, team)

        project = Project()
        project.assigned_team = team

        with self.assertRaisesMessage(ProjectHasAssignedTeam, ""):
            user_team_join_project(user, project)

    def test_join_project_already_in_queue(self):
        user = Teacher()
        user.save()
        project = user_create_project(user, self.project_name, self.project_description)
        project.save()

        self.assertTrue(Project.objects.filter(name=self.project_name).exists())

        account_create_student("1234", "test_student_username", "test@mail.com", "test_pass")

        self.assertTrue(Student.objects.filter(username='test_student_username', email='test@mail.com').exists())
        user2 = Student.objects.get(username='test_student_username')

        user_create_team(user2, "test_team")

        self.assertTrue(Team.objects.filter(name="test_team").exists())

        user_team_join_project(user2, project)

        self.assertTrue(Project.objects.filter(name=self.project_name).exists())
        project.refresh_from_db()
        self.assertTrue(project.all_teams.filter(name=user2.team.name).exists())

        with self.assertRaisesMessage(TeamAlreadyInProjectQueue, ""):
            user_team_join_project(user2, project)

    def test_leave_project(self):
        user = Teacher()
        user.save()
        project = user_create_project(user, self.project_name, self.project_description)
        project.save()

        self.assertTrue(Project.objects.filter(name=self.project_name).exists())

        account_create_student("1234", "test_student_username", "test@mail.com", "test_pass")

        self.assertTrue(Student.objects.filter(username='test_student_username', email='test@mail.com').exists())
        user2 = Student.objects.get(username='test_student_username')

        user_create_team(user2, "test_team")

        self.assertTrue(Team.objects.filter(name="test_team").exists())

        user_team_join_project(user2, project)

        self.assertTrue(Project.objects.filter(name=self.project_name).exists())
        project.refresh_from_db()
        self.assertTrue(project.all_teams.filter(name=user2.team.name).exists())

        user_team_leave_project(user2, project)
        project.refresh_from_db()
        self.assertFalse(project.all_teams.filter(name=user2.team.name).exists())

    def test_leave_project_as_a_teacher(self):
        user = Teacher()
        user.save()
        project = user_create_project(user, self.project_name, self.project_description)
        project.save()

        self.assertTrue(Project.objects.filter(name=self.project_name).exists())

        with self.assertRaisesMessage(MustBeStudent, ""):
            user_team_leave_project(user, project)

    def test_leave_project_as_student_without_team(self):
        user = Student()
        project = Project()

        with self.assertRaisesMessage(UserNotInTeam, ""):
            user_team_leave_project(user, project)

    def test_leave_project_with_project_assigned(self):
        user = Teacher()
        user.save()
        project = user_create_project(user, self.project_name, self.project_description)
        project.save()

        self.assertTrue(Project.objects.filter(name=self.project_name).exists())

        account_create_student("1234", "test_student_username", "test@mail.com", "test_pass")

        self.assertTrue(Student.objects.filter(username='test_student_username', email='test@mail.com').exists())
        user2 = Student.objects.get(username='test_student_username')

        user_create_team(user2, "test_team")

        self.assertTrue(Team.objects.filter(name="test_team").exists())
        team = Team.objects.get(name="test_team")

        user_team_join_project(user2, project)
        project.assigned_team = team

        with self.assertRaisesMessage(ProjectHasAssignedTeam, ""):
            user_team_leave_project(user2, project)

    def test_leave_project_not_in_queue(self):
        user = Teacher()
        user.save()
        project = user_create_project(user, self.project_name, self.project_description)
        project.save()

        self.assertTrue(Project.objects.filter(name=self.project_name).exists())

        account_create_student("1234", "test_student_username", "test@mail.com", "test_pass")

        self.assertTrue(Student.objects.filter(username='test_student_username', email='test@mail.com').exists())
        user2 = Student.objects.get(username='test_student_username')

        user_create_team(user2, "test_team")

        self.assertTrue(Team.objects.filter(name="test_team").exists())

        with self.assertRaisesMessage(TeamNotInProjectQueue, ""):
            user_team_leave_project(user2, project)

    def test_assign_teams_to_project_as_student(self):
        user = Student()

        with self.assertRaisesMessage(MustBeTeacher, ""):
            assign_teams_to_projects(user)

    def test_assign_team_to_project(self):
        user = Teacher()
        user.save()
        project = user_create_project(user, self.project_name, self.project_description)
        project.save()

        student1 = Student(username='student1_username', email="student1@mail.com", student_no=1111)
        student1.set_password('student1_password')
        student1.save()

        student2 = Student(username='student2_username', email="student2@mail.com", student_no=1234)
        student2.set_password('student2_password')
        student2.save()

        user_create_team(student1, "test_team")
        user_join_team(student2, student1.team)

        user_team_join_project(student1, project)

        assign_team_to_project(project)

        student1.refresh_from_db()
        student2.refresh_from_db()
        project.refresh_from_db()

        self.assertEqual(project.assigned_team, student1.team)
        self.assertTrue(project.all_teams.count() == 0)
        self.assertEqual(project.status, Project.PROJECT_STATUS_CLOSED)

        self.assertEqual(project.assigned_team.first_teammate.status, Student.STUDENT_STATUS_ASSIGNED)
        self.assertEqual(project.assigned_team.second_teammate.status, Student.STUDENT_STATUS_ASSIGNED)

    def test_user_edit_project(self):
        teach = Teacher(username='teacher_username', email="teacher@mail.com")
        teach.set_password('teacher_password')
        teach.save()
        teach.refresh_from_db()

        project = Project.objects.create(name='test_project', description='test_description', author_id=teach.id)
        project.save()
        project.refresh_from_db()

        user_edit_project(teach, project.id, 'new_project_name', 'new_project_description')

        self.assertFalse(Project.objects.filter(name='test_project', description='test_description').exists())
        self.assertTrue(Project.objects.filter(name='new_project_name', description='new_project_description').exists())

    def test_user_edit_project_not_author(self):
        teach = Teacher(username='teacher_username', email="teacher@mail.com")
        teach.set_password('teacher_password')
        teach.save()
        teach.refresh_from_db()

        teach2 = Teacher(username='teacher2_username', email="teacher2@mail.com")
        teach2.set_password('teacher_password')
        teach2.save()
        teach2.refresh_from_db()

        project = Project.objects.create(name='test_project', description='test_description', author_id=teach.id)
        project.save()
        project.refresh_from_db()

        with self.assertRaisesMessage(MustBeAuthor, ""):
            user_edit_project(teach2, project.id, 'new_project_name', 'new_project_description')

        self.assertTrue(Project.objects.filter(name='test_project', description='test_description').exists())
        self.assertFalse(Project.objects.filter(name='new_project_name',
                                                description='new_project_description').exists())

    def test_user_edit_project_name_already_exist(self):
        teach = Teacher(username='teacher_username', email="teacher@mail.com")
        teach.set_password('teacher_password')
        teach.save()
        teach.refresh_from_db()

        project = Project.objects.create(name='test_project', description='test_description', author_id=teach.id)
        project.save()
        project.refresh_from_db()

        project2 = Project.objects.create(name='test_project2', description='test_description2', author_id=teach.id)
        project2.save()
        project2.refresh_from_db()

        with self.assertRaisesMessage(ProjectWithGivenNameAlreadyExists, ""):
            user_edit_project(teach, project.id, 'test_project2', 'new_project_description')

        self.assertTrue(Project.objects.filter(name='test_project', description='test_description').exists())
        self.assertFalse(Project.objects.filter(name='new_project2', description='new_project_description').exists())


# VIEWS TESTS

class ViewsTests(TestCase):

    def setUp(self):
        stud = Student(username='student_username', email="student@mail.com", student_no=1111)
        stud.set_password('student_password')
        stud.save()

        teach = Teacher(username='teacher_username', email="teacher@mail.com")
        teach.set_password('teacher_password')
        teach.save()

        teach2 = Teacher(username='teacher_username_2', email="teacher_2@mail.com")
        teach2.set_password('teacher_password')
        teach2.save()

    # unlogged user - should be redirected to login view
    def test_unlogged_user_get_index(self):
        response = self.client.get(reverse('index_url'))
        self.assertRedirects(response, reverse('account_login_url') + '?next=' + reverse('index_url'))

    def test_unlogged_user_get_projects(self):
        response = self.client.get(reverse('projects_list_url'))
        self.assertRedirects(response, reverse('account_login_url') + '?next=' + reverse('projects_list_url'))

    def test_unlogged_user_get_teams(self):
        response = self.client.get(reverse('teams_list_url'))
        self.assertRedirects(response, reverse('account_login_url') + '?next=' + reverse('teams_list_url'))

    # login tests
    def test_student_login(self):
        login = self.client.login(username='student_username', password='student_password')
        self.assertTrue(login)

    def test_teacher_login(self):
        login = self.client.login(username='teacher_username', password='teacher_password')
        self.assertTrue(login)

    def test_student_login_from_view(self):
        response = self.client.post(reverse('account_login_url'), {'username': 'student_username',
                                                                   'password': 'student_password'})
        self.assertRedirects(response, reverse('index_url'))

        response = self.client.get(reverse('teams_list_url'))
        self.assertEqual(response.status_code, 200)

    def test_teacher_login_from_view(self):
        response = self.client.post(reverse('account_login_url'), {'username': 'teacher_username',
                                                                   'password': 'teacher_password'})
        self.assertRedirects(response, reverse('index_url'))

        response = self.client.get(reverse('teams_list_url'))
        self.assertEqual(response.status_code, 200)

    def test_user_login_from_view_with_next(self):
        response = self.client.post(reverse('account_login_url') + '?next=' + reverse('projects_list_url'),
                                    {'username': 'student_username', 'password': 'student_password'})
        self.assertRedirects(response, reverse('projects_list_url'))

    def test_not_existing_user_login_from_view(self):
        response = self.client.post(reverse('account_login_url'), {'username': 'test', 'password': 'test_pass'})
        self.assertEqual(response.status_code, 200)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Username or password is incorrect. Try again.')

    def test_student_wrong_password_login_from_view(self):
        response = self.client.post(reverse('account_login_url'), {'username': 'student_username',
                                                                   'password': 'wrong_pass'})
        self.assertEqual(response.status_code, 200)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Username or password is incorrect. Try again.')

    def test_teacher_wrong_password_login_from_view(self):
        response = self.client.post(reverse('account_login_url'), {'username': 'teacher_username',
                                                                   'password': 'wrong_pass'})
        self.assertEqual(response.status_code, 200)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Username or password is incorrect. Try again.')

    def test_login_as_authenticated_user(self):
        self.client.login(username='student_username', password='student_password')

        response = self.client.get(reverse('account_login_url'))
        self.assertRedirects(response, reverse('index_url'))

        response = self.client.post(reverse('account_login_url'), {'username': 'test', 'password': 'test_pass'})
        self.assertRedirects(response, reverse('index_url'))

    # logout tests
    def test_logout(self):
        self.client.login(username='student_username', password='student_password')
        self.client.get(reverse('account_logout_url'))

        response = self.client.get(reverse('projects_list_url'))
        self.assertRedirects(response, reverse('account_login_url') + '?next=' + reverse('projects_list_url'))

    # account create tests
    def test_student_account_create_from_view(self):
        response = self.client.get(reverse('account_create_url'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('account_create_url'), {'username': 'test_stud_username',
                                                                    'email': 'test@mail.com',
                                                                    'password': "test_pass",
                                                                    'password_repeat': "test_pass",
                                                                    'account_type': "1",
                                                                    'student_no': "1234"})

        self.assertRedirects(response, reverse('account_login_url'))

        self.assertTrue(Student.objects.filter(username='test_stud_username', email='test@mail.com').exists())

    def test_teacher_account_create_from_view(self):
        response = self.client.get(reverse('account_create_url'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('account_create_url'), {'username': 'test_teacher_username',
                                                                    'email': 'test@mail.com',
                                                                    'password': "test_pass",
                                                                    'password_repeat': "test_pass",
                                                                    'account_type': "2"})

        self.assertRedirects(response, reverse('account_login_url'))

        self.assertTrue(Teacher.objects.filter(username='test_teacher_username', email='test@mail.com').exists())

    def test_account_create_from_view_with_the_same_username(self):
        response = self.client.get(reverse('account_create_url'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('account_create_url'), {'username': 'teacher_username',
                                                                    'email': 'test@mail.com',
                                                                    'password': "test_pass",
                                                                    'password_repeat': "test_pass",
                                                                    'account_type': "2"})

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'User with given username already exists.')

    def test_account_create_from_view_with_the_same_email(self):
        response = self.client.get(reverse('account_create_url'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('account_create_url'), {'username': 'test_stud_username',
                                                                    'email': 'student@mail.com',
                                                                    'password': "test_pass",
                                                                    'password_repeat': "test_pass",
                                                                    'account_type': "2"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'User with given email already exists.')

    def test_student_account_create_from_view_with_the_same_student_no(self):
        response = self.client.get(reverse('account_create_url'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('account_create_url'), {'username': 'test_stud_username',
                                                                    'email': 'test@mail.com',
                                                                    'password': "test_pass",
                                                                    'password_repeat': "test_pass",
                                                                    'account_type': "1",
                                                                    'student_no': "1111"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Student with given student no already exists.')

    def test_account_create_from_view_with_wrong_forms(self):
        response = self.client.get(reverse('account_create_url'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('account_create_url'), {'username': 'test_stud_username',
                                                                    'email': 'wrong@mail',
                                                                    'password': "test_pass",
                                                                    'password_repeat': "test_pass",
                                                                    'account_type': "1",
                                                                    'student_no': "1111"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter a valid email address.')

    def test_student_account_login_after_create(self):
        response = self.client.get(reverse('account_create_url'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('account_create_url'), {'username': 'test_stud_username',
                                                                    'email': 'test@mail.com',
                                                                    'password': "test_pass",
                                                                    'password_repeat': "test_pass",
                                                                    'account_type': "1",
                                                                    'student_no': "1234"})

        self.assertRedirects(response, reverse('account_login_url'))

        login = self.client.login(username='test_stud_username', password='test_pass')

        self.assertTrue(login)

    def test_account_create_being_logged(self):
        self.client.login(username='student_username', password='student_password')
        response = self.client.get(reverse('account_create_url'))
        self.assertRedirects(response, reverse('index_url'))

        response = self.client.post(reverse('account_create_url'), {'username': 'test_teacher_username',
                                                                    'email': 'test@mail.com',
                                                                    'password': "test_pass",
                                                                    'password_repeat': "test_pass",
                                                                    'account_type': "2"})
        self.assertRedirects(response, reverse('index_url'))

    def test_teacher_account_login_after_create(self):
        response = self.client.get(reverse('account_create_url'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('account_create_url'), {'username': 'test_teacher_username',
                                                                    'email': 'test@mail.com',
                                                                    'password': "test_pass",
                                                                    'password_repeat': "test_pass",
                                                                    'account_type': "2"})

        self.assertRedirects(response, reverse('account_login_url'))

        login = self.client.login(username='test_teacher_username', password='test_pass')

        self.assertTrue(login)

    def test_delete_account(self):
        self.client.login(username='student_username', password='student_password')
        response = self.client.post(reverse('account_delete_url'), follow=True)
        self.assertRedirects(response, reverse('account_login_url'))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Your account was deleted.')

        self.assertFalse(Student.objects.filter(username="student_username").exists())

    def test_delete_account_already_in_team(self):
        student = Student.objects.get(username="student_username")
        user_create_team(student, "test_team")

        self.client.login(username='student_username', password='student_password')
        response = self.client.post(reverse('account_delete_url'), follow=True)
        self.assertRedirects(response, reverse('index_url'))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You can\'t delete your account now. Leave your team first.')

        self.assertTrue(Student.objects.filter(username="student_username").exists())

    # account detail view
    def test_account_detail_view(self):
        self.client.login(username="student_username", password="student_password")
        response = self.client.get(reverse('account_details_url'))
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, "account/details.html")

    # change mail
    def test_change_mail_from_view(self):
        self.client.login(username="student_username", password="student_password")
        response = self.client.get(reverse('account_change_email_url'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('account_change_email_url'), {'new_email': 'test@123.pl'})
        self.assertEqual(response.status_code, 200)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Email changed.')

        self.assertTrue(Student.objects.filter(username='student_username', email='test@123.pl').exists())

    def test_change_mail_from_view_with_invalid_mail(self):
        self.client.login(username="student_username", password="student_password")
        response = self.client.get(reverse('account_change_email_url'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('account_change_email_url'), {'new_email': 'wrong@mail'})
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'Enter a valid email address.')

    def test_change_mail_from_view_email_alredy_in_use(self):
        stud = Student(username='student_username2', email="test@123.pl", student_no=1234)
        stud.set_password('student_password')
        stud.save()

        self.client.login(username="student_username", password="student_password")
        response = self.client.get(reverse('account_change_email_url'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('account_change_email_url'), {'new_email': 'test@123.pl'})
        self.assertEqual(response.status_code, 200)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'User with given email already exists.')

        self.assertFalse(Student.objects.filter(username='student_username', email='test@123.pl').exists())

    # change password
    def test_change_password_from_view(self):
        self.client.login(username="student_username", password="student_password")
        response = self.client.get(reverse('account_change_password_url'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('account_change_password_url'), {'current_password': 'student_password',
                                                                             'new_password': "new_password",
                                                                             'new_password_repeat': "new_password"})
        self.assertEqual(response.status_code, 200)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Password changed.')

        student = Student.objects.get(username="student_username")
        self.assertTrue(student.check_password("new_password"))

    def test_change_password_from_view_invalid_current(self):
        self.client.login(username="student_username", password="student_password")
        response = self.client.get(reverse('account_change_password_url'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('account_change_password_url'), {'current_password': 'wrong_password',
                                                                             'new_password': "new_password",
                                                                             'new_password_repeat': "new_password"})
        self.assertEqual(response.status_code, 200)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Invalid current password.')

        student = Student.objects.get(username="student_username")
        self.assertTrue(student.check_password("student_password"))  # check if still old-one

    def test_change_password_from_view_repeat_not_match(self):
        self.client.login(username="student_username", password="student_password")
        response = self.client.get(reverse('account_change_password_url'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('account_change_password_url'), {'current_password': 'student_password',
                                                                             'new_password': "new_password",
                                                                             'new_password_repeat': "new_password2"})
        self.assertEqual(response.status_code, 200)

        student = Student.objects.get(username="student_username")
        self.assertTrue(student.check_password("student_password"))  # check if still old-one

    # team view
    def test_team_create_from_view(self):
        self.client.login(username="student_username", password="student_password")
        response = self.client.get(reverse('team_create_url'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('team_create_url'), {'name': 'test_team'}, follow=True)

        self.assertRedirects(response, reverse('teams_list_url'))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Team created.')

        self.assertTrue(Team.objects.filter(name='test_team').exists())

    def test_team_create_from_view_with_wrong_forms(self):
        self.client.login(username="student_username", password="student_password")
        response = self.client.get(reverse('team_create_url'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('team_create_url'), {'name': ''}, follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertFalse(Team.objects.filter(name='').exists())

    def test_team_create_from_view_as_teacher(self):
        self.client.login(username="teacher_username", password="teacher_password")

        response = self.client.post(reverse('team_create_url'), {'name': ''}, follow=True)

        self.assertRedirects(response, reverse('index_url'))

        self.assertFalse(Team.objects.filter(name='test_team').exists())

    def test_team_create_already_in_team(self):
        student = Student.objects.get(username="student_username")
        user_create_team(student, "test_team")

        self.client.login(username="student_username", password="student_password")

        response = self.client.post(reverse('team_create_url'), {'name': 'test_team2'}, follow=True)

        self.assertRedirects(response, reverse('teams_list_url'))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You already have a team. Quit your team first.')

        self.assertFalse(Team.objects.filter(name='test_team2').exists())

    def test_team_create_with_name_already_exists(self):
        student2 = Student(username='student2_username', email="student2@mail.com", student_no=1234)
        student2.set_password('student2_password')
        student2.save()

        user_create_team(student2, "test_team")

        self.client.login(username="student_username", password="student_password")

        response = self.client.post(reverse('team_create_url'), {'name': 'test_team'}, follow=True)

        self.assertEqual(response.status_code, 200)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Team with given name already exists.')

    # team join
    def test_team_join(self):
        student = Student.objects.get(username="student_username")
        user_create_team(student, "test_team")

        student2 = Student(username='student2_username', email="student2@mail.com", student_no=1234)
        student2.set_password('student2_password')
        student2.save()

        self.client.login(username="student2_username", password="student2_password")

        response = self.client.post(reverse('team_join_url'), {'team_id': student.team_id}, follow=True)

        self.assertRedirects(response, reverse('teams_list_url'))

        student.team.refresh_from_db()
        student2.refresh_from_db()
        self.assertEqual(student.team_id, student2.team_id)
        self.assertEqual(student.team.second_teammate, student2)

    def test_team_join_as_teacher(self):
        student = Student.objects.get(username="student_username")
        user_create_team(student, "test_team")

        self.client.login(username="teacher_username", password="teacher_password")

        response = self.client.post(reverse('team_join_url'), {'team_id': student.team_id}, follow=True)

        self.assertRedirects(response, reverse('index_url'))

    def test_team_join_when_already_in_team(self):
        student = Student.objects.get(username="student_username")
        user_create_team(student, "test_team")

        student2 = Student(username='student2_username', email="student2@mail.com", student_no=1234)
        student2.set_password('student2_password')
        student2.save()

        user_create_team(student2, "test_team2")

        self.client.login(username="student2_username", password="student2_password")

        response = self.client.post(reverse('team_join_url'), {'team_id': student.team_id}, follow=True)

        self.assertRedirects(response, reverse('teams_list_url'))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You already have a team. Quit your team first.')

    def test_team_join_full_team(self):
        student = Student.objects.get(username="student_username")
        user_create_team(student, "test_team")
        team = Team.objects.get(name="test_team")

        student2 = Student(username='student2_username', email="student2@mail.com", student_no=1234)
        student2.set_password('student2_password')
        student2.save()

        user_join_team(student2, team)

        student3 = Student(username='student3_username', email="student3@mail.com", student_no=12345)
        student3.set_password('student3_password')
        student3.save()

        self.client.login(username="student3_username", password="student3_password")

        response = self.client.post(reverse('team_join_url'), {'team_id': student.team_id}, follow=True)

        self.assertRedirects(response, reverse('teams_list_url'))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'The selected team is already full.')

    def test_team_join_team_not_exist(self):
        self.client.login(username="student_username", password="student_password")

        response = self.client.post(reverse('team_join_url'), {'team_id': 1}, follow=True)

        self.assertRedirects(response, reverse('teams_list_url'))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Invalid team.')

    # team details
    def test_team_details_view_user_in_team(self):
        student = Student.objects.get(username="student_username")
        user_create_team(student, "test_team")

        self.client.login(username="student_username", password="student_password")

        response = self.client.get(reverse('team_details_url', kwargs={'id': student.team_id}), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'team/details.html')

    def test_team_details_view_user_not_in_team(self):
        student = Student.objects.get(username="student_username")
        user_create_team(student, "test_team")

        student2 = Student(username='student2_username', email="student2@mail.com", student_no=1234)
        student2.set_password('student2_password')
        student2.save()

        self.client.login(username="student2_username", password="student2_password")

        response = self.client.get(reverse('team_details_url', kwargs={'id': student.team_id}), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'team/details.html')

    def test_team_details_team_not_exist(self):
        self.client.login(username="student_username", password="student_password")

        response = self.client.get(reverse('team_details_url', kwargs={'id': 123}), follow=True)

        self.assertRedirects(response, reverse('teams_list_url'))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Invalid team.')

    # team leave
    def test_team_leave_only_one_student(self):
        student = Student.objects.get(username="student_username")
        user_create_team(student, "test_team")

        self.client.login(username="student_username", password="student_password")

        response = self.client.post(reverse('team_leave_url'), {'team_id': student.team_id}, follow=True)

        self.assertRedirects(response, reverse('teams_list_url'))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You left the team.')

        student.refresh_from_db()

        self.assertEqual(student.team, None)
        self.assertFalse(Team.objects.filter(name="test_team").exists())

    def test_team_leave_first_student(self):
        student = Student.objects.get(username="student_username")
        user_create_team(student, "test_team")

        student2 = Student(username='student2_username', email="student2@mail.com", student_no=1234)
        student2.set_password('student2_password')
        student2.save()

        team = Team.objects.get(name="test_team")

        user_join_team(student2, team)

        self.client.login(username="student_username", password="student_password")

        response = self.client.post(reverse('team_leave_url'), {'team_id': student.team_id}, follow=True)

        self.assertRedirects(response, reverse('teams_list_url'))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You left the team.')

        student.refresh_from_db()
        student2.refresh_from_db()
        team.refresh_from_db()

        self.assertEqual(student.team, None)
        self.assertTrue(Team.objects.filter(name="test_team").exists())

        self.assertEqual(team.first_teammate, student2)
        self.assertEqual(team.second_teammate, None)
        self.assertEqual(student2.team, team)

    def test_team_leave_second_student(self):
        student = Student.objects.get(username="student_username")
        user_create_team(student, "test_team")

        team = Team.objects.get(name="test_team")

        student2 = Student(username='student2_username', email="student2@mail.com", student_no=1234)
        student2.set_password('student2_password')
        student2.save()

        user_join_team(student2, team)

        self.client.login(username="student2_username", password="student2_password")

        response = self.client.post(reverse('team_leave_url'), {'team_id': student.team_id}, follow=True)

        self.assertRedirects(response, reverse('teams_list_url'))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You left the team.')

        student.refresh_from_db()
        student2.refresh_from_db()
        team.refresh_from_db()

        self.assertEqual(student2.team, None)
        self.assertTrue(Team.objects.filter(name="test_team").exists())

        self.assertEqual(team.first_teammate, student)
        self.assertEqual(team.second_teammate, None)
        self.assertEqual(student.team, team)

    def test_team_leave_as_teacher(self):
        student = Student.objects.get(username="student_username")
        user_create_team(student, "test_team")

        self.client.login(username="teacher_username", password="teacher_password")

        response = self.client.post(reverse('team_join_url'), {'team_id': student.team_id}, follow=True)

        self.assertRedirects(response, reverse('index_url'))

    def test_team_leave_user_not_in_team(self):
        student = Student.objects.get(username="student_username")
        user_create_team(student, "test_team")

        student2 = Student(username='student2_username', email="student2@mail.com", student_no=1234)
        student2.set_password('student2_password')
        student2.save()

        self.client.login(username="student2_username", password="student2_password")

        response = self.client.post(reverse('team_leave_url'), {'team_id': student.team_id}, follow=True)

        self.assertRedirects(response, reverse('teams_list_url'))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You must be in a team in order to quit it.')

    def test_team_leave_student_assigned(self):
        student = Student.objects.get(username="student_username")
        user_create_team(student, "test_team")
        student.status = Student.STUDENT_STATUS_ASSIGNED
        student.save()

        self.client.login(username="student_username", password="student_password")

        response = self.client.post(reverse('team_leave_url'), {'team_id': student.team_id}, follow=True)

        self.assertRedirects(response, reverse('teams_list_url'))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You can\'t leave a team assigned to a project.')

    # project view
    def test_project_create_from_view(self):
        self.client.login(username="teacher_username", password="teacher_password")
        response = self.client.get(reverse('project_create_url'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('project_create_url'), {'name': 'test_project',
                                                                    'description': 'test_project_description'},
                                    follow=True)

        self.assertRedirects(response, reverse('projects_list_url'))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Project created.')

        self.assertTrue(Project.objects.filter(name='test_project', description='test_project_description').exists())

    def test_project_create_from_view_as_student(self):
        self.client.login(username="student_username", password="student_password")

        response = self.client.post(reverse('project_create_url'), {'name': 'test_project',
                                                                    'description': 'test_project_description'},
                                    follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('index_url'))

        # messages = list(response.context['messages'])
        # self.assertEqual(len(messages), 1)
        # self.assertEqual(str(messages[0]), 'Only teachers are allowed to create projects.')

        self.assertFalse(Project.objects.filter(name='test_project', description='test_project_description').exists())

    def test_project_create_from_view_with_wrong_forms(self):
        self.client.login(username="teacher_username", password="teacher_password")
        response = self.client.get(reverse('project_create_url'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('project_create_url'), {'name': 'test_project',
                                                                    'description': ''},
                                    follow=True)

        self.assertEqual(response.status_code, 200)

        self.assertFalse(Project.objects.filter(name='test_project').exists())

    def test_project_join(self):
        teacher = Teacher.objects.get(username="teacher_username")
        student = Student.objects.get(username="student_username")

        user_create_project(teacher, "test_project", "test_project_description")
        user_create_team(student, "test_team")

        project = Project.objects.get(name="test_project")

        self.client.login(username="student_username", password="student_password")
        response = self.client.post(reverse('project_join_url'), {'project_id': project.id}, follow=True)

        self.assertRedirects(response, reverse('projects_list_url'))

        project.refresh_from_db()

        self.assertTrue(project.all_teams.filter(name=student.team.name).exists())

    def test_project_join_not_exist(self):
        student = Student.objects.get(username="student_username")

        user_create_team(student, "test_team")

        self.client.login(username="student_username", password="student_password")
        response = self.client.post(reverse('project_join_url'), {'project_id': 1}, follow=True)

        self.assertRedirects(response, reverse('projects_list_url'))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Invalid project.')

    def test_project_join_as_teacher(self):
        teacher = Teacher.objects.get(username="teacher_username")
        user_create_project(teacher, "test_project", "test_project_description")

        project = Project.objects.get(name="test_project")

        self.client.login(username="teacher_username", password="teacher_password")
        response = self.client.post(reverse('project_join_url'), {'project_id': project.id}, follow=True)

        self.assertRedirects(response, reverse('index_url'))

    def test_project_join_user_not_in_team(self):
        teacher = Teacher.objects.get(username="teacher_username")

        user_create_project(teacher, "test_project", "test_project_description")

        project = Project.objects.get(name="test_project")

        self.client.login(username="student_username", password="student_password")
        response = self.client.post(reverse('project_join_url'), {'project_id': project.id}, follow=True)

        self.assertRedirects(response, reverse('projects_list_url'))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You have no team. Join or create your own team first.')

    def test_project_join_team_already_in_project(self):
        teacher = Teacher.objects.get(username="teacher_username")
        student = Student.objects.get(username="student_username")

        user_create_project(teacher, "test_project", "test_project_description")
        user_create_project(teacher, "test_project2", "test_project_description2")
        user_create_team(student, "test_team")

        project = Project.objects.get(name="test_project")
        project2 = Project.objects.get(name="test_project2")

        self.client.login(username="student_username", password="student_password")
        self.client.post(reverse('project_join_url'), {'project_id': project.id}, follow=True)

        response = self.client.post(reverse('project_join_url'), {'project_id': project2.id}, follow=True)

        self.assertRedirects(response, reverse('projects_list_url'))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Your team is already in the project queue.')

    def test_project_join_already_assigned(self):
        teacher = Teacher.objects.get(username="teacher_username")
        student = Student.objects.get(username="student_username")

        user_create_project(teacher, "test_project", "test_project_description")
        user_create_team(student, "test_team")

        team = Team.objects.create(name="test_team2")

        project = Project.objects.get(name="test_project")
        project.assigned_team = team
        project.save()

        self.client.login(username="student_username", password="student_password")
        response = self.client.post(reverse('project_join_url'), {'project_id': project.id}, follow=True)

        self.assertRedirects(response, reverse('projects_list_url'))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'This project has already an assigned team.')

    def test_project_leave(self):
        teacher = Teacher.objects.get(username="teacher_username")
        student = Student.objects.get(username="student_username")

        user_create_project(teacher, "test_project", "test_project_description")
        user_create_team(student, "test_team")

        project = Project.objects.get(name="test_project")

        self.client.login(username="student_username", password="student_password")
        self.client.post(reverse('project_join_url'), {'project_id': project.id}, follow=True)

        self.assertTrue(project.all_teams.filter(name=student.team.name).exists())

        self.client.post(reverse('project_leave_url'), {'project_id': project.id}, follow=True)

        self.assertFalse(project.all_teams.filter(name=student.team.name).exists())

    def test_project_leave_not_exist(self):
        self.client.login(username="student_username", password="student_password")

        response = self.client.post(reverse('project_leave_url'), {'project_id': 1}, follow=True)

        self.assertRedirects(response, reverse('projects_list_url'))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Invalid project.')

    def test_project_leave_as_teacher(self):
        teacher = Teacher.objects.get(username="teacher_username")

        user_create_project(teacher, "test_project", "test_project_description")

        project = Project.objects.get(name="test_project")

        self.client.login(username="teacher_username", password="teacher_password")
        response = self.client.post(reverse('project_leave_url'), {'project_id': project.id}, follow=True)

        self.assertRedirects(response, reverse('index_url'))

    def test_project_leave_user_not_in_team(self):
        teacher = Teacher.objects.get(username="teacher_username")

        user_create_project(teacher, "test_project", "test_project_description")

        project = Project.objects.get(name="test_project")

        self.client.login(username="student_username", password="student_password")
        response = self.client.post(reverse('project_leave_url'), {'project_id': project.id}, follow=True)

        self.assertRedirects(response, reverse('projects_list_url'))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You have no team. Join or create your own team first.')

    def test_project_leave_already_assigned(self):
        student = Student.objects.get(username="student_username")
        teacher = Teacher.objects.get(username="teacher_username")

        user_create_project(teacher, "test_project", "test_project_description")
        user_create_team(student, "test_team")

        project = Project.objects.get(name="test_project")
        user_team_join_project(student, project)

        team = Team.objects.create(name="test_team2")
        project.assigned_team = team
        project.save()

        self.client.login(username="student_username", password="student_password")
        response = self.client.post(reverse('project_leave_url'), {'project_id': project.id}, follow=True)
    
        self.assertRedirects(response, reverse('projects_list_url'))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'This project has already an assigned team.')

    def test_project_leave_team_not_in_project_queue(self):
        teacher = Teacher.objects.get(username="teacher_username")
        student = Student.objects.get(username="student_username")

        user_create_project(teacher, "test_project", "test_project_description")
        user_create_team(student, "test_team")

        project = Project.objects.get(name="test_project")

        self.client.login(username="student_username", password="student_password")

        response = self.client.post(reverse('project_leave_url'), {'project_id': project.id}, follow=True)

        self.assertRedirects(response, reverse('projects_list_url'))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Your team is not in the project queue.')

    def test_project_details(self):
        teacher = Teacher.objects.get(username="teacher_username")
        student = Student.objects.get(username="student_username")

        user_create_project(teacher, "test_project", "test_project_description")
        user_create_team(student, "test_team")

        project = Project.objects.get(name="test_project")

        self.client.login(username="student_username", password="student_password")

        response = self.client.get(reverse('project_details_url', kwargs={'id': project.id}))

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "test_project_description")

    def test_project_details_not_exists(self):
        student = Student.objects.get(username="student_username")

        user_create_team(student, "test_team")

        self.client.login(username="student_username", password="student_password")

        response = self.client.get(reverse('project_details_url', kwargs={'id': 123}), follow=True)

        self.assertRedirects(response, reverse('projects_list_url'))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Invalid project.')

    def test_project_delete(self):
        teacher = Teacher.objects.get(username="teacher_username")

        user_create_project(teacher, "test_project", "test_project_description")

        project = Project.objects.get(name="test_project")

        self.client.login(username="teacher_username", password="teacher_password")
        response = self.client.post(reverse('project_delete_url'), {'project_id': project.id}, follow=True)

        self.assertRedirects(response, reverse('projects_list_url'))
        self.assertFalse(Project.objects.filter(name="test_project").exists())

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Project deleted.')

    def test_project_delete_with_assigned_team(self):
        teacher = Teacher.objects.get(username="teacher_username")
        student = Student.objects.get(username="student_username")

        user_create_project(teacher, "test_project", "test_project_description")
        user_create_team(student, "test_team")

        project = Project.objects.get(name="test_project")

        project.assigned_team = Team.objects.get(name="test_team")
        project.save()

        self.client.login(username="teacher_username", password="teacher_password")
        response = self.client.post(reverse('project_delete_url'), {'project_id': project.id}, follow=True)

        self.assertRedirects(response, reverse('projects_list_url'))
        self.assertTrue(Project.objects.filter(name="test_project").exists())

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You cannot delete a project that has an assigned team.')

    def test_project_delete_not_exist(self):
        self.client.login(username="teacher_username", password="teacher_password")
        response = self.client.post(reverse('project_delete_url'), {'project_id': 1}, follow=True)

        self.assertRedirects(response, reverse('projects_list_url'))

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Invalid project.')

    def test_project_delete_as_student(self):
        teacher = Teacher.objects.get(username="teacher_username")
        user_create_project(teacher, "test_project", "test_project_description")

        project = Project.objects.get(name="test_project")

        self.client.login(username="student_username", password="student_password")
        response = self.client.post(reverse('project_delete_url'), {'project_id': project.id}, follow=True)

        self.assertRedirects(response, reverse('index_url'))

        self.assertTrue(Project.objects.filter(name="test_project").exists())

    def test_team_assign(self):
        teacher = Teacher.objects.get(username="teacher_username")
        student = Student.objects.get(username="student_username")

        student2 = Student(username='student2_username', email="student2@mail.com", student_no=1234)
        student2.set_password('student2_password')
        student2.save()

        user_create_project(teacher, "test_project", "test_project_description")
        user_create_team(student, "test_team")

        team = Team.objects.get(name="test_team")
        user_join_team(student2, team)

        project = Project.objects.get(name="test_project")

        user_team_join_project(student2, project)
        project.refresh_from_db()

        self.assertTrue(project.all_teams.filter(name="test_team").exists())

        self.client.login(username="teacher_username", password="teacher_password")
        response = self.client.post(reverse('team_assign_url'), follow=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Assigning completed. Assigned teams to 1 projects.')

        team.refresh_from_db()
        project.refresh_from_db()
        student.refresh_from_db()
        student2.refresh_from_db()

        self.assertRedirects(response, reverse('projects_list_url'))
        self.assertFalse(project.all_teams.filter(name="test_team").exists())
        self.assertEqual(project.assigned_team, team)
        self.assertEqual(team.project, project)
        self.assertTrue(project.all_teams.count() == 0)
        self.assertEqual(project.status, Project.PROJECT_STATUS_CLOSED)
        self.assertEqual(student.status, Student.STUDENT_STATUS_ASSIGNED)
        self.assertEqual(student2.status, Student.STUDENT_STATUS_ASSIGNED)

    def test_team_assign_with_no_ready_teams(self):
        teacher = Teacher.objects.get(username="teacher_username")
        student = Student.objects.get(username="student_username")

        user_create_project(teacher, "test_project", "test_project_description")
        user_create_team(student, "test_team")

        project = Project.objects.get(name="test_project")

        user_team_join_project(student, project)
        project.refresh_from_db()

        self.assertTrue(project.all_teams.filter(name="test_team").exists())

        self.client.login(username="teacher_username", password="teacher_password")
        response = self.client.post(reverse('team_assign_url'), follow=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Assigning completed. Assigned teams to 0 projects.')

    def test_project_edit_from_view(self):
        teacher = Teacher.objects.get(username="teacher_username")
        project = user_create_project(teacher, "test_project", "test_project_description")

        self.client.login(username="teacher_username", password="teacher_password")

        response = self.client.get(reverse('project_edit_url', kwargs={'id': project.id}))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('project_edit_url', kwargs={'id': project.id}), {'name': 'new_name',
                                                                                             'description': 'new_desc'},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('project_details_url', kwargs={'id': project.id}))
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Project edit success.')
        project = Project.objects.get(pk=project.pk)
        self.assertEqual(project.name, 'new_name')
        self.assertEqual(project.description, 'new_desc')

    def test_project_edit_from_view_invalid_project(self):
        Teacher.objects.get(username="teacher_username")

        self.client.login(username="teacher_username", password="teacher_password")

        response = self.client.get(reverse('project_edit_url', kwargs={'id': '0'}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('projects_list_url'))

        response = self.client.post(reverse('project_edit_url', kwargs={'id': '0'}), {'name': 'asd',
                                                                                      'description': 'desc'},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('projects_list_url'))
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Invalid project.')

    def test_project_edit_from_view_invalid_form(self):
        teacher = Teacher.objects.get(username="teacher_username")
        project = user_create_project(teacher, "test_project", "test_project_description")

        self.client.login(username="teacher_username", password="teacher_password")

        response = self.client.post(reverse('project_edit_url', kwargs={'id': project.id}), {'name': 'asd',
                                                                                             'description': ''})
        self.assertEqual(response.status_code, 200)
        project = Project.objects.get(pk=project.pk)
        self.assertTrue(project.description, 'test_project_description')

    def test_project_edit_from_view_other_author(self):
        teacher = Teacher.objects.get(username="teacher_username")
        project = user_create_project(teacher, "test_project", "test_project_description")

        self.client.login(username="teacher_username_2", password="teacher_password")

        response = self.client.post(reverse('project_edit_url', kwargs={'id': project.id}), {'name': 'asd',
                                                                                             'description': 'desc'})
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Only author can edit project.')

    def test_project_edit_from_view_unique_name(self):
        teacher = Teacher.objects.get(username="teacher_username")
        user_create_project(teacher, "test_project", "test_project_description")
        project2 = user_create_project(teacher, "test_project_2", "test_project_2_description")

        self.client.login(username="teacher_username", password="teacher_password")

        response = self.client.post(reverse('project_edit_url', kwargs={'id': project2.id}),
                                    {'name': 'test_project', 'description': 'test_project_2_description'})
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Project with given name already exists.')

    # test wrong path
    def test_error_view(self):
        response = self.client.get('/wrong_path/')
        self.assertEqual(response.status_code, 404)

        self.assertTemplateUsed(response, 'http_error.html')


# MODELS TESTS (db integrity)

class ModelsTests(TestCase):

    def test_create_student_with_the_same_username(self):
        user = Student(username='test_username', student_no=1234)
        user.set_password('test_password')
        user.save()

        user = Student(username='test_username', student_no=1212)
        user.set_password('test_password')
        with self.assertRaises(IntegrityError):
            user.save()

    def test_create_student_with_the_same_student_no(self):
        user = Student(username='test_username', student_no=1234)
        user.set_password('test_password')
        user.save()

        user = Student(username='test_username2', student_no=1234)
        user.set_password('test_password')
        with self.assertRaises(IntegrityError):
            user.save()


# FORMS TESTS

class FormsTests(TestCase):

    def test_account_create_form(self):
        data = {'username': 'test_stud_username',
                'email': 'test@mail.com',
                'password': "test_pass",
                'password_repeat': "test_pass",
                'account_type': "1",
                'student_no': "1234"}
        form = AccountCreateForm(data=data)
        self.assertTrue(form.is_valid())

    def test_account_create_form_pass_repeat(self):
        data = {'username': 'test_stud_username',
                'email': 'test@mail.com',
                'password': "test_pass",
                'password_repeat': "test_pass2",
                'account_type': "1",
                'student_no': "1234"}
        form = AccountCreateForm(data=data)
        self.assertFalse(form.is_valid())

    def test_account_create_form_no_stud_no(self):
        data = {'username': 'test_stud_username',
                'email': 'test@mail.com',
                'password': "test_pass",
                'password_repeat': "test_pass",
                'account_type': "1", }
        form = AccountCreateForm(data=data)
        self.assertFalse(form.is_valid())

    def test_account_create_form_stud_no_not_a_number(self):
        data = {'username': 'test_stud_username',
                'email': 'test@mail.com',
                'password': "test_pass",
                'password_repeat': "test_pass",
                'account_type': "1",
                'student_no': "wrong_number"}
        form = AccountCreateForm(data=data)
        self.assertFalse(form.is_valid())

    def test_account_change_password(self):
        data = {'current_password': "1234",
                'new_password': "new_pass",
                'new_password_repeat': "new_pass"}
        form = AccountChangePasswordForm(data=data)
        self.assertTrue(form.is_valid())

    def test_account_change_password_not_matching(self):
        data = {'current_password': "1234",
                'new_password': "new_pass",
                'new_password_repeat': "wrong_pass"}
        form = AccountChangePasswordForm(data=data)
        self.assertFalse(form.is_valid())

    def test_account_change_email(self):
        data = {'new_email': "test@mail.com"}
        form = AccountChangeEmailForm(data=data)
        self.assertTrue(form.is_valid())

    def test_account_change_email_invaild(self):
        data = {'new_email': "test@mail"}
        form = AccountChangeEmailForm(data=data)
        self.assertFalse(form.is_valid())
