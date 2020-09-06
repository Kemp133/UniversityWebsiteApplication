from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
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

	def rows_exist_in_table(self, table: WebElement, num_of_rows: int = 0, error_msg: str = None):
		min_num_of_rows = num_of_rows - 1
		trs = table.find_elements_by_tag_name("tr")
		self.assertTrue(len(trs) > min_num_of_rows, error_msg) if error_msg is not None else self.assertTrue(
			len(trs) > min_num_of_rows,
			f"{table.get_attribute('id')} doesn't have the required number of rows. Minimum Expected: {num_of_rows}, Actual: {len(trs)}")

	def test_can_load_cv_page(self):
		# The user loads up the website and goes to the cv section
		self.browser.get(f'{self.live_server_url}/cv')

		# Check that CV is mentioned in the title
		self.assertIn('CV', self.browser.title)

		# The user sees that there is a table that contains basic information, specifically my name and contact email
		try:
			basic_information = self.browser.find_element_by_id("table_BasicInfo")
		except NoSuchElementException as nsee:
			self.fail(nsee.msg)

		## Check that the table contains at least my name and contact email
		details = basic_information.find_elements_by_tag_name("td")

		if len(details) < 2:
			self.fail("The basic information table does not contain at least two entries")

		values_to_test = ["Johnathon Kemp", "kemp133@googlemail.com"]

		for val in values_to_test:
			self.assertIn(val, [data.text for data in details],
						  f"The following value could not be found in the table: {val}\nValues searched: {values_to_test}")

		# The user finishes looking through the basic information, and scrolls down to begin looking at the past
		# education history. They notice a section for GCSE results, and another for A-Level results

		## Check that there are two tables present (one for GCSE, the other for A-Level)
		past_education_tables = self.browser.find_elements_by_class_name("table_PastEducation")
		num_of_education_tables = len(past_education_tables)
		self.assertEqual(num_of_education_tables, 2, "Number of past education tables is not equal to 2.\nActual"
													 " number of tables: " + str(num_of_education_tables))

		## Check that there is a table for at least Secondary and College level education
		required_education_table_ids = ["id_SecondaryEducation", "id_CollegeEducation"]
		actual_education_table_ids = [str(val.get_attribute("id")) for val in past_education_tables]

		for val in required_education_table_ids:
			self.assertIn(val, actual_education_table_ids,
						  f"Required value, {val}, not found in table ids. Actual values: {actual_education_table_ids}")

		## Check that both tables actually have some rows attached to them
		for table in past_education_tables:
			self.rows_exist_in_table(table, 1, f"Given table does not have any rows: {table.get_attribute('id')}")

		# The user then scrolls down again, and comes to the skills and hobby section of the CV
		## Check that there's a table for each thing, i.e. one for skills and another for hobbies
		skills_table = self.browser.find_element_by_id("table_Skills")
		hobbies_table = self.browser.find_element_by_id("table_Hobbies")

		## Check that, once again, these items have at least one row inside of them
		self.rows_exist_in_table(skills_table, 1)
		self.rows_exist_in_table(hobbies_table, 1)

		# The user then scrolls down to the final section, which shows my past work experience
		## Check that there's at least one table containing this information
		past_experience = self.browser.find_elements_by_class_name("table_PastExperience")

		self.assertTrue(len(past_experience) >= 1, "There isn't at least one table for the past experience section")

		# The user scrolls down further realising this is the end of the CV. Heartbroken that it's come to an end, they
		# decide to email me with a work offer purely based on how good my CV was (*wink wink*) ;)

		# END OF TESTS
		self.fail("Reached end of tests!")

	def test_can_modify_cv_attributes(self):
		# I come to realise that the CV is missing some information, so I decide to modify the CV to add this
		# information

		## Attempt to navigate to the modify view
		self.browser.get(f"{self.live_server_url}/cv/manage")

		## Verify that the view is redirected to the log in view as I haven't been authenticated yet
		self.assertEqual(self.browser.title, "Log In")

		# The log in screen comes up, so I enter my credentials to allow myself access to the modify view
		time.sleep(10)

		## Check that the browser title is now equal to Manage CV
		self.assertEqual(self.browser.title, "Manage CV")

		# Reached end of test
		self.fail("Reached end of test!")
