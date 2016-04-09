from ProjectManagerApp.models import UserBase


class AuthenticationBackend(object):
    def authenticate(self, username=None, password=None):
        try:
            user = UserBase.objects.get(username=username)
        except UserBase.DoesNotExist:
            return None

        if user.check_password(password) is False:
            return None

        return user

    def get_user(self, user_id):
        try:
            return UserBase.objects.get(pk=user_id)
        except UserBase.DoesNotExist:
            return None
