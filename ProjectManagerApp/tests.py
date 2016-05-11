from django.test import TestCase
from .models import User, Student, Teacher, Team, Project
from .services import *
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from .forms import AccountCreateForm

# Create your tests here.


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

    def test_create_student_with_the_same_studnet_no(self):
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


class ManageTeamsServicesTests(TestCase):

    def test_create_team(self):
        user = Student(username='test_username', email='test@mail.com', student_no="1234")
        user.save()

        user_create_team(user, "test_team")

        self.assertTrue(Team.objects.filter(name="test_team").exists())
        team = Team.objects.get(name="test_team")
        self.assertEqual(team.first_teammate, user)
        self.assertEqual(user.team, team)

    def test_leave_one_person_team(self):
        user = Student(username='test_username', email='test@mail.com', student_no="1234")
        user.save()

        user_create_team(user, "test_team")
        self.assertTrue(Team.objects.filter(name="test_team").exists())
        team = Team.objects.get(name="test_team")
        self.assertEqual(user.team, team)

        user_team_leave(user)
        self.assertFalse(Team.objects.filter(name="test_team").exists())
        self.assertEqual(user.team, None)

    def test_leave_first_from_two_persons_team(self):
        user = Student(username='test_username', email='test@mail.com', student_no="1234")
        user.save()

        user2 = Student(username='test_username2', email='test2@mail.com', student_no="1212")
        user2.save()

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
        user = Student(username='test_username', email='test@mail.com', student_no="1234")
        user.save()

        user2 = Student(username='test_username2', email='test2@mail.com', student_no="1212")
        user2.save()

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


class ManageProjectsServicesTests(TestCase):

    project_name = "test_project_name"
    project_descripton = "test_project_descrption"

    def test_create_project_as_student(self):
        user = Student()

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
        self.assertTrue(Project.objects.filter(name=self.project_name).exists())

    def test_delete_project(self):
        user = Teacher()
        user.save()
        project = user_create_project(user, self.project_name, self.project_descripton)
        project.save()

        self.assertTrue(Project.objects.filter(name=self.project_name).exists())

        user_delete_project(user, project)

        self.assertFalse(Project.objects.filter(name=self.project_name).exists())

    #TODO
    def test_join_project(self):
        user = Teacher()
        user.save()
        project = user_create_project(user, self.project_name, self.project_descripton)
        project.save()

        self.assertTrue(Project.objects.filter(name=self.project_name).exists())

        account_create_student("1234", "test_student_username", "test@mail.com", "test_pass")

        self.assertTrue(Student.objects.filter(username='test_student_username', email='test@mail.com').exists())
        user2 = Student.objects.get(username='test_student_username')

        user_create_team(user2, "test_team")

        self.assertTrue(Team.objects.filter(name="test_team").exists())
        team = Team.objects.get(name="test_team")

        user_team_join_project(user2, project)

        self.assertTrue(Project.objects.filter(name=self.project_name).exists())
        project.refresh_from_db()
        self.assertTrue(project.all_teams.filter(name=user2.team.name).exists())

    #TODO
    def test_join_project_as_a_teacher(self):
        user = Teacher()
        user.save()
        project = user_create_project(user, self.project_name, self.project_descripton)
        project.save()

        self.assertTrue(Project.objects.filter(name=self.project_name).exists())

        with self.assertRaisesMessage(MustBeStudent, ""):
            user_team_join_project(user, project)

    #TODO
    def test_leave_project_as_a_teacher(self):
        user = Teacher()
        user.save()
        project = user_create_project(user, self.project_name, self.project_descripton)
        project.save()

        self.assertTrue(Project.objects.filter(name=self.project_name).exists())

        with self.assertRaisesMessage(MustBeStudent, ""):
            user_team_leave_project(user, project)


