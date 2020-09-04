from selenium import webdriver

from django.test import LiveServerTestCase

import unittest
import time


class LoadCVTest(LiveServerTestCase):
	def setUp(self) -> None:
		# Get a window to test in
		self.browser = webdriver.Firefox()

	def tearDown(self) -> None:
		self.browser.quit()

	def test_can_load_cv_page(self):
		# The user loads up the website and goes to the cv section
		self.browser.get(f'{self.live_server_url}/cv')

		# Check that CV is mentioned in the title
		self.assertIn('CV', self.browser.title)

		# Fail as we don't currently have any tests
		self.fail('Finished the Test!')
