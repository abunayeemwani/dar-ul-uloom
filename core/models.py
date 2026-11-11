import uuid
import os
import re
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


def validate_pdf_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Only PDF files are supported for library digital copies.')


class Announcement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    date_posted = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date_posted']

    def __str__(self):
        return self.title


class Member(models.Model):
    CATEGORY_CHOICES = [
        ('ADMIN', 'Administration'),
        ('FACULTY', 'Academic Faculty / Asatizah'),
        ('SHURA', 'Majlis-e-Shura (Governing Council)'),
        ('STAFF', 'Support Staff'),
    ]
    name = models.CharField(max_length=150)
    parentage = models.CharField(max_length=150, blank=True, verbose_name="Parentage / Father's Name")
    aadhaar_number = models.CharField(max_length=12, blank=True, verbose_name="Aadhaar / National ID")
    address = models.TextField(blank=True, verbose_name="Residential Address")
    
    designation = models.CharField(max_length=150, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='FACULTY')
    contact_phone = models.CharField(max_length=20, blank=True, help_text="Will only be shown if authorized")
    contact_email = models.EmailField(blank=True)
    photo = models.ImageField(upload_to='members/', blank=True, null=True)
    bio = models.TextField(blank=True, verbose_name="Short Biography / Academic Services")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.designation}"


class Student(models.Model):
    CLASS_CHOICES = [
        ('HIFZ', 'Hifz-ul-Quran (Tahfeez)'),
        ('NAZRA', 'Nazra Quran & Qiraat'),
        ('AALIM_1', 'Aalimiyyah - Year 1 (Ibtedaiya)'),
        ('AALIM_2', 'Aalimiyyah - Year 2 (Sanviya)'),
        ('AALIM_3', 'Aalimiyyah - Year 3 (Salisa)'),
        ('DAWRA', 'Dawra-e-Hadith (Khatm-e-Bukhari)'),
    ]
    registration_no = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)
    parentage = models.CharField(max_length=150, verbose_name="Father's / Guardian's Name")
    dob = models.DateField(null=True, blank=True, verbose_name="Date of Birth")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Contact / Guardian Phone")
    aadhaar_number = models.CharField(max_length=12, blank=True, verbose_name="Aadhaar / National ID")
    address = models.TextField(blank=True, verbose_name="Residential Address")
    
    current_class = models.CharField(max_length=20, choices=CLASS_CHOICES)
    admission_year = models.PositiveIntegerField(default=2024)
    district = models.CharField(max_length=100, default='Pulwama')
    photo = models.ImageField(upload_to='students/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['registration_no']

    def __str__(self):
        return f"{self.registration_no} - {self.name} ({self.get_current_class_display()})"


class Alumni(models.Model):
    name = models.CharField(max_length=150)
    parentage = models.CharField(max_length=150, blank=True, verbose_name="Father's Name")
    dob = models.DateField(null=True, blank=True, verbose_name="Date of Birth")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Phone Number")
    aadhaar_number = models.CharField(max_length=12, blank=True, verbose_name="Aadhaar / National ID")
    address = models.TextField(blank=True, verbose_name="Residential Address")
    
    completion_year = models.PositiveIntegerField()
    qualification_attained = models.CharField(max_length=200, blank=True, help_text="e.g. Hafiz-ul-Quran, Fazil-e-Dars-e-Nizami")
    current_engagement = models.CharField(max_length=250, blank=True, help_text="e.g. Imam & Khateeb, Teacher, Higher Studies")
    native_place = models.CharField(max_length=150, default='Jammu & Kashmir')
    photo = models.ImageField(upload_to='alumni/', blank=True, null=True)

    class Meta:
        verbose_name_plural = "Alumni"
        ordering = ['-completion_year', 'name']

    def __str__(self):
        return f"{self.name} ({self.completion_year})"


class Book(models.Model):
    CATEGORY_CHOICES = [
        ('QURAN', 'Quran & Sciences of Quran'),
        ('TAFSEER', 'Tafseer-ul-Quran'),
        ('HADITH', 'Hadith & Usool-ul-Hadith'),
        ('FIQH', 'Fiqh & Fatawa'),
        ('ARABIC', 'Arabic Language, Nahw & Sarf'),
        ('HISTORY', 'Tareekh & Seerat-un-Nabi ﷺ'),
    ]
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    accession_no = models.CharField(max_length=50, blank=True)
    volumes = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='books/', blank=True, null=True)
    pdf_file = models.FileField(
        upload_to='books/pdfs/',
        blank=True,
        null=True,
        validators=[validate_pdf_extension],
        help_text="Upload digitized edition / Kitab in PDF format."
    )
    has_digital_copy = models.BooleanField(default=False)

    class Meta:
        ordering = ['category', 'title']

    def save(self, *args, **kwargs):
        # Automatically mark as having digital copy if PDF is uploaded
        if self.pdf_file:
            self.has_digital_copy = True
        super().save(*args, **kwargs)
    
    @property
    def file_size_mb(self):
        """Returns file size in MB safely without raising FileNotFoundError or storage exceptions."""
        if bool(self.pdf_file):
            try:
                if self.pdf_file.storage.exists(self.pdf_file.name):
                    return round(self.pdf_file.size / (1024 * 1024), 2)
            except Exception:
                return None
        return None

    def __str__(self):
        return f"{self.title} - {self.author}"


