from django.db import models
from multiselectfield import MultiSelectField
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import uuid


class Invoice(models.Model):
    # Your existing fields...
    Name = models.CharField(max_length=255)
    Street = models.CharField(max_length=255)
    City = models.CharField(max_length=255)
    Phonenumber = models.CharField(max_length=20)
    Invoice_Number = models.CharField(max_length=36, unique=True, default=uuid.uuid4, editable=False)
    Date_of_Payment = models.DateField()
    AmountPaid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def convert_to_str(self, amount):
        return f"{amount} KES"

    def netto(self, amount, mwst=0.19):
        return round(amount * (1 / (1 + mwst)), 2)

    def create_pdf_from_data(self, amount_paid=None):
        # Specify the base directory to save PDFs
        base_dir = 'path/to/save/'

        # Ensure the base directory exists, create it if necessary
        os.makedirs(base_dir, exist_ok=True)

        # Construct the full path for the PDF file
        pdf_path = os.path.join(base_dir, f'{self.Name}_{self.Invoice_Number}.pdf')

        # Example: Use ReportLab to generate a more detailed PDF
        pdf = canvas.Canvas(pdf_path, pagesize=letter)

        # Set font and font size
        pdf.setFont("Helvetica", 12)

        # Company details
        pdf.drawString(100, 770, "AG German School Ltd.")
        pdf.drawString(100, 755, "Ambank House")
        pdf.drawString(100, 740, "00100 CBD, Nairobi")

        # Load and draw the image
        logo_path = 'C:/Users/deann/PycharmProjects/agCrm/crmpage/static/img/AG_German_Institute.png'
        image_width = 100
        image_height = 50
        image_x = 400
        image_y = 750
        pdf.drawImage(logo_path, image_x, image_y, width=image_width, height=image_height, preserveAspectRatio=True)

        # Invoice title
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(100, 720, f"Receipt for {self.Date_of_Payment.strftime('%B, %Y')}")
        pdf.line(100, 715, 500, 715)  # Horizontal line

        # Invoice details
        invoice_details_x = 400
        pdf.setFont("Helvetica", 10)
        pdf.drawString(invoice_details_x, 700, f"Receipt for: {self.Name}")
        pdf.drawString(invoice_details_x, 685, f"Address: {self.City}")
        pdf.drawString(invoice_details_x, 670, f"Phone Number: {self.Phonenumber}")
        pdf.drawString(invoice_details_x, 655, f"Receipt Number: {self.Invoice_Number}")
        pdf.drawString(invoice_details_x, 640, f"Date of Payment: {self.Date_of_Payment.strftime('%Y-%m-%d')}")

        # Description of services and costs
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(100, 620, "Description of services Costs")
        pdf.line(100, 615, 500, 615)  # Horizontal line

        # Example: Calculate total amount
        total_amount = self.AmountPaid if self.AmountPaid is not None else 15000

        # Add more content as needed
        pdf.setFont("Helvetica", 10, leading=12)
        pdf.drawString(100, 600, "Monthly Tuition for AG German Institute")
        pdf.drawString(100, 585,
                       f"Includes all course materials and classes for {self.Date_of_Payment.strftime('%m/%Y')}")
        pdf.drawString(400, 600, f"{self.convert_to_str(amount_paid)}")  # Updated line with dynamic amount_paid

        # Total
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(100, 570, "Total")
        pdf.line(100, 560, 500, 560)  # Horizontal line

        # Draw the top separator line
        pdf.line(100, 565, 500, 565)

        # Calculate the width of the total amount text
        total_text = f"Total {self.convert_to_str(amount_paid)}"
        text_width = pdf.stringWidth(total_text, "Helvetica-Bold", 12)

        # Calculate the position to center the text
        center_x = 400

        # Draw the total amount text
        pdf.drawString(center_x, 545, total_text)

        # Draw the bottom separator line
        pdf.line(100, 540, 500, 540)

        # Center align the additional information
        center_x = 300  # Adjust as needed
        additional_info_y = 510
        line_height = 12  # Adjust the line height

        pdf.setFont("Helvetica", 10)

        # Akodgan Glaszner German School Ltd. - Ambank House - 00100 CBD, Nairobi
        text = "Akodgan Glaszner German School Ltd. - Ambank House - 00100 CBD, Nairobi"
        text_width = pdf.stringWidth(text, "Helvetica", 10)
        pdf.drawString(center_x - text_width / 2, additional_info_y, text)
        additional_info_y -= line_height

        # +254 110853 892 - info@germaninstitute.co.ke - www.germaninstitute.co.ke
        text = "+254 110853 892 - info@germaninstitute.co.ke - www.germaninstitute.co.ke"
        text_width = pdf.stringWidth(text, "Helvetica", 10)
        pdf.drawString(center_x - text_width / 2, additional_info_y, text)
        additional_info_y -= line_height

        # Save the PDF
        pdf.save()

        return pdf_path


