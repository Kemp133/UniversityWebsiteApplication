from django.urls import path
from .views import (index, manage, add_basic_information, add_past_education, add_skill, add_hobby, add_past_experience,
					add_subject_to_education, delete_education, toggle_subject, delete_subject, toggle_skill,
					delete_skill, toggle_hobby, delete_hobby, toggle_basic_information, delete_basic_information)


urlpatterns = [
	path("", index, name='cv-index'),
	path("manage", manage, name='cv-manage'),
	path("manage/add/BasicInformation", add_basic_information, name='cv-add-basic-information'),
	path("manage/toggle/BasicInformation/<int:pk>", toggle_basic_information, name="cv-toggle-BasicInformation"),
	path("manage/delete/BasicInformation/<int:pk>", delete_basic_information, name="cv-delete-BasicInformation"),
	path("manage/add/PastEducation", add_past_education, name='cv-add-past-education'),
	path("manage/add/PastEducation/<int:pk>", add_subject_to_education, name="cv-add-subject-to-education"),
	path("manage/delete/PastEducation/<int:pk>", delete_education, name="cv-delete-education"),
	path("manage/toggle/subject/<int:pk>", toggle_subject, name="cv-toggle-subject"),
	path("manage/delete/subject/<int:pk>", delete_subject, name="cv-delete-subject"),
	path("manage/add/skill", add_skill, name='cv-add-skill'),
	path("manage/toggle/skill/<int:pk>", toggle_skill, name="cv-toggle-skill"),
	path("manage/delete/skill/<int:pk>", delete_skill, name="cv-delete-skill"),
	path("manage/add/hobby", add_hobby, name='cv-add-hobby'),
	path("manage/toggle/hobby/<int:pk>", toggle_hobby, name="cv-toggle-hobby"),
	path("manage/delete/hobby/<int:pk>", delete_hobby, name="cv-delete-hobby"),
	path("manage/add/PastExperience", add_past_experience, name='cv-add-past-experience'),
]
