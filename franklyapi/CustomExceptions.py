class UserNotFoundException(Exception):

    def __init__(self, value='User not found.'):
        self.value = value

    def __str__(self):
        return repr(self.value)

class PasswordTooShortException(Exception):

    def __init__(self, value='Password too short.'):
        self.value = value

    def __str__(self):
        return repr(self.value)

class BlockedUserException(Exception):

    def __init__(self, value='User blocked.'):
        self.value = value

    def __str__(self):
        return repr(self.value)


class BadRequestException(Exception):

    def __init__(self, value='Bad request'):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UserAlreadyExistsException(Exception):

    def __init__(self, value='Could not upload file.'):
        self.value = value

    def __str__(self):
        return repr(self.value)


class PostNotFoundException(Exception):

    def __init__(self, value='Post not found.'):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ObjectNotFoundException(Exception):

    def __init__(self, value='Object not found.'):
        self.value = value

    def __str__(self):
        return repr(self.value)


class BadFileFormatException(Exception):

    def __init__(self, value='Not a valid file format.'):
        self.value = value

    def __str__(self):
        return repr(self.value)


class InvalidUserException(Exception):

    def __init__(self, value='User not valid.'):
        self.value = value

    def __str__(self):
        return repr(self.value)


class InvalidTokenException(Exception):

    def __init__(self, value='External token not valid.'):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UploadFaliureException(Exception):

    def __init__(self, value='Couldnot upload file to server.'):
        self.value = value

    def __str__(self):
        return repr(self.value)


class InvalidTypeException(Exception):

    def __init__(self, value='Invalid URL.'):
        self.value = value

    def __str__(self):
        return repr(self.value)


class PasswordMismatchException(Exception):

    def __init__(self, value='Credentials not matched.'):
        self.value = value

    def __str__(self):
        return repr(self.value)


class NoPermissionException(Exception):

    def __init__(self, value='Credentials not matched.'):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UploadFaliureException(Exception):

    def __init__(self, value='Could not upload file.'):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UnameUnavailableException(Exception):

    def __init__(self, value='Username Unavailable'):
        self.value = value

    def __str__(self):
        return repr(self.value)


class EmailUnavailableException(Exception):

    def __init__(self, value='Could not communicate with Redis.'):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ObjectNotFoundException(Exception):

    def __init__(self, value='Object not found'):
        self.value = value

    def __str__(self):
        return repr(self.value)

class TimeElapsedException(Exception):

    def __init__(self, value='Object not found'):
        self.value = value

    def __str__(self):
        return repr(self.value)

