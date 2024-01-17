from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Response, Candidate, Application
from django.utils.html import format_html
from .models import Teacher, Student, Attendance
from .models import Sheet2Application
from .models import Contract
from django import forms


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('get_candidate_name', 'signed_contract')
    search_fields = ('candidate__First_Name', 'candidate__Last_Name')  # Adjust based on your Candidate model fields
    list_per_page = 10

    def get_candidate_name(self, obj):
        return f"{obj.candidate.First_Name} {obj.candidate.Last_Name}"

    get_candidate_name.short_description = 'Candidate Name'


@admin.register(Teacher)
class TeacherAdmin(ImportExportModelAdmin):
    list_display = (
    'course_class_no', 'course_intake', 'lec_first_name', 'lec_last_name', 'lec_phone_number', 'lec_email_address',
    'lec_class_name')
    search_fields = ('course_class_no', 'lec_first_name', 'lec_last_name')
    list_per_page = 10


@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin):
    list_display = (
    'student_first_name', 'student_second_name', 'student_phone_number', 'student_email_address', 'course_class_no',
    'course_intake')
    search_fields = (
    'student_first_name', 'student_second_name', 'student_phone_number', 'student_email_address', 'course_class_no')
    list_per_page = 10


class AttendanceAdminForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the way the candidates field is displayed, you can use any widget you prefer
        self.fields['candidates'].widget.attrs['style'] = 'width: 300px;'  # Adjust the width as needed

@admin.register(Attendance)
class AttendanceAdmin(ImportExportModelAdmin):
    list_display = ('get_candidate_name', 'date_of_class', 'get_absent_status')
    search_fields = ('candidates__First_Name', 'candidates__Last_Name', 'date_of_class', 'is_present', 'is_late', 'is_absent')
    list_per_page = 10
    form = AttendanceAdminForm

    def get_candidate_name(self, obj):
        return f"{obj.candidates.First_Name} {obj.candidates.Last_Name}"

    def get_absent_status(self, obj):
        if obj.is_present:
            return 'Present'
        elif obj.is_late:
            return 'Late'
        elif obj.is_absent:
            return 'Absent'
        else:
            return 'N/A'

    get_candidate_name.short_description = 'Candidate Name'
    get_absent_status.short_description = 'Absent Status'


class ApplicationAdmin(ImportExportModelAdmin):
    list_display = ('timestamp', 'name', 'phone_number', 'email', 'age')
    search_fields = ('name', 'email')  # Enable search by name and email
    list_per_page = 10


admin.site.register(Application, ApplicationAdmin)

@admin.register(Sheet2Application)
class Sheet2ApplicationAdmin(ImportExportModelAdmin):
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
