from ProjectManagerApp.exceptions import UserAlreadyInTeam, MustBeStudent, UserNotInTeam, MustBeTeacher, \
    ProjectHasAssignedTeam, UserWithGivenUsernameAlreadyExists, StudentWithGivenStudentNoAlreadyExists, \
    TeamAlreadyInProjectQueue, TeamNotInProjectQueue, UserWithGivenEmailAlreadyExists, InvalidPassword, \
    TeamIsFull, UserAssignedToProject
from ProjectManagerApp.models import Student, Team, Teacher, Project, UserBase
import random


def user_join_team(user, team):
    if not isinstance(user, Student):
        raise MustBeStudent

    if user.team:
        raise UserAlreadyInTeam

    if team.first_teammate and team.second_teammate:
        raise TeamIsFull

    if team.first_teammate is None:
        team.first_teammate = user
    elif team.second_teammate is None:
        team.second_teammate = user
    team.save(force_update=True)

    user.team = team
    user.save()


def user_create_team(user, team_name):
    if not isinstance(user, Student):
        raise MustBeStudent

    if user.team:
        raise UserAlreadyInTeam

    team = Team()
    team.name = team_name
    team.save()

    user_join_team(user, team)

    return team


def user_team_leave(user):
    if not isinstance(user, Student):
        raise MustBeStudent

    if not user.team:
        raise UserNotInTeam

    if user.status == Student.STUDENT_STATUS_ASSIGNED:
        raise UserAssignedToProject

    team = user.team

    if team.first_teammate == user:
        team.first_teammate = None
        if team.second_teammate is not None:
            team.first_teammate = team.second_teammate
            team.second_teammate = None
    elif team.second_teammate == user:
        team.second_teammate = None

    if team.first_teammate is None and team.second_teammate is None:
        team.delete()
    else:
        team.save(force_update=True)

    user.team = None
    user.save()

    if team.first_teammate is not None:
        team.first_teammate.team.refresh_from_db()


def assign_team_to_project(project):
    ready_teams = project.all_teams.exclude(first_teammate__isnull=True).exclude(second_teammate__isnull=True)
    count = ready_teams.count()
    if count:
        index = random.randint(0, count - 1)
        result = ready_teams.all()[index]
        project.assigned_team = result
        if result.first_teammate and result.second_teammate:
            result.first_teammate.status = Student.STUDENT_STATUS_ASSIGNED
            result.second_teammate.status = Student.STUDENT_STATUS_ASSIGNED
            result.first_teammate.save(force_update=True)
            result.second_teammate.save(force_update=True)
            project.status = Project.PROJECT_STATUS_CLOSED
            for team in project.all_teams.all():
                project.all_teams.remove(team)
            project.save(force_update=True)
            return 1


def assign_teams_to_projects(user):
    if not isinstance(user, Teacher):
        raise MustBeTeacher

    projects_assigned = 0
    for project in Project.objects.all():
        if not project.assigned_team:
            result = assign_team_to_project(project)
            projects_assigned += result

    return projects_assigned


def user_team_join_project(user, project):
    if not isinstance(user, Student):
        raise MustBeStudent

    if not user.team:
        raise UserNotInTeam

    if Project.objects.filter(all_teams__pk__exact=user.team.pk).exists():
        raise TeamAlreadyInProjectQueue

    if project.assigned_team:
        raise ProjectHasAssignedTeam

    project.all_teams.add(user.team)
    project.save(force_update=True)


def user_team_leave_project(user, project):
    if not isinstance(user, Student):
        raise MustBeStudent

    if not user.team:
        raise UserNotInTeam

    if not project.all_teams.filter(pk=user.team.pk).exists():
        raise TeamNotInProjectQueue

    if project.assigned_team:
        raise ProjectHasAssignedTeam

    project.all_teams.remove(user.team)
    project.save(force_update=True)


def user_delete_project(user, project):
    if not isinstance(user, Teacher):
        raise MustBeTeacher

    if project.assigned_team:
        raise ProjectHasAssignedTeam

    project.delete()


def user_create_project(user, project_name, project_description):
    if not isinstance(user, Teacher):
        raise MustBeTeacher

    project = Project()
    project.name = project_name
    project.description = project_description
    project.status = Project.PROJECT_STATUS_OPEN
    project.assigned_team = None
    project.author = user

    project.save()

    return project


def validate_common_create_user_rules(username, email):
    try:
        if UserBase.objects.get(username__iexact=username):
            raise UserWithGivenUsernameAlreadyExists
    except UserBase.DoesNotExist:
        pass

    try:
        if UserBase.objects.get(email__iexact=email):
            raise UserWithGivenEmailAlreadyExists
    except UserBase.DoesNotExist:
        pass

    return True


def account_create_teacher(username, email, password):
    validate_common_create_user_rules(username, email)
    teacher = Teacher()
    teacher.is_staff = True
    teacher.username = username
    teacher.email = email
    teacher.set_password(password)

    teacher.save()


def account_create_student(student_no, username, email, password):
    validate_common_create_user_rules(username, email)
    try:
        if Student.objects.get(student_no=student_no):
            raise StudentWithGivenStudentNoAlreadyExists
    except UserBase.DoesNotExist:
        pass

    student = Student()
    student.is_staff = False
    student.student_no = student_no
    student.status = Student.STUDENT_STATUS_UNASSIGNED
    student.username = username
    student.email = email
    student.set_password(password)

    student.save()


def user_change_password(user, current_password, new_password):
    if user.check_password(current_password) is False:
        raise InvalidPassword

    user.set_password(new_password)
    user.save(force_update=True)


def user_change_email(user, new_email):
    try:
        if UserBase.objects.get(email__iexact=new_email):
            raise UserWithGivenEmailAlreadyExists
    except UserBase.DoesNotExist:
        pass

    user.email = new_email
    user.save(force_update=True)


def user_delete_account(user):
    if user.team:
        raise UserAlreadyInTeam

    user.delete()
