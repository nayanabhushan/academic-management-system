
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from academics.models import StudentRecord
from .models import AuthorizedFaculty


User = get_user_model()


class StudentRegistrationForm(forms.Form):

    enrollment_no = forms.CharField(max_length=30)

    college_email = forms.EmailField()

    joining_code = forms.CharField(max_length=12)

    password1 = forms.CharField(
        widget=forms.PasswordInput
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput
    )

    def clean(self):
        cleaned_data = super().clean()

        enrollment_no = cleaned_data.get("enrollment_no")
        college_email = cleaned_data.get("college_email")
        joining_code = cleaned_data.get("joining_code")
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if not all([
            enrollment_no,
            college_email,
            joining_code,
            password1,
            password2
        ]):
            return cleaned_data

        try:
            student = StudentRecord.objects.select_related(
                "section"
            ).get(
                enrollment_no=enrollment_no,
                college_email__iexact=college_email
            )
        except StudentRecord.DoesNotExist:
            raise forms.ValidationError(
                "Enrollment number or college email does not match our records."
            )

        if student.section.joining_code != joining_code:
            raise forms.ValidationError(
                "Invalid section joining code."
            )

        if User.objects.filter(
            email__iexact=college_email
        ).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        if User.objects.filter(
            username=college_email
        ).exists():
            raise forms.ValidationError(
                "An account with this username already exists."
            )

        if password1 != password2:
            self.add_error(
                "password2",
                "The passwords do not match."
            )
        else:
            validate_password(password1)

        self.student_record = student

        return cleaned_data

class TeacherRegistrationForm(forms.Form):

    faculty_id = forms.CharField(max_length=30)
    college_email = forms.EmailField()

    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()

        faculty_id = cleaned_data.get("faculty_id")
        college_email = cleaned_data.get("college_email")
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if not all([faculty_id, college_email, password1, password2]):
            return cleaned_data

        try:
            faculty = AuthorizedFaculty.objects.get(
                faculty_id=faculty_id,
                college_email__iexact=college_email,
                is_active=True
            )
        except AuthorizedFaculty.DoesNotExist:
            raise forms.ValidationError(
                "Faculty ID or college email is invalid, or faculty is not authorised."
            )

        if User.objects.filter(email__iexact=college_email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        if User.objects.filter(username=college_email).exists():
            raise forms.ValidationError(
                "An account with this username already exists."
            )

        if password1 != password2:
            self.add_error("password2", "The passwords do not match.")
        else:
            validate_password(password1)

        self.faculty_record = faculty

        return cleaned_data
