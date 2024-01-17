from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Response, Candidate, Application, Teacher, Student, Attendance, Sheet2Application, Contract
from django.forms import modelformset_factory, CheckboxSelectMultiple
from .models import Contract


class DateInput(forms.DateInput):
    input_type = 'date'


class TimeInput(forms.TimeInput):
    input_type = 'time'


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['candidates', 'date_of_class', 'is_present', 'is_absent', 'is_late', 'absent_reason']

    date_of_class = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    is_present = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    is_absent = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    is_late = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    absent_reason = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

class ContractUploadForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ['signed_contract']


class YourInvoiceForm(forms.Form):
    Date_of_Payment = forms.DateField(label='Date of Payment', widget=forms.DateInput(attrs={'type': 'date'}))
    AmountPaid = forms.DecimalField(label='Amount Paid', max_digits=10, decimal_places=2, required=False)
    # Add other fields as needed



class CandidateFilterForm(forms.Form):
    ADDRESS_CHOICES = [
        ('Other', 'Other'),
        ('Mombasa', 'Mombasa (001)'),
        ('Kwale', 'Kwale (002 )'),
        ('Kilifi', 'Kilifi (003)'),
        ('Tana River', 'Tana River (004)'),
        ('Lamu', 'Lamu (005)'),
        ('Taita–Taveta', 'Taita–Taveta (006)'),
        ('Garissa', 'Garissa (007)'),
        ('Wajir', 'Wajir (008)'),
        ('Mandera', 'Mandera (009)'),
        ('Marsabit', 'Marsabit (010)'),
        ('Isiolo', 'Isiolo (011)'),
        ('Meru', 'Meru (012)'),
        ('Tharaka-Nithi', 'Tharaka-Nithi (013)'),
        ('Embu', 'Embu (014)'),
        ('Kitui', 'Kitui (015)'),
        ('Makueni', 'Makueni (017)'),
        ('Nyandarua', 'Nyandarua (018)'),
        ('Nyeri', 'Nyeri (019)'),
        ('Kirinyaga', 'Kirinyaga (020)'),
        ('Muranga', 'Muranga (021)'),
        ('Kiambu', 'Kiambu (022)'),
        ('Turkana', 'Turkana (023)'),
        ('West Pokot', 'West Pokot (024)'),
        ('Samburu', 'Samburu (025)'),
        ('Trans-Nzoia', 'Trans-Nzoia (026)'),
        ('Uasin Gishu', 'Uasin Gishu (027)'),
        ('Elgeyo-Marakwet', 'Elgeyo-Marakwet (028)'),
        ('Nandi Kapsabet', 'Nandi Kapsabet (029)'),
        ('Baringo Kabarnet', 'Baringo Kabarnet (030)'),
        ('Laikipia', 'Laikipia (031)'),
        ('Nakuru', 'Nakuru (032)'),
        ('Narok', 'Narok (033)'),
        ('Kajiado', 'Kajiado (034)'),
        ('Kericho', 'Kericho (035)'),
        ('Bomet', 'Bomet (036)'),
        ('Kakamega', 'Kakamega (037)'),
        ('Vihiga', 'Vihiga (038)'),
        ('Bungoma', 'Bungoma (039)'),
        ('Busia', 'Busia (040)'),
        ('Siaya', 'Siaya (041)'),
        ('Kisumu', 'Kisumu (042)'),
        ('Homa Bay', 'Homa Bay (043)'),
        ('Migori', 'Migori (044)'),
        ('Kisii', 'Kisii (045)'),
        ('Nyamira', 'Nyamira (046)'),
        ('Nairobi', 'Nairobi (047)'),
        # Add other choices as needed
    ]

    course_class_no = forms.CharField(max_length=255, required=False)
    course_intake = forms.CharField(max_length=255, required=False)
    address = forms.ChoiceField(choices=ADDRESS_CHOICES, required=False)
    # Add other fields as needed


