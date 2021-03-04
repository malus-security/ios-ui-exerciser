
import unittest
import os
from appium import webdriver
from time import sleep
from appium.webdriver.common.touch_action import TouchAction

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

	# setup a new dictionary structure

	def setup_screen_dict(self):

		# initialize new screen dict

		if self.screens.get(self.current_button_list_hash) is None:
			self.screens[self.current_button_list_hash] = {}

		# initialize new button list for the dict

		if self.screens[self.current_button_list_hash].get('buttons') is None:
			self.screens[self.current_button_list_hash]['buttons'] = []

		# initialize transition list for the dict

		if self.screens[self.current_button_list_hash].get('next_buttons') is None:
			self.screens[self.current_button_list_hash]['next_buttons'] = []

		# initialize interest classes list for the dict

		if self.screens[self.current_button_list_hash].get('interest_classes') is None:
			self.screens[self.current_button_list_hash]['interest_classes'] = []

	# reset the current page and current page's hash

	def reparse(self):
		self.current_button_list = self.driver.find_elements_by_class_name(self.random_interest_class)
		self.current_button_list_hash = self.hashinshin(self.driver.
			find_elements_by_class_name('XCUIElementTypeStaticText'))

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

		# compute hash based on button list

		new_xml_hash = self.hashinshin(self.driver.
			find_elements_by_class_name('XCUIElementTypeStaticText'))

		if new_xml_hash != self.current_button_list_hash:
			return True

		return False

	# perform an action on an element and do the necessary associacions

	def perform_action_on(self, element):

		element_name = self.set_element_name_for(element)

		# add button to visited buttons for the current screen list

		self.screens[self.current_button_list_hash]['buttons'].append(element_name)

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
		# hacky solution: check if the hash of the button list differs

		self.needs_reparse = self.has_screen_changed()

		if self.needs_reparse:

			# add tapped button to list of next_buttons for the current screen
			# 0 -> placeholder for the next screen we get into
			# should be (next_button, screen_it_leads_to)

			current_screen_next_buttons = self.screens[self.current_button_list_hash]['next_buttons']

			if not element_name in current_screen_next_buttons:
				current_screen_next_buttons.append([element_name, 0])

		# bump wait time

		self.timeout = time.time() + 25 # s

	# perform action on previously untapped random button

	def perform_action_randomly(self):

		# check if we haven't already visited all interest classes on this screen

		unvisited_interest_classes = [visited for visited in self.classes_of_interest if not visited[1]]

		if not unvisited_interest_classes:
			print('Everything visited here. Pressing random visited button')

			# get a random next button which we know will lead to a new screen

			current_screen_buttons = self.screens[self.current_button_list_hash].get('next_buttons')

			# if there are no next buttons try a normal buttton

			if not current_screen_buttons:

				# if there are no visited buttons, exit with error

				if not self.screens[self.current_button_list_hash].get('buttons'):
					sys.exit('No visited buttons to tap. Exiting... ')

				current_screen_buttons = self.screens[self.current_button_list_hash].get('buttons')

				random_visited_button_name = random.choice(current_screen_buttons)
			else:
				random_visited_button_name = random.choice(current_screen_buttons)[0]

			print('Tapping random visited button: ' + random_visited_button_name)

			random_visited_button = self.driver.find_element_by_name(random_visited_button_name)

			if random_visited_button.is_displayed():

				self.perform_action_on(random_visited_button)

				return True

			return False

		# get random element_name from interest list and check if it can be pressed

		selected_class = random.choice(unvisited_interest_classes)

		print('Selecting random unvisited class: ' + selected_class[0])

		random_element_list = self.driver.find_elements_by_class_name(selected_class[0])

		# check if for some reason there are no elements in current screen list

		if len(random_element_list) == 0:
			print('Nothing to press in this class. Moving on!')

			# mark current class as visited

			self.screens[self.current_button_list_hash]['interest_classes'].append(self.random_interest_class)

			return False

		random_element = random.choice(random_element_list)

		random_element_name = self.set_element_name_for(random_element)

		print('Tapping random button: ' + random_element_name)

		# check if element is visible

		if random_element.is_displayed():

			self.perform_action_on(random_element)

			return True

		return False

	# start of the actual script

	def testGetElements(self):

		self.needs_reparse = True
		self.screens = {}

		self.classes_of_interest = [
		"XCUIElementTypeButton",
		"XCUIElementTypeCell",
		"XCUIElementTypeLink",
		"XCUIElementTypeImage",
		"XCUIElementTypeStaticText",
		# "XCUIElementTypeKey",
		]

		# set max time to wait before pressing random buttons

		self.timeout = time.time() + 25; # s

		while True:
			# setup random interest class

			self.random_interest_class = random.choice(self.classes_of_interest)

			print('Current interest class is: ' + self.random_interest_class)

			# get a list of all the elements of interest (visible and invisible) on the screen

			elements = self.driver.find_elements_by_class_name(self.random_interest_class)

			# leave time to receive response from Appium with element list

			sleep(3)

			# get source and hash for list of buttons on screen if needed

			if self.needs_reparse:
				self.reparse()

			# setup the dictionary

			self.setup_screen_dict()

			# check if the current class has already been visited

			if self.random_interest_class in self.screens[self.current_button_list_hash]['interest_classes']:
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

				if not element.is_displayed():
					continue

				# check if the button has already been explored

				if element_name in self.screens[self.current_button_list_hash]['buttons']:
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

				self.screens[self.current_button_list_hash]['interest_classes'].append(self.random_interest_class)

		self.driver.close_app()



if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(LoginTests)
	unittest.TextTestRunner(verbosity=2).run(suite)
