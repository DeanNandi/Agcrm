from django.contrib.auth import authenticate, login, logout
from .forms import CreateUserForm
from .forms import MyForm, CandidateInfo, PostResults, AddCourse, AddStudent
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils import timezone
from xhtml2pdf import pisa
from io import BytesIO
from django.template.loader import get_template
from .models import Student, Teacher
from datetime import timedelta
import requests
import json
from .models import Response, Sheet2Application, Application
from django.http import HttpResponseBadRequest
from .forms import EditApps, EditSheet2App, EditEldoret
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .forms import YourInvoiceForm
from .models import Invoice, Contract
from .forms import ContractUploadForm
from django.forms import modelformset_factory
from .models import Candidate, Attendance, PaymentHistory, UniquePayment
from .forms import AttendanceForm
import uuid
from django.db.models import Max
from django.shortcuts import render, redirect
from .models import ClassAttendance, Eldoret_Applicant, FeeStructure, Discount
from .forms import FeeStructureForm, EldoretInfo, DiscountForm
from django.core.exceptions import ObjectDoesNotExist
from .forms import LevelForm
from .forms import EditCandidate
# class fees
from datetime import datetime, timedelta
# pip install python-dateutil
from .models import ClassFee, MonthRange
from .forms import ClassFeeForm, MonthRangeForm
# new fees (pip install python-dateutil) (change edit_candidate)
from .models import SchoolFee
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from .forms import SchoolFeeForm
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse
# admissions
from .forms import AdmissionForm
from .models import Admission
from django.db.models import Max
# CourseFee
from .forms import CourseFeeForm
from .models import CourseFee
from django.db.models import Max

# Map full address names to their abbreviations
COURSE_CLASSES_DICT = dict(
    Nairobi_CBD='CBD',
    Nairobi_Hospital= 'NBH',
    Nairobi_Karen='KHS',
    Nairobi_Daystar='DUS',
    Mombasa='MSA',
    Muranga='MRG',
    Kisumu='KSM',
    Kisii='KSI',
    Eldoret='ELD',
    Thika='THK'
)

def generate_admission_numbers():
    now = datetime.now()
    year_prefix = now.strftime('%y')  # Last two digits of the year
    month_prefix = now.strftime('%m')  # Month as two digits

    for candidate in Candidate.objects.all():
        # Skip candidates who already have an admission number
        if candidate.admission_number:
            continue

        course_abbreviation = COURSE_CLASSES_DICT.get(candidate.Course_Location, 'OTH')

        # Generate the prefix for the new admission number
        new_admission_prefix = f"{year_prefix}{month_prefix}{course_abbreviation}"

        # Find the highest number for the current prefix
        max_admission_number = Candidate.objects.filter(admission_number__startswith=new_admission_prefix).aggregate(Max('admission_number'))['admission_number__max']

        if max_admission_number:
            # Increment the last number by 1
            last_number = int(max_admission_number[-6:]) + 1
        else:
            # Start with 1 if no admission number exists for the current prefix
            last_number = 1

        # Assign the new admission number
        candidate.admission_number = f"{new_admission_prefix}{last_number:06d}"
        candidate.save()

# Run the function
generate_admission_numbers()



def edit_candidate(request, pk, model_type):
    if model_type == 'Candidate':
        model = Candidate
        form_class = EditCandidate
    else:
        return HttpResponseBadRequest("Invalid model type")

    item = get_object_or_404(model, pk=pk)
    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            # Use the 'reverse' function to dynamically construct the redirect URL
            return redirect(reverse('candidate_detail', kwargs={'candidate_id': item.pk}))
    else:
        form = form_class(instance=item)

    return render(request, 'edit_data.html', {'form': form})
class SchoolFeeCreate(CreateView):
    model = SchoolFee
    form_class = SchoolFeeForm
    template_name = 'schoolfee_form.html'

    def get_initial(self):
        initial = super().get_initial()
        # Get the candidate based on the passed pk and set it as initial form value
        self.candidate_pk = self.kwargs.get('pk')
        initial['candidate'] = Candidate.objects.get(pk=self.candidate_pk)
        return initial

    def get_success_url(self):
        # Use the captured candidate_pk to construct the success URL
        return reverse('unique_payment', kwargs={'candidate_id': self.candidate_pk})


class SchoolFeeUpdate(UpdateView):
    model = SchoolFee
    form_class = SchoolFeeForm
    template_name = 'schoolfee_form.html'

    def get_success_url(self):
        # Get the candidate_id from the updated SchoolFee record
        candidate_id = self.object.candidate.id
        # Construct the URL to redirect to the unique-payment history of the candidate
        return reverse('unique_payment', kwargs={'candidate_id': candidate_id})


class SchoolFeeDelete(DeleteView):
    model = SchoolFee
    template_name = 'schoolfee_confirm_delete.html'

    def get_object(self, queryset=None):
        # This method is called before deleting the object to ensure the object exists
        obj = super(SchoolFeeDelete, self).get_object(queryset)
        # Store candidate_id for later use in get_success_url
        self.candidate_id = obj.candidate.id
        return obj

    def get_success_url(self):
        # Use the stored candidate_id to construct the success URL
        return reverse('unique_payment', kwargs={'candidate_id': self.candidate_id})
def generate_invoice_number():
    return str(uuid.uuid4().hex)[:12]


