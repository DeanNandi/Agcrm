from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Response, Candidate, Application, Teacher, Student, Attendance, Sheet2Application, Contract
from django.utils.html import format_html
from django import forms
from .models import PaymentHistory, UniquePayment, ClassAttendance, Eldoret_Applicant, FeeStructure, Discount
from .models import ClassFee
from .models import SchoolFee, Invoice, Admission
from .models import CourseFee

@admin.register(CourseFee)
class CourseFeeAdmin(admin.ModelAdmin):
    list_display = ('Name', 'Invoice_Number', 'Starting_Date', 'Ending_Date', 'Amount_to_Pay', 'pdf_view_link')
    list_filter = ('Name', 'Starting_Date', 'Ending_Date')

    def pdf_view_link(self, obj):
        # Check if the PDF file exists for the CourseFee object
        if obj.pdf_file:
            return format_html(f'<a href="{obj.pdf_file.url}" target="_blank">View PDF</a>')
        return "No PDF"

    pdf_view_link.short_description = 'Fee Structure PDF'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Assuming you want to generate/update the PDF when the CourseFee is saved/updated
        # and that your `create_pdf_for_fee_structure` method does not require parameters
        # or can handle being called without them.
        obj.create_pdf_for_fee_structure()

@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ('Name', 'admission_number', 'Date_of_Admission', 'pdf_view_link')
    list_filter = ('Name', 'admission_number', 'Date_of_Admission',)

    def pdf_view_link(self, obj):
        # Construct the URL based on a known structure and the object's attributes
        # Assuming your MEDIA_URL is set to '/media/' in settings.py and your Django project
        # is configured to serve files from the 'media' directory
        pdf_filename = f"{obj.Name}_{obj.admission_number}.pdf"
        pdf_url = f"/media/{pdf_filename}"  # Update this if your media structure is different

        return format_html(f'<a href="{pdf_url}" target="_blank">View PDF</a>')

    pdf_view_link.short_description = 'PDF Admissions'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # You might still want to generate or update the PDF when the model is saved
        # But consider checking if it's necessary to avoid unnecessary generation
        obj.create_pdf_from_data(obj.admission_number)
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('Name', 'City', 'Date_of_Payment', 'pdf_view_link')
    list_filter = ('Name', 'City', 'Date_of_Payment')

    def pdf_view_link(self, obj):
        # Construct the URL based on a known structure and the object's attributes
        # Assuming your MEDIA_URL is set to '/media/' in settings.py and your Django project
        # is configured to serve files from the 'media' directory
        pdf_filename = f"{obj.Name}_{obj.Invoice_Number}.pdf"
        pdf_url = f"/media/{pdf_filename}"  # Update this if your media structure is different

        return format_html(f'<a href="{pdf_url}" target="_blank">View PDF</a>')

    pdf_view_link.short_description = 'PDF Receipts'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # You might still want to generate or update the PDF when the model is saved
        # But consider checking if it's necessary to avoid unnecessary generation
        obj.create_pdf_from_data(obj.AmountPaid)
@admin.register(SchoolFee)
class SchoolFeeAdmin(ImportExportModelAdmin):
    list_display = ['candidate', 'starting_month', 'due_date', 'total_amount_to_pay', 'invoice_number']
    list_filter = ['starting_month']
    list_per_page = 10


@admin.register(ClassFee)
class ClassFeeAdmin(ImportExportModelAdmin):
    list_display = ('candidate', 'class_assignment', 'starting_date', 'invoice_number', 'total_amount_to_pay')
    search_fields = ('candidate', 'class_assignment', 'invoice_number')
    list_per_page = 10


@admin.register(Discount)
class DiscountAdmin(ImportExportModelAdmin):
    list_display = ('discount_amount', 'date', 'discount_number')
    search_fields = ('discount_amount', 'date', 'discount_number')
    list_per_page = 10


@admin.register(FeeStructure)
class FeeStructureAdmin(ImportExportModelAdmin):
    list_display = ('candidate', 'fee_assignment', 'total_amount_to_pay', 'starting_date', 'invoice_number')
    search_fields = (
    'candidate__First_Name', 'candidate__Last_Name', 'fee_assignment', 'total_amount_to_pay', 'starting_date',
    'invoice_number')
    list_per_page = 10


