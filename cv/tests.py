from django.test import TestCase


# Create your tests here.
class CVPageTest(TestCase):

	def test_uses_index_template(self):
		response = self.client.get("/cv/")
		self.assertTemplateUsed(response, 'cv/index.html')
