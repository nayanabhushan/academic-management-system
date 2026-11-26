
from django.urls import path
from . import views

urlpatterns = [
    path(
        "register/student/",
        views.student_register,
        name="student_register"
    ),

    path(
        "register/teacher/",
        views.teacher_register,
        name="teacher_register"
    ),
    path("login/", views.user_login, name="login"),
    path("login/", views.user_login, name="student_login"),
]

