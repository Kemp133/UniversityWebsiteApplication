from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

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

		# The user sees that there is a table that contains basic information
		try:
			basic_information = self.browser.find_element_by_id("table_BasicInfo")
		except NoSuchElementException as nsee:
			self.fail(nsee.msg)

		# Check that the table contains at least my name and contact email
		details = basic_information.find_elements_by_tag_name("td")

		if len(details) < 2:
			self.fail("The basic information table does not contain at least two entries")

		values_to_test = ["Johnathon Kemp", "kemp133@googlemail.com"]

		for val in values_to_test:
			self.assertIn(val, (data.text for data in details),
						  f"The following value could not be found in the table: {val}\nValues searched: {values_to_test}")

		# The user finishes looking through the basic information, and scrolls down to begin looking at the past
		# education history

		# Check that there are two tables present (one for GCSE, the other for A-Level)
		past_education_tables = self.browser.find_elements_by_class_name("table_PastEducation")
		num_of_education_tables = len(past_education_tables)
		self.assertEqual(num_of_education_tables, 2, "Number of past education tables is not equal to 2.\nActual"
														" number of tables: " + str(num_of_education_tables))

		# Check that there is a table for at least Secondary and College level education
		required_education_table_ids = ["id_SecondaryEducation", "id_CollegeEducation"]
		actual_education_table_ids = (str(val.id) for val in past_education_tables)

		for val in required_education_table_ids:
			self.assertIn(val, actual_education_table_ids,
						  f"Required value, {val}, not found in table ids. Actual values: {actual_education_table_ids}")

		# Check that both tables actually have some rows attached to them
		for table in past_education_tables:
			self.assertTrue(len(table.find_elements_by_tag_name("tr")) > 0, f"Given table does not have any rows: {table}")

		self.fail("Reached end of tests!")