def unique_payments(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    payments = UniquePayment.objects.filter(candidate=candidate)
    discounts = Discount.objects.all()
    unique_fees = FeeStructure.objects.filter(candidate=candidate)
    class_fees = ClassFee.objects.filter(candidate=candidate)
    fees = SchoolFee.objects.filter(candidate=candidate).order_by('starting_month')

    try:
        # Get the FeeStructure associated with the candidate
        fee_structure = FeeStructure.objects.get(candidate=candidate)
        total_amount_to_pay = fee_structure.total_amount_to_pay
    except FeeStructure.DoesNotExist:
        total_amount_to_pay = 135000  # Default amount

    try:
        # Get the latest Discount Applied
        discount_structure = Discount.objects.latest('date')
        discount_given = discount_structure.discount_amount
    except Discount.DoesNotExist:
        discount_given = 0  # Default amount

    total_amount_paid = sum(payment.amount_paid for payment in payments)
    total_discounts_applied = sum(discount.discount_amount for discount in discounts)
    balance_remaining = total_amount_to_pay - total_amount_paid - total_discounts_applied

    # Calculate "Payments Made" for each SchoolFee instance
    fees_with_payments = []
    for fee in fees:
        if total_amount_paid > 0:
            payment_for_month = min(total_amount_paid, fee.total_amount_to_pay)
            total_amount_paid -= payment_for_month
        else:
            payment_for_month = 0  # Set to 0 if total_amount_paid is exhausted

        fees_with_payments.append({
            'fee': fee,
            'payment_made': payment_for_month
        })

    return render(request, 'unique_payments.html', {
        'candidate': candidate,
        'payments': payments,
        'total_amount_to_pay': total_amount_to_pay,
        'total_amount_paid': sum(payment.amount_paid for payment in payments),  # Recalculate to include all payments
        'balance_remaining': balance_remaining,
        'discounts': discounts,
        'discount_given': discount_given,
        'total_discounts_applied': total_discounts_applied,
        'unique_fees': unique_fees,
        'fees_with_payments': fees_with_payments,  # Pass fees with calculated payments
        'class_fees': class_fees,
    })


def update_school_fees(request, candidate_id):
    # Get the specific candidate based on the passed candidate_id
    candidate = get_object_or_404(Candidate, pk=candidate_id)

    today = timezone.now().date()
    for month_offset in range(6):  # Iterate through the next 6 months
        month_start = today.replace(day=1) + relativedelta(months=+month_offset)
        month_end = (month_start + relativedelta(months=+1, days=-1))  # Last day of the month

        # Check if a SchoolFee record already exists for this candidate and starting_month
        fee_record, created = SchoolFee.objects.get_or_create(
            candidate=candidate,
            starting_month=month_start,
            defaults={
                'due_date': month_end,
                'total_amount_to_pay': 15000,
            }
        )

        # If the record was newly created, set the invoice_number
        if created:
            fee_record.invoice_number = generate_invoice_number()
            fee_record.save()

    # Redirect to the unique_payments view for the updated candidate
    return redirect('unique_payment', candidate_id=candidate_id)


def update_month_range(request, month_id):
    month = get_object_or_404(MonthRange, pk=month_id)
    if request.method == 'POST':
        form = MonthRangeForm(request.POST, instance=month)
        if form.is_valid():
            form.save()
            return redirect('student-card')
    else:
        form = MonthRangeForm(instance=month)
    return render(request, 'update_month_pay_form.html', {'form': form, 'month': month})


def add_month_to_class_fee(request, class_fee_id):
    class_fee = get_object_or_404(ClassFee, pk=class_fee_id)

    if request.method == 'POST':
        form = MonthRangeForm(request.POST)
        if form.is_valid():
            month_range = form.save(commit=False)
            month_range.class_fee = class_fee
            month_range.amount_to_pay = class_fee.total_amount_to_pay  # Set this to match ClassFee's total
            month_range.save()
            return redirect(
                'some-view')  # Redirect to a relevant view, make sure to replace 'some-view' with your actual view name
    else:
        form = MonthRangeForm()

    return render(request, 'add_month_form.html', {'form': form, 'class_fee': class_fee})


def remove_month_from_class_fee(request, month_range_id):
    month_range = get_object_or_404(MonthRange, pk=month_range_id)
    class_fee_id = month_range.class_fee.id
    month_range.delete()
    return redirect('some-view', class_fee_id=class_fee_id)  # Redirect to a relevant view


def create_class_fee(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)

    if request.method == 'POST':
        form = ClassFeeForm(request.POST)
        if form.is_valid():
            class_fee = form.save(commit=False)
            class_fee.candidate = candidate
            class_fee.invoice_number = str(uuid.uuid4().hex)[:12]
            class_fee.save()

            # Starting from the starting_date, create MonthRange instances for 6 months
            for i in range(6):
                month_date = class_fee.starting_date + relativedelta(months=+i)
                # Format month_name as "Day Month Year", e.g., "01 January 2024"
                month_name = month_date.strftime('%d %B %Y')
                MonthRange.objects.create(
                    class_fee=class_fee,
                    month_name=month_name,
                    amount_to_pay=class_fee.total_amount_to_pay
                )

            return redirect('student-card')  # Replace 'student-card' with your actual redirect URL name
    else:
        form = ClassFeeForm()

    return render(request, 'class_fee_form.html', {'form': form, 'candidate': candidate})


def update_candidates(request):
    CandidateFormSet = modelformset_factory(Candidate, fields=('Level_Of_German',), extra=0)
    if request.method == 'POST':
        level_form = LevelForm(request.POST)
        if level_form.is_valid():
            level = level_form.cleaned_data['level']
            if 'submit_level' in request.POST:
                formset = CandidateFormSet(queryset=Candidate.objects.filter(Level_Of_German=level))
            elif 'submit_formset' in request.POST:
                formset = CandidateFormSet(request.POST)
                if formset.is_valid():
                    formset.save()
                    return redirect('candidates')
                else:
                    for form in formset:
                        if form.errors:
                            for field in form:
                                for error in field.errors:
                                    print(f'Error in {field.label}: {error}')
        else:
            formset = CandidateFormSet(queryset=Candidate.objects.none())
    else:
        level_form = LevelForm()
        formset = CandidateFormSet(queryset=Candidate.objects.none())

    return render(request, 'update_candidates.html', {'formset': formset, 'level_form': level_form})


def add_candidate(request):
    thank_you_message = None
    if request.method == 'POST':
        candidate_info = CandidateInfo(request.POST, request.FILES)
        if candidate_info.is_valid():
            candidate_info.save()
            thank_you_message = "The Information is Captured! Do you want to find this record? "
            return render(request, 'add_candidate.html', {'thank_you_message': thank_you_message})
    else:
        candidate_info = CandidateInfo()

    context = {'candidate_info': candidate_info, 'thank_you_message': thank_you_message}

    return render(request, 'add_candidate.html', context)


def create_fee_structure(request):
    fees = FeeStructure.objects.all()
    thank_you_message = None

    if request.method == 'POST':
        form = FeeStructureForm(request.POST)
        if form.is_valid():
            # Generate a unique receipt number using UUID
            invoice_number = str(uuid.uuid4().hex)[:12]
            fee_structure = form.save(commit=False)
            fee_structure.invoice_number = invoice_number

            # Calculate duration
            date_format = "%Y-%m-%d"
            a = datetime.strptime(str(fee_structure.starting_date), date_format)
            b = datetime.strptime(str(fee_structure.due_date), date_format)
            delta = b - a
            fee_structure.duration = delta.days  # this will give you the duration in days

            # Get candidates that match the fee_assignment
            matching_candidates = Candidate.objects.filter(Level_Of_German=fee_structure.fee_assignment)

            # Set the candidate field of the FeeStructure for each matching candidate
            for candidate in matching_candidates:
                fee_structure.candidate = candidate
                fee_structure.save()

            thank_you_message = "Fee Structure Updated! Go back Home?"
            return render(request, 'fee_structure.html', {'thank_you_message': thank_you_message})
    else:
        form = FeeStructureForm()

    context = {'form': form,
               'thank_you_message': thank_you_message,
               'fees': fees,
               }

    return render(request, 'fee_structure.html', context)


def create_discount(request):
    discounts = Discount.objects.all()
    thank_you_message = None

    form = DiscountForm(request.POST)
    if form.is_valid():
        # Generate a unique receipt number using UUID
        discount_number = str(uuid.uuid4().hex)[:12]
        discount_structure = form.save(commit=False)
        discount_structure.discount_number = discount_number
        discount_structure.save()
        thank_you_message = "Discount Applied! Go back Home?"
        return render(request, 'discount_structure.html', {'thank_you_message': thank_you_message})
    else:
        form = DiscountForm()

    context = {'form': form,
               'thank_you_message': thank_you_message,
               'discounts': discounts,
               }

    return render(request, 'discount_structure.html', context)


def add_eldored_applicant(request):
    thank_you_message = None

    if request.method == 'POST':
        eldoret_info = EldoretInfo(request.POST, request.FILES)
        if eldoret_info.is_valid():
            eldoret_info.save()
            thank_you_message = "Thank you for your submission! Do you want to make another submission?"
            return render(request, 'eldoret_applicantions.html', {'thank_you_message': thank_you_message})

    else:
        eldoret_info = EldoretInfo()

    context = {'eldoret_info': eldoret_info, 'thank_you_message': thank_you_message}

    return render(request, 'eldoret_applicantions.html', context)

def generate_admission(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)

    if request.method == 'POST':
        form = AdmissionForm(request.POST)
        if form.is_valid():
            name = f"{candidate.First_Name} {candidate.Last_Name}"
            admission_number = f"{candidate.admission_number}"
            Date_of_Admission = form.cleaned_data['Date_of_Admission']
            German_Level = form.cleaned_data['German_Level']

            # Create an instance of the Invoice class
            admission = Admission()
            # Set the fields with the extracted data
            admission.Name = name
            admission.Date_of_Admission = Date_of_Admission
            admission.admission_number = admission_number
            admission.German_Level = German_Level


            pdf_path = admission.create_pdf_for_admissions()


            with open(pdf_path, 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="{name}_{admission_number}.pdf"'
                return response

    else:
        form = AdmissionForm()

    return render(request, 'generate_admission.html', {'form': form})


def generate_course_fee(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)

    if request.method == 'POST':
        form = CourseFeeForm(request.POST)
        if form.is_valid():
            name = f"{candidate.First_Name} {candidate.Last_Name}"
            Starting_Date = form.cleaned_data['Starting_Date']
            Ending_Date = form.cleaned_data['Ending_Date']
            Amount_to_Pay = form.cleaned_data['Amount_to_Pay']

            # Generate a unique receipt number using UUID
            invoice_number = str(uuid.uuid4().hex)[:12]

            # Create an instance of the Invoice class
            courseFee = CourseFee()
            # Set the fields with the extracted data
            courseFee.Name = name
            courseFee.Starting_Date = Starting_Date
            courseFee.Invoice_Number = invoice_number  # Set the generated receipt number
            courseFee.Ending_Date = Ending_Date
            courseFee.Amount_to_Pay = Amount_to_Pay

            pdf_path = courseFee.create_pdf_for_fee_structure()

            with open(pdf_path, 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="{name}_{invoice_number}.pdf"'
                return response

    else:
        form = CourseFeeForm()

    return render(request, 'generate_fee_structure.html', {'form': form})

def candidate_detail(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    contract = candidate.contract if hasattr(candidate, 'contract') else None

    # Construct the name in the same way as in the generate_admission view
    candidate_name = f"{candidate.First_Name} {candidate.Last_Name}"

    # Try to get the corresponding Admission record based on the name
    admission = Admission.objects.filter(Name=candidate_name).first()

    return render(request, 'candidate_detail.html', {
        'candidate': candidate,
        'contract': contract,
        'admission': admission,
    })


def generate_invoice(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)

    if request.method == 'POST':
        form = YourInvoiceForm(request.POST)
        if form.is_valid():
            name = f"{candidate.First_Name} {candidate.Last_Name}"
            street = candidate.Street_Address if candidate.Street_Address else ""
            city = candidate.Address
            phonenumber = candidate.phone_number

            # Generate a unique receipt number using UUID
            invoice_number = str(uuid.uuid4().hex)[:12]

            date_of_payment = form.cleaned_data['Date_of_Payment']
            amount_paid = form.cleaned_data['AmountPaid']

            # Create an instance of the Invoice class
            invoice = Invoice()
            # Set the fields with the extracted data
            invoice.Name = name
            invoice.Street = street
            invoice.City = city
            invoice.Phonenumber = phonenumber
            invoice.Invoice_Number = invoice_number  # Set the generated receipt number
            invoice.Date_of_Payment = date_of_payment

            pdf_path = invoice.create_pdf_from_data(amount_paid=amount_paid)


            # Save payment history
            payment_history = PaymentHistory.objects.create(
                candidate_name=name,
                phone_number=phonenumber,
                receipt_number=invoice_number,
                date_of_payment=date_of_payment,
                amount_paid=amount_paid
            )

            # Update Payment history
            unique_payment = UniquePayment.objects.create(
                candidate=candidate,  # Assign the candidate instance
                receipt_number=invoice_number,
                date_of_payment=date_of_payment,
                amount_paid=amount_paid
            )

            with open(pdf_path, 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="{name}_{invoice_number}.pdf"'
                return response

    else:
        form = YourInvoiceForm()

    return render(request, 'generate_invoice.html', {'form': form})

import calendar
from .forms import MonthSelectorForm
def index(request, year=datetime.now().year, month=datetime.now().month):
    if request.method == 'POST':
        form = MonthSelectorForm(request.POST)
        if form.is_valid():
            month_year = form.cleaned_data['month_year']
            year = month_year.year
            month = month_year.month
            # Now you can use 'year' and 'month' to filter your attendance records
    else:
        form = MonthSelectorForm()
    teacher = Teacher.objects.all()
    response = Response.objects.all()
    total_students = Candidate.objects.filter(Results="Paid").count()
    eligible_Applications = Application.objects.filter(Reply="Eligible").count()
    total_candidates = Candidate.objects.count()
    total_applications = Application.objects.count()
    attendance_records = ClassAttendance.objects.all()

    # Calculate the number of days in the specified month
    days_in_month = calendar.monthrange(year, month)[1]

    # Generate a list of dates for the specified month, excluding weekends
    month_dates = [datetime(year, month, day) for day in range(1, days_in_month + 1)
                   if datetime(year, month, day).weekday() < 5]  # 0-4 are weekdays

    # Check for attendance records for each day in the specified month
    attendance_status = {}
    for date in month_dates:
        attendance_recorded = ClassAttendance.objects.filter(date=date.date()).exists()
        attendance_status[date.date()] = 'Attendance Captured' if attendance_recorded else 'Attendance Not Captured'

    # Get the name of the selected month
    selected_month_name = calendar.month_name[month]

    # Fee structure and discount information handling
    try:
        fee_structure = FeeStructure.objects.latest('starting_date')
        fee_date = fee_structure.starting_date
        total_amount_to_pay = fee_structure.total_amount_to_pay
    except ObjectDoesNotExist:
        total_amount_to_pay = 15000  # Default amount
        fee_date = datetime.date(2024, 1, 31)  # Default date

    try:
        discount_structure = Discount.objects.latest('date')
        discount_date = discount_structure.date
        discount_given = discount_structure.discount_amount
    except ObjectDoesNotExist:
        discount_given = 0  # Default amount
        discount_date = datetime.date(2024, 1, 31)  # Default date



    context = {
        'teacher': teacher,
        'response': response,
        'total_students': total_students,
        'eligible_Applications': eligible_Applications,
        'total_candidates': total_candidates,
        'total_applications': total_applications,
        'total_amount_to_pay': total_amount_to_pay,
        'discount_given': discount_given,
        'fee_date': fee_date,
        'discount_date': discount_date,
        'attendance_records': attendance_records,
        'attendance_status': attendance_status,
        'selected_month_name': selected_month_name,
        'form': form,

    }

    return render(request, 'index.html', context)


def payment_history_view(request):
    unique_cohorts = Candidate.objects.values_list('course_intake', flat=True).distinct()
    selected_cohort = request.GET.get('cohort')

    # Fetching payment history from UniquePayment model
    payment_history = UniquePayment.objects.all()

    # Fetching additional data from the Candidate model
    candidates = Candidate.objects.all()
    fees = FeeStructure.objects.all()
    discounts = Discount.objects.all()
    if selected_cohort:
        candidates = candidates.filter(course_intake=selected_cohort)

    # Calculating total paid and balance for each candidate
    candidate_data = []
    for candidate in candidates:
        payments = UniquePayment.objects.filter(candidate=candidate)
        total_amount_paid = sum(payment.amount_paid for payment in payments)
        total_discounts_applied = sum(discount.discount_amount for discount in discounts)
        balance_remaining = sum(fee.total_amount_to_pay for fee in fees) - total_amount_paid - total_discounts_applied
        candidate_data.append({
            'id': candidate.id,  # Add candidate ID to the dictionary
            'name': f"{candidate.First_Name} {candidate.Last_Name}",
            'cohort': candidate.course_intake,
            'total_paid': total_amount_paid,
            'balance': balance_remaining,
        })

    return render(request, 'payment_history.html', {
        'candidate_data': candidate_data,
        'unique_cohorts': unique_cohorts,
        'selected_cohort': selected_cohort,
    })


def student(request):
    unique_course_locations = Candidate.objects.values_list('Course_Location', flat=True).distinct()
    unique_qualifications = Candidate.objects.values_list('Qualification', flat=True).distinct()
    unique_addresses = Candidate.objects.values_list('Address', flat=True).distinct()
    unique_cohorts = Candidate.objects.values_list('course_intake', flat=True).distinct()

    # Get selected filter values from the request
    selected_course_location = request.GET.get('course_location')
    selected_qualification = request.GET.get('qualification')
    selected_address = request.GET.get('address')
    selected_cohort = request.GET.get('cohort')

    # Filter candidates based on the selected filter values
    candidates = Candidate.objects.all()

    if selected_course_location:
        candidates = candidates.filter(Course_Location=selected_course_location)

    if selected_qualification:
        candidates = candidates.filter(Qualification=selected_qualification)

    if selected_address:
        candidates = candidates.filter(Address=selected_address)

    if selected_cohort:
        candidates = candidates.filter(course_intake=selected_cohort)

    return render(request, 'student.html', {
        'candidates': candidates,
        'unique_course_locations': unique_course_locations,
        'unique_qualifications': unique_qualifications,
        'unique_addresses': unique_addresses,
        'unique_cohorts': unique_cohorts,
        'selected_course_location': selected_course_location,
        'selected_qualification': selected_qualification,
        'selected_address': selected_address,
        'selected_cohort': selected_cohort,
    })

def class_attendance_record(request):
    unique_class_time = Candidate.objects.values_list('Time', flat=True).distinct()

    # Filter candidates based on the selected filter values
    selected_class_time = request.GET.get('Time')

    thank_you_message = None
    candidates = Candidate.objects.all()
    if selected_class_time:
        candidates = candidates.filter(Time=selected_class_time)

    teachers = Teacher.objects.all()

    # Get choices for absent_reason field
    absent_reason_choices = ClassAttendance._meta.get_field('absent_reason').choices

    if request.method == 'POST':
        date = request.POST.get('date')

        for candidate in candidates:
            present_key = f'present_{candidate.id}'
            absent_reason_key = f'absent_reason_{candidate.id}'

            present = request.POST.get(present_key)
            absent_reason = request.POST.get(absent_reason_key)

            # Check if present checkbox is checked
            present_value = present == 'on'

            # Check if either present or absent_reason is provided
            if present_value or absent_reason:
                # Create ClassAttendance instance and save
                ClassAttendance.objects.create(
                    candidate=candidate,
                    date=date,
                    present=present_value,
                    absent_reason=absent_reason
                )

        thank_you_message = "Attendance Captured! Do you want to make another submission?"

    context = {
        'thank_you_message': thank_you_message,
        'candidates': candidates,
        'teachers': teachers,
        'absent_reason_choices': absent_reason_choices,
        'unique_class_time': unique_class_time,
        'selected_class_time': selected_class_time,
    }
    return render(request, 'class_attendance.html', context)





def get_weekday_range(start_date, end_date):
    weekdays = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5:  # Exclude weekends (0-4 represent Monday to Friday)
            weekdays.append(current_date)
        current_date += timedelta(days=1)
    return weekdays


def getPdfPage(request):
    today = timezone.now()
    candidates = Candidate.objects.all()
    teacher = Teacher.objects.all()

    # Set the date range for the next 10 weekdays
    start_date = today.date()  # Use only the date part
    end_date = start_date + timedelta(days=15)
    weekdays_range = get_weekday_range(start_date, end_date)

    data = {'candidates': candidates, 'teacher': teacher, 'today': today, 'weekdays_range': weekdays_range}
    template = get_template('pdf_page.html')
    data_p = template.render(data)
    response = BytesIO()

    pdfPage = pisa.pisaDocument(BytesIO(data_p.encode("UTF-8")), response)
    if not pdfPage.err:
        return HttpResponse(response.getvalue(), content_type="application/pdf")
    else:
        return HttpResponse("Error Generating PDF")


def record_attendance(request, candidate_id):
    # Get the Candidate instance based on the candidate_id
    candidate = Candidate.objects.get(id=candidate_id)

    # Assuming there is a related Attendance record for the candidate
    attendance_record = Attendance.objects.filter(candidate=candidate).first()

    if attendance_record:
        teacher = attendance_record.teacher
    else:
        # If no attendance record is found, you may need to modify this logic
        teacher = None

    AttendanceFormSet = modelformset_factory(Attendance, form=AttendanceForm, extra=1)

    if request.method == 'POST':
        formset = AttendanceFormSet(request.POST, queryset=Attendance.objects.none())
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.candidate = candidate
                instance.save()
            return redirect('course_view')  # Redirect to a success page or another view

    else:
        formset = AttendanceFormSet(queryset=Attendance.objects.none())

    context = {
        'formset': formset,
        'candidate': candidate,
        'teacher': teacher,
    }

    return render(request, 'record_attendance.html', context)


def course_view(request):
    candidates = Candidate.objects.all()
    teachers = Teacher.objects.all()

    context = {
        'candidates': candidates,
        'teachers': teachers,
    }

    return render(request, 'course_view.html', context)


def attendance_details(request, candidate_id):
    candidate = Candidate.objects.get(id=candidate_id)
    teachers = Teacher.objects.all()
    attendances = ClassAttendance.objects.filter(candidate=candidate)

    context = {
        'candidate': candidate,
        'teachers': teachers,  # Use 'teachers' instead of 'teacher'
        'attendances': attendances,
    }

    return render(request, 'attendance_details.html', context)


def candidate_list(request, candidate_id=None):
    if candidate_id is not None:
        try:
            candidate = Candidate.objects.get(pk=candidate_id)
        except Candidate.DoesNotExist:
            # Handle the case where the candidate with the given ID does not exist
            candidate = None
    else:
        candidate = None
    contract = candidate.contract if hasattr(candidate, 'contract') else None
    # Fetch unique values for each filter from the database
    unique_course_locations = Candidate.objects.values_list('Course_Location', flat=True).distinct()
    unique_qualifications = Candidate.objects.values_list('Qualification', flat=True).distinct()
    unique_addresses = Candidate.objects.values_list('Address', flat=True).distinct()
    unique_cohorts = Candidate.objects.values_list('course_intake', flat=True).distinct()

    # Get selected filter values from the request
    selected_course_location = request.GET.get('course_location')
    selected_qualification = request.GET.get('qualification')
    selected_address = request.GET.get('address')
    selected_cohort = request.GET.get('cohort')

    # Filter candidates based on the selected filter values
    candidates = Candidate.objects.all()

    if selected_course_location:
        candidates = candidates.filter(Course_Location=selected_course_location)

    if selected_qualification:
        candidates = candidates.filter(Qualification=selected_qualification)

    if selected_address:
        candidates = candidates.filter(Address=selected_address)

    if selected_cohort:
        candidates = candidates.filter(course_intake=selected_cohort)

    return render(request, 'candidate_list.html', {
        'candidates': candidates,
        'unique_course_locations': unique_course_locations,
        'unique_qualifications': unique_qualifications,
        'unique_addresses': unique_addresses,
        'unique_cohorts': unique_cohorts,
        'selected_course_location': selected_course_location,
        'selected_qualification': selected_qualification,
        'selected_address': selected_address,
        'selected_cohort': selected_cohort,
        'contract': contract,
        'candidate': candidate,
    })


def upload_contract(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    contract, created = Contract.objects.get_or_create(candidate=candidate)

    if request.method == 'POST':
        form = ContractUploadForm(request.POST, request.FILES, instance=contract)
        if form.is_valid():
            form.save()
            # Use reverse to dynamically generate the URL for the candidate_detail view
            return redirect(reverse('candidate_detail', args=[candidate_id]))
    else:
        form = ContractUploadForm(instance=contract)

    return render(request, 'candidate_detail.html', {'form': form, 'candidate': candidate})


def apps_edit(request, pk, model_type):
    if model_type == 'application':
        model = Application
        form_class = EditApps
    elif model_type == 'sheet2application':
        model = Sheet2Application
        form_class = EditSheet2App
    else:
        return HttpResponseBadRequest("Invalid model type")

    item = get_object_or_404(model, pk=pk)

    if request.method == "POST":
        form = form_class(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('applications')  # Replace with the appropriate URL
    else:
        form = form_class(instance=item)

    return render(request, 'edit_data.html', {'form': form})


def add_applications(request):
    thank_you_message = None

    if request.method == 'POST':
        candidate_info = CandidateInfo(request.POST, request.FILES)
        if candidate_info.is_valid():
            candidate_info.save()
            thank_you_message = "Thank you for your submission! Do you want to make another submission?"
            return render(request, 'add_applications.html', {'thank_you_message': thank_you_message})

    else:
        candidate_info = CandidateInfo()

    context = {'candidate_info': candidate_info, 'thank_you_message': thank_you_message}

    return render(request, 'add_applications.html', context)



def eldoret_edit(request, pk, model_type):
    if model_type == 'Eldoret_Applicant':
        model = Eldoret_Applicant
        form_class = EditEldoret
    else:
        return HttpResponseBadRequest("Invalid model type")

    item = get_object_or_404(model, pk=pk)

    if request.method == "POST":
        form = form_class(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('enrolled_eldoret')  # Replace with the appropriate URL
    else:
        form = form_class(instance=item)

    return render(request, 'edit_data.html', {'form': form})


def update_database(request):
    # Set up Google Sheets API credentials
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict({
        "type": "service_account",
        "project_id": "aggerman-sheets",
        "private_key_id": "f393f9ef2934e9d3a8e4c95fc063ce74784bfce1",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDjFe9roGzAdF5w\nc0dIJlR+8RcqZ/B96GHAZRG1bLtn04j+oG6kx8P5yDE3UOoAQIBCZ81bywX/c30N\nAmv0y17R8YxlxmzOSRB+7ov7fWW3WSQRGkfMOR6MKu+b3q+U3XMv4iZz93ntIfQz\nw4yeKgy2cCmlijEqNw+cUj+CLzgXNPxKAbAlBfsnLjR4/0ynT+hIYptBIljD1tO0\n8MiI4Ykb8ON2M1WfejYA9usxEvdN7+o38s1RN+gPkIKIHreBSTu1q89le2HXZG7c\n6AuHNV6Ib2s/0Jjszuaxw3I67M7DPEF+iZcOQvlSm/L1Bl+OWbJl+Ri5lvI78J5s\nRNiYHj6JAgMBAAECggEABi0mDmjWHGPt36QbB7jXKn63MRWTonEMG5YEJcmXzUqh\nGr/VUpEGYQhTYlxGiQw4ENZO7RS4DIshFxX+RrGzWgV2WpxLgE7XboRhdU0jU5nO\nk9KBqmnRTWGrk7M6VlOxmtdNUXElNVBrmm7Sp8igAORLFbANB0dpGsjX5lwPa/4d\nUpawCQSxOkq2JCflObXtk1RkK5uKDGaqW9hgbw4dNFPvL4+dU35dBbfu4CgsSXxY\noKO7YxWyEYLRxnza8A36P78hdwAWfDriiGdkhow8oJnfO82Fj/eVW9sB6UPOwSe1\nRGe7nNBGz6020bcXRUM94O05VlxVCKTX2tuT8GCqewKBgQD0cI2s8hEM7TvI/w1l\nWbWcJpE9U+rdc6t06hCZrd5mRI2E/bcNZdhOE4wlASmHLMHYVfBLRPlVB3Nor3v8\nXhG4Vd+lXpYK55Ei5ZrX3jkO/FzEiiwP0Xnh6ZkrO+R5ro+7eTjJlU4Zduwr6a3R\ntME0YCpwJfjIszPNjeIuoQDOCwKBgQDt00au3Yr6AV63wb+51SgUXwEMWfpHHczn\nX0WJodhfUCbCksvc7TM+4G0O/SK/9W3R+YL4jzZwGkwqrWNDKEFzeOBP7GQDYIND\nc3hw7ASLLBBghtu0VmkBs+8j16ZPV2PdG+9/n+SgrDeRxaHNNO9u2MSjnBEk3rX+\ngrHTsV+GOwKBgCgj24AM+DPROUIWcBK2mpYb1znk7+qRthQq47L41E6i70Jpj4fJ\ns62OlDL3b+RcuzBVXHJfzznhUVhdiNS2dd55a5JyZ90+jZzXa4gLW/9T/b/gmL+4\nPHWWsKpi2XAJ9Fxq2aJwvDR+TOYhJ4QKVLfPGujzs1jx5I3awMu7cLBlAoGARQvo\n4o3ZcnoBWNI8aqRzDW8Dq+VXn1wMiEQFuU6utgVcK3NZEpwfG6smnoppk1ea+bI6\nDxXtFSDdaiqKvg2q6u52GV4lL0HO+j9FAWvUad9yJcQhdzr7I45s6HgMhc52ZNRe\ndSwjwW4eeAjrz9sFhKYUePevloe+SNUC8dX2SM8CgYACqtd9nWbzRLncAjOi01lj\nre3hYKFhED2KboGOyuN44XV+cfLUANRYPNsKXgFIJUGhRK27KuDOAk4wMD8eAIdr\nesxP8VKiRP9MucKemgbNE1Jut5RJjieTT/61xqyE0TvDRst+MVL8ep+OEhsK/FKZ\n8QkXCXQoQvWTHTZoW3WoTA==\n-----END PRIVATE KEY-----\n",
        "client_email": "service-account@aggerman-sheets.iam.gserviceaccount.com",
        "client_id": "101007819498863171311",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/service-account%40aggerman-sheets.iam.gserviceaccount.com"
    }, scope)

    client = gspread.authorize(credentials)

    # Get all values from the sheet
    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/15wAn9MyVGw2S_FlcMyvfCSIQQhydYQM8v-5XFFUDASg/edit#gid=0'
    sheet_name = 'Sheet1'
    sheet = client.open_by_url(spreadsheet_url).worksheet(sheet_name)

    # Get all values from the sheet
    values = sheet.get_all_values()

    # Update the Django database
    for row in values[1:]:  # Skip header row
        timestamp, name, phone_number, email, age, qualification, location, level_of_german, enrol_in_course, questions, time_for_class, online_or_physical, days_for_class, license_number = row
        Application.objects.update_or_create(
            timestamp=timestamp,
            defaults={
                'name': name,
                'phone_number': phone_number,
                'email': email,
                'age': age,
                'qualification': qualification,
                'location': location,
                'level_of_german': level_of_german,
                'enrol_in_course': enrol_in_course,
                'questions': questions,
                'time_for_class': time_for_class,
                'online_or_physical': online_or_physical,
                'days_for_class': days_for_class,
                'license_number': license_number
            }
        )

    return render(request, 'model.html', {'success_message': 'Data updated successfully.'})


def update_sheet2_database(request):
    # Set up Google Sheets API credentials
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict({
        "type": "service_account",
        "project_id": "aggerman-sheets",
        "private_key_id": "f393f9ef2934e9d3a8e4c95fc063ce74784bfce1",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDjFe9roGzAdF5w\nc0dIJlR+8RcqZ/B96GHAZRG1bLtn04j+oG6kx8P5yDE3UOoAQIBCZ81bywX/c30N\nAmv0y17R8YxlxmzOSRB+7ov7fWW3WSQRGkfMOR6MKu+b3q+U3XMv4iZz93ntIfQz\nw4yeKgy2cCmlijEqNw+cUj+CLzgXNPxKAbAlBfsnLjR4/0ynT+hIYptBIljD1tO0\n8MiI4Ykb8ON2M1WfejYA9usxEvdN7+o38s1RN+gPkIKIHreBSTu1q89le2HXZG7c\n6AuHNV6Ib2s/0Jjszuaxw3I67M7DPEF+iZcOQvlSm/L1Bl+OWbJl+Ri5lvI78J5s\nRNiYHj6JAgMBAAECggEABi0mDmjWHGPt36QbB7jXKn63MRWTonEMG5YEJcmXzUqh\nGr/VUpEGYQhTYlxGiQw4ENZO7RS4DIshFxX+RrGzWgV2WpxLgE7XboRhdU0jU5nO\nk9KBqmnRTWGrk7M6VlOxmtdNUXElNVBrmm7Sp8igAORLFbANB0dpGsjX5lwPa/4d\nUpawCQSxOkq2JCflObXtk1RkK5uKDGaqW9hgbw4dNFPvL4+dU35dBbfu4CgsSXxY\noKO7YxWyEYLRxnza8A36P78hdwAWfDriiGdkhow8oJnfO82Fj/eVW9sB6UPOwSe1\nRGe7nNBGz6020bcXRUM94O05VlxVCKTX2tuT8GCqewKBgQD0cI2s8hEM7TvI/w1l\nWbWcJpE9U+rdc6t06hCZrd5mRI2E/bcNZdhOE4wlASmHLMHYVfBLRPlVB3Nor3v8\nXhG4Vd+lXpYK55Ei5ZrX3jkO/FzEiiwP0Xnh6ZkrO+R5ro+7eTjJlU4Zduwr6a3R\ntME0YCpwJfjIszPNjeIuoQDOCwKBgQDt00au3Yr6AV63wb+51SgUXwEMWfpHHczn\nX0WJodhfUCbCksvc7TM+4G0O/SK/9W3R+YL4jzZwGkwqrWNDKEFzeOBP7GQDYIND\nc3hw7ASLLBBghtu0VmkBs+8j16ZPV2PdG+9/n+SgrDeRxaHNNO9u2MSjnBEk3rX+\ngrHTsV+GOwKBgCgj24AM+DPROUIWcBK2mpYb1znk7+qRthQq47L41E6i70Jpj4fJ\ns62OlDL3b+RcuzBVXHJfzznhUVhdiNS2dd55a5JyZ90+jZzXa4gLW/9T/b/gmL+4\nPHWWsKpi2XAJ9Fxq2aJwvDR+TOYhJ4QKVLfPGujzs1jx5I3awMu7cLBlAoGARQvo\n4o3ZcnoBWNI8aqRzDW8Dq+VXn1wMiEQFuU6utgVcK3NZEpwfG6smnoppk1ea+bI6\nDxXtFSDdaiqKvg2q6u52GV4lL0HO+j9FAWvUad9yJcQhdzr7I45s6HgMhc52ZNRe\ndSwjwW4eeAjrz9sFhKYUePevloe+SNUC8dX2SM8CgYACqtd9nWbzRLncAjOi01lj\nre3hYKFhED2KboGOyuN44XV+cfLUANRYPNsKXgFIJUGhRK27KuDOAk4wMD8eAIdr\nesxP8VKiRP9MucKemgbNE1Jut5RJjieTT/61xqyE0TvDRst+MVL8ep+OEhsK/FKZ\n8QkXCXQoQvWTHTZoW3WoTA==\n-----END PRIVATE KEY-----\n",
        "client_email": "service-account@aggerman-sheets.iam.gserviceaccount.com",
        "client_id": "101007819498863171311",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/service-account%40aggerman-sheets.iam.gserviceaccount.com"
    }, scope)

    client = gspread.authorize(credentials)

    # Get all values from the sheet
    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/15wAn9MyVGw2S_FlcMyvfCSIQQhydYQM8v-5XFFUDASg/edit#gid=0'
    sheet_name = 'Sheet2'
    sheet = client.open_by_url(spreadsheet_url).worksheet(sheet_name)

    # Get all values from the sheet
    values = sheet.get_all_values()

    # Update the Django database
    for row in values[1:]:  # Skip header row
        timestamp, name, phone_number, email, age, qualification, location, level_of_german, enrol_in_course, questions, time_for_class, online_or_physical, days_for_class = row
        Sheet2Application.objects.update_or_create(
            timestamp=timestamp,
            defaults={
                'name': name,
                'phone_number': phone_number,
                'email': email,
                'age': age,
                'qualification': qualification,
                'location': location,
                'level_of_german': level_of_german,
                'enrol_in_course': enrol_in_course,
                'questions': questions,
                'time_for_class': time_for_class,
                'online_or_physical': online_or_physical,
                'days_for_class': days_for_class
            }
        )

    return render(request, 'model.html', {'success_message': 'Data updated successfully.'})


def model(request):
    return render(request, 'model.html', {})


def rejected(request):
    sheet2 = Sheet2Application.objects.all()
    data = Application.objects.all()

    context = {'data': data, 'sheet2': sheet2}

    return render(request, 'rejected.html', context)


def later_on(request):
    sheet2 = Sheet2Application.objects.all()
    data = Application.objects.all()

    context = {'data': data, 'sheet2': sheet2}

    return render(request, 'not_now.html', context)


def applications(request):
    filter_sheet2 = request.GET.get('filter_sheet2')

    if filter_sheet2:
        # Case-insensitive filtering based on the selected Sheet2Application name
        data = Application.objects.filter(sheet2application__name__icontains=filter_sheet2)
    else:
        # If no filter is applied, retrieve all applications
        data = Application.objects.all()

    sheet2 = Sheet2Application.objects.all()
    context = {'data': data, 'sheet2': sheet2, 'filter_sheet2': filter_sheet2}

    return render(request, 'applications.html', context)


def mpesa(request):
    json_file_url = 'https://deannandi.co.ke/darajaapp/Mpesastkresponse.json'
    response = requests.get(json_file_url)

    try:
        response_text = response.text
        print("Response Text:", response_text)

        data = []
        decoder = json.JSONDecoder()
        pos = 0

        while pos < len(response_text):
            try:
                obj, pos = decoder.raw_decode(response_text, pos)
                data.append(obj)
                print("Parsed Data:", obj)
            except json.JSONDecodeError as e:
                pos += 1  # Move past the current character causing the error

    except json.JSONDecodeError as e:
        data = []
        error_message = str(e)
        response_text = f"Error: {error_message}"

    return render(request, 'mpesa.html', {'data': data})


def add_teacher(request):
    TeacherFormSet = modelformset_factory(Teacher, form=AddCourse, extra=1)

    if request.method == 'POST':
        formset = TeacherFormSet(request.POST, queryset=Teacher.objects.none())
        if formset.is_valid():
            formset.save()
            return redirect('/')  # Redirect to a success page or another view

    else:
        formset = TeacherFormSet(queryset=Teacher.objects.none())

    return render(request, 'add_teacher.html', {'formset': formset})


def add_student_view(request):
    StudentFormSet = modelformset_factory(Student, form=AddStudent, extra=1)

    if request.method == 'POST':
        formset = StudentFormSet(request.POST, queryset=Student.objects.none())
        if formset.is_valid():
            formset.save()
            return redirect('/')  # Redirect to a success page or another view

    else:
        formset = StudentFormSet(queryset=Student.objects.none())

    return render(request, 'new_student.html', {'formset': formset})


def edit_results(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)

    if request.method == 'POST':
        form = PostResults(request.POST, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, 'Results updated successfully')
        else:
            messages.error(request, 'Invalid form data. Please correct the errors.')

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else:
        form = PostResults(instance=candidate)

    return render(request, 'edit_results_modal.html', {'form': form, 'candidate': candidate})


def edit_item(request, pk, model, cls):
    item = get_object_or_404(model, pk=pk)

    if request.method == "POST":
        form = cls(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('responses')
    else:
        form = cls(instance=item)

        return render(request, 'edit_item.html', {'form': form})


def status_edit(request, pk):
    return edit_item(request, pk, Response, MyForm)


def enrolled_eldoret(request):
    eldoret = Eldoret_Applicant.objects.all()

    context = {'eldoret': eldoret}

    return render(request, 'enrolled_eldoret.html', context)


def my_form(request):
    if request.method == "POST":
        form = MyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('responses')
    else:
        form = MyForm()
    return render(request, 'Updated_Candidate_Profile.html', {'form': form})


def updated_candidate(request):
    candidates = Candidate.objects.all()
    context = {'candidates': candidates}

    return render(request, 'Updated_Candidate_Profile.html', context)


def separation(request):
    data = Application.objects.all()
    sheet2 = Sheet2Application.objects.all()  # Assuming Sheet2Application is your model for sheet2 data
    candidates = Candidate.objects.all()

    # Create a set of email addresses from the candidates
    candidate_emails = set(candidate.email_address for candidate in candidates)

    context = {'data': data, 'sheet2': sheet2, 'candidates': candidates, 'candidate_emails': candidate_emails}
    return render(request, 'responses.html', context)


def success(request):
    return render(request, 'import_success.html', {})


def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + user)

            return redirect('login')

    context = {'form': form}
    return render(request, 'register.html', context)


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                messages.info(request, 'Username OR password is incorrect')

        context = {}
        return render(request, 'login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')
