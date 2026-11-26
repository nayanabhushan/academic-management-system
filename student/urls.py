from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.student_dashboard, name="student_dashboard"),
    path("profile/", views.student_profile, name="student_profile"),
    path("attendance/", views.student_attendance, name="student_attendance"),
    path("assignments/", views.student_assignments, name="student_assignments"),
    path(
    "assignments/<int:assignment_id>/submit/",
    views.student_submit_assignment,
    name="student_submit_assignment"
),
    path("marks/", views.student_marks, name="student_marks"),
    path("timetable/", views.student_timetable, name="student_timetable"),
    path("notices/", views.student_notices, name="student_notices"),
    path("materials/", views.student_materials, name="student_materials"),
]