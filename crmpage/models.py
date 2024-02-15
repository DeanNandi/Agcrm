from django.db import models
from multiselectfield import MultiSelectField
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import uuid
from django.utils import timezone
from django.core.files.base import ContentFile
from io import BytesIO
# Fee Structure new
from datetime import timedelta

class CourseFee(models.Model):
    Name = models.CharField(max_length=255)
    Starting_Date = models.DateField()
    Ending_Date = models.DateField()
    Amount_to_Pay = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    Invoice_Number = models.CharField(max_length=36, unique=True, default=uuid.uuid4, editable=False)
    pdf_file = models.FileField(upload_to='Fee_structures/', null=True, blank=True)

    def convert_to_str(self, amount):
        return f"{amount} KES"

    def netto(self, amount, mwst=0.19):
        return round(amount * (1 / (1 + mwst)), 2)

    def create_pdf_for_fee_structure(self, amount_paid=None):
        # Specify the base directory to save PDFs
        base_dir = 'C:/Users/deann/PycharmProjects/agCrm/media'

        # Example PDF generation logic using ReportLab
        pdf_buffer = BytesIO()
        pdf = canvas.Canvas(pdf_buffer)

        # Ensure the base directory exists, create it if necessary
        os.makedirs(base_dir, exist_ok=True)

        # Construct the full path for the PDF file
        pdf_path = os.path.join(base_dir, f'{self.Name}_{self.Invoice_Number}.pdf')

        # Example: Use ReportLab to generate a more detailed PDF
        pdf = canvas.Canvas(pdf_path, pagesize=letter)

        # Set font and font size
        pdf.setFont("Helvetica", 12)

        # Company details
        pdf.drawString(100, 670, "Fee Structure.")
        pdf.drawString(100, 650, "AG German School Ltd.")
        pdf.drawString(100, 630, "Ambank House")
        pdf.drawString(100, 610, "00100 CBD, Nairobi")

        # Load and draw the image
        logo_path = 'C:/Users/deann/PycharmProjects/agCrm/crmpage/static/img/AG_German_Institute.png'
        image_width = 100
        image_height = 50
        image_x = 400
        image_y = 700
        pdf.drawImage(logo_path, image_x, image_y, width=image_width, height=image_height, preserveAspectRatio=True)

        # Fees title
        invoice_details_x2 = 400
        pdf.setFont("Helvetica", 10)
        pdf.drawString(invoice_details_x2, 545, f"Fee Structure for: {self.Name}")
        pdf.drawString(invoice_details_x2, 525, f"Invoice Number: {self.Invoice_Number}")
        pdf.drawString(invoice_details_x2, 505, f"Date: {self.Starting_Date.strftime('%Y-%m-%d')}")

        # Increase space after Invoice details
        pdf.drawString(100, 500, " " * 5)  # Add space

        # Description of services and costs
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(100, 465, f"Description of services")
        pdf.line(100, 460, 500, 460)  # Horizontal line

        # Calculate the number of months
        delta = self.Ending_Date - self.Starting_Date
        months = (
                             self.Ending_Date.year - self.Starting_Date.year) * 12 + self.Ending_Date.month - self.Starting_Date.month

        # Fees details
        current_date = self.Starting_Date
        fees_y_position = 442  # Starting Y position for fees details
        monthly_fee = float(self.Amount_to_Pay)  # Assuming this is the monthly fee
        for _ in range(months + 1):
            # Add fee detail for each month
            pdf.drawString(100, fees_y_position,
                           f"Tuition for AG German Institute for month {current_date.strftime('%m/%Y')} - {self.convert_to_str(monthly_fee)}")
            fees_y_position -= 20  # Adjust Y position for the next entry
            current_date += timedelta(days=30)  # Approximation to move to the next month

        # Total
        total_amount = monthly_fee * (months + 1)
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(400, fees_y_position - 20, "Total")
        pdf.line(100, fees_y_position - 30, 500, fees_y_position - 30)  # Horizontal line
        pdf.drawString(400, fees_y_position - 50, f"Total {self.convert_to_str(total_amount)}")
        pdf.line(100, fees_y_position - 60, 500, fees_y_position - 60)  # Horizontal line
        pdf.line(100, fees_y_position - 55, 500, fees_y_position - 55)  # Horizontal line


        # Calculate the position to center the text
        center_x = 400

        # Increase space after Total section
        pdf.drawString(100, 300, " " * 5)  # Add space

        # Center align the additional information
        center_x = 300  # Adjust as needed
        additional_info_y = 240
        line_height = 12  # Adjust the line height

        pdf.setFont("Helvetica", 10)

        # Akodgan Glaszner German School Ltd. - Ambank House - 00100 CBD, Nairobi
        text = "Akodgan Glaszner German School Ltd. - Ambank House - 00100 CBD, Nairobi"
        text_width = pdf.stringWidth(text, "Helvetica", 10)
        pdf.drawString(center_x - text_width / 2, additional_info_y, text)
        additional_info_y -= line_height

        # +254 110853 892 - info@germaninstitute.co.ke - www.germaninstitute.co.ke
        text = "Phone and WhatsApp +254 110853 892 - info@germaninstitute.co.ke - www.germaninstitute.co.ke"
        text_width = pdf.stringWidth(text, "Helvetica", 10)
        pdf.drawString(center_x - text_width / 2, additional_info_y, text)
        additional_info_y -= line_height

        # Bank Details
        text = "Kenya Commercial Bank - Account number 1321761716 or MPESA Paybill: 522 533 Account No: 774 5020"
        text_width = pdf.stringWidth(text, "Helvetica", 10)
        pdf.drawString(center_x - text_width / 2, additional_info_y, text)
        additional_info_y -= line_height

        # Appreciation
        text = "Thank you for being part of our Institution"
        text_width = pdf.stringWidth(text, "Helvetica", 10)
        pdf.drawString(center_x - text_width / 2, additional_info_y, text)
        additional_info_y -= line_height

        # Save the PDF
        pdf.save()

        # Get the PDF data
        pdf_data = pdf_buffer.getvalue()
        pdf_buffer.close()

        # Generate a PDF filename
        pdf_filename = f"{self.Name}_{self.Invoice_Number}.pdf"

        # Save the PDF file to the pdf_file field
        self.pdf_file.save(pdf_filename, ContentFile(pdf_data))
        self.save()
        return pdf_path

