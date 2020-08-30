import datetime
from UniversityWebsiteApplication.settings import MEDIA_ROOT


def get_new_path_in_media_root(old_path):
	# Get the current date ready to construct the required image path
	date = datetime.date.today()

	# Format the path to create with the MEDIA_ROOT, current year, current date, and filename
	filename = old_path.split("/")[-1]
	new_media_path = f'{MEDIA_ROOT}/blog/{date.year}/{date.month}/{filename}'

	return new_media_path
