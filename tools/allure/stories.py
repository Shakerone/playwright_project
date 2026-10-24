from enum import Enum


class AllureStory(str, Enum):
    COURSES = "Courses"
    DASHBOARD = "Dashboard"
    REGISTRATION = "Registration"
    AUTHORIZATION = "Authorization"
