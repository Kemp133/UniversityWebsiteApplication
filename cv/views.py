from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import (BasicInformation, PastExperience, Skill, Hobby, PastExperience, Institution, Education, Subject,
					 Experience)
from .forms import SubjectForm, InstituteForm, ExperienceForm


# Create your views here.
def index(request):
	basic_information = BasicInformation.objects.all()[:5]
	skills = Skill.objects.all()[:5]
	hobbies = Hobby.objects.all()[:5]
	education = Education.objects.all()[:5]
	experience = PastExperience.objects.all()[:5]

	return render(request, "cv/index.html", {'title': 'My CV',
											  'basic_information': basic_information,
											  'skills': skills,
											  'hobbies': hobbies,
											  'education': education,
											  'experience': experience})


@login_required
def manage(request):
	basic_information = BasicInformation.objects.all()[:5]
	skills = Skill.objects.all()
	hobbies = Hobby.objects.all()
	education = Education.objects.all()
	experience = PastExperience.objects.all()

	return render(request, "cv/manage.html", {'title': 'Manage CV',
											  'basic_information': basic_information,
											  'skills': skills,
											  'hobbies': hobbies,
											  'education': education,
											  'experience': experience})


@login_required
def add_basic_information(request):
	if request.method == "POST":
		info_name = request.POST.get('name', '')
		info_value = request.POST.get('value', '')

		basic_info = BasicInformation()
		basic_info.information_name = info_name
		basic_info.information_value = info_value
		basic_info.save()

		return redirect('cv-manage', permanent=True)

	return render(request, 'cv/add/add_basic_information.html', {'title': 'Add Basic Information'})


@login_required
def toggle_basic_information(request, pk):
	bi = get_object_or_404(BasicInformation, pk=pk)
	bi.active = not bi.active
	bi.save()

	return redirect('cv-manage', permanent=True)


@login_required
def delete_basic_information(request, pk):
	bi = get_object_or_404(BasicInformation, pk=pk)

	if request.method == "POST":
		bi.delete()

		return redirect('cv-manage', permanent=True)

	return render(request, 'cv/delete/delete_basic_information.html', {'title': 'Delete Basic Information',
																	   'basic_information': bi})


@login_required
def add_past_education(request):
	if request.method == "POST":
		form = InstituteForm(request.POST)

		if form.is_valid():
			# Save the institute object to the database, and get a reference to the created object ready to create an
			# instance of Education
			institute: Institution
			institute = form.save(commit=False)
			institute.save()

			education = Education()
			education.institution = institute
			education.save()

			return redirect('cv-manage', permanent=True)

	form = InstituteForm()
	return render(request, 'cv/add/add_past_education.html', {'title': 'Add Past Education',
															  'form': form})


@login_required
def delete_education(request, pk: int):
	# Get an instance of the current object
	education = get_object_or_404(Education, pk=pk)

	if request.method == "POST":
		# Delete every subject attached to this education
		for sub in education.subject.all():
			sub.delete()

		# Delete the institution that the grades belong to
		education.institution.delete()

		# Delete the education object itself
		education.delete()

		# Redirect to the manage view, and don't allow the user to return back to this view
		return redirect('cv-manage', permanent=True)

	# Render the delete_education view ready to show to the user
	return render(request, 'cv/delete/delete_education.html', {'title': 'Delete Education',
														'education': education})


@login_required
def add_subject_to_education(request, pk: int):
	education = get_object_or_404(Education, pk=pk)

	if request.method == "POST":
		form = SubjectForm(request.POST)

		if form.is_valid():
			subject: Subject
			subject = form.save(commit=False)
			subject.save()

			education.subject.add(subject)
			education.save()

			return redirect('cv-manage')

	form = SubjectForm()
	return render(request, 'cv/add/add_subject_to_education.html', {'title': 'Add Subject To Education',
																'education': education,
																'form': form})


@login_required
def toggle_subject(request, pk):
	subject = get_object_or_404(Subject, pk=pk)
	subject.active = not subject.active
	subject.save()

	return redirect('cv-manage', permanent=True)


