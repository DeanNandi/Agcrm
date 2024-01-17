# create_pdf.py

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.conf import settings
import os

def create_invoice_pdf(invoice, amount_paid=None):
    # Specify the base directory to save PDFs
    base_dir = 'path/to/save/'

    # Ensure the base directory exists, create it if necessary
    os.makedirs(base_dir, exist_ok=True)

    # Construct the full path for the PDF file
    pdf_path = os.path.join(base_dir, f'{invoice.Name}_{invoice.Invoice_Number}.pdf')

    # Example: Use ReportLab to generate a more detailed PDF
    pdf = canvas.Canvas(pdf_path, pagesize=letter)

    # Set font
    pdf.setFont("Helvetica", 12)

    # Add content to the PDF using data from the Invoice model
    pdf.drawString(100, 750, f"Invoice for: {invoice.Name}")
    pdf.drawString(100, 730, f"Address: {invoice.Street}, {invoice.City}")
    pdf.drawString(100, 710, f"Phone Number: {invoice.Phonenumber}")
    pdf.drawString(100, 690, f"Invoice Number: {invoice.Invoice_Number}")
    pdf.drawString(100, 670, f"Date of Payment: {invoice.Date_of_Payment.strftime('%Y-%m-%d')}")

    # Additional content
    pdf.drawString(100, 650, "Description of services:")
    pdf.drawString(120, 630, "- Monthly Tuition for AG German Institute")
    pdf.drawString(120, 615,
                   f"- Includes all course materials and classes for {invoice.Date_of_Payment.strftime('%m/%Y')}")

    # Calculate total amount
    total_amount = amount_paid if amount_paid is not None else 15000
    pdf.drawString(100, 595, f"Total Amount: {invoice.convert_to_str(total_amount)}")

    # Save the PDF
    pdf.save()

    return pdf_path
