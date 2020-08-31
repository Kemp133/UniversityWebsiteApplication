import datetime
import os
import typing

from UniversityWebsiteApplication.settings import MEDIA_ROOT
from blog.Util.Exceptions import report_exception


def get_new_path_in_media_root(old_path):
	# Get the current date ready to construct the required image path
	date = datetime.date.today()

	# Format the path to create with the MEDIA_ROOT, current year, current date, and filename
	filename = old_path.split("/")[-1]
	new_media_path = f'{MEDIA_ROOT}/blog/{date.year}/{date.month}/{filename}'

	return new_media_path


def delete_file_in_media(to_delete: typing.List[str]):
	for val in to_delete:
		try:
			if os.path.exists(val):
				os.remove(val)
		except:
			report_exception()
		else:
			continue

