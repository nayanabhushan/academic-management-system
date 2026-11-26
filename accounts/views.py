
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login

from accounts.forms import StudentRegistrationForm, TeacherRegistrationForm


User = get_user_model()


def student_register(request):

    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)

        if form.is_valid():
            student_record = form.student_record

            user = User.objects.create_user(
                username=student_record.college_email,
                email=student_record.college_email,
                first_name=student_record.name,
                password=form.cleaned_data["password1"],
                role=User.Role.STUDENT
            )

            student_record.user = user
            student_record.save(update_fields=["user"])

            login(request, user)

            return render(
                request,
                "accounts/registration_success.html"
            )

    else:
        form = StudentRegistrationForm()

    return render(
        request,
        "accounts/student_register.html",
        {"form": form}
    )

def teacher_register(request):

    if request.method == "POST":
        form = TeacherRegistrationForm(request.POST)

        if form.is_valid():
            faculty_record = form.faculty_record

            user = User.objects.create_user(
                username=faculty_record.college_email,
                email=faculty_record.college_email,
                first_name=faculty_record.full_name,
                password=form.cleaned_data["password1"],
                role=User.Role.TEACHER
            )

            faculty_record.user = user
            faculty_record.save(update_fields=["user"])

            login(request, user)

            return render(
                request,
                "accounts/registration_success.html"
            )

    else:
        form = TeacherRegistrationForm()

    return render(
        request,
        "accounts/teacher_register.html",
        {"form": form}
    )
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect



def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Superuser / Admin
            if user.is_superuser:
                return redirect("/admin/")

            # Student
            elif user.role == "STUDENT":
                return redirect("/student/dashboard/")

            # Teacher
            elif user.role == "TEACHER":
                return redirect("/teacher/dashboard/")

            else:
                return redirect("/accounts/login/")

    else:
        form = AuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})
