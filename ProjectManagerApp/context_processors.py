from ProjectManagerApp.models import Student, Teacher  # , Team, Project


def is_student(request):
    return {'is_student': isinstance(request.user, Student)}


def is_teacher(request):
    return {'is_teacher': isinstance(request.user, Teacher)}


def user_has_team(request):
    return {'user_has_team': isinstance(request.user, Student) and request.user.team is not None}


# def teams():
#    return {'teams': Team.objects.all()}


# def projects():
#    return {'projects': Project.objects.all()}
