class UserAlreadyInTeam(Exception):
    pass


class UserNotInTeam(Exception):
    pass


class MustBeStudent(Exception):
    pass


class MustBeTeacher(Exception):
    pass


class ProjectHasAssignedTeam(Exception):
    pass


class UserWithGivenUsernameAlreadyExists(Exception):
    pass


class UserWithGivenEmailAlreadyExists(Exception):
    pass


class StudentWithGivenStudentNoAlreadyExists(Exception):
    pass


class TeamAlreadyInProjectQueue(Exception):
    pass


class TeamNotInProjectQueue(Exception):
    pass


class InvalidPassword(Exception):
    pass
