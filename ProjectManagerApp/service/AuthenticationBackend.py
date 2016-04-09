from ProjectManagerApp.models import UserBase, Student, Teacher


class AuthenticationBackend(object):
    def authenticate(self, username=None, password=None):
        try:
            user_base = UserBase.objects.get(username=username)
        except UserBase.DoesNotExist:
            return None

        if user_base.check_password(password) is False:
            return None

        return self.__map_base_user_to_derived_user(user_base)

    def get_user(self, user_id):
        try:
            user_base = UserBase.objects.get(pk=user_id)
        except UserBase.DoesNotExist:
            return None

        return self.__map_base_user_to_derived_user(user_base)

    def __map_base_user_to_derived_user(self, user_base):
        try:
            student = user_base.student
            return student
        except Student.DoesNotExist:
            pass

        try:
            teacher = user_base.teacher
            return teacher
        except Teacher.DoesNotExist:
            pass

        raise NotImplementedError('Unknown user type')
