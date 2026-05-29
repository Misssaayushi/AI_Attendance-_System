from app.middleware.error_handler import NotFoundException, BadRequestException

class StudentNotFoundException(NotFoundException):
    def __init__(self, message: str = "Student not found"):
        super().__init__(message)

class DuplicateRollNumberException(BadRequestException):
    def __init__(self, message: str = "Roll number already registered"):
        super().__init__(message)

class DuplicateEmailException(BadRequestException):
    def __init__(self, message: str = "Email address already registered"):
        super().__init__(message)

class InvalidFaceEncodingException(BadRequestException):
    def __init__(self, message: str = "face_encoding must contain exactly 128 float values"):
        super().__init__(message)


class AttendanceNotFoundException(NotFoundException):
    def __init__(self, message: str = "Attendance record not found"):
        super().__init__(message)


class DuplicateAttendanceException(BadRequestException):
    def __init__(self, message: str = "Attendance already marked for this student today"):
        super().__init__(message)


class AttendanceVerificationException(BadRequestException):
    def __init__(self, message: str = "Attendance verification failed"):
        super().__init__(message)


class ExcelExportException(BadRequestException):
    def __init__(self, message: str = "Excel export operation failed"):
        super().__init__(message)


class ExcelTemplateValidationException(BadRequestException):
    def __init__(self, message: str = "Invalid Excel template or parameters"):
        super().__init__(message)


class ExcelWriteException(BadRequestException):
    def __init__(self, message: str = "Unable to write attendance into workbook"):
        super().__init__(message)
