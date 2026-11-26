from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils.dateparse import parse_date
from django.utils import timezone

from academics.models import (
    TeachingAssignment,
    AttendanceRecord,
    Assignment,
    AssignmentSubmission,
    MarksRecord,
)

@login_required
def teacher_dashboard(request):
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Only teachers can access this page.")

    return render(request, "teacher/dashboard.html")


@login_required
def teacher_sections(request):
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Only teachers can access this page.")

    assignments = TeachingAssignment.objects.filter(
        teacher=request.user
    ).select_related(
        "section", "subject"
    ).prefetch_related("section__students")

    section_data = {}

    for assignment in assignments:
        section = assignment.section

        if section.id not in section_data:
            section_data[section.id] = {
                "section": section,
                "subjects": [],
                "student_count": section.students.count(),
            }

        section_data[section.id]["subjects"].append(
            assignment.subject.name
        )

    context = {
        "sections": list(section_data.values()),
        "total_sections": len(section_data),
        "total_students": sum(
            item["student_count"]
            for item in section_data.values()
        ),
    }

    return render(request, "teacher/sections.html", context)


@login_required
def teacher_attendance(request):
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Only teachers can access this page.")

    assignments = TeachingAssignment.objects.filter(
        teacher=request.user
    ).select_related("section", "subject")

    attendance_records = AttendanceRecord.objects.filter(
        teaching_assignment__teacher=request.user
    ).select_related(
        "student",
        "teaching_assignment__subject",
        "teaching_assignment__section"
    ).order_by("-date")

    total_records = attendance_records.count()

    present_count = attendance_records.filter(
        status=AttendanceRecord.Status.PRESENT
    ).count()

    absent_count = attendance_records.filter(
        status=AttendanceRecord.Status.ABSENT
    ).count()

    late_count = attendance_records.filter(
        status=AttendanceRecord.Status.LATE
    ).count()

    overall_percentage = (
        round(
            ((present_count + late_count) / total_records) * 100, 1
        )
        if total_records else 0
    )

    total_students = sum(
        assignment.section.students.count()
        for assignment in assignments
    )

    subject_attendance = []

    for assignment in assignments:
        records = attendance_records.filter(
            teaching_assignment=assignment
        )

        total = records.count()

        attended = records.filter(
            status__in=[
                AttendanceRecord.Status.PRESENT,
                AttendanceRecord.Status.LATE
            ]
        ).count()

        percentage = (
            round((attended / total) * 100, 1)
            if total else 0
        )

        subject_attendance.append({
            "name": assignment.subject.name,
            "section": assignment.section.section,
            "percentage": percentage,
        })

    context = {
        "assignments": assignments,
        "attendance_records": attendance_records,
        "overall_percentage": overall_percentage,
        "present_count": present_count,
        "absent_count": absent_count,
        "late_count": late_count,
        "total_students": total_students,
        "subject_attendance": subject_attendance,
    }

    return render(request, "teacher/attendance.html", context)