class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = '__all__'


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class CandidateInfo(forms.ModelForm):
    # Validations
    First_Name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    Last_Name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last name'}))
    Other_Address = forms.CharField(label='Address Information', required=False,
                                    widget=forms.TextInput(attrs={'placeholder': 'Apartment, studio, or floor'}))
    Street_Address = forms.CharField(label='Street', required=False,
                                     widget=forms.TextInput(
                                         attrs={'placeholder': 'Africa 118, Westlands, Nairobi'}))
    Zip_Address = forms.CharField(label='Zip', required=False,
                                  widget=forms.TextInput(attrs={'placeholder': '00100'}))
    phone_number = forms.CharField(label='Primary Phone Number',
                                   widget=forms.TextInput(attrs={'placeholder': 'Input as (+254) 7***'}))
    secondary_phone_number = forms.CharField(label='Secondary Phone Number', required=False,
                                             widget=forms.TextInput(attrs={'placeholder': 'Input as (+254) 7***'}))
    emergency_contact = forms.CharField(label='Emergency Contact Person', required=False,
                                        widget=forms.TextInput(attrs={'placeholder': 'Their name'}))
    emergency_phone_number = forms.CharField(label='Emergency Contact', required=False,
                                             widget=forms.TextInput(attrs={'placeholder': 'Input as (+254) 7***'}))
    email_address = forms.CharField(label='Email Address',
                                    widget=forms.TextInput(attrs={'placeholder': 'user@gmail/outlook.com'}))
    secondary_email_address = forms.CharField(label='Secondary Email Address', required=False,
                                              widget=forms.TextInput(attrs={'placeholder': 'user@gmail/outlook.com'}))
    Licence_No = forms.CharField(label='Licence Number', required=False)
    High_School_name = forms.CharField(label='High School Name', required=True, )
    High_School_grade = forms.CharField(label='High School Grade',
                                        widget=forms.TextInput(attrs={'placeholder': 'KCSE Grade only (A-)'}))
    High_School_Year = forms.CharField(label='Year Attained',
                                       widget=forms.TextInput(attrs={'placeholder': '2008'}))
    High_School_Year_start = forms.CharField(label='Year Started',
                                             widget=forms.TextInput(attrs={'placeholder': '2003'}))
    # uni one
    University_Name = forms.CharField(label='Name of University', required=False)
    Degree = forms.CharField(label='Name of Degree', required=False)
    GPA = forms.CharField(label='GPA Attained', required=False)
    University_Year_start = forms.CharField(label='Year Started', required=False,
                                             widget=forms.TextInput(attrs={'placeholder': '2003'}))
    University_Year = forms.CharField(label='Year Attained', required=False,
                                             widget=forms.TextInput(attrs={'placeholder': '2008'}))
    # uni two
    University_Name_secondary = forms.CharField(label='Name of University', required=False,)
    Degree_secondary = forms.CharField(label='Name of Second Degree', required=False, )
    GPA_secondary = forms.CharField(label='GPA Attained', required=False, )
    University_secondary_Year_start = forms.CharField(label='Year Started', required=False,
                                             widget=forms.TextInput(attrs={'placeholder': '2003'}))
    University_Year_secondary = forms.CharField(label='Year Attained', required=False,
                                             widget=forms.TextInput(attrs={'placeholder': '2008'}))
    # uni three
    University_Name_tertiary = forms.CharField(label='Name of University', required=False, )
    Degree_tertiary = forms.CharField(label='Name of third Degree', required=False, )
    GPA_tertiary = forms.CharField(label='GPA Attained', required=False, )
    University_tertiary_Year_start = forms.CharField(label='Year Started',
                                             widget=forms.TextInput(attrs={'placeholder': '2003'}), required=False,)
    University_Year_tertiary = forms.CharField(label='Year Attained',
                                             widget=forms.TextInput(attrs={'placeholder': '2008'}), required=False,)
    # college one
    College_Name = forms.CharField(label='Name of College', required=False)
    College_Degree = forms.CharField(label='Name of Degree', required=False)
    College_GPA = forms.CharField(label='GPA Attained', required=False)
    College_Degree_Year_start = forms.CharField(label='Year Started',
                                             widget=forms.TextInput(attrs={'placeholder': '2003'}), required=False,)
    College_Year = forms.CharField(label='Year Attained',
                                             widget=forms.TextInput(attrs={'placeholder': '2008'}), required=False,)
    # college two
    College_Name_secondary = forms.CharField(label='Name of College', required=False, )
    College_Degree_secondary = forms.CharField(label='Name of Second Degree', required=False, )
    College_GPA_secondary = forms.CharField(label='GPA Attained', required=False, )
    College_Degree_secondary_Year_start = forms.CharField(label='Year Started',
                                             widget=forms.TextInput(attrs={'placeholder': '2003'}), required=False,)
    College_Year_Secondary = forms.CharField(label='Year Attained',
                                             widget=forms.TextInput(attrs={'placeholder': '2008'}), required=False,)
    # college three
    College_Name_tertiary = forms.CharField(label='Name of College', required=False, )
    College_Degree_tertiary = forms.CharField(label='Name of third Degree', required=False, )
    College_GPA_tertiary = forms.CharField(label='GPA Attained', required=False, )
    College_tertiary_Year_start = forms.CharField(label='Year Started',
                                             widget=forms.TextInput(attrs={'placeholder': '2003'}), required=False,)
    College_Year_tertiary = forms.CharField(label='Year Attained',
                                             widget=forms.TextInput(attrs={'placeholder': '2008'}), required=False,)

    # Institution one
    Institution_name = forms.CharField(label='Name of Institution', required=False)
    Ward_name = forms.CharField(label='Name of Ward', required=False)
    Hours_worked = forms.CharField(label='Hours Worked', required=False)
    Institution_Year_start = forms.CharField(label='Year Started',
                                             widget=forms.TextInput(attrs={'placeholder': '2003'}), required=False,)
    Institution_Year_end = forms.CharField(label='Year Attained',
                                             widget=forms.TextInput(attrs={'placeholder': '2008'}), required=False,)

    # Institution two
    Institution_name_secondary = forms.CharField(label='Name of Institution', required=False, )
    Ward_name_secondary = forms.CharField(label='Name of Ward', required=False, )
    Hours_worked_secondary = forms.CharField(label='Hours Worked', required=False, )
    Institution_secondary_Year_start = forms.CharField(label='Year Started',
                                             widget=forms.TextInput(attrs={'placeholder': '2003'}), required=False,)
    Institution_secondary_Year_end = forms.CharField(label='Year Attained',
                                             widget=forms.TextInput(attrs={'placeholder': '2008'}), required=False,)
    # Institution three
    Institution_name_tertiary = forms.CharField(label='Name of Institution', required=False, )
    Ward_name_tertiary = forms.CharField(label='Name of Ward', required=False, )
    Hours_worked_tertiary = forms.CharField(label='Hours Worked', required=False, )
    Institution_tertiary_Year_start = forms.CharField(label='Year Started',
                                             widget=forms.TextInput(attrs={'placeholder': '2003'}), required=False,)
    Institution_tertiary_Year_end = forms.CharField(label='Year Attained',
                                             widget=forms.TextInput(attrs={'placeholder': '2008'}), required=False,)
    # File upload German Certs
    german_file = forms.FileField(label='German Certification',
                                  required=False,
                                  widget=forms.ClearableFileInput(
                                      attrs={
                                          'style': 'font-size: 13px'
                                      }
                                  )
                                  )
    # File upload English Certs
    english_file = forms.FileField(label='English Certification',
                                   required=False,
                                   widget=forms.ClearableFileInput(
                                       attrs={
                                           'style': 'font-size: 13px'
                                       }
                                   )
                                   )
    # File upload Licence Certs
    Licence_file = forms.FileField(label='Licence File',
                                   required=False,
                                   widget=forms.ClearableFileInput(
                                       attrs={
                                           'style': 'font-size: 13px'
                                       }
                                   )
                                   )
    # File upload High School Certs
    High_School_file = forms.FileField(label='High school Certificate',
                                       required=False,
                                       widget=forms.ClearableFileInput(
                                           attrs={
                                               'style': 'font-size: 13px'
                                           }
                                       )
                                       )
    # File upload University Certs
    University_file = forms.FileField(label='University Certificate',
                                      required=False,
                                      widget=forms.ClearableFileInput(
                                          attrs={
                                              'style': 'font-size: 13px'
                                          }
                                      )
                                      )
    # File upload Sec-University Certs
    University_secondary_file = forms.FileField(label='Secondary-University Certificate',
                                                required=False,
                                                widget=forms.ClearableFileInput(
                                                    attrs={
                                                        'style': 'font-size: 13px'
                                                    }
                                                )
                                                )
    # File upload University_tertiary_file
    University_tertiary_file = forms.FileField(label='University Tertiary Certificate ',
                                               required=False,
                                               widget=forms.ClearableFileInput(
                                                   attrs={
                                                       'style': 'font-size: 13px'
                                                   }
                                               )
                                               )
    # File upload College_Degree_file
    College_Degree_file = forms.FileField(label='College Certificate',
                                          required=False,
                                          widget=forms.ClearableFileInput(
                                              attrs={
                                                  'style': 'font-size: 13px'
                                              }
                                          )
                                          )
    # File upload College_Degree_secondary_file
    College_Degree_secondary_file = forms.FileField(label='College Certificate secondary',
                                                    required=False,
                                                    widget=forms.ClearableFileInput(
                                                        attrs={
                                                            'style': 'font-size: 13px'
                                                        }
                                                    )
                                                    )
    # File upload College_tertiary_file
    College_tertiary_file = forms.FileField(label='College tertiary Certificate',
                                            required=False,
                                            widget=forms.ClearableFileInput(
                                                attrs={
                                                    'style': 'font-size: 13px'
                                                }
                                            )
                                            )
    # File upload Institution_file
    Institution_file = forms.FileField(label='Institution Certificate',
                                       required=False,
                                       widget=forms.ClearableFileInput(
                                           attrs={
                                               'style': 'font-size: 13px'
                                           }
                                       )
                                       )
    # File upload Institution_file_secondary
    Institution_file_secondary = forms.FileField(label='Institution secondary Certificate',
                                                 required=False,
                                                 widget=forms.ClearableFileInput(
                                                     attrs={
                                                         'style': 'font-size: 13px'
                                                     }
                                                 )
                                                 )
    # File upload Institution_file_tertiary
    Institution_file_tertiary = forms.FileField(label='Institution tertiary Certificate',
                                                required=False,
                                                widget=forms.ClearableFileInput(
                                                    attrs={
                                                        'style': 'font-size: 13px'
                                                    }
                                                )
                                                )

    class Meta:
        model = Candidate
        fields = '__all__'
        widgets = {
            'Date_of_Birth': DateInput(),
            'child_date_of_birth': DateInput(),
            'child_date_of_birth2': DateInput(),
            'Schedule_Interview_date': DateInput(),
            'Schedule_Interview_time': TimeInput(),

        }
        labels = {
            'Address': 'County',
            'fluency_in_language': 'English Level',
            'Level_Of_German': 'German Level',
            'photo': 'Passport Photo',
            'Child_name2': 'Second Child',
            'child_sex2': 'Sex',
            'child_date_of_birth': 'Date Of Birth',
            'child_date_of_birth2': 'Date Of Birth',
            'child_sex': 'Sex',

        }


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['lec_first_name', 'lec_last_name', 'lec_phone_number', 'lec_email_address', 'lec_class_name']


