import os
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Announcement, Member, Student, Alumni, Book, AcademicResult, Ijtima
from .models import AdmissionApplication
from .forms import AdmissionApplicationForm
from django.http import FileResponse, Http404
from django.utils.text import slugify
from .models import Book


def home(request):
    announcements = Announcement.objects.filter(is_active=True)[:5]
    upcoming_events = Ijtima.objects.filter(status='UPCOMING')[:3]
    recent_alumni = Alumni.objects.all()[:4]
    context = {
        'announcements': announcements,
        'upcoming_events': upcoming_events,
        'recent_alumni': recent_alumni,
        'page_title': "Home"
    }
    return render(request, 'core/home.html', context)


def about(request):
    return render(request, 'core/about.html', {'page_title': "About the Institution"})


def members_list(request):
    category = request.GET.get('category', '')
    query = request.GET.get('q', '')

    members = Member.objects.all()
    if category:
        members = members.filter(category=category)
    if query:
        members = members.filter(Q(name__icontains=query))

    context = {
        'members': members,
        'selected_category': category,
        'query': query,
        'categories': Member.CATEGORY_CHOICES,
        'page_title': "Institutional Members & Asatizah"
    }
    return render(request, 'core/members.html', context)


def students_list(request):
    selected_class = request.GET.get('class', '')
    query = request.GET.get('q', '')

    students = Student.objects.filter(is_active=True)
    if selected_class:
        students = students.filter(current_class=selected_class)
    if query:
        students = students.filter(Q(name__icontains=query) | Q(registration_no__icontains=query) | Q(parentage__icontains=query))

    context = {
        'students': students,
        'selected_class': selected_class,
        'query': query,
        'classes': Student.CLASS_CHOICES,
        'page_title': "Current Students Directory"
    }
    return render(request, 'core/students.html', context)


def alumni_list(request):
    year = request.GET.get('year', '')
    query = request.GET.get('q', '')

    alumni = Alumni.objects.all()
    if year:
        alumni = alumni.filter(completion_year=year)
    if query:
        alumni = alumni.filter(Q(name__icontains=query) | Q(qualification_attained__icontains=query) | Q(current_engagement__icontains=query))

    years = Alumni.objects.values_list('completion_year', flat=True).distinct().order_by('-completion_year')

    context = {
        'alumni': alumni,
        'years': years,
        'selected_year': year,
        'query': query,
        'page_title': "Passout Students (Alumni)"
    }
    return render(request, 'core/alumni.html', context)


def library_list(request):
    category = request.GET.get('category', '')
    query = request.GET.get('q', '')

    books = Book.objects.all()
    if category:
        books = books.filter(category=category)
    if query:
        books = books.filter(Q(title__icontains=query) | Q(author__icontains=query))

    context = {
        'books': books,
        'selected_category': category,
        'query': query,
        'categories': Book.CATEGORY_CHOICES,
        'page_title': "Maktaba (Islamic Library)"
    }
    return render(request, 'core/library.html', context)


def results_portal(request):
    query = request.GET.get('reg_no', '').strip()
    result = None
    searched = False

    if query:
        searched = True
        result = AcademicResult.objects.filter(
            Q(student__registration_no__iexact=query) | Q(student__name__icontains=query)
        ).select_related('student').prefetch_related('breakdowns').first()

    context = {
        'query': query,
        'searched': searched,
        'result': result,
        'page_title': "Academic Results Verification"
    }
    return render(request, 'core/results.html', context)


def result_print(request, pk):
    result = get_object_or_404(AcademicResult.objects.select_related('student').prefetch_related('breakdowns'), pk=pk)
    return render(request, 'core/result_detail_print.html', {'result': result})


def ijtimat_list(request):
    status = request.GET.get('status', 'UPCOMING')
    events = Ijtima.objects.all()

    if status in ['UPCOMING', 'COMPLETED']:
        events = events.filter(status=status)

    context = {
        'events': events,
        'selected_status': status,
        'page_title': "Ijtimat & Gatherings"
    }
    return render(request, 'core/ijtimat.html', context)


def ijtimat_detail(request, slug):
    event = get_object_or_404(Ijtima, slug=slug)
    return render(request, 'core/ijtimat_detail.html', {'event': event, 'page_title': event.title})


def admission_apply(request):
    if request.method == 'POST':
        form = AdmissionApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save()
            messages.success(
                request,
                f"Alhamdulillah! Admission form submitted successfully. Your tracking number is {application.reference_id}."
            )
            return redirect('admission_success', reference_id=application.reference_id)
    else:
        form = AdmissionApplicationForm()

    return render(request, 'core/admission_apply.html', {
        'form': form,
        'page_title': "Online Admission Application"
    })

def admission_success(request, reference_id):
    application = get_object_or_404(AdmissionApplication, reference_id=reference_id)
    return render(request, 'core/admission_success.html', {
        'application': application,
        'page_title': "Application Confirmation"
    })

def admission_status(request):
    ref_id = request.GET.get('ref_id', '').strip().upper()
    application = None
    searched = False

    if ref_id:
        searched = True
        application = AdmissionApplication.objects.filter(reference_id=ref_id).first()

    return render(request, 'core/admission_status.html', {
        'ref_id': ref_id,
        'searched': searched,
        'application': application,
        'page_title': "Track Admission Status"
    })


def download_book_pdf(request, pk):
    """Serves the PDF file as an attachment to trigger browser download."""
    book = get_object_or_404(Book, pk=pk)
    if not book.pdf_file:
        raise Http404("No digital copy available for this book.")

    safe_filename = f"{slugify(book.title)}.pdf"
    response = FileResponse(book.pdf_file.open('rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{safe_filename}"'
    return response


def view_book_pdf(request, pk):
    """Opens the PDF directly inside the browser's native PDF reader."""
    book = get_object_or_404(Book, pk=pk)
    if not book.pdf_file:
        raise Http404("No digital copy available for this book.")

    safe_filename = f"{slugify(book.title)}.pdf"
    response = FileResponse(book.pdf_file.open('rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{safe_filename}"'
    return response