class Student(models.Model):
    student_first_name = models.CharField(max_length=255)
    student_second_name = models.CharField(max_length=255)
    student_phone_number = models.CharField(max_length=50, blank=True, null=True, unique=True)
    student_email_address = models.EmailField(max_length=70, blank=True, null=True, unique=True)
    course_class_no = models.CharField(max_length=255)
    course_intake = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.student_first_name} {self.student_second_name}"


SEX = (
    ('None', 'None'),
    ('Male', 'Male'),
    ('Female', 'Female')
)

YES_or_NO = (
    ('Pending', 'Pending'),
    ('Yes', 'Yes'),
    ('No', 'No')
)

REPLY = (
    ('Incomplete', 'Incomplete'),
    ('Completed', 'Completed'),
)

RESULTS = (
    ('Paid', 'Paid'),
    ('Not-Paid', 'Not-Paid')
)

DAYS = (
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
    ('Sunday', 'Sunday'),

)
TIME = (
    ('None', 'None'),
    ('morning (around 8:00 - 12:00)', 'morning (around 8:00 - 12:00)'),
    ('afternoon (around 12:00 - 16:00)', 'afternoon (around 12:00 - 16:00)'),
    ('evening (around 16:30 - 20:30)', 'evening (around 16:30 - 20:30)'),

)

LANGUAGE = (
    ('None', 'None'),
    ('English Beginner', 'English Beginner'),
    ('English Intermediate', 'English Intermediate'),
    ('English Advanced', 'English Advanced'),
)

GERMAN = (
    ('None', 'None'),
    ('A1', 'A1'),
    ('A2', 'A2'),
    ('B1', 'B1'),
    ('B2', 'B2'),

)
LEVELS = (
    ('None', 'None'),
    ('Beginner', 'Beginner'),
    ('Intermediate', 'Intermediate'),
    ('Advanced', 'Advanced'),
)

COURSE_LOCATION = (
    ('Nairobi-CBD', 'Nairobi-CBD'),
    ('Nairobi-Daystar', 'Nairobi-Daystar'),
    ('Mombasa', 'Mombasa'),
    ('Muranga', 'Muranga'),
    ('Kisumu', 'Kisumu'),
    ('Kisii', 'Kisii'),
    ('Eldoret', 'Eldoret'),

)
ADDRESS = (
    ('Type a County', 'Type a County'),
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

)
COHORT = (
    ('Class (DEC-AUG 2023/2024 Semester)', 'Class (DEC-AUG 2023/2024 Semester)'),
    ('Class (JAN-SEPT 2024 Semester)', 'Class (JAN-SEPT 2024 Semester)'),

)

QUALIFICATION = (
    ('Kenya Registerd Community Health Nurse (KRCHN)', 'Kenya Registerd Community Health Nurse (KRCHN)'),
    ('Kenya Enrolled Community Health Nurse (KECHN)', 'Kenya Enrolled Community Health Nurse (KECHN)'),
    ('B.Sc Nursing (BSN)', 'B.Sc Nursing (BSN)'),
    ('Newly Graduated Nursing Student (diploma/BSN)', 'Newly Graduated Nursing Student (diploma/BSN)'),
    ('Nurse Aid', 'Nurse Aid'),
    ('Clinical Officer', 'Clinical Officer'),
    ('Other Qualification', 'Other Qualification'),
)


