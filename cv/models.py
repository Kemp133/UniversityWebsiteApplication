from django.db.models import (Model, TextChoices, CharField, ForeignKey, ManyToManyField, CASCADE, BooleanField,
							  DateField, TextField)


# Create your models here.
class Subject(Model):
	class Grades(TextChoices):
		A_STAR = 'A*', 'A*'
		A = 'A', 'A'
		B = 'B', 'B'
		C = 'C', 'C'
		D = 'D', 'D'
		E = 'E', 'E'
		F = 'F', 'F'
		FAIL = 'FAIL', 'FAIL'
		NONE = 'N/A', 'N/A'

	class EducationStage(TextChoices):
		GCSE = "GCSE", "GCSE"
		A_LEVEL = "A_LEVEL", "A Level"
		HIGHER = "HIGHER", "Higher Education"
		NONE = "NONE", "N/a"

	name = CharField(max_length=64)
	stage = CharField(max_length=8, choices=EducationStage.choices, default=EducationStage.NONE)
	predicted_grade = CharField(max_length=4, choices=Grades.choices, default=Grades.NONE)
	actual_grade = CharField(max_length=4, choices=Grades.choices, default=Grades.NONE)
	active = BooleanField(default=True)


class Institution(Model):
	name = CharField(max_length=256)
	address_line_1 = CharField(max_length=256)
	address_line_2 = CharField(max_length=256)
	address_line_3 = CharField(max_length=256, blank=True)
	address_line_4 = CharField(max_length=256)
	post_code = CharField(max_length=8)


class Education(Model):
	institution = ForeignKey(Institution, CASCADE)
	subject = ManyToManyField(Subject, related_name="education_institute")


class BasicInformation(Model):
	information_name = CharField(max_length=256, blank=False)
	information_value = CharField(max_length=256, blank=False)
	active = BooleanField(default=True)


class Skill(Model):
	skill_name = CharField(max_length=128, blank=False)
	skill_explanation = CharField(max_length=512, blank=False)
	active = BooleanField(default=True)


class Hobby(Model):
	hobby_name = CharField(max_length=128, blank=False)
	hobby_description = CharField(max_length=512, blank=False)
	active = BooleanField(default=True)


class Experience(Model):
	placement_start = DateField()
	placement_end = DateField(blank=True, null=True)
	notes = TextField()
	active = BooleanField(default=True)


class PastExperience(Model):
	institution = ForeignKey(Institution, CASCADE)
	experience = ManyToManyField(Experience, related_name='past_experience')