@login_required
def delete_subject(request, pk):
	subject = get_object_or_404(Subject, pk=pk)

	if request.method == "POST":
		subject.delete()
		return redirect('cv-manage', permanent=True)

	return render(request, 'cv/delete/delete_subject.html', {'title': 'Delete Subject',
													  'subject': subject})


@login_required
def add_skill(request):
	if request.method == "POST":
		skill_name = request.POST.get('skill_name', '')
		skill_explanation = request.POST.get('skill_explanation', '')

		skill = Skill()
		skill.skill_name = skill_name
		skill.skill_explanation = skill_explanation
		skill.save()

		return redirect('cv-manage', permanent=True)

	return render(request, 'cv/add/add_skill.html', {'title': 'Add Skill'})


@login_required
def toggle_skill(request, pk):
	skill = get_object_or_404(Skill, pk=pk)
	skill.active = not skill.active
	skill.save()

	return redirect('cv-manage', permanent=True)


@login_required
def delete_skill(request, pk):
	skill = get_object_or_404(Skill, pk=pk)

	if request.method == "POST":
		skill.delete()

		return redirect('cv-manage', permanent=True)

	return render(request, 'cv/delete/delete_skill.html', {'title': 'Delete Skill',
													'skill': skill})


@login_required
def add_hobby(request):
	if request.method == "POST":
		hobby_name = request.POST.get('hobby_name', '')
		hobby_description = request.POST.get('hobby_description', '')

		hobby = Hobby()
		hobby.hobby_name = hobby_name
		hobby.hobby_description = hobby_description
		hobby.save()

		return redirect('cv-manage', permanent=True)

	return render(request, 'cv/add/add_hobby.html', {'title': 'Add Hobby'})


@login_required
def toggle_hobby(request, pk):
	hobby = get_object_or_404(Hobby, pk=pk)
	hobby.active = not hobby.active
	hobby.save()

	return redirect('cv-manage', permanent=True)


@login_required
def delete_hobby(request, pk):
	hobby = get_object_or_404(Hobby, pk=pk)

	if request.method == "POST":
		hobby.delete()

		return redirect('cv-manage', permanent=True)

	return render(request, 'cv/delete/delete_hobby.html', {'title': 'Delete Hobby',
														   'hobby': hobby})


@login_required
def add_past_experience_institute(request):
	if request.method == "POST":
		form = InstituteForm(request.POST)

		if form.is_valid():
			institute: Institution
			institute = form.save(commit=False)
			institute.save()

			pe = PastExperience()
			pe.institution = institute
			pe.save()

			return redirect('cv-manage', permanent=True)

	form = InstituteForm()
	return render(request, 'cv/add/add_past_experience_institute.html', {'title': 'Add Past Experience Institute',
																		 'form': form})


@login_required
def add_past_experience(request, pk):
	pe = get_object_or_404(PastExperience, pk=pk)
	if request.method == "POST":
		form = ExperienceForm(request.POST)

		if form.is_valid():
			exp: Experience
			exp = form.save(commit=False)
			exp.save()

			pe.experience.add(exp)
			pe.save()

			return redirect('cv-manage', permanent=True)

	form = ExperienceForm()
	return render(request, 'cv/add/add_past_experience.html', {'title': 'Add Past Experience',
															   'past_experience': pe,
															   'form': form})


@login_required
def delete_past_experience(request, pk):
	experience = get_object_or_404(PastExperience, pk=pk)

	if request.method == "POST":
		# Delete all the experience for this object
		for val in experience.experience.all():
			val.delete()

		# Delete the institution
		experience.institution.delete()

		# Now delete this object
		experience.delete()

		return redirect('cv-manage', permanent=True)

	return render(request, 'cv/delete/delete_past_experience.html', {'title': 'Delete Experience',
																	 'experience': experience})


@login_required
def delete_experience(request, pk):
	experience = get_object_or_404(Experience, pk=pk)

	if request.method == "POST":
		experience.delete()
		return redirect('cv-manage', permanent=True)

	return render(request, 'cv/delete/delete_experience.html', {'title': 'Delete Experience',
																'experience': experience})
