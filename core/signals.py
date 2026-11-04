from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone
from .models import AdmissionApplication, Student


# Map admission department choices to Student CLASS_CHOICES
COURSE_TO_STUDENT_CLASS_MAP = {
    'HIFZ': 'HIFZ',
    'NAZRA': 'NAZRA',
    'AALIM_IBTEDA': 'AALIM_1',
    'AALIM_MUTAWAS': 'AALIM_2',
    'AALIM_AALIYA': 'DAWRA',
}


def generate_next_registration_number(year):
    """
    Generates the next sequential registration number in format:
    SR-<YEAR>-<001> (e.g., SR-2026-001)
    """
    prefix = f"SR-{year}-"
    last_student = (
        Student.objects.filter(registration_no__startswith=prefix)
        .order_by('-registration_no')
        .first()
    )

    if last_student:
        try:
            last_seq = int(last_student.registration_no.split('-')[-1])
            next_seq = last_seq + 1
        except (ValueError, IndexError):
            next_seq = 1
    else:
        next_seq = 1

    return f"{prefix}{next_seq:03d}"


@receiver(post_save, sender=AdmissionApplication)
def create_student_on_acceptance(sender, instance, created, **kwargs):
    """
    Listens for AdmissionApplication saves. If status is 'ACCEPTED' and 
    the student has not yet been registered, creates a new Student record.
    """
    if instance.status == 'ACCEPTED':
        # Check if already converted to a student using matching credentials
        existing_student = Student.objects.filter(
            name__iexact=instance.student_name,
            parentage__iexact=instance.father_name,
            admission_year=instance.application_date.year,
        ).first()

        if not existing_student:
            with transaction.atomic():
                current_year = timezone.now().year
                reg_no = generate_next_registration_number(current_year)
                target_class = COURSE_TO_STUDENT_CLASS_MAP.get(
                    instance.preferred_course, 'HIFZ'
                )

                new_student = Student(
                    registration_no=reg_no,
                    name=instance.student_name,
                    parentage=instance.father_name,
                    current_class=target_class,
                    admission_year=current_year,
                    district=instance.district or 'Pulwama',
                    is_active=True,
                )

                # Copy applicant photo if uploaded
                if instance.student_photo:
                    new_student.photo = instance.student_photo

                new_student.save()

                # Record the newly assigned registration ID inside admin notes
                if instance.reference_id not in (instance.admin_notes or ''):
                    note_entry = f"\n[System Auto-Enrollment]: Enrolled as Student with ID: {reg_no} on {timezone.now().strftime('%Y-%m-%d %H:%M')}"
                    instance.admin_notes = (instance.admin_notes or '') + note_entry
                    # Save only admin_notes without triggering recursive loop
                    AdmissionApplication.objects.filter(pk=instance.pk).update(
                        admin_notes=instance.admin_notes
                    )