class AcademicResult(models.Model):
    STATUS_CHOICES = [
        ('MUMTAZ', 'Mumtaz (Distinction / 1st Div with Honors)'),
        ('JAYYID_JIDDAN', 'Jayyid Jiddan (Very Good / 1st Div)'),
        ('JAYYID', 'Jayyid (Good / 2nd Div)'),
        ('MAQBOOL', 'Maqbool (Pass / 3rd Div)'),
        ('RASIB', 'Rasib (Re-appear)'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    academic_year = models.CharField(max_length=15, default='2024-25')
    examination_name = models.CharField(max_length=150, default='Annual Imtihan-e-Aam')
    class_name = models.CharField(max_length=100)
    total_marks = models.PositiveIntegerField(default=500)
    marks_obtained = models.PositiveIntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='MUMTAZ')
    remarks = models.CharField(max_length=255, default='Alhamdulillah, promoted to the next grade.')
    issue_date = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
        if self.total_marks > 0:
            self.percentage = round((self.marks_obtained / self.total_marks) * 100, 2)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-academic_year', 'student__registration_no']

    def __str__(self):
        return f"{self.student.registration_no} - {self.examination_name} ({self.academic_year})"


class ResultSubjectBreakdown(models.Model):
    result = models.ForeignKey(AcademicResult, on_delete=models.CASCADE, related_name='breakdowns')
    subject_name = models.CharField(max_length=100)
    max_marks = models.PositiveIntegerField(default=100)
    obtained_marks = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.subject_name}: {self.obtained_marks}/{self.max_marks}"


