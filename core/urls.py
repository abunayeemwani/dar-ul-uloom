from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('members/', views.members_list, name='members'),
    path('students/', views.students_list, name='students'),
    path('alumni/', views.alumni_list, name='alumni'),
    path('library/', views.library_list, name='library'),
    path('results/', views.results_portal, name='results'),
    path('results/<int:pk>/print/', views.result_print, name='result_print'),
    path('ijtimat/', views.ijtimat_list, name='ijtimat'),
    path('ijtimat/<slug:slug>/', views.ijtimat_detail, name='ijtimat_detail'),
    path('admissions/', views.admission_apply, name='admission_apply'),
    path('admissions/confirmation/<str:reference_id>/', views.admission_success, name='admission_success'),
    path('admissions/status/', views.admission_status, name='admission_status'),
    path('library/<int:pk>/download/', views.download_book_pdf, name='book_download'),
    path('library/<int:pk>/read/', views.view_book_pdf, name='book_read'),
    path('gallery/', views.gallery_list, name='gallery'),
    path('accounts/', views.accounts_summary, name='accounts'),
    path('members/<int:pk>/', views.member_detail, name='member_detail'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('alumni/<int:pk>/', views.alumni_detail, name='alumni_detail'),
]