class Candidate(models.Model):
    First_Name = models.CharField(max_length=255)
    Last_Name = models.CharField(max_length=255)
    Date_of_Birth = models.DateField(max_length=50, blank=True, null=True)
    Sex = models.CharField(max_length=50, null=True, choices=SEX, default='None')
    Address = models.CharField(max_length=100, null=True, choices=ADDRESS, default='Other')
    # cohorts
    course_intake = models.CharField(max_length=255, choices=COHORT, blank=True, null=True)
    # image candidate
    photo = models.ImageField(upload_to='candidate_photos/', null=True, blank=True)
    Street_Address = models.CharField(max_length=512, blank=True, null=True)
    Other_Address = models.CharField(max_length=50, blank=True, null=True)
    Zip_Address = models.CharField(max_length=50, blank=True, null=True)
    fluency_in_language = models.CharField(max_length=50, null=True, choices=LANGUAGE, default='None')
    english_file = models.FileField(blank=True, null=True)
    Level_Of_German = models.CharField(max_length=50, null=True, choices=GERMAN, default='None')
    german_file = models.FileField(blank=True, null=True)
    Spouse = models.CharField(max_length=50, null=True, choices=YES_or_NO, default='Pending')
    Spouse_Name = models.CharField(max_length=512, blank=True, null=True)
    Children = models.CharField(max_length=50, null=True, choices=YES_or_NO, default='Pending')
    Child_name = models.CharField(max_length=512, blank=True, null=True)
    child_sex = models.CharField(max_length=255, choices=SEX, default='None')
    child_date_of_birth = models.CharField(max_length=512, blank=True, null=True)
    Child_name2 = models.CharField(max_length=512, blank=True, null=True)
    child_sex2 = models.CharField(max_length=255, choices=SEX, default='None')
    child_date_of_birth2 = models.CharField(max_length=512, blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True, unique=True)
    secondary_phone_number = models.CharField(max_length=50, blank=True, null=True)
    emergency_contact = models.CharField(max_length=512, blank=True, null=True)
    emergency_phone_number = models.CharField(max_length=50, blank=True, null=True)
    email_address = models.EmailField(max_length=70, blank=True, null=True, unique=True)
    secondary_email_address = models.EmailField(max_length=70, blank=True, null=True)
    Licence_No = models.CharField(max_length=100, blank=True, null=True)
    Licence_file = models.FileField(blank=True, null=True)
    # qualification
    Qualification = models.CharField(max_length=255, choices=QUALIFICATION, null=True)
    # end of it
    High_School_name = models.CharField(max_length=512, blank=True, null=True)
    High_School_Year_start = models.CharField(max_length=4, blank=True, null=True)
    High_School_grade = models.CharField(max_length=3, blank=True, null=True)
    High_School_Year = models.CharField(max_length=4, blank=True, null=True)
    High_School_file = models.FileField(blank=True, null=True)
    # Uni one
    University_Name = models.CharField(max_length=512, blank=True, null=True)
    Degree = models.CharField(max_length=512, blank=True, null=True)
    GPA = models.CharField(max_length=10, blank=True, null=True)
    University_Year_start = models.CharField(max_length=4, blank=True, null=True)
    University_Year = models.CharField(max_length=4, blank=True, null=True)
    University_file = models.FileField(blank=True, null=True)
    # uni two
    University_Name_secondary = models.CharField(max_length=512, blank=True, null=True)
    Degree_secondary = models.CharField(max_length=100, blank=True, null=True)
    GPA_secondary = models.CharField(max_length=10, blank=True, null=True)
    University_secondary_Year_start = models.CharField(max_length=4, blank=True, null=True)
    University_Year_secondary = models.CharField(max_length=4, blank=True, null=True)
    University_secondary_file = models.FileField(blank=True, null=True)
    # uni three
    University_Name_tertiary = models.CharField(max_length=512, blank=True, null=True)
    University_tertiary_Year_start = models.CharField(max_length=4, blank=True, null=True)
    Degree_tertiary = models.CharField(max_length=100, blank=True, null=True)
    GPA_tertiary = models.CharField(max_length=10, blank=True, null=True)
    University_Year_tertiary = models.CharField(max_length=4, blank=True, null=True)
    University_tertiary_file = models.FileField(blank=True, null=True)
    # college one
    College_Name = models.CharField(max_length=512, blank=True, null=True)
    College_Degree_Year_start = models.CharField(max_length=4, blank=True, null=True)
    College_Degree = models.CharField(max_length=100, blank=True, null=True)
    College_GPA = models.CharField(max_length=10, blank=True, null=True)
    College_Year = models.CharField(max_length=4, blank=True, null=True)
    College_Degree_file = models.FileField(blank=True, null=True)
    # college two
    College_Name_secondary = models.CharField(max_length=512, blank=True, null=True)
    College_Degree_secondary_Year_start = models.CharField(max_length=4, blank=True, null=True)
    College_Degree_secondary = models.CharField(max_length=100, blank=True, null=True)
    College_GPA_secondary = models.CharField(max_length=10, blank=True, null=True)
    College_Year_Secondary = models.CharField(max_length=4, blank=True, null=True)
    College_Degree_secondary_file = models.FileField(blank=True, null=True)
    # college three
    College_Name_tertiary = models.CharField(max_length=512, blank=True, null=True)
    College_tertiary_Year_start = models.CharField(max_length=4, blank=True, null=True)
    College_Degree_tertiary = models.CharField(max_length=100, blank=True, null=True)
    College_GPA_tertiary = models.CharField(max_length=10, blank=True, null=True)
    College_Year_tertiary = models.CharField(max_length=4, blank=True, null=True)
    College_tertiary_file = models.FileField(blank=True, null=True)
    # Institution one
    Institution_name = models.CharField(max_length=512, blank=True, null=True)
    Ward_name = models.CharField(max_length=512, blank=True, null=True)
    Hours_worked = models.CharField(max_length=512, blank=True, null=True)
    Institution_Year_start = models.CharField(max_length=4, blank=True, null=True)
    Institution_Year_end = models.CharField(max_length=4, blank=True, null=True)
    Institution_file = models.FileField(blank=True, null=True)
    # Institution two
    Institution_name_secondary = models.CharField(max_length=512, blank=True, null=True)
    Ward_name_secondary = models.CharField(max_length=512, blank=True, null=True)
    Hours_worked_secondary = models.CharField(max_length=512, blank=True, null=True)
    Institution_secondary_Year_start = models.CharField(max_length=4, blank=True, null=True)
    Institution_secondary_Year_end = models.CharField(max_length=4, blank=True, null=True)
    Institution_file_secondary = models.FileField(blank=True, null=True)
    # Institution three
    Institution_name_tertiary = models.CharField(max_length=512, blank=True, null=True)
    Ward_name_tertiary = models.CharField(max_length=512, blank=True, null=True)
    Hours_worked_tertiary = models.CharField(max_length=512, blank=True, null=True)
    Institution_tertiary_Year_end = models.CharField(max_length=4, blank=True, null=True)
    Institution_tertiary_Year_start = models.CharField(max_length=4, blank=True, null=True)
    Institution_file_tertiary = models.FileField(blank=True, null=True)
    # updated location
    Course_Location = models.CharField(max_length=50, choices=COURSE_LOCATION, null=True, )
    # end
    Days = MultiSelectField(max_length=50, choices=DAYS)
    Time = models.CharField(max_length=50, null=True, choices=TIME, default='None')
    Results = models.CharField(max_length=50, blank=True, null=True, choices=RESULTS, default='Not-Paid')
    Schedule_Interview_date = models.DateField(max_length=50, blank=True, null=True)
    Schedule_Interview_time = models.TimeField(max_length=50, blank=True, null=True)
    admission_number = models.CharField(max_length=6, unique=True, blank=True, null=True)

    def __str__(self):
        return f"{self.First_Name} {self.Last_Name}"


