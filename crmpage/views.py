from django.contrib.auth import authenticate, login, logout
from .forms import CreateUserForm
from .forms import MyForm, MyApplications, CandidateInfo, PostResults, AddCourse, AddStudent
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
from .forms import EditApps, EditSheet2App
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .forms import YourInvoiceForm
from .models import Invoice, Contract
from .forms import ContractUploadForm
from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from .models import Candidate, Attendance
from .forms import AttendanceForm
import uuid
from django.db.models import Max
from django.forms import formset_factory


def generate_admission_numbers():
    candidates = Candidate.objects.all()

    for candidate in candidates:
        if not candidate.admission_number:
            # Generate a unique 6-digit admission number
            max_admission_number = Candidate.objects.aggregate(Max('admission_number'))['admission_number__max']
            new_admission_number = int(max_admission_number or 0) + 1
            candidate.admission_number = f"{new_admission_number:06d}"
            candidate.save()


# Run the function
generate_admission_numbers()


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
    candidate = get_object_or_404(Candidate, id=candidate_id)

    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.candidate = candidate
            instance.teacher = candidate.teachers.first()  # Adjust this logic based on your requirements
            instance.save()
            return redirect('course_view')

    else:
        form = AttendanceForm()

    context = {
        'form': form,
        'candidate': candidate,
    }

    return render(request, 'record_attendance.html', context)


def course_view(request):
    candidates = Candidate.objects.all()
    teachers = Teacher.objects.all()

    if request.method == 'POST':
        for candidate in candidates:
            form = AttendanceForm(request.POST, prefix=str(candidate.id))
            if form.is_valid():
                instance = form.save(commit=False)
                instance.candidates.add(candidate)
                instance.teacher = candidate.teacher  # Set the teacher from the candidate
                instance.save()

        return redirect('/')  # Redirect to a success page or another view

    context = {
        'candidates': candidates,
        'teachers': teachers,
    }

    return render(request, 'course_view.html', context)


def attendance_details(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    teachers = Teacher.objects.all()
    attendances = Attendance.objects.filter(candidates=candidate)  # Use the candidates field

    context = {
        'candidate': candidate,
        'teachers': teachers,
        'attendances': attendances,
    }

    return render(request, 'attendance_details.html', context)

def candidate_detail(request, candidate_id):
    candidate = Candidate.objects.get(pk=candidate_id)
    contract = candidate.contract if hasattr(candidate, 'contract') else None
    return render(request, 'candidate_detail.html', {'candidate': candidate, 'contract': contract})


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
            return redirect('/candidates/', pk=candidate_id)  # Use the correct URL name and parameter
    else:
        form = ContractUploadForm(instance=contract)

    return render(request, 'candidate_detail.html', {'form': form, 'candidate': candidate})


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

            # Create an instance of the Invoice class
            invoice = Invoice()
            # Set the fields with the extracted data
            invoice.Name = name
            invoice.Street = street
            invoice.City = city
            invoice.Phonenumber = phonenumber
            invoice.Invoice_Number = invoice_number  # Set the generated receipt number
            invoice.Date_of_Payment = date_of_payment

            pdf_path = invoice.create_pdf_from_data(amount_paid=form.cleaned_data['AmountPaid'])

            with open(pdf_path, 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="{name}_{invoice_number}.pdf"'
                return response

    else:
        form = YourInvoiceForm()

    return render(request, 'generate_invoice.html', {'form': form})


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


def index(request):
    teacher = Teacher.objects.all()
    response = Response.objects.all()
    total_students = Candidate.objects.filter(Results="Passed").count()
    total_responses = Response.objects.filter(Situation="Pending").count()
    total_applications = Application.objects.count()

    context = {'teacher': teacher, 'response': response, 'total_students': total_students,
               'total_responses': total_responses, 'total_applications': total_applications}
    return render(request, 'index.html', context)


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


def add_candidate(request):
    if request.method == 'POST':
        candidate_info = CandidateInfo(request.POST, request.FILES)
        if candidate_info.is_valid():
            candidate_info.save()
            return redirect('responses')
    else:
        candidate_info = CandidateInfo()
    return render(request, 'add_candidate.html', {'candidate_info': candidate_info})


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
