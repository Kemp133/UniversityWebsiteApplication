from django.forms import ModelForm
from .models import Subject, Institution


class SubjectForm(ModelForm):
	class Meta:
		model = Subject
		fields = ['name', 'predicted_grade', 'actual_grade']


class InstituteForm(ModelForm):
	class Meta:
		model = Institution
		fields = ['name', 'address_line_1', 'address_line_2', 'address_line_3', 'address_line_4', 'post_code']