class Teacher(models.Model):
    lec_first_name = models.CharField(max_length=255)
    lec_last_name = models.CharField(max_length=255)
    course_class_no = models.CharField(max_length=255)
    course_intake = models.CharField(max_length=255)
    lec_phone_number = models.CharField(max_length=50, blank=True, null=True, unique=True)
    lec_email_address = models.EmailField(max_length=70, blank=True, null=True, unique=True)
    lec_class_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.lec_first_name} {self.lec_last_name}"



class Attendance(models.Model):
    candidates = models.ManyToManyField('Candidate', related_name='attendances')
    date_of_class = models.DateField(blank=True, null=True)
    is_present = models.BooleanField(default=False)
    is_absent = models.BooleanField(default=False)
    is_late = models.BooleanField(default=False)
    absent_reason = models.CharField(max_length=255, blank=True, null=True)
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE, related_name='attendances')

    def __str__(self):
        return f"{self.candidates} - {self.teacher} - {self.date_of_class}"



class Contract(models.Model):
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name='contract')
    signed_contract = models.FileField(upload_to='signed_contracts/', null=True, blank=True)

    def __str__(self):
        return f"{self.candidate} {self.signed_contract}"


YES_or_NO = (
    ('Pending', 'Pending'),
    ('Yes', 'Yes'),
    ('No', 'No')
)