class Admission(models.Model):
    Name = models.CharField(max_length=255)
    admission_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    Date_of_Admission = models.DateField()
    GERMAN_LEVEL = (
        ('A1', 'A1'),
        ('A2', 'A2'),
        ('B1', 'B1'),
        ('B2', 'B2'),
    )
    German_Level = models.CharField(max_length=50, null=True, choices=GERMAN_LEVEL, default='None')
    pdf_file = models.FileField(upload_to='admissions/', null=True, blank=True)


    def create_pdf_for_admissions(self):
        # Specify the base directory to save PDFs
        base_dir = 'C:/Users/deann/PycharmProjects/agCrm/media'

        # Example PDF generation logic using ReportLab
        pdf_buffer = BytesIO()
        pdf = canvas.Canvas(pdf_buffer)

        # Ensure the base directory exists, create it if necessary
        os.makedirs(base_dir, exist_ok=True)

        # Construct the full path for the PDF file
        pdf_path = os.path.join(base_dir, f'{self.Name}_{self.admission_number}.pdf')

        # Example: Use ReportLab to generate a more detailed PDF
        pdf = canvas.Canvas(pdf_path, pagesize=letter)

        # Set font and font size
        pdf.setFont("Helvetica", 12)

        # Company details
        pdf.drawString(100, 670, "Admission Letter.")
        pdf.drawString(100, 650, "AG German School Ltd.")
        pdf.drawString(100, 630, "Ambank House")
        pdf.drawString(100, 610, "00100 CBD, Nairobi")

        # Load and draw the image
        logo_path = 'C:/Users/deann/PycharmProjects/agCrm/crmpage/static/img/AG_German_Institute.png'
        image_width = 100
        image_height = 50
        image_x = 400
        image_y = 700
        pdf.drawImage(logo_path, image_x, image_y, width=image_width, height=image_height, preserveAspectRatio=True)

        # Admissions title
        invoice_details_x2 = 400
        pdf.setFont("Helvetica", 10)
        pdf.drawString(invoice_details_x2, 545, f"Admission for: {self.Name}")
        pdf.drawString(invoice_details_x2, 525, f"Admission Number: {self.admission_number}")
        pdf.drawString(invoice_details_x2, 505, f"Date: {self.Date_of_Admission.strftime('%Y-%m-%d')}")

        # Increase space after Invoice details
        pdf.drawString(100, 500, " " * 5)  # Add space

        # Description of services and costs
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(100, 460, f"Dear {self.Name},")

        # Increase space after Description title
        pdf.drawString(100, 450, " " * 5)  # Add space

        # Add more content as needed
        pdf.setFont("Helvetica", 10, leading=12)
        pdf.drawString(100, 442, f"We are pleased to inform you that you have been admitted to the AG German Institute for the ")
        pdf.drawString(100, 430,
                       f"class of {self.Date_of_Admission.strftime('%B, %Y')}.")

        pdf.drawString(100, 400,
                       f"Attached to the letter of admission you will find the fee structure for the training programme ")

        pdf.drawString(100, 388,
                       f"at {self.German_Level} level.")

        pdf.drawString(100, 350,
                       f"We congratulate you. We look forward to seeing you.")
        pdf.drawString(100, 320,
                       f"Sincerely,")

        # Load and draw the image
        logo_path = 'C:/Users/deann/PycharmProjects/agCrm/crmpage/static/img/tobias_new.jpg'
        image_width = 100
        image_height = 50
        image_x = 100
        image_y = 260
        pdf.drawImage(logo_path, image_x, image_y, width=image_width, height=image_height, preserveAspectRatio=True)

        pdf.drawString(100, 230,
                       f"Tobias Glaszner")
        pdf.drawString(100, 210,
                       f"Director")

        # Increase space after Content section
        pdf.drawString(100, 240, " " * 2)  # Add space

        # Save the PDF
        pdf.save()

        # Get the PDF data
        pdf_data = pdf_buffer.getvalue()
        pdf_buffer.close()

        # Generate a PDF filename
        pdf_filename = f"{self.Name}_{self.Date_of_Admission}.pdf"

        # Save the PDF file to the pdf_file field
        self.pdf_file.save(pdf_filename, ContentFile(pdf_data))
        self.save()
        return pdf_path

