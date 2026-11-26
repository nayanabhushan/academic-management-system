from django.contrib import admin
from .models import (
    Section,
    Subject,
    TeachingAssignment,
    StudentRecord,
    AttendanceRecord,
    Assignment,
    AssignmentSubmission,
    MarksRecord,
)

admin.site.register(Section)
admin.site.register(Subject)
admin.site.register(TeachingAssignment)
admin.site.register(StudentRecord)
admin.site.register(AttendanceRecord)
admin.site.register(Assignment)
admin.site.register(AssignmentSubmission)
admin.site.register(MarksRecord)