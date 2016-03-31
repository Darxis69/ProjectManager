from django.contrib.auth.models import User


class AuthenticationBackend(object):
    @staticmethod
    def authenticate(username=None, password=None):
        if username == "admin" and password == "pass":
            user = User(username=username)
            return user

        return None

    @staticmethod
    def get_user(user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