class Invoice(models.Model):
    # Your existing fields...
    Name = models.CharField(max_length=255)
    Street = models.CharField(max_length=255)
    City = models.CharField(max_length=255)
    Phonenumber = models.CharField(max_length=20)
    Invoice_Number = models.CharField(max_length=36, unique=True, default=uuid.uuid4, editable=False)
    Date_of_Payment = models.DateField()
    AmountPaid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pdf_file = models.FileField(upload_to='receipts/', null=True, blank=True)


    def convert_to_str(self, amount):
        return f"{amount} KES"

    def netto(self, amount, mwst=0.19):
        return round(amount * (1 / (1 + mwst)), 2)

    def create_pdf_from_data(self, amount_paid=None):
        # Specify the base directory to save PDFs
        base_dir = 'C:/Users/deann/PycharmProjects/agCrm/media'

        # Example PDF generation logic using ReportLab
        pdf_buffer = BytesIO()
        pdf = canvas.Canvas(pdf_buffer)

        # Ensure the base directory exists, create it if necessary
        os.makedirs(base_dir, exist_ok=True)

        # Construct the full path for the PDF file
        pdf_path = os.path.join(base_dir, f'{self.Name}_{self.Invoice_Number}.pdf')

        # Example: Use ReportLab to generate a more detailed PDF
        pdf = canvas.Canvas(pdf_path, pagesize=letter)

        # Set font and font size
        pdf.setFont("Helvetica", 12)

        # Company details
        pdf.drawString(100, 670, "AG German School Ltd.")
        pdf.drawString(100, 650, "Ambank House")
        pdf.drawString(100, 630, "00100 CBD, Nairobi")

        # Load and draw the image
        logo_path = 'C:/Users/deann/PycharmProjects/agCrm/crmpage/static/img/AG_German_Institute.png'
        image_width = 100
        image_height = 50
        image_x = 400
        image_y = 700
        pdf.drawImage(logo_path, image_x, image_y, width=image_width, height=image_height, preserveAspectRatio=True)

        # Invoice title
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(100, 545, f"Receipt for {self.Date_of_Payment.strftime('%B, %Y')}")
        pdf.line(100, 675, 525, 675)  # Horizontal line

        # Increase space after Receipt title
        pdf.drawString(100, 500, " " * 5)  # Add space

        # Receipt Student Details
        invoice_details_x2 = 100
        pdf.setFont("Helvetica", 10)
        pdf.drawString(invoice_details_x2, 460, f"Receipt for: {self.Name}")
        pdf.drawString(invoice_details_x2, 420, f"Phone Number: {self.Phonenumber}")

        # Invoice details
        invoice_details_x = 350
        pdf.setFont("Helvetica", 10)

        pdf.drawString(invoice_details_x, 395, f"Receipt Number: {self.Invoice_Number}")
        pdf.drawString(invoice_details_x, 381, f"Date of Payment: {self.Date_of_Payment.strftime('%Y-%m-%d')}")

        # Increase space after Invoice details
        pdf.drawString(100, 300, " " * 5)  # Add space

        # Description of services and costs
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(100, 265, "Description of services Costs")
        pdf.line(100, 560, 200, 560)  # Horizontal line

        # Increase space after Description title
        pdf.drawString(100, 250, " " * 5)  # Add space

        # Example: Calculate total amount
        total_amount = self.AmountPaid if self.AmountPaid is not None else 15000

        # Add more content as needed
        pdf.setFont("Helvetica", 10, leading=12)
        pdf.drawString(100, 242, "Monthly Tuition for AG German Institute")
        pdf.drawString(100, 225,
                       f"Includes all course materials and classes for {self.Date_of_Payment.strftime('%m/%Y')}")
        pdf.drawString(400, 220, f"{self.convert_to_str(amount_paid)}")  # Updated line with dynamic amount_paid

        # Increase space after Content section
        pdf.drawString(100, 200, " " * 5)  # Add space

        # Total
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(100, 115, "Total")
        pdf.line(100, 105, 500, 405)  # Horizontal line

        # Draw the top separator line
        pdf.line(100, 110, 500, 410)

        # Calculate the width of the total amount text
        total_text = f"Total {self.convert_to_str(amount_paid)}"
        text_width = pdf.stringWidth(total_text, "Helvetica-Bold", 12)

        # Calculate the position to center the text
        center_x = 100

        # Draw the total amount text
        pdf.drawString(center_x, 390, total_text)

        # Draw the bottom separator line
        pdf.line(100, 385, 500, 385)

        # Increase space after Total section
        pdf.drawString(100, 365, " " * 5)  # Add space

        # Center align the additional information
        center_x = 300  # Adjust as needed
        additional_info_y = 360
        line_height = 12  # Adjust the line height

        pdf.setFont("Helvetica", 10)

        # Akodgan Glaszner German School Ltd. - Ambank House - 00100 CBD, Nairobi
        text = "Akodgan Glaszner German School Ltd. - Ambank House - 00100 CBD, Nairobi"
        text_width = pdf.stringWidth(text, "Helvetica", 10)
        pdf.drawString(center_x - text_width / 2, additional_info_y, text)
        additional_info_y -= line_height

        # +254 110853 892 - info@germaninstitute.co.ke - www.germaninstitute.co.ke
        text = "Phone and WhatsApp +254 110853 892 - info@germaninstitute.co.ke - www.germaninstitute.co.ke"
        text_width = pdf.stringWidth(text, "Helvetica", 10)
        pdf.drawString(center_x - text_width / 2, additional_info_y, text)
        additional_info_y -= line_height

        # Bank Details
        text = "Kenya Commercial Bank - Account number 1321761716 or MPESA Paybill: 522 533 Account No: 774 5020"
        text_width = pdf.stringWidth(text, "Helvetica", 10)
        pdf.drawString(center_x - text_width / 2, additional_info_y, text)
        additional_info_y -= line_height

        # Appreciation
        text = "Thank you for being part of our Institution"
        text_width = pdf.stringWidth(text, "Helvetica", 10)
        pdf.drawString(center_x - text_width / 2, additional_info_y, text)
        additional_info_y -= line_height

        # Save the PDF
        pdf.save()

        # Get the PDF data
        pdf_data = pdf_buffer.getvalue()
        pdf_buffer.close()

        # Generate a PDF filename
        pdf_filename = f"{self.Name}_{self.Invoice_Number}.pdf"

        # Save the PDF file to the pdf_file field
        self.pdf_file.save(pdf_filename, ContentFile(pdf_data))
        self.save()
        return pdf_path


