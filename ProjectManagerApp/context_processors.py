from ProjectManagerApp.models import Student  # , Team, Project


def is_student(request):
    return {'is_student': isinstance(request.user, Student)}


# def teams():
#    return {'teams': Team.objects.all()}


# def projects():
#    return {'projects': Project.objects.all()}
