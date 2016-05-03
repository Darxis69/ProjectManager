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


class StudentWithGivenStudentNoAlreadyExists(Exception):
    pass
