import sys

from blog.models import BlogImageToMove, BlogExceptions


class BlogTagMethodNotImplementedException(Exception):
	# This should be set in the base class, so that any unimplemented methods can be detected quickly
	pass


def report_exception():
	exc_type, value, traceback = sys.exc_info()
	new_exception = BlogExceptions()
	new_exception.exc_type = exc_type
	new_exception.value = value
	new_exception.traceback = traceback
	new_exception.save()
