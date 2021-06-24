
import unittest
import os
from appium import webdriver
from time import sleep
from appium.webdriver.common.touch_action import TouchAction

from difflib import SequenceMatcher
import difflib
import hashlib
import time
import random
import string
import uuid
import sys

class LoginTests(unittest.TestCase):

	def setUp(self):
		self.driver = webdriver.Remote(
			command_executor='http://127.0.0.1:4723/wd/hub',
			desired_capabilities={
				'platformName': 'iOS',
				'platformVersion': '14.2',
				'udid': '',
				'deviceName': '',
				'bundleId': 'com.google.chrome.ios'
			}
		)

	def tearDown(self):
		self.driver.quit()

	# function that returns a random string of fixed length

	def get_random_string(self, length):
		letters = string.ascii_letters
		result_string = ''.join(random.choice(letters) for i in range(length))
		return result_string

	# hacky function to decide text should be sent

	def should_send_text(self):

		random_nr = random.randint(0,3) # 25% chance

		# also check if keyboard is shown

		if self.driver.is_keyboard_shown() and random_nr == 2:
			return True

		return False

	# setup a new dictionary entry for the current screen

	def setup_screen_dict(self):

		# initialize new screen dict

		if self.screens.get(self.current_xml_page_hash) is None:
			self.screens[self.current_xml_page_hash] = {}

		# initialize new button list for the dict

		if self.screens[self.current_xml_page_hash].get('buttons') is None:
			self.screens[self.current_xml_page_hash]['buttons'] = []

		# initialize transition list for the dict

		if self.screens[self.current_xml_page_hash].get('next_buttons') is None:
			self.screens[self.current_xml_page_hash]['next_buttons'] = []

		# initialize interest classes list for the dict

		if self.screens[self.current_xml_page_hash].get('interest_classes') is None:
			self.screens[self.current_xml_page_hash]['interest_classes'] = []

		# initialize similarity list

		if self.screens[self.current_xml_page_hash].get('similarity_list') is None:
			self.screens[self.current_xml_page_hash]['similarity_list'] = {}

		# save page source for future reference

		if self.screens[self.current_xml_page_hash].get('page_source') is None:
			self.screens[self.current_xml_page_hash]['page_source'] = self.driver.page_source

	# similarity function to be used in identifying difference ratio between two
	# strings

	def compute_string_similarity(self, a, b):
	    return SequenceMatcher(None, a, b).ratio()

	# concatenate static text from a static element list
	# CURRENTLY NOT USED ANYMORE

	def aggregate_static_text(self, static_text_elements_list):

		concatenated_static_string = ''

		# concatenate every name attribute of static text elements of the argument list

		for static_element in static_text_elements_list:

			if static_element.get_attribute('name') is not None:

				concatenated_static_string += static_element.get_attribute('name') + " "

		return concatenated_static_string

	# function to calculate similarity to all previously visited screens

	def compute_similarity(self, current_screen_hash):

		current_screen_page_source = self.screens[current_screen_hash]['page_source']

		for screen_hash, screen_info in self.screens.items():

			if screen_hash != current_screen_hash:

				self.screens[current_screen_hash]['similarity_list'].update\
					({screen_hash : self.compute_string_similarity(screen_info['page_source']\
					, current_screen_page_source)})

	# reset the current page and current page's hash

	def reparse(self):

		self.current_xml_page_source = self.driver.page_source

		self.current_xml_page_hash = self.hashinshin(self.current_xml_page_source)

		# setup the dictionary

		self.setup_screen_dict()

		# compute similarity for the current screen

		self.compute_similarity(self.current_xml_page_hash)

		# after a reparsing, set marker to false

		self.needs_reparse = False

	# set element name if none provided in the app

	def set_element_name_for(self, element):

		element_name = element.get_attribute('name')

		if not element_name:

			element_name = str(uuid.uuid4())

		return element_name

	# simple function to return the md5 hash of a string

	def hashinshin(self, to_hash):
		return hashlib.md5(str(to_hash).encode()).hexdigest()

	# function to check if screen has changed using hashing

	def has_screen_changed(self):

		new_xml_page_source = self.driver.page_source

		# compute hash of new page source

		new_xml_hash = self.hashinshin(new_xml_page_source)

		if new_xml_hash != self.current_xml_page_hash:

			if self.compute_string_similarity(self.current_xml_page_source, new_xml_page_source) > 0.9:

				print("Similar screens identified. Continuing tapping...")

				return False

			# for hash, similarity in self.screens[self.current_xml_page_hash]['similarity_list'].items():
			#
			# 	if similarity > 0.95:
			#
			# 		self.current_screen_hash = hash
			#
			# 		return False

			return True

		return False

	# perform an action on an element and do the necessary associacions

	def perform_action_on(self, element):

		element_name = self.set_element_name_for(element)

		# add button to visited buttons for the current screen list

		self.screens[self.current_xml_page_hash]['buttons'].append(element_name)

		# tap the element

		actions = TouchAction(self.driver)
		actions.tap(element)
		actions.perform()

		# leave some time for button action to happen

		sleep(2)

		# check if keyboard is shown and send keys 25% of the time

		if self.should_send_text():
			string_to_send = self.get_random_string(8)
			element.send_keys(string_to_send + "\n")

		# check if the screen changed
		# hacky solution: check if the hash of the page differs

		self.needs_reparse = self.has_screen_changed()

		if self.needs_reparse:

			# add tapped button to list of next_buttons for the current screen
			# 0 -> placeholder for the next screen we get into
			# should be (next_button, screen_it_leads_to)

			current_screen_next_buttons = self.screens[self.current_xml_page_hash]['next_buttons']

			if not element_name in current_screen_next_buttons:

				current_screen_next_buttons.append([element_name, 0])

		# bump wait time

		self.timeout = time.time() + 25 # s

	# perform action on previously tapped random button

	def perform_action_randomly(self):

		# check if we haven't already visited all interest classes on this screen

		unvisited_interest_classes = [visited for visited in self.classes_of_interest if not visited[1]]

		if not unvisited_interest_classes:
			print('Everything visited here. Pressing random visited button')

			# get a random next button which we know will lead to a new screen

			current_screen_buttons = self.screens[self.current_xml_page_hash].get('next_buttons')

			# if there are no next buttons try a normal buttton

			if not current_screen_buttons:

				# if there are no visited buttons, tap a random button

				if not self.screens[self.current_xml_page_hash].get('buttons'):

					print('No visited buttons to tap. Choosing random button from interest class... ')

					button_list = self.current_button_list

					random_visited_button_name = random.choice(button_list)

				current_screen_buttons = self.screens[self.current_xml_page_hash].get('buttons')

				random_visited_button_name = random.choice(current_screen_buttons)
			else:
				random_visited_button_name = random.choice(current_screen_buttons)[0]

			print('Tapping random visited button: ' + random_visited_button_name)

			random_visited_button = self.driver.find_element_by_name(random_visited_button_name)

			# check if element is visible

			if self.check_visibility_for_items:

				if random_visited_button.is_displayed():

					self.perform_action_on(random_visited_button)

					return True

				return False

			else:
				self.perform_action_on(random_visited_button)

				return True


		# get random element_name from interest list and check if it can be pressed

		selected_class = random.choice(unvisited_interest_classes)

		print('Selecting random unvisited class: ' + selected_class[0])

		random_element_list = self.driver.find_elements_by_class_name(selected_class[0])

		# check if for some reason there are no elements in current screen list

		if len(random_element_list) == 0:

			print('Nothing to press in this class. Moving on!')

			# mark current class as visited

			self.screens[self.current_xml_page_hash]['interest_classes'].append(self.random_interest_class)

			return False

		random_element = random.choice(random_element_list)

		random_element_name = self.set_element_name_for(random_element)

		print('Tapping random button: ' + random_element_name)

		# check if element is visible

		if self.check_visibility_for_items:

			if random_visited_button.is_displayed():

				self.perform_action_on(random_visited_button)

				return True

			return False

		else:
			self.perform_action_on(random_visited_button)

			return True

	# start of the actual script

	def testGetElements(self):

		self.needs_reparse = True

		self.screens = {}

		# setting for checking item visibility before tapping button

		self.check_visibility_for_items = True

		# desired classes of interes

		self.classes_of_interest = [
		"XCUIElementTypeButton",
		"XCUIElementTypeCell",
		"XCUIElementTypeLink",
		"XCUIElementTypeImage",
		# "XCUIElementTypeStaticText",
		# "XCUIElementTypeKey",
		# "XCUIElementTypeOther",
		]

		# set empty concatenated string for static text retention

		self.current_concatenated_static_string = ''

		# set max time to wait before pressing random buttons

		self.timeout = time.time() + 75 # s

		while True:

			# get source and hash for list of buttons on screen if needed

			if self.needs_reparse:

				self.reparse()

				# setup random interest class

				self.random_interest_class = random.choice(self.classes_of_interest)

				print('Current interest class is: ' + self.random_interest_class)

				# get a list of all the elements of interest (visible and invisible) on the screen

				self.current_button_list = self.driver.find_elements_by_class_name(self.random_interest_class)

				elements = self.current_button_list

				# if no elements on the list, move to another interest class

				if not bool(elements):

					print("No elements in the current interest class")

					self.screens[self.current_xml_page_hash]['interest_classes'].append(self.random_interest_class)

					continue

			# check if the current class has already been visited

			if self.random_interest_class in self.screens[self.current_xml_page_hash]['interest_classes']:
				continue

			# if script takes too long to press button check if it exceeds wait time
			# and press random button

			if time.time() > self.timeout:

				if not self.perform_action_randomly():
					continue

			# try pressing every element in succsession

			for element in elements:

				element_name = self.set_element_name_for(element)

				# check if element is visible

				if self.check_visibility_for_items:
					if not element.is_displayed():
						continue

				# check if the button has already been explored

				if element_name in self.screens[self.current_xml_page_hash]['buttons']:
					continue

				print("Now Tapping: " + element_name)

				self.perform_action_on(element)

				# if current screen needs reparsing then we dont need to check
				# the other buttons

				if self.needs_reparse:
					break

			# if the screen has not changed and we passed through the entire
			# element list for the current class

			if not self.needs_reparse:

				# add interest class to visited list for the current screen

				self.screens[self.current_xml_page_hash]['interest_classes'].append(self.random_interest_class)

		self.driver.close_app()



if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(LoginTests)
	unittest.TextTestRunner(verbosity=2).run(suite)
