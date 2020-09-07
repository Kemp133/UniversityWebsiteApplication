from django.forms import ModelForm, SelectDateWidget
from .models import Subject, Institution, Experience, Education


class SubjectForm(ModelForm):
	class Meta:
		model = Subject
		fields = ['name', 'stage', 'predicted_grade', 'actual_grade']


class InstituteForm(ModelForm):
	class Meta:
		model = Institution
		fields = ['name', 'address_line_1', 'address_line_2', 'address_line_3', 'address_line_4', 'post_code']


class ExperienceForm(ModelForm):
	class Meta:
		model = Experience
		fields = ['placement_start', 'placement_end', 'notes']
		widgets = {
			'placement_start': SelectDateWidget(empty_label="Start Date", years=range(2000, 2101)),
			'placement_end': SelectDateWidget(empty_label="End Date (Leave if not finished)", years=range(2000, 2101))
		}


class UpdateFinishDateForm(ModelForm):
	class Meta:
		model = Experience
		fields = ['placement_end']
		widgets = {
			'placement_end': SelectDateWidget(empty_label="Date Finished", years=range(2000, 2101))
		}
