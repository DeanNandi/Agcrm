from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Response, Candidate, Application
from django.utils.html import format_html
from .models import School, Student, Attendance
from .models import Sheet2Application




@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = (
    'course_class_no', 'course_intake', 'lec_first_name', 'lec_last_name', 'lec_phone_number', 'lec_email_address',
    'lec_class_name')
    search_fields = ('course_class_no', 'lec_first_name', 'lec_last_name')
    list_per_page = 10


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
    'student_first_name', 'student_second_name', 'student_phone_number', 'student_email_address', 'course_class_no',
    'course_intake')
    search_fields = (
    'student_first_name', 'student_second_name', 'student_phone_number', 'student_email_address', 'course_class_no')
    list_per_page = 10


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'school', 'date_of_class', 'start_time', 'end_time', 'absent')
    search_fields = (
    'student__student_first_name', 'school__lec_first_name', 'school__lec_last_name', 'date_of_class', 'absent')
    list_per_page = 10


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'name', 'phone_number', 'email', 'age')
    search_fields = ('name', 'email')  # Enable search by name and email
    list_per_page = 10


admin.site.register(Application, ApplicationAdmin)

@admin.register(Sheet2Application)
class Sheet2ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'timestamp', 'name', 'phone_number', 'email', 'age')
    search_fields = ('name', 'email')  # Enable search by name and email
    list_per_page = 10

@admin.register(Candidate)
class CandidateAdmin(ImportExportModelAdmin):
    list_display = ('First_Name', 'Last_Name', 'Date_of_Birth', 'Sex', 'Address', 'Results')
    search_fields = ('First_Name', 'Last_Name', 'Date_of_Birth', 'Sex', 'Address', 'Results')
    list_per_page = 5
    pass

    # function for icons Interviews
    def _(self, obj):
        if obj.Situation == 'Interview':
            return True
        elif obj.Situation == 'Pending':
            return None
        else:
            return False

    _.boolean = True

    # function for the text
    def status(self, obj):
        if obj.Situation == 'Interview':
            color = '#28a745'
        elif obj.Situation == 'Pending':
            color = '#fea95e'
        else:
            color = 'red'
        return format_html('<strong><p style="color: {}">{}</p></strong>'.format(color, obj.Situation))

    status.allow_tags = True
    pass


@admin.register(Response)
class ResponsesAdmin(ImportExportModelAdmin):
    list_display = ('Name', 'PhoneNumber', 'Email', 'Age', 'Qualification', 'status', '_')
    search_fields = ('Name', 'PhoneNumber', 'Email', 'Age', 'Qualification', 'Situation')
    list_per_page = 10

    # function for icons Interviews
    def _(self, obj):
        if obj.Situation == 'Interview':
            return True
        elif obj.Situation == 'Pending':
            return None
        else:
            return False

    _.boolean = True

    # function for the text
    def status(self, obj):
        if obj.Situation == 'Interview':
            color = '#28a745'
        elif obj.Situation == 'Pending':
            color = '#fea95e'
        else:
            color = 'red'
        return format_html('<strong><p style="color: {}">{}</p></strong>'.format(color, obj.Situation))

    status.allow_tags = True
    pass