class Discount(models.Model):
    discount_amount = models.IntegerField()
    date = models.DateField()
    discount_number = models.CharField(max_length=12)


class PaymentHistory(models.Model):
    candidate_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    receipt_number = models.CharField(max_length=12, unique=True)
    date_of_payment = models.DateField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.candidate_name} - Receipt: {self.receipt_number}"


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
    ('Nairobi_CBD', 'Nairobi_CBD'),
    ('Nairobi_Hospital', 'Nairobi_Hospital'),
    ('Nairobi_Karen', 'Nairobi_Karen'),
    ('Nairobi_Daystar', 'Nairobi_Daystar'),
    ('Mombasa', 'Mombasa'),
    ('Muranga', 'Muranga'),
    ('Kisumu', 'Kisumu'),
    ('Kisii', 'Kisii'),
    ('Eldoret', 'Eldoret'),
    ('Thika', 'Thika'),

)

COURSE_CLASSES = (
    ('Nairobi-CBD', 'CBD'),
    ('Nairobi-Hospital', 'NBH'),
    ('Nairobi-Karen', 'KHS'),
    ('Nairobi-Daystar', 'DUS'),
    ('Mombasa', 'MSA'),
    ('Muranga', 'MRG'),
    ('Kisumu', 'KSM'),
    ('Kisii', 'KSI'),
    ('Eldoret', 'ELD'),
    ('Thika', 'THK'),
)


