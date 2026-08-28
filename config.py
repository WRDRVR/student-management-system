class Config:
    SECRET_KEY = "development-secret_Key"
    USERS_DB = "USERS.db"
    STUDENTS_DB = "SMS.db"

class TestingConfig(Config):
    TESTING = True
    USERS_DB = "test_USERS.db"
    STUDENTS_DB = "test_STUDENTS.db"