class Ijtima(models.Model):
    STATUS_CHOICES = [
        ('UPCOMING', 'Upcoming'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Postponed / Cancelled'),
    ]
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    date_and_time = models.DateTimeField()
    venue = models.CharField(max_length=255, default='Main Jamea Masjid / Seminar Hall, Darul Uloom Campus, Achagoza, Pulwama')
    speaker_or_guest = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    poster = models.ImageField(upload_to='ijtimat/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='UPCOMING')

    class Meta:
        verbose_name = "Ijtima & Event"
        verbose_name_plural = "Ijtimat & Gatherings"
        ordering = ['-date_and_time']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class AdmissionApplication(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Application Submitted (Pending Review)'),
        ('UNDER_REVIEW', 'Under Scrutiny by Shura / Admissions Branch'),
        ('INTERVIEW_SCHEDULED', 'Shortlisted for Oral / Hifz Interview'),
        ('ACCEPTED', 'Admitted / Admission Confirmed'),
        ('REJECTED', 'Application Declined'),
    ]

    DEPARTMENT_CHOICES = [
        ('HIFZ', 'Shu\'ba-e-Tahfeez (Quran Memorization & Tajweed)'),
        ('NAZRA', 'Shu\'ba-e-Nazra (Basic Quranic Recitation & Deeniyat)'),
        ('AALIM_IBTEDA', 'Aalimiyyah - Preparatory / Primary (Ibtedai)'),
        ('AALIM_MUTAWAS', 'Aalimiyyah - Intermediate (Mutawassita)'),
        ('AALIM_AALIYA', 'Aalimiyyah - Advanced (Aaliya / Dawra-e-Hadith)'),
    ]

    RESIDENCE_PREFERENCE = [
        ('BOARDING', 'Residential Boarder (Muqeem / Hostel Accommodation Required)'),
        ('DAY_SCHOLAR', 'Non-Residential Day Scholar (Ghair-Muqeem)'),
    ]

    # Unique Reference Tracking Number (e.g. ADM-2026-8A4F)
    reference_id = models.CharField(max_length=20, unique=True, editable=False)
    
    # Student Details
    student_name = models.CharField(max_length=150, verbose_name="Candidate Full Name")
    dob = models.DateField(verbose_name="Date of Birth")
    preferred_course = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES)
    residence_type = models.CharField(max_length=20, choices=RESIDENCE_PREFERENCE, default='BOARDING')
    previous_madrasa_or_school = models.CharField(max_length=255, blank=True, verbose_name="Previous Madrasa / School Attended")
    last_class_passed = models.CharField(max_length=100, blank=True, verbose_name="Last Qualification / Para Completed")

    # Guardian & Family Details
    father_name = models.CharField(max_length=150, verbose_name="Father's / Guardian's Full Name")
    guardian_contact = models.CharField(max_length=20, verbose_name="Primary Mobile Contact Number")
    email = models.EmailField(blank=True)

    # Address
    residential_address = models.TextField(verbose_name="Village / Mohalla / House Details")
    district = models.CharField(max_length=100, default="Pulwama")
    state = models.CharField(max_length=100, default="Jammu & Kashmir")
    pincode = models.CharField(max_length=10, default="192302", blank=True)
    aadhaar_number = models.CharField(max_length=16, blank=True)

    # Supporting Documents (Optional during initial online form)
    student_photo = models.ImageField(upload_to='admissions/photos/', blank=True, null=True)
    aadhaar = models.FileField(upload_to='admissions/documents/', blank=True, null=True, verbose_name=" Aadhaar")

    # Administrative Review Section
    application_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='PENDING')
    interview_date = models.DateTimeField(null=True, blank=True, verbose_name="Scheduled Test / Interview Date")
    admin_notes = models.TextField(blank=True, help_text="Confidential assessment notes by Nazim-e-Taleemat")

    class Meta:
        ordering = ['-application_date']
        verbose_name = "Admission Application"
        verbose_name_plural = "Online Admission Applications"

    def save(self, *args, **kwargs):
        if not self.reference_id:
            # Generate short distinctive institutional tracking code
            current_year = timezone.now().year
            unique_token = uuid.uuid4().hex[:6].upper()
            self.reference_id = f"ADM-{current_year}-{unique_token}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference_id} - {self.student_name} ({self.get_preferred_course_display()})"


class GalleryItem(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('IMAGE', 'Photograph / Image'),
        ('VIDEO', 'Video (YouTube / Direct URL)'),
    ]

    title = models.CharField(max_length=200)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='IMAGE')
    
    # For Images
    image_file = models.ImageField(upload_to='gallery/images/', blank=True, null=True)
    
    # For Videos (YouTube link or direct MP4/video link)
    video_url = models.URLField(
        blank=True,
        null=True,
        help_text="Paste YouTube video link (e.g., https://www.youtube.com/watch?v=... or https://youtu.be/...)"
    )
    # Optional custom cover/thumbnail for video
    thumbnail = models.ImageField(upload_to='gallery/thumbnails/', blank=True, null=True)
    
    caption = models.TextField(blank=True, help_text="Short description or context of the photo/video.")
    date_captured = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False, help_text="Highlight in top section")

    class Meta:
        ordering = ['-date_captured', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_media_type_display()})"

    @property
    def youtube_embed_id(self):
        """Extracts the YouTube video ID from various link formats."""
        if not self.video_url:
            return None
        pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
        match = re.search(pattern, self.video_url)
        return match.group(1) if match else None


def validate_pdf_sheet(value):
    """Enforces that the uploaded audit statement is strictly a PDF file."""
    ext = os.path.splitext(value.name)[1].lower()
    if ext != '.pdf':
        raise ValidationError('Only PDF audit reports (.pdf) are allowed. Excel/CSV files are not accepted.')


