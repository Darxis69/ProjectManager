from ProjectManagerApp.models import Student, Teacher, Team, Project


def is_student(request):
    return {'is_student': isinstance(request.user, Student)}


def is_teacher(request):
    return {'is_teacher': isinstance(request.user, Teacher)}


def has_user_team(request):
    return {'has_user_team': isinstance(request.user, Student) and request.user.team is not None}


def teams_count(request):
    return {'teams_count': Team.objects.all().count()}


def projects_count(request):
    return {'teams_count': Project.objects.all().count()}
