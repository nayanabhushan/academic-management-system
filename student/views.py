
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.utils import timezone

from academics.models import (
    AttendanceRecord,
    TeachingAssignment,
    Assignment,
    AssignmentSubmission,
    MarksRecord,
)


@login_required
def student_dashboard(request):
    if request.user.role != "STUDENT":
        return HttpResponseForbidden(
            "Only students can access this page."
        )

    student = request.user.student_record

    attendance_records = AttendanceRecord.objects.filter(
        student=student
    )

    total_classes = attendance_records.count()

    classes_attended = attendance_records.filter(
        status__in=[
            AttendanceRecord.Status.PRESENT,
            AttendanceRecord.Status.LATE
        ]
    ).count()

    attendance_percentage = (
        round((classes_attended / total_classes) * 100, 1)
        if total_classes else 0
    )

    today = timezone.now()

    pending_assignments = Assignment.objects.filter(
        teaching_assignment__section=student.section,
        status=Assignment.Status.ACTIVE
    ).exclude(
        submissions__student=student
    ).filter(
        due_date__isnull=True
    ).count()

    pending_assignments += Assignment.objects.filter(
        teaching_assignment__section=student.section,
        status=Assignment.Status.ACTIVE,
        due_date__gte=today
    ).exclude(
        submissions__student=student
    ).count()

    context = {
        "student": student,
        "attendance_percentage": attendance_percentage,
        "pending_assignments": pending_assignments,
        "upcoming_classes": [],
    }

    return render(
        request,
        "student/dashboard.html",
        context
    )


@login_required
def student_profile(request):
    if request.user.role != "STUDENT":
        return HttpResponseForbidden(
            "Only students can access this page."
        )

    student = request.user.student_record

    context = {
        "student": student,
        "section": student.section,
    }

    return render(
        request,
        "student/profile.html",
        context
    )


@login_required
def student_attendance(request):
    if request.user.role != "STUDENT":
        return HttpResponseForbidden(
            "Only students can access this page."
        )

    student = request.user.student_record

    attendance_records = AttendanceRecord.objects.filter(
        student=student
    ).select_related(
        "teaching_assignment__subject"
    ).order_by("-date")

    total_classes = attendance_records.count()

    classes_attended = attendance_records.filter(
        status__in=[
            AttendanceRecord.Status.PRESENT,
            AttendanceRecord.Status.LATE
        ]
    ).count()

    classes_missed = attendance_records.filter(
        status=AttendanceRecord.Status.ABSENT
    ).count()

    overall_percentage = (
        round((classes_attended / total_classes) * 100, 1)
        if total_classes else 0
    )

    subject_data = {}

    for record in attendance_records:
        subject = record.teaching_assignment.subject

        if subject.id not in subject_data:
            subject_data[subject.id] = {
                "subject": subject,
                "total_classes": 0,
                "classes_attended": 0,
                "classes_missed": 0,
            }

        subject_data[subject.id]["total_classes"] += 1

        if record.status in [
            AttendanceRecord.Status.PRESENT,
            AttendanceRecord.Status.LATE
        ]:
            subject_data[subject.id]["classes_attended"] += 1
        elif record.status == AttendanceRecord.Status.ABSENT:
            subject_data[subject.id]["classes_missed"] += 1

    subject_attendance = []

    for item in subject_data.values():
        total = item["total_classes"]
        attended = item["classes_attended"]

        item["percentage"] = (
            round((attended / total) * 100, 1)
            if total else 0
        )

        subject_attendance.append(item)

    recent_attendance = attendance_records[:10]

    context = {
        "total_classes": total_classes,
        "classes_attended": classes_attended,
        "classes_missed": classes_missed,
        "overall_percentage": overall_percentage,
        "subject_attendance": subject_attendance,
        "recent_attendance": recent_attendance,
    }

    return render(
        request,
        "student/attendance.html",
        context
    )