class AddCourse(forms.ModelForm):
    course_class_no = forms.CharField(label='Class Number', required=False,
                                      widget=forms.TextInput(attrs={'placeholder': 'GERMAN CLASS 0001'}))
    course_intake = forms.CharField(label='Course Intake', required=False,
                                    widget=forms.TextInput(attrs={'placeholder': '(DEC-AUG 2023/2024)'}))
    lec_class_name = forms.CharField(label='Class Name', widget=forms.TextInput(attrs={'placeholder': 'Class A1'}))

    class Meta:
        model = Teacher
        fields = '__all__'
        labels = {
            'course_class_no': 'Class Number',
            'course_intake': 'Course Intake',
            'lec_first_name': 'First Name',
            'lec_last_name': 'Last Name',
            'lec_phone_number': 'Phone Number',
            'lec_email_address': 'Email',
            'lec_class_name': 'Class Name'
        }


class AddStudent(forms.ModelForm):
    course_class_no = forms.CharField(required=False, label='Class Number',
                                      widget=forms.TextInput(attrs={'placeholder': 'GERMAN CLASS 0001'}))
    course_intake = forms.CharField(required=False, label='Course Intake',
                                    widget=forms.TextInput(attrs={'placeholder': '(DEC-AUG 2023/2024)'}))

    class Meta:
        model = Student
        fields = ['student_first_name', 'student_second_name', 'student_phone_number', 'student_email_address',
                  'course_class_no', 'course_intake']