@admin.register(Eldoret_Applicant)
class EldoretApplicantAdmin(ImportExportModelAdmin):
    list_display = ('First_Name', 'Last_Name', 'Date_of_Birth', 'Sex', 'Address')
    search_fields = ('First_Name', 'Last_Name', 'Date_of_Birth', 'Sex', 'Address')
    list_per_page = 10


@admin.register(ClassAttendance)
class ClassAttendanceAdmin(ImportExportModelAdmin):
    list_display = ('candidate', 'date', 'present', 'absent_reason')
    search_fields = ('candidate__First_Name', 'candidate__Last_Name', 'date')
    list_per_page = 10


@admin.register(UniquePayment)
class UniquePaymentAdmin(ImportExportModelAdmin):
    list_display = ('get_candidate_name', 'receipt_number', 'date_of_payment', 'amount_paid')
    search_fields = ('candidate__First_Name', 'receipt_number', 'date_of_payment', 'amount_paid')
    list_per_page = 10

    def get_candidate_name(self, obj):
        return f"{obj.candidate.First_Name} {obj.candidate.Last_Name}"

    get_candidate_name.short_description = 'Candidate Name'


@admin.register(PaymentHistory)
class PaymentHistoryAdmin(ImportExportModelAdmin):
    list_display = ('candidate_name', 'phone_number', 'receipt_number', 'date_of_payment', 'amount_paid')
    search_fields = ('candidate_name', 'phone_number', 'receipt_number')
    list_per_page = 10


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


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('get_candidate_name', 'signed_contract')
    search_fields = ('candidate__First_Name', 'candidate__Last_Name')
    list_per_page = 10

    def get_candidate_name(self, obj):
        return f"{obj.candidate.First_Name} {obj.candidate.Last_Name}"

    get_candidate_name.short_description = 'Candidate Name'


class AttendanceAdminForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the way the candidate field is displayed, you can use any widget you prefer
        self.fields['candidate'].widget.attrs['style'] = 'width: 300px;'  # Adjust the width as needed


@admin.register(Attendance)
class AttendanceAdmin(ImportExportModelAdmin):
    list_display = ('get_candidate_name', 'date_of_class', 'start_time', 'end_time', 'absent')
    search_fields = ('candidate__First_Name', 'candidate__Last_Name', 'date_of_class', 'absent')
    list_per_page = 10
    form = AttendanceAdminForm

    def get_candidate_name(self, obj):
        return f"{obj.candidate.First_Name} {obj.candidate.Last_Name}"

    get_candidate_name.short_description = 'Candidate Name'


class ApplicationAdmin(ImportExportModelAdmin):
    list_display = ('timestamp', 'name', 'phone_number', 'email', 'age')
    search_fields = ('name', 'email')
    list_per_page = 10


admin.site.register(Application, ApplicationAdmin)


@admin.register(Sheet2Application)
class Sheet2ApplicationAdmin(ImportExportModelAdmin):
    list_display = (
        'timestamp', 'name', 'phone_number', 'email', 'age')
    search_fields = ('name', 'email')
    list_per_page = 10


@admin.register(Candidate)
class CandidateAdmin(ImportExportModelAdmin):
    list_display = ('First_Name', 'Last_Name', 'admission_number', 'Sex', 'Results')
    search_fields = ('First_Name', 'Last_Name', 'admission_number', 'Sex', 'Results')
    list_per_page = 5
    pass

    def _(self, obj):
        if obj.Results == 'Paid':
            return True
        elif obj.Results == 'Not-Paid':
            return None
        else:
            return False

    _.boolean = True

    def status(self, obj):
        if obj.Results == 'Paid':
            color = '#28a745'
        elif obj.Results == 'Not-Paid':
            color = '#fea95e'
        else:
            color = 'red'
        return format_html('<strong><p style="color: {}">{}</p></strong>'.format(color, obj.Results))

    status.allow_tags = True
    pass


@admin.register(Response)
class ResponsesAdmin(ImportExportModelAdmin):
    list_display = ('Name', 'PhoneNumber', 'Email', 'Age', 'Qualification', 'status', '_')
    search_fields = ('Name', 'PhoneNumber', 'Email', 'Age', 'Qualification', 'Situation')
    list_per_page = 10

    def _(self, obj):
        if obj.Situation == 'Interview':
            return True
        elif obj.Situation == 'Pending':
            return None
        else:
            return False

    _.boolean = True

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
