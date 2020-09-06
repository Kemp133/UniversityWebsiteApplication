from django.test import TestCase


# Create your tests here.
class CVPageTest(TestCase):

	def test_uses_index_template(self):
		response = self.client.get("/cv/")
		self.assertTemplateUsed(response, 'cv/index.html')

	def test_manage_view_exists_without_authentication(self):
		# Try and navigate to the manage view of the cv application
		response = self.client.get("/cv/manage")

		# Assert that the view redirects to the log in screen, as this view requires the user to be logged in
		self.assertRedirects(response, "/account/login")
