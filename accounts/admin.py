from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, AuthorizedFaculty


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('User Role', {'fields': ('role',)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('User Role', {'fields': ('role',)}),
    )

@admin.register(AuthorizedFaculty)
class AuthorizedFacultyAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'faculty_id', 'college_email', 'is_active')
    search_fields = ('full_name', 'faculty_id', 'college_email')