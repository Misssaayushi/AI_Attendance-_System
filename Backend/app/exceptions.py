from app.middleware.error_handler import BadRequestException, DatabaseException, NotFoundException

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


class EmailConfigurationException(BadRequestException):
    def __init__(self, message: str = "Invalid email configuration"):
        super().__init__(message)


class EmailAttachmentException(BadRequestException):
    def __init__(self, message: str = "Invalid or missing email attachment"):
        super().__init__(message)


class EmailDeliveryException(BadRequestException):
    def __init__(self, message: str = "Email delivery failed"):
        super().__init__(message)


class AnalyticsValidationException(BadRequestException):
    def __init__(self, message: str = "Invalid analytics request"):
        super().__init__(message)


class AnalyticsQueryException(DatabaseException):
    def __init__(self, message: str = "Analytics query execution failed"):
        super().__init__(message)


class AnalyticsDataException(NotFoundException):
    def __init__(self, message: str = "No analytics data found"):
        super().__init__(message)
