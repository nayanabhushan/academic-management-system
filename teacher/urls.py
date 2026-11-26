from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.teacher_dashboard, name="teacher_dashboard"),
    path("sections/", views.teacher_sections, name="teacher_sections"),
    path("attendance/", views.teacher_attendance, name="teacher_attendance"),
    path("attendance/mark/", views.teacher_mark_attendance, name="teacher_mark_attendance"),
    path("assignments/", views.teacher_assignments, name="teacher_assignments"),
    path("assignments/create/", views.teacher_create_assignment, name="teacher_create_assignment"),
    path(
    "assignments/<int:assignment_id>/submissions/",
    views.teacher_assignment_submissions,
    name="teacher_assignment_submissions"
),
    path("marks/enter/", views.teacher_enter_marks, name="teacher_enter_marks"),
]