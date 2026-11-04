from django import forms
from .models import AdmissionApplication

class AdmissionApplicationForm(forms.ModelForm):
    class Meta:
        model = AdmissionApplication
        fields = [
            'student_name', 'dob', 'preferred_course', 'residence_type',
            'previous_madrasa_or_school', 'last_class_passed',
            'father_name', 'guardian_contact', 'email',
            'residential_address', 'district', 'state', 'pincode',
            'student_photo', 'aadhaar'
        ]
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 text-xs border border-gray-300 rounded-lg focus:outline-none focus:border-islamic-dark'}),
            'student_name': forms.TextInput(attrs={'placeholder': 'Full name of candidate', 'class': 'w-full px-3 py-2 text-xs border border-gray-300 rounded-lg focus:outline-none focus:border-islamic-dark'}),
            'preferred_course': forms.Select(attrs={'class': 'w-full px-3 py-2 text-xs border border-gray-300 rounded-lg focus:outline-none focus:border-islamic-dark bg-white'}),
            'residence_type': forms.Select(attrs={'class': 'w-full px-3 py-2 text-xs border border-gray-300 rounded-lg focus:outline-none focus:border-islamic-dark bg-white'}),
            'previous_madrasa_or_school': forms.TextInput(attrs={'placeholder': 'Previous school or Maktab name', 'class': 'w-full px-3 py-2 text-xs border border-gray-300 rounded-lg focus:outline-none focus:border-islamic-dark'}),
            'last_class_passed': forms.TextInput(attrs={'placeholder': 'e.g. 5th Standard, Nazra Quran, or 5 Paras', 'class': 'w-full px-3 py-2 text-xs border border-gray-300 rounded-lg focus:outline-none focus:border-islamic-dark'}),
            'father_name': forms.TextInput(attrs={'placeholder': 'Father or legal guardian name', 'class': 'w-full px-3 py-2 text-xs border border-gray-300 rounded-lg focus:outline-none focus:border-islamic-dark'}),
            'guardian_contact': forms.TextInput(attrs={'placeholder': '10-digit mobile number', 'class': 'w-full px-3 py-2 text-xs border border-gray-300 rounded-lg focus:outline-none focus:border-islamic-dark'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Optional email address', 'class': 'w-full px-3 py-2 text-xs border border-gray-300 rounded-lg focus:outline-none focus:border-islamic-dark'}),
            'residential_address': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Complete residential address', 'class': 'w-full px-3 py-2 text-xs border border-gray-300 rounded-lg focus:outline-none focus:border-islamic-dark'}),
            'district': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-xs border border-gray-300 rounded-lg focus:outline-none focus:border-islamic-dark'}),
            'state': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-xs border border-gray-300 rounded-lg focus:outline-none focus:border-islamic-dark'}),
            'pincode': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-xs border border-gray-300 rounded-lg focus:outline-none focus:border-islamic-dark'}),
            'student_photo': forms.FileInput(attrs={'class': 'text-xs text-gray-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-emerald-50 file:text-islamic-dark hover:file:bg-emerald-100'}),
            'aadhaar': forms.FileInput(attrs={'class': 'text-xs text-gray-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-emerald-50 file:text-islamic-dark hover:file:bg-emerald-100'}),
        }