
import unittest
import os
from appium import webdriver
from time import sleep
from appium.webdriver.common.touch_action import TouchAction

import xml.etree.ElementTree as ET
import hashlib
import time
import random
import string

class LoginTests(unittest.TestCase):

	def setUp(self):
		self.driver = webdriver.Remote(
			command_executor='http://127.0.0.1:4723/wd/hub',
			desired_capabilities={
				'platformName': 'iOS',
				'platformVersion': '14.2',
				'udid': <Device UDID>,
				'deviceName': <Device Name>,
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

	# simple function to return the md5 hash of a string

	def hashinshin(self, to_hash):
		return hashlib.md5(to_hash.encode()).hexdigest()

	# function to check if screen has changed using hashing

	def has_screen_changed(self):
		new_xml_hash = self.hashinshin(self.driver.page_source)

		if new_xml_hash != self.current_xml_page_source_hash:
			return True

		return False

	# check if element can be pressed to avoid trigerring error

	def can_press_button(self, element_name):
		try:
			self.driver.find_element_by_accessibility_id(element_name)
			return True
		except Exception as e:
			return False

	# reset the current page and current page's hash

	def reparse(self):
		self.current_xml_page_source = self.driver.page_source
		self.current_xml_page_source_hash = self.hashinshin(self.current_xml_page_source)

	# hacky function to decide text should be sent

	def should_send_text(self):

		random_nr = random.randint(0,3) # 25% chance

		# also check if keyboard is shown

		if self.driver.is_keyboard_shown() and random_nr == 2:
			return True

		return False

	def test(self):

		needs_reparse = True
		screens = {}

		# set max time to wait before pressing random buttons

		timeout = time.time() + 20; # s

		while True:

			# get source and hash for new screen if needed

			if needs_reparse:
				self.reparse()
				needs_reparse = False

			# after script ran out of buttons to press check if it exceeds wait time
			# and press random button

			if time.time() > timeout:

				# get random next_button and check if it can be pressed

				random_screen = random.choice(list(screens.keys()))

				# if the random screen we chose does not have a list of buttons yet

				if screens[random_screen].get('buttons') is None:
					break;

				random_element_name = random.choice(screens[random_screen]['buttons'])

				print('Tapping random button: ' + random_element_name)

				if self.can_press_button(random_element_name):

					# add button to visited buttons for the current screen list

					screens[self.current_xml_page_source_hash]['buttons'].append(random_element_name)

					# tap the element

					element = self.driver.find_element_by_accessibility_id(random_element_name)
					actions = TouchAction(self.driver)
					actions.tap(element)
					actions.perform()

					# leave some time for button action to happen

					sleep(2)

					# check if keyboard is shown and send keys 25% of the time

					if self.should_send_text():
						string_to_send = self.get_random_string(8)
						element.send_keys(string_to_send + "\n")

					# force reparsing of screen

					needs_reparse = True

					screens[self.current_xml_page_source_hash]['next_buttons'].append([random_element_name, 0])

					# bump wait time

					timeout = time.time() + 20 # s

					continue

			# initialise new screen dict

			if screens.get(self.current_xml_page_source_hash) is None:
				screens[self.current_xml_page_source_hash] = {}

			# initialize new button list for the dict

			if screens[self.current_xml_page_source_hash].get('buttons') is None:
				screens[self.current_xml_page_source_hash]['buttons'] = []

			# initialize transition list for the dict

			if screens[self.current_xml_page_source_hash].get('next_buttons') is None:
				screens[self.current_xml_page_source_hash]['next_buttons'] = []

			root = ET.fromstring(self.current_xml_page_source)

			# search for all interactable buttons

			for elem in root.iter('XCUIElementTypeButton'):
				element_name = elem.attrib.get('name')

				# check if the button has accessibility id set

				if element_name is None:
					continue

				# check if the button has already been explored
				# TODO: Pretify the check

				tapped = 0;
				for key, value in screens.items():

					if element_name in value['buttons']:
						tapped = 1
						break;

				if tapped:
					continue

				print("Now Tapping: " + element_name)

				# tap button if possible
				if self.can_press_button(element_name):
					# add button to visited buttons for the current screen list

					screens[self.current_xml_page_source_hash]['buttons'].append(element_name)

					element = self.driver.find_element_by_accessibility_id(element_name)

					actions = TouchAction(self.driver)
					actions.tap(element)
					actions.perform()

					# leave some time for button action to happen

					sleep(2)

					# bump timeout for the screen
					timeout = time.time() + 20 # s

				else:
					continue

				# check if keyboard is shown and send keys 25% of the time

				if self.should_send_text():
					string_to_send = self.get_random_string(8)
					element.send_keys(string_to_send + "\n")

				# check if the screen changed and prepare to reparse xml source
				# hacky solution: check if the xml hash differs

				needs_reparse = self.has_screen_changed()

				if needs_reparse:

					# add tapped button to list of next_buttons for the current screen
					# 0 -> placeholder for the next screen we get into
					# should be (next_button, screen_it_leads_to)

					screens[self.current_xml_page_source_hash]['next_buttons'].append([element_name, 0])

					break

		self.driver.close_app()



if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(LoginTests)
	unittest.TextTestRunner(verbosity=2).run(suite)
