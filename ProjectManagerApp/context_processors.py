from ProjectManagerApp.models import Student, Teacher, Team, Project


def is_student(request):
    return {'is_student': isinstance(request.user, Student)}


def is_teacher(request):
    return {'is_teacher': isinstance(request.user, Teacher)}


def has_user_team(request):
    return {'has_user_team': isinstance(request.user, Student) and request.user.team is not None}


def user_team_assigned_project(request):
    if not isinstance(request.user, Student) or not request.user.team:
        return {'user_team_assigned_project': False}

    return {'user_team_assigned_project': Project.objects.filter(assigned_team=request.user.team)}


def user_team_applied_project(request):
    if not isinstance(request.user, Student) or not request.user.team:
        return {'user_team_applied_project': False}

    for project in Project.objects.all():
        if request.user.team and project.all_teams.filter(name=request.user.team.name):
            return {'user_team_applied_project': project}

    return {'user_team_applied_project': False}


def teams_count(request):
    return {'teams_count': Team.objects.all().count()}


def projects_count(request):
    return {'projects_count': Project.objects.all().count()}


def teams(request):
    return {'teams': Team.objects.all()}


def projects(request):
    return {'projects': Project.objects.all()}


def max_field_length(request):
    return {'max_field_length': 15}