@login_required
def teacher_mark_attendance(request):
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Only teachers can access this page.")

    assignments = TeachingAssignment.objects.filter(
        teacher=request.user
    ).select_related("section", "subject")

    selected_assignment = None
    students = []
    error_message = None

    if request.method == "POST":
        assignment_id = request.POST.get("assignment")
        selected_date = request.POST.get("date", "")
        class_type = request.POST.get("class_type", "LECTURE")
    else:
        assignment_id = request.GET.get("assignment")
        selected_date = request.GET.get("date", "")
        class_type = request.GET.get("class_type", "LECTURE")

    selected_class_type = class_type

    if assignment_id:
        try:
            selected_assignment = assignments.get(id=assignment_id)
        except (TeachingAssignment.DoesNotExist, ValueError, TypeError):
            error_message = "Invalid teaching assignment."

    if selected_assignment:
        if class_type not in [
            AttendanceRecord.ClassType.LECTURE,
            AttendanceRecord.ClassType.PRACTICAL
        ]:
            error_message = "Invalid class type."

        attendance_date = parse_date(selected_date)

        if not attendance_date:
            error_message = "Please select a valid date."

        students = list(
            selected_assignment.section.students.all().order_by("name")
        )

        previous_statuses = {}

        if request.method == "POST":
            for student in students:
                previous_statuses[student.id] = request.POST.get(
                    f"status_{student.id}", ""
                )

        elif attendance_date and not error_message:
            previous_records = AttendanceRecord.objects.filter(
                teaching_assignment=selected_assignment,
                date=attendance_date,
                class_type=class_type
            )

            previous_statuses = {
                record.student_id: record.status
                for record in previous_records
            }

        for student in students:
            student.previous_status = previous_statuses.get(
                student.id, ""
            )

        if request.method == "POST" and not error_message:
            valid_statuses = {
                choice[0]
                for choice in AttendanceRecord.Status.choices
            }

            for student in students:
                status = request.POST.get(f"status_{student.id}")

                if status not in valid_statuses:
                    error_message = (
                        f"Please select a valid status for {student.name}."
                    )
                    break

            if not error_message:
                with transaction.atomic():
                    for student in students:
                        AttendanceRecord.objects.update_or_create(
                            student=student,
                            teaching_assignment=selected_assignment,
                            date=attendance_date,
                            class_type=class_type,
                            defaults={
                                "status": request.POST.get(
                                    f"status_{student.id}"
                                ),
                                "marked_by": request.user,
                            }
                        )

                return redirect("teacher_attendance")

    context = {
        "assignments": assignments,
        "selected_assignment": selected_assignment,
        "students": students,
        "selected_date": selected_date,
        "selected_class_type": selected_class_type,
        "error_message": error_message,
    }

    return render(
        request,
        "teacher/mark_attendance.html",
        context
    )

@login_required
def teacher_assignments(request):
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Only teachers can access this page.")

    assignments = Assignment.objects.filter(
        teaching_assignment__teacher=request.user
    ).select_related(
        "teaching_assignment__section",
        "teaching_assignment__subject"
    ).prefetch_related(
        "submissions"
    )

    for assignment in assignments:
        assignment.submission_count = assignment.submissions.count()

    total_assignments = assignments.count()

    active_count = assignments.filter(
        status=Assignment.Status.ACTIVE
    ).count()

    closed_count = assignments.filter(
        status=Assignment.Status.CLOSED
    ).count()

    draft_count = assignments.filter(
        status=Assignment.Status.DRAFT
    ).count()

    context = {
        "assignments": assignments,
        "total_assignments": total_assignments,
        "active_count": active_count,
        "closed_count": closed_count,
        "draft_count": draft_count,
    }

    return render(
        request,
        "teacher/assignments.html",
        context
    )

@login_required
def teacher_assignment_submissions(request, assignment_id):
    if request.user.role != "TEACHER":
        return HttpResponseForbidden(
            "Only teachers can access submissions."
        )

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        teaching_assignment__teacher=request.user
    )

    submissions = AssignmentSubmission.objects.filter(
        assignment=assignment
    ).select_related(
        "student"
    ).order_by("-submitted_at")

    context = {
        "assignment": assignment,
        "submissions": submissions,
    }

    return render(
        request,
        "teacher/assignment_submissions.html",
        context
    )


