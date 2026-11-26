
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class CustomUser(AbstractUser):

    class Role(models.TextChoices):
        TEACHER = "TEACHER", "Teacher"
        STUDENT = "STUDENT", "Student"

    role = models.CharField(
        max_length=10,
        choices=Role.choices
    )


class AuthorizedFaculty(models.Model):
    full_name = models.CharField(max_length=150)
    faculty_id = models.CharField(max_length=30, unique=True)
    college_email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="faculty_record"
    )

    def __str__(self):
        return f"{self.full_name} ({self.faculty_id})"