SITUATION = (
    ('Pending', 'Pending'),
    ('Rejected', 'Rejected'),
    ('Interview', 'Interview'),
    ('Not Now', 'Not Now')
)

REPLYING = (
    ('Pending', 'Pending'),
    ('Completed', 'Completed'),
)


class Response(models.Model):
    Timestamp = models.CharField(max_length=2555)
    Name = models.CharField(max_length=2555)
    PhoneNumber = models.CharField(max_length=2555)
    Email = models.CharField(max_length=2555)
    Age = models.CharField(max_length=255)
    Qualification = models.CharField(max_length=2555)
    Licence_number = models.CharField(max_length=2555)
    Location = models.CharField(max_length=2555)
    level_of_German = models.CharField(max_length=255)
    enrol_to_course = models.CharField(max_length=2555)
    participate_in_course = models.CharField(max_length=255)
    time_class = models.CharField(max_length=255)
    days_class = models.CharField(max_length=255)
    questions = models.TextField()
    Situation = models.CharField(max_length=50, null=True, choices=SITUATION, default='Pending')
    date = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    Reply = models.CharField(max_length=50, null=True, choices=REPLYING, default='Pending')


ELIGIBILITY = (
    ('Pending', 'Pending'),
    ('Eligible', 'Eligible'),
    ('Not-Eligible', 'Not-Eligible'),
    ('Not-Now', 'Not-Now')
)


class Sheet2Application(models.Model):
    timestamp = models.CharField(max_length=512, blank=True, null=True)
    name = models.CharField(max_length=512, blank=True, null=True)
    phone_number = models.CharField(max_length=512, blank=True, null=True)
    email = models.CharField(max_length=512, blank=True, null=True)
    age = models.CharField(max_length=512, blank=True, null=True)
    qualification = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=512, blank=True, null=True)
    level_of_german = models.CharField(max_length=512, blank=True, null=True)
    enrol_in_course = models.CharField(max_length=512, blank=True, null=True)
    questions = models.CharField(max_length=512, blank=True, null=True)
    time_for_class = models.CharField(max_length=512, blank=True, null=True)
    online_or_physical = models.CharField(max_length=512, blank=True, null=True)
    days_for_class = models.CharField(max_length=512, blank=True, null=True)
    Reply = models.CharField(max_length=50, null=True, choices=ELIGIBILITY, default='Pending')


class Application(models.Model):
    timestamp = models.CharField(max_length=512, blank=True, null=True)
    name = models.CharField(max_length=512, blank=True, null=True)
    phone_number = models.CharField(max_length=512, blank=True, null=True)
    email = models.CharField(max_length=512, blank=True, null=True)
    age = models.CharField(max_length=512, blank=True, null=True)
    qualification = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=512, blank=True, null=True)
    level_of_german = models.CharField(max_length=512, blank=True, null=True)
    enrol_in_course = models.CharField(max_length=512, blank=True, null=True)
    questions = models.CharField(max_length=512, blank=True, null=True)
    time_for_class = models.CharField(max_length=512, blank=True, null=True)
    online_or_physical = models.CharField(max_length=512, blank=True, null=True)
    days_for_class = models.CharField(max_length=512, blank=True, null=True)
    license_number = models.CharField(max_length=512, blank=True, null=True)
    Reply = models.CharField(max_length=50, null=True, choices=ELIGIBILITY, default='Pending')
    sheet2application = models.ForeignKey(Sheet2Application, on_delete=models.CASCADE, null=True, blank=True)