class FinancialYear(models.Model):
    year_label = models.CharField(
        max_length=50,
        unique=True,
        help_text="e.g. 2025-2026"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    
    opening_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Previous Year Balance (Opening Balance)"
    )
    manual_total_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Leave blank to calculate automatically from line items below."
    )
    manual_total_expenditure = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Leave blank to calculate automatically from line items below."
    )
    
    # Strictly PDF Audit Report
    audit_sheet = models.FileField(
        upload_to='accounts/pdf_reports/',
        blank=True,
        null=True,
        validators=[validate_pdf_sheet],
        help_text="Upload the certified annual financial audit report strictly in PDF format."
    )
    auditor_or_accountant = models.CharField(
        max_length=150,
        blank=True,
        default="Majlis-e-Shura Audit Committee",
        help_text="Certified by Chartered Accountant or Shura Finance Committee"
    )
    remarks = models.TextField(blank=True, help_text="Institutional notes or financial audit remarks.")
    is_published = models.BooleanField(default=True, help_text="Show publicly on website")

    class Meta:
        ordering = ['-start_date']
        verbose_name = "Financial Year & Accounts Summary"
        verbose_name_plural = "Financial Years & Accounts"

    def __str__(self):
        return self.year_label

    @property
    def total_income(self):
        if self.manual_total_income is not None:
            return self.manual_total_income
        aggregate = self.entries.filter(entry_type='INCOME').aggregate(models.Sum('amount'))['amount__sum']
        return aggregate or Decimal('0.00')

    @property
    def total_expenditure(self):
        if self.manual_total_expenditure is not None:
            return self.manual_total_expenditure
        aggregate = self.entries.filter(entry_type='EXPENSE').aggregate(models.Sum('amount'))['amount__sum']
        return aggregate or Decimal('0.00')

    @property
    def closing_balance(self):
        return (self.opening_balance + self.total_income) - self.total_expenditure

    @property
    def audit_sheet_filename(self):
        if self.audit_sheet:
            return os.path.basename(self.audit_sheet.name)
        return ""


class IncomeExpenseEntry(models.Model):
    ENTRY_TYPES = [
        ('INCOME', 'Income (Aamadani / Zakat / Atiyaat)'),
        ('EXPENSE', 'Expenditure (Kharch / Matbakh / Asatizah)'),
    ]

    CATEGORY_CHOICES = [
        # Income categories
        ('ZAKAT', 'Zakat & Imdaad'),
        ('SADAQAH', 'Sadaqaat & Atiyaat-e-Aam'),
        ('CONSTRUCTION_FUND', 'Tameer-e-Madrasa (Building Construction Fund)'),
        ('FITRA_SKIN', 'Sadqat-ul-Fitr & Qurbani Skins'),
        ('DONATION_MONTHLY', 'Monthly Community Contributions (Mahana Chandajat)'),
        ('OTHER_INCOME', 'Other Educational Grants / Receipts'),

        # Expense categories
        ('HONORARIUM', 'Asatizah & Staff Honorarium (Mahanah Tankhwah)'),
        ('KITCHEN_MESS', 'Matbakh & Hostel Mess (Boarding Food & Rations)'),
        ('CAMPUS_MAINTENANCE', 'Building Maintenance, Power & Water Supply'),
        ('STUDENT_WELFARE', 'Student Books, Uniforms & Medical Care (Imdad-e-Talaba)'),
        ('EVENT_EXPENSE', 'Annual Dastarbandi & Conference Expenses'),
        ('OFFICE_ADMIN', 'Stationery, Printing & Office Expenses'),
        ('OTHER_EXPENSE', 'Other Institutional Contingencies'),
    ]

    financial_year = models.ForeignKey(FinancialYear, on_delete=models.CASCADE, related_name='entries')
    entry_type = models.CharField(max_length=10, choices=ENTRY_TYPES)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    head_title = models.CharField(max_length=200, blank=True, help_text="e.g. 'Ration & Provisions for Matbakh'")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['entry_type', '-amount']
        verbose_name = "Detailed Ledger Entry"
        verbose_name_plural = "Detailed Ledger Entries"

    def __str__(self):
        return f"{self.get_entry_type_display()} - {self.head_title}: ₹{self.amount}"
