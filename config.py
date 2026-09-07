class Config:
    SECRET_KEY = "development-secret_Key"
    USERS_DB = "USERS.db"
    STUDENTS_DB = "SMS.db"
    EMAIL_VER = "email_verify.db"
    PHONE_VER = "phone_verify.db"

class TestingConfig(Config):
    TESTING = True
    USERS_DB = "test_USERS.db"
    STUDENTS_DB = "test_STUDENTS.db"
    EMAIL_VER = "test_email_verify.db"
    PHONE_VER = "test_phone_verfiy.db"