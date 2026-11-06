from django.contrib import admin, messages
from .models import Announcement, Member, Student, Alumni, Book, AcademicResult, ResultSubjectBreakdown, Ijtima, AdmissionApplication, GalleryItem, FinancialYear, IncomeExpenseEntry
from django.utils.html import format_html, mark_safe


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_posted', 'is_active')
    list_filter = ('is_active', 'date_posted')
    search_fields = ('title', 'content')


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'designation', 'category')
    list_filter = ('category',)
    search_fields = ('name', 'designation', 'qualification')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('registration_no', 'name', 'parentage', 'current_class', 'admission_year', 'is_active')
    list_filter = ('current_class', 'admission_year', 'is_active')
    search_fields = ('registration_no', 'name', 'parentage')


@admin.register(Alumni)
class AlumniAdmin(admin.ModelAdmin):
    list_display = ('name', 'completion_year', 'qualification_attained', 'current_engagement', 'native_place')
    list_filter = ('completion_year',)
    search_fields = ('name', 'qualification_attained', 'current_engagement')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'volumes', 'accession_no')
    list_filter = ('category', 'has_digital_copy')
    search_fields = ('title', 'author', 'accession_no')
    readonly_fields = ('has_digital_copy',)
    fields = (
        'title',
        'author',
        'category',
        'accession_no',
        'volumes',
        'description',
        'cover_image',
        'pdf_file',
        'has_digital_copy',
    )


class SubjectBreakdownInline(admin.TabularInline):
    model = ResultSubjectBreakdown
    extra = 5


@admin.register(AcademicResult)
class AcademicResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'examination_name', 'academic_year', 'marks_obtained', 'total_marks', 'percentage', 'status')
    list_filter = ('academic_year', 'status')
    search_fields = ('student__name', 'student__registration_no', 'examination_name')
    inlines = [SubjectBreakdownInline]


@admin.register(Ijtima)
class IjtimaAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_and_time', 'venue', 'status')
    list_filter = ('status', 'date_and_time')
    search_fields = ('title', 'venue', 'description', 'speaker_or_guest')
    prepopulated_fields = {'slug': ('title',)}


@admin.action(description="Accept & officially enroll selected candidates as Students")
def accept_and_enroll_applications(modeladmin, request, queryset):
    updated_count = 0
    for app in queryset:
        if app.status != 'ACCEPTED':
            app.status = 'ACCEPTED'
            app.save()  # Triggers the post_save signal
            updated_count += 1

    modeladmin.message_user(
        request,
        f"Alhamdulillah! {updated_count} application(s) were marked as ACCEPTED and enrolled into the Student Registry.",
        messages.SUCCESS,
    )


@admin.register(AdmissionApplication)
class AdmissionApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'reference_id',
        'student_name',
        'preferred_course',
        'residence_type',
        'guardian_contact',
        'status',
        'interview_date',
        'application_date',
    )
    list_filter = ('status', 'preferred_course', 'residence_type', 'district')
    search_fields = ('reference_id', 'student_name', 'father_name', 'guardian_contact')
    readonly_fields = ('reference_id', 'application_date')
    actions = [accept_and_enroll_applications]

    fieldsets = (
        ('Identification & Course', {
            'fields': ('reference_id', 'status', 'application_date', 'preferred_course', 'residence_type')
        }),
        ('Candidate Biodata', {
            'fields': ('student_name', 'dob', 'previous_madrasa_or_school', 'last_class_passed', 'student_photo', 'aadhaar')
        }),
        ('Family & Guardian Information', {
            'fields': ('father_name', 'guardian_contact', 'email', 'residential_address', 'district', 'state', 'pincode')
        }),
        ('Institutional Scrutiny & Enrollment', {
            'fields': ('interview_date', 'admin_notes')
        }),
    )


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'media_type', 'date_captured', 'is_featured')
    list_filter = ('media_type', 'is_featured', 'date_captured')
    search_fields = ('title', 'caption')
    view_on_site = False


class IncomeExpenseEntryInline(admin.TabularInline):
    model = IncomeExpenseEntry
    extra = 0
    fields = ('entry_type', 'category', 'amount', 'head_title', 'notes')


@admin.register(FinancialYear)
class FinancialYearAdmin(admin.ModelAdmin):
    list_display = (
        'year_label',
        'opening_balance',
        'total_income',
        'total_expenditure',
        'closing_balance',
        'has_audit_pdf',
        'is_published',
    )
    list_filter = ('is_published',)
    search_fields = ('year_label', 'remarks', 'auditor_or_accountant')
    inlines = [IncomeExpenseEntryInline]
    view_on_site = False

    @admin.display(description="Audit PDF")
    def has_audit_pdf(self, obj):
        if bool(obj.audit_sheet):
            return mark_safe('PDF Attached')
        return mark_safe('No PDF')