@login_required
def teacher_enter_marks(request):
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Only teachers can access this page.")

    assignments = TeachingAssignment.objects.filter(
        teacher=request.user
    ).select_related("section", "subject")

    selected_assignment = None
    students = []
    error_message = None

    assignment_id = (
        request.POST.get("assignment")
        if request.method == "POST"
        else request.GET.get("assignment")
    )

    assessment_name = request.POST.get(
        "assessment_name", ""
    ) if request.method == "POST" else ""

    if assignment_id:
        try:
            selected_assignment = assignments.get(id=assignment_id)
        except (TeachingAssignment.DoesNotExist, ValueError, TypeError):
            error_message = "Invalid teaching assignment."

    if selected_assignment:
        students = list(
            selected_assignment.section.students.all().order_by("name")
        )

        if request.method == "POST" and not error_message:
            assessment_name = assessment_name.strip()

            if not assessment_name:
                error_message = "Please enter an assessment name."

            try:
                total_marks = int(request.POST.get("total_marks", ""))
                if total_marks <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                total_marks = None
                error_message = "Enter a valid total marks value greater than zero."

            marks_to_save = []

            if not error_message:
                for student in students:
                    raw_marks = request.POST.get(
                        f"marks_{student.id}", ""
                    ).strip()

                    try:
                        obtained = Decimal(raw_marks)
                    except (InvalidOperation, ValueError):
                        error_message = f"Enter valid marks for {student.name}."
                        break

                    if (
                        not obtained.is_finite()
                        or obtained < 0
                        or obtained > total_marks
                    ):
                        error_message = (
                            f"Marks for {student.name} must be between "
                            f"0 and {total_marks}."
                        )
                        break

                    marks_to_save.append((student, obtained))

            if not error_message:
                with transaction.atomic():
                    for student, obtained in marks_to_save:
                        MarksRecord.objects.update_or_create(
                            student=student,
                            teaching_assignment=selected_assignment,
                            assessment_name=assessment_name,
                            defaults={
                                "total_marks": total_marks,
                                "marks_obtained": obtained,
                                "entered_by": request.user,
                            }
                        )

                return redirect(
                    f"{request.path}?assignment={selected_assignment.id}"
                )

    context = {
        "assignments": assignments,
        "selected_assignment": selected_assignment,
        "students": students,
        "assessment_name": assessment_name,
        "error_message": error_message,
    }

    return render(
        request,
        "teacher/enter_marks.html",
        context
    )

@login_required
def teacher_create_assignment(request):
    if request.user.role != "TEACHER":
        return HttpResponseForbidden(
            "Only teachers can create assignments."
        )

    teaching_assignments = TeachingAssignment.objects.filter(
        teacher=request.user
    ).select_related("section", "subject")

    error_message = None

    if request.method == "POST":
        teaching_assignment_id = request.POST.get(
            "teaching_assignment"
        )
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        due_date_raw = request.POST.get("due_date", "").strip()
        total_marks_raw = request.POST.get("total_marks", "").strip()
        status = request.POST.get("status", "DRAFT")

        try:
            teaching_assignment = teaching_assignments.get(
                id=teaching_assignment_id
            )
        except (TeachingAssignment.DoesNotExist, ValueError, TypeError):
            teaching_assignment = None
            error_message = "Please select a valid subject and section."

        if not error_message and not title:
            error_message = "Please enter an assignment title."

        try:
            total_marks = int(total_marks_raw)
            if total_marks <= 0:
                raise ValueError
        except (ValueError, TypeError):
            total_marks = None
            error_message = "Total marks must be greater than zero."

        if status not in [
            Assignment.Status.DRAFT,
            Assignment.Status.ACTIVE,
        ]:
            error_message = "Please select a valid assignment status."

        due_date = None

        if due_date_raw:
            from django.utils.dateparse import parse_datetime

            due_date = parse_datetime(due_date_raw)

            if due_date is None:
                error_message = "Please enter a valid due date and time."
            elif timezone.is_naive(due_date):
                due_date = timezone.make_aware(due_date)

        if not error_message:
            Assignment.objects.create(
                teaching_assignment=teaching_assignment,
                title=title,
                description=description,
                due_date=due_date,
                total_marks=total_marks,
                status=status,
            )

            return redirect("teacher_assignments")

    context = {
        "teaching_assignments": teaching_assignments,
        "error_message": error_message,
    }

    return render(
        request,
        "teacher/create_assignment.html",
        context
    )
