from ProjectManagerApp.exceptions import UserAlreadyInTeam, MustBeStudent, UserNotInTeam, MustBeTeacher, ProjectHasAssignedTeam
from ProjectManagerApp.models import Student, Team, Teacher, Project


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
    elif team.second_teammate == user:
        team.second_teammate = None

    if team.first_teammate is None and team.second_teammate is None:
        # TODO exception checking
        team.delete()
    else:
        team.save(force_update=True)

    user.team = None
    user.save()


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