class PostResults(forms.ModelForm):
    class Meta:
        model = Candidate  # Specify the model for the form
        fields = ['First_Name', 'Last_Name', 'Results']
        labels = {
            'Results': 'Transaction',


        }

    def __init__(self, *args, **kwargs):
        super(PostResults, self).__init__(*args, **kwargs)
        readonly_fields = ['First_Name', 'Last_Name']

        for field_name in readonly_fields:
            self.fields[field_name].widget.attrs.update({'readonly': 'readonly'})


class EditApps(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['name', 'phone_number', 'email', 'age', 'qualification', 'location', 'level_of_german',
                  'enrol_in_course', 'Reply']
        labels = {
            'enrol_in_course': 'When To Start',
            'Reply': 'Eligibility Check',

        }

    def __init__(self, *args, **kwargs):
        super(EditApps, self).__init__(*args, **kwargs)
        readonly_fields = ['name', 'phone_number', 'email', 'age', 'qualification', 'location', 'level_of_german',
                           'enrol_in_course']

        for field_name in readonly_fields:
            self.fields[field_name].widget.attrs.update({'readonly': 'readonly'})


class EditSheet2App(forms.ModelForm):
    class Meta:
        model = Sheet2Application
        fields = ['name', 'phone_number', 'email', 'age', 'qualification', 'location', 'level_of_german',
                  'enrol_in_course', 'Reply']  # Add the relevant fields from Sheet2Application model
        labels = {
            'enrol_in_course': 'When To Start',
            'Reply': 'Eligibility Check',

        }

    def __init__(self, *args, **kwargs):
        super(EditSheet2App, self).__init__(*args, **kwargs)
        readonly_fields = ['name', 'phone_number', 'email', 'age', 'qualification', 'location', 'level_of_german',
                           'enrol_in_course']

        for field_name in readonly_fields:
            self.fields[field_name].widget.attrs.update({'readonly': 'readonly'})


class MyForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['Name', 'Email', 'Situation']


class MyApplications(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['Timestamp', 'Name', 'PhoneNumber', 'Email', 'Age', 'Qualification', 'Licence_number',
                  'Location', 'level_of_German',
                  'enrol_to_course',
                  'participate_in_course',
                  'time_class', 'days_class', 'questions', 'Reply']
        labels = {
            'Timestamp': 'Time', 'Name': 'Name', 'PhoneNumber': 'Telephone',
            'Email': 'Email', 'Age': 'Age', 'Qualification': 'Qualification',
            'Licence_number': 'Licence Number',
            'Location': 'Location', 'level_of_German': 'level of German',
            'enrol_to_course': 'When To be Enrolled',
            'participate_in_course': 'Physical or Online Classes?',
            'time_class': 'Class Times', 'days_class': 'Days for Class', 'questions': 'Any Questions',
            'Reply': 'Form Completion Status'
        }
