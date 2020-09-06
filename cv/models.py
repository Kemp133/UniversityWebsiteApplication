from django.db import models


# Create your models here.
class Subject(models.Model):
	class Grades(models.TextChoices):
		A_STAR = 'A*', 'A*'
		A = 'A', 'A'
		B = 'B', 'B'
		C = 'C', 'C'
		D = 'D', 'D'
		E = 'E', 'E'
		F = 'F', 'F'
		FAIL = 'FAIL', 'FAIL'
		NONE = 'N/A', 'N/A'

	name = models.CharField(max_length=64)
	predicted_grade = models.CharField(max_length=4, choices=Grades.choices, default=Grades.NONE)
	actual_grade = models.CharField(max_length=4, choices=Grades.choices, default=Grades.NONE)
	active = models.BooleanField(default=True)


class Institution(models.Model):
	name = models.CharField(max_length=256)
	address_line_1 = models.CharField(max_length=256)
	address_line_2 = models.CharField(max_length=256, blank=True)
	address_line_3 = models.CharField(max_length=256)
	address_line_4 = models.CharField(max_length=256)
	post_code = models.CharField(max_length=8)


class Education(models.Model):
	institution = models.ForeignKey(Institution, models.CASCADE)
	subject = models.ForeignKey(Subject, models.CASCADE)


class BasicInformation(models.Model):
	information_name = models.CharField(max_length=256, blank=False)
	information_value = models.CharField(max_length=256, blank=False)
	active = models.BooleanField(default=True)
