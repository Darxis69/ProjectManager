from ProjectManagerApp.exceptions import UserAlreadyInTeam, MustBeStudent, UserNotInTeam, MustBeTeacher, \
    ProjectHasAssignedTeam, UserWithGivenUsernameAlreadyExists, StudentWithGivenStudentNoAlreadyExists, \
    TeamAlreadyInProjectQueue, TeamNotInProjectQueue
from ProjectManagerApp.models import Student, Team, Teacher, Project, UserBase


def user_join_team(user, team):
    if not isinstance(user, Student):
        raise MustBeStudent

    if user.team:
        raise UserAlreadyInTeam

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


def account_create_teacher(username, email, password):
    try:
        if UserBase.objects.get(username__iexact=username):
            raise UserWithGivenUsernameAlreadyExists
    except UserBase.DoesNotExist:
        pass

    teacher = Teacher()
    teacher.is_staff = True
    teacher.username = username
    teacher.email = email
    teacher.set_password(password)

    teacher.save()


def account_create_student(student_no, username, email, password):
    try:
        if UserBase.objects.get(username__iexact=username):
            raise UserWithGivenUsernameAlreadyExists
    except UserBase.DoesNotExist:
        pass

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
