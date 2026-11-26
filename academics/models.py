
from django.conf import settings
from django.db import models


class Section(models.Model):
    course = models.CharField(max_length=100)
    section = models.CharField(max_length=20)
    semester = models.PositiveSmallIntegerField()
    academic_year = models.CharField(max_length=20)
    joining_code = models.CharField(max_length=12, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_sections"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["course", "section", "semester", "academic_year"],
                name="unique_academic_section"
            )
        ]

    def __str__(self):
        return f"{self.course} - {self.section} - Semester {self.semester}"


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class TeachingAssignment(models.Model):
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="teaching_assignments"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name="teaching_assignments"
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="teaching_assignments"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["section", "subject"],
                name="unique_subject_per_section"
            )
        ]

    def __str__(self):
        return f"{self.subject} - {self.section}"


class StudentRecord(models.Model):
    name = models.CharField(max_length=150)
    enrollment_no = models.CharField(max_length=30, unique=True)
    college_email = models.EmailField(unique=True)
    section = models.ForeignKey(
        Section,
        on_delete=models.PROTECT,
        related_name="students"
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_record"
    )

    def __str__(self):
        return f"{self.name} ({self.enrollment_no})"


class AttendanceRecord(models.Model):
    class Status(models.TextChoices):
        PRESENT = "PRESENT", "Present"
        ABSENT = "ABSENT", "Absent"
        LATE = "LATE", "Late"

    class ClassType(models.TextChoices):
        LECTURE = "LECTURE", "Lecture"
        PRACTICAL = "PRACTICAL", "Practical"

    student = models.ForeignKey(
        StudentRecord,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )
    teaching_assignment = models.ForeignKey(
        TeachingAssignment,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )
    date = models.DateField()
    class_type = models.CharField(
        max_length=20,
        choices=ClassType.choices,
        default="LECTURE"
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices
    )
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="marked_attendance"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "student",
                    "teaching_assignment",
                    "date",
                    "class_type"
                ],
                name="unique_student_attendance_per_class"
            )
        ]

    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"


class Assignment(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ACTIVE = "ACTIVE", "Active"
        CLOSED = "CLOSED", "Closed"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    teaching_assignment = models.ForeignKey(
        TeachingAssignment,
        on_delete=models.CASCADE,
        related_name="assignments"
    )
    total_marks = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT
    )

    class Meta:
        ordering = ["due_date"]

    def __str__(self):
        return self.title


class AssignmentSubmission(models.Model):
    submission_file = models.FileField(
        upload_to="assignments/submissions/"
    )
    submitted_at = models.DateTimeField(auto_now=True)
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="submissions"
    )
    student = models.ForeignKey(
        StudentRecord,
        on_delete=models.CASCADE,
        related_name="assignment_submissions"
    )

    class Meta:
        ordering = ["-submitted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["assignment", "student"],
                name="unique_student_assignment_submission"
            )
        ]

    def __str__(self):
        return f"{self.student} - {self.assignment}"


class MarksRecord(models.Model):
    assessment_name = models.CharField(max_length=100)
    total_marks = models.PositiveIntegerField()
    marks_obtained = models.DecimalField(
        max_digits=7,
        decimal_places=2
    )
    created_at = models.DateTimeField(auto_now_add=True)
    entered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="entered_marks"
    )
    student = models.ForeignKey(
        StudentRecord,
        on_delete=models.CASCADE,
        related_name="marks_records"
    )
    teaching_assignment = models.ForeignKey(
        TeachingAssignment,
        on_delete=models.CASCADE,
        related_name="marks_records"
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "student",
                    "teaching_assignment",
                    "assessment_name"
                ],
                name="unique_student_assessment_marks"
            )
        ]

    def __str__(self):
        return (
            f"{self.student} - {self.assessment_name} - "
            f"{self.marks_obtained}/{self.total_marks}"
        )