@login_required
def student_marks(request):
    if request.user.role != "STUDENT":
        return HttpResponseForbidden(
            "Only students can access this page."
        )

    student = request.user.student_record

    marks_records = MarksRecord.objects.filter(
        student=student
    ).select_related(
        "teaching_assignment__subject"
    ).order_by("-created_at")

    totals = marks_records.aggregate(
        total_obtained=Sum("marks_obtained"),
        total_possible=Sum("total_marks")
    )

    total_obtained = totals["total_obtained"] or 0
    total_possible = totals["total_possible"] or 0

    overall_percentage = (
        round((total_obtained / total_possible) * 100, 2)
        if total_possible else 0
    )

    subject_count = marks_records.values(
        "teaching_assignment__subject"
    ).distinct().count()

    context = {
        "marks_records": marks_records,
        "overall_percentage": overall_percentage,
        "subject_count": subject_count,
    }

    return render(
        request,
        "student/marks.html",
        context
    )


@login_required
def student_assignments(request):
    if request.user.role != "STUDENT":
        return HttpResponseForbidden(
            "Only students can access this page."
        )

    student = request.user.student_record

    assignments = Assignment.objects.filter(
        teaching_assignment__section=student.section,
        status=Assignment.Status.ACTIVE
    ).select_related(
        "teaching_assignment__subject",
        "teaching_assignment__section"
    ).order_by("due_date")

    submissions = AssignmentSubmission.objects.filter(
        student=student,
        assignment__in=assignments
    )

    submitted_ids = set(
        submissions.values_list(
            "assignment_id",
            flat=True
        )
    )

    today = timezone.now()

    pending_count = 0
    submitted_count = 0
    overdue_count = 0

    for assignment in assignments:
        assignment.is_submitted = (
            assignment.id in submitted_ids
        )

        assignment.is_overdue = (
            not assignment.is_submitted
            and assignment.due_date is not None
            and assignment.due_date < today
        )

        if assignment.is_submitted:
            submitted_count += 1
        elif assignment.is_overdue:
            overdue_count += 1
        else:
            pending_count += 1

    context = {
        "assignments": assignments,
        "total_assignments": assignments.count(),
        "pending_count": pending_count,
        "submitted_count": submitted_count,
        "overdue_count": overdue_count,
    }

    return render(
        request,
        "student/assignments.html",
        context
    )


@login_required
def student_submit_assignment(request, assignment_id):
    if request.user.role != "STUDENT":
        return HttpResponseForbidden(
            "Only students can submit assignments."
        )

    if request.method != "POST":
        return redirect("student_assignments")

    student = request.user.student_record

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        teaching_assignment__section=student.section,
        status=Assignment.Status.ACTIVE
    )

    uploaded_file = request.FILES.get("submission_file")

    if not uploaded_file:
        return HttpResponse(
            "Please select a file to submit.",
            status=400
        )

    allowed_extensions = {
        "pdf",
        "doc",
        "docx",
        "ppt",
        "pptx"
    }

    file_extension = (
        uploaded_file.name.rsplit(".", 1)[-1].lower()
    )

    if (
        "." not in uploaded_file.name
        or file_extension not in allowed_extensions
    ):
        return HttpResponse(
            "Invalid file format. Allowed formats: "
            "PDF, DOC, DOCX, PPT and PPTX.",
            status=400
        )

    max_file_size = 10 * 1024 * 1024

    if uploaded_file.size > max_file_size:
        return HttpResponse(
            "File size cannot exceed 10 MB.",
            status=400
        )

    AssignmentSubmission.objects.update_or_create(
        assignment=assignment,
        student=student,
        defaults={
            "submission_file": uploaded_file
        }
    )

    return redirect("student_assignments")


@login_required
def student_timetable(request):
    if request.user.role != "STUDENT":
        return HttpResponseForbidden(
            "Only students can access this page."
        )

    return HttpResponse(
        "Student timetable feature will be available in Phase 2."
    )


@login_required
def student_notices(request):
    if request.user.role != "STUDENT":
        return HttpResponseForbidden(
            "Only students can access this page."
        )

    return HttpResponse(
        "Student notices feature will be available in Phase 2."
    )


@login_required
def student_materials(request):
    if request.user.role != "STUDENT":
        return HttpResponseForbidden(
            "Only students can access this page."
        )

    return HttpResponse(
        "Student study materials feature will be available in Phase 2."
    )