class ViewsTests(TestCase):

    def setUp(self):
        stud = Student(username='student_username', email="student@mail.com", student_no=1111)
        stud.set_password('student_password')
        stud.save()

        teach = Teacher(username='teacher_username', email="teacher@mail.com")
        teach.set_password('teacher_password')
        teach.save()


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


    # login tests
    def test_student_login(self):
        login = self.client.login(username='student_username', password='student_password')
        self.assertTrue(login)

    def test_teacher_login(self):
        login = self.client.login(username='teacher_username', password='teacher_password')
        self.assertTrue(login)

    def test_student_login_from_view(self):
        response = self.client.post('/account/login/', {'username': 'student_username', 'password': 'student_password'})
        self.assertRedirects(response, '/index/')

        response = self.client.get('/teams/')
        self.assertEqual(response.status_code, 200)

    def test_teacher_login_from_view(self):
        response = self.client.post('/account/login/', {'username': 'teacher_username', 'password': 'teacher_password'})
        self.assertRedirects(response, '/index/')

        response = self.client.get('/teams/')
        self.assertEqual(response.status_code, 200)

    def test_user_login_from_view_with_next(self):
        response = self.client.post('/account/login/?next=/projects/', {'username': 'student_username', 'password': 'student_password'})
        self.assertRedirects(response, '/projects/')

    def test_not_existing_user_login_from_view(self):
        response = self.client.post('/account/login/', {'username': 'test', 'password': 'test_pass'})
        self.assertEqual(response.status_code, 200)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Username or password is incorrect. Try again.')

    def test_student_wrong_password_login_from_view(self):
        response = self.client.post('/account/login/', {'username': 'student_username', 'password': 'wrong_pass'})
        self.assertEqual(response.status_code, 200)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Username or password is incorrect. Try again.')

    def test_teacher_wrong_password_login_from_view(self):
        response = self.client.post('/account/login/', {'username': 'teacher_username', 'password': 'wrong_pass'})
        self.assertEqual(response.status_code, 200)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Username or password is incorrect. Try again.')

    def test_login_as_authenticated_user(self):
        self.client.login(username='student_username', password='student_password')

        response = self.client.get('/account/login/')
        self.assertRedirects(response, '/index/')

        response = self.client.post('/account/login/', {'username': 'test', 'password': 'test_pass'})
        self.assertRedirects(response, '/index/')


    # logout tests
    def test_logout(self):
        self.client.login(username='student_username', password='student_password')
        response = self.client.get('/account/logout/')

        response = self.client.get('/projects/')
        self.assertRedirects(response, '/account/login/?next=/projects/')


    # account create tests
    def test_student_account_create_from_view(self):
        response = self.client.get('/account/create/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/account/create/',{ 'username': 'test_stud_username',
                                                         'email': 'test@mail.com',
                                                         'password': "test_pass",
                                                         'password_repeat': "test_pass",
                                                         'account_type': "1",
                                                         'student_no': "1234"})

        self.assertRedirects(response, '/account/login/')

        self.assertTrue(Student.objects.filter(username='test_stud_username', email='test@mail.com').exists())

    def test_teacher_account_create_from_view(self):
        response = self.client.get('/account/create/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/account/create/',{ 'username': 'test_teacher_username',
                                                         'email': 'test@mail.com',
                                                         'password': "test_pass",
                                                         'password_repeat': "test_pass",
                                                         'account_type': "2"})

        self.assertRedirects(response, '/account/login/')

        self.assertTrue(Teacher.objects.filter(username='test_teacher_username', email='test@mail.com').exists())

    def test_account_create_from_view_with_the_same_username(self):
        response = self.client.get('/account/create/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/account/create/',{ 'username': 'teacher_username',
                                                         'email': 'test@mail.com',
                                                         'password': "test_pass",
                                                         'password_repeat': "test_pass",
                                                         'account_type': "2"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'User with given username already exists.')

    def test_account_create_from_view_with_the_same_email(self):
        response = self.client.get('/account/create/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/account/create/',{ 'username': 'test_stud_username',
                                                         'email': 'student@mail.com',
                                                         'password': "test_pass",
                                                         'password_repeat': "test_pass",
                                                         'account_type': "2"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'User with given email already exists.')

    def test_student_account_create_from_view_with_the_same_student_no(self):
        response = self.client.get('/account/create/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/account/create/',{ 'username': 'test_stud_username',
                                                         'email': 'test@mail.com',
                                                         'password': "test_pass",
                                                         'password_repeat': "test_pass",
                                                         'account_type': "1",
                                                         'student_no': "1111"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Student with given student no already exists.')


    # TODO
    def test_account_create_from_view_with_wrong_forms(self):
        response = self.client.get('/account/create/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/account/create/',{ 'username': 'test_stud_username',
                                                         'email': 'wrong@mail',
                                                         'password': "test_pass",
                                                         'password_repeat': "test_pass",
                                                         'account_type': "1",
                                                         'student_no': "1111"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter a valid email address.')

    def test_student_account_login_after_create(self):
        response = self.client.get('/account/create/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/account/create/',{ 'username': 'test_stud_username',
                                                         'email': 'test@mail.com',
                                                         'password': "test_pass",
                                                         'password_repeat': "test_pass",
                                                         'account_type': "1",
                                                         'student_no': "1234"})

        self.assertRedirects(response, '/account/login/')

        login = self.client.login(username='test_stud_username', password='test_pass')

        self.assertTrue(login)

    def test_account_create_being_logged(self):
        self.client.login(username='student_username', password='student_password')
        response = self.client.get('/account/create/')
        self.assertRedirects(response, '/index/')

        response = self.client.post('/account/create/',{ 'username': 'test_teacher_username',
                                                         'email': 'test@mail.com',
                                                         'password': "test_pass",
                                                         'password_repeat': "test_pass",
                                                         'account_type': "2"})
        self.assertRedirects(response, '/index/')

    def test_teacher_account_login_after_create(self):
        response = self.client.get('/account/create/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/account/create/',{ 'username': 'test_teacher_username',
                                                         'email': 'test@mail.com',
                                                         'password': "test_pass",
                                                         'password_repeat': "test_pass",
                                                         'account_type': "2"})

        self.assertRedirects(response, '/account/login/')

        login = self.client.login(username='test_teacher_username', password='test_pass')

        self.assertTrue(login)




class ModelsTests(TestCase):

    def test_create_studnet_with_the_same_username(self):
        user = Student(username='test_username', student_no=1234)
        user.set_password('test_password')
        user.save()

        user = Student(username='test_username', student_no=1212)
        user.set_password('test_password')
        with self.assertRaises(IntegrityError):
            user.save()

    def test_create_studnet_with_the_same_student_no(self):
        user = Student(username='test_username', student_no=1234)
        user.set_password('test_password')
        user.save()

        user = Student(username='test_username2', student_no=1234)
        user.set_password('test_password')
        with self.assertRaises(IntegrityError):
            user.save()


class FormsTests(TestCase):

    def test_account_create_form(self):
        data = { 'username': 'test_stud_username',
                 'email': 'test@mail.com',
                 'password': "test_pass",
                 'password_repeat': "test_pass",
                 'account_type': "1",
                 'student_no': "1234"}
        form = AccountCreateForm(data=data)
        self.assertTrue(form.is_valid())

    def test_account_create_form_pass_repeat(self):
        data = { 'username': 'test_stud_username',
                 'email': 'test@mail.com',
                 'password': "test_pass",
                 'password_repeat': "test_pass2",
                 'account_type': "1",
                 'student_no': "1234"}
        form = AccountCreateForm(data=data)
        self.assertFalse(form.is_valid())

    def test_account_create_form_no_stud_no(self):
        data = { 'username': 'test_stud_username',
                 'email': 'test@mail.com',
                 'password': "test_pass",
                 'password_repeat': "test_pass",
                 'account_type': "1",}
        form = AccountCreateForm(data=data)
        self.assertFalse(form.is_valid())

    def test_account_create_form_stud_no_not_a_number(self):
        data = { 'username': 'test_stud_username',
                 'email': 'test@mail.com',
                 'password': "test_pass",
                 'password_repeat': "test_pass",
                 'account_type': "1",
                 'student_no': "wrong_number"}
        form = AccountCreateForm(data=data)
        self.assertFalse(form.is_valid())