ADDRESS = (
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
ADMISSION_ADDRESS = (
    ('Mombasa', 'MSA'),
    ('Kwale', 'KWL'),
    ('Kilifi', 'KLF'),
    ('Tana River', 'TRV'),
    ('Lamu', 'LMU'),
    ('Taita–Taveta', 'TVT'),
    ('Garissa', 'GRS'),
    ('Wajir', 'WJR'),
    ('Mandera', 'MDR'),
    ('Marsabit', 'MRS'),
    ('Isiolo', 'ISL'),
    ('Meru', 'MRU'),
    ('Tharaka-Nithi', 'TNT'),
    ('Embu', 'EMB'),
    ('Kitui', 'KTU'),
    ('Machakos', 'MCK'),  # Added from your document
    ('Makueni', 'MKN'),
    ('Nyandarua', 'NDR'),  # Updated abbreviation from your document
    ('Nyeri', 'NYR'),  # Updated abbreviation from your document
    ('Kirinyaga', 'KRG'),
    ('Muranga', 'MRG'),  # Updated abbreviation from your document
    ('Kiambu', 'KMB'),  # Updated abbreviation from your document
    ('Turkana', 'TRK'),
    ('West Pokot', 'WPK'),
    ('Samburu', 'SBR'),  # Updated abbreviation from your document
    ('Trans-Nzoia', 'TNZ'),
    ('Uasin Gishu', 'UGS'),  # Updated abbreviation from your document
    ('Elgeyo-Marakwet', 'EMK'),
    ('Nandi', 'NDI'),  # Updated abbreviation from your document
    ('Baringo', 'BRG'),
    ('Laikipia', 'LKP'),
    ('Nakuru', 'NKR'),  # Updated abbreviation from your document
    ('Narok', 'NRK'),
    ('Kajiado', 'KJD'),
    ('Kericho', 'KRC'),
    ('Bomet', 'BMT'),
    ('Kakamega', 'KKG'),
    ('Vihiga', 'VHG'),
    ('Bungoma', 'BGM'),
    ('Busia', 'BSA'),
    ('Siaya', 'SYA'),
    ('Kisumu', 'KSM'),
    ('Homa Bay', 'HBY'),
    ('Migori', 'MGR'),
    ('Kisii', 'KSI'),
    ('Nyamira', 'NMR'),  # Updated abbreviation from your document
    ('Nairobi', 'NBI'),  # Updated abbreviation from your document
)

COHORT = (
    ('Class (DEC-AUG 2023/2024 Semester)', 'Class (DEC-AUG 2023/2024 Semester)'),
    ('Class (JAN-SEPT 2024 Semester)', 'Class (JAN-SEPT 2024 Semester)'),
    ('Class (FEB-OCT 2024 Semester)', 'Class (FEB-OCT 2024 Semester)'),

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
    GERMAN = (
        ('A1', 'A1'),
        ('A2', 'A2'),
        ('B1', 'B1'),
        ('B2', 'B2'),
        ('C1', 'C1'),
        ('C2', 'C2'),
    )
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
    admission_number = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def __str__(self):
        return f"{self.First_Name} {self.Last_Name}"


ELIGIBILITY = (
    ('Pending', 'Pending'),
    ('Eligible', 'Eligible'),
    ('Not-Eligible', 'Not-Eligible'),
    ('Not-Now', 'Not-Now')
)

ELDORET_TIME = (
    ('None', 'None'),
    ('morning (around 8:30 - 12:30)', 'morning (around 8:30 - 12:30)'),
    ('afternoon (around 13:00 - 17:00)', 'afternoon (around 13:00 - 17:00)'),
    ('evening (around 17:30 - 21:00)', 'evening (around 17:30 - 21:00)'),

)


class Eldoret_Applicant(models.Model):
    First_Name = models.CharField(max_length=255)
    Last_Name = models.CharField(max_length=255)
    Date_of_Birth = models.DateField(max_length=50, blank=True, null=True)
    Sex = models.CharField(max_length=50, null=True, choices=SEX, default='None')
    Address = models.CharField(max_length=100, null=True, choices=ADDRESS, default='Other')
    # cohorts
    course_intake = models.CharField(max_length=255, choices=COHORT, blank=True, null=True)
    # image candidate
    photo = models.ImageField(upload_to='candidate_photos/', null=True, blank=True)
    Identification_Card_Image = models.ImageField(upload_to='applicant_ID_photos/')
    Street_Address = models.CharField(max_length=512, blank=True, null=True)
    Other_Address = models.CharField(max_length=50, blank=True, null=True)
    Zip_Address = models.CharField(max_length=50, blank=True, null=True)
    fluency_in_language = models.CharField(max_length=50, null=True, choices=LANGUAGE, default='None', blank=True)
    english_file = models.FileField(blank=True, null=True)
    Level_Of_German = models.CharField(max_length=50, null=True, choices=GERMAN, default='None', blank=True)
    german_file = models.FileField(blank=True, null=True)
    Spouse = models.CharField(max_length=50, null=True, choices=YES_or_NO, default='Pending')
    Spouse_Qualification = models.CharField(max_length=512, blank=True, null=True)
    Children = models.CharField(max_length=50, null=True, choices=YES_or_NO, default='Pending')
    Number_Of_Children = models.IntegerField(max_length=512, blank=True, null=True)
    Child_name = models.CharField(max_length=512, blank=True, null=True)
    child_sex = models.CharField(max_length=255, choices=SEX, default='None', blank=True, null=True)
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
    Grade = models.CharField(max_length=512, blank=True, null=True)
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
    Course_Location = models.CharField(max_length=50, choices=COURSE_LOCATION, blank=True, null=True)
    # end
    Days = MultiSelectField(max_length=50, choices=DAYS, blank=True, null=True)
    Time = models.CharField(max_length=50, null=True, choices=ELDORET_TIME, default='None')
    Eligibility = models.CharField(max_length=50, blank=True, null=True, choices=ELIGIBILITY, default='Pending')

    def __str__(self):
        return f"{self.First_Name} {self.Last_Name}"


ABSENT_REASON_CHOICES = [
    ('Too Late', 'Too Late'),
    ('Absent with Excuse', 'Absent with Excuse'),
    ('Absent without Excuse', 'Absent without Excuse'),
]


def generate_invoice_number():
    return str(uuid.uuid4().hex)[:12]


class SchoolFee(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, null=True, blank=True)
    starting_month = models.DateField()
    due_date = models.DateField()
    total_amount_to_pay = models.IntegerField(default=15000)  # Set fixed amount
    invoice_number = models.CharField(max_length=12)

    def __str__(self):
        return f"{self.candidate} - {self.invoice_number}"


FEE_ASSIGNMENT = (
    ('A1', 'A1'),
    ('A2', 'A2'),
    ('B1', 'B1'),
    ('B2', 'B2'),

)


class FeeStructure(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, null=True, blank=True)
    total_amount_to_pay = models.IntegerField()
    invoice_number = models.CharField(max_length=12)
    fee_assignment = models.CharField(max_length=50, null=True, choices=FEE_ASSIGNMENT, default='Not-Set', blank=True)
    starting_date = models.DateField()
    due_date = models.DateField(default=timezone.now)
    duration = models.IntegerField(blank=True, null=True)  # change this to IntegerField


CLASS_ASSIGNMENT = (
    ('A1', 'A1'),
    ('A2', 'A2'),
    ('B1', 'B1'),
    ('B2', 'B2'),

)


class ClassFee(models.Model):
    candidate = models.CharField(max_length=255)
    class_assignment = models.CharField(max_length=50, null=True, choices=CLASS_ASSIGNMENT, default='Not-Set',
                                        blank=True)
    starting_date = models.DateField(default=timezone.now)
    invoice_number = models.CharField(max_length=12)
    total_amount_to_pay = models.IntegerField()


class MonthRange(models.Model):
    class_fee = models.ForeignKey(ClassFee, related_name='months', on_delete=models.CASCADE)
    month_name = models.CharField(max_length=20)
    amount_to_pay = models.IntegerField()  # No default value


class ClassAttendance(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    date = models.DateField()
    present = models.BooleanField()
    absent_reason = models.CharField(max_length=255, choices=ABSENT_REASON_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"{self.candidate} - {self.date}"


class UniquePayment(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    receipt_number = models.CharField(max_length=12, unique=True)
    date_of_payment = models.DateField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.candidate} - Receipt: {self.receipt_number}"


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
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    date_of_class = models.DateField(max_length=50, blank=True, null=True)
    start_time = models.TimeField(max_length=50, blank=True, null=True)
    end_time = models.TimeField(max_length=50, blank=True, null=True)
    absent = models.CharField(max_length=50, null=True, choices=YES_or_NO, default='Pending')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='attendances')

    def __str__(self):
        return f"{self.candidate} - {self.date_of_class}"


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
