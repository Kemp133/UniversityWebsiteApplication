from django.test import TestCase
from django.urls import resolve
from cv.views import index


# Create your tests here.
class CVPageTest(TestCase):

	def test_cv_url_resolves_to_home_page_view(self):
		cv_index = resolve('/cv/')
		self.assertEqual(cv_index.func, index)
