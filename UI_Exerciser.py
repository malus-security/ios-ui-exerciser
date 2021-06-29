
import unittest
import os
from appium import webdriver
from time import sleep
from appium.webdriver.common.touch_action import TouchAction

from argparse import ArgumentParser
from difflib import SequenceMatcher
import difflib
import hashlib
import random
import string
import time
import sys


class LoginTests(unittest.TestCase):

	# function to setup server session with desired capabilities

	def setUp(self):
		self.driver = webdriver.Remote(
			command_executor='http://127.0.0.1:4723/wd/hub',
			desired_capabilities={
				'platformName': 'iOS',
				'platformVersion': '14.2',
				'udid': '00008020-000874A02682002E',
				'deviceName': 'Andrew\'s Xs Max',
				'bundleId': 'com.google.chrome.ios'
			}
		)

	# simple function to return the md5 hash of a string

	def hashinshin(self, to_hash):
		return hashlib.md5(to_hash.encode()).hexdigest()

	# similarity function to be used in identifying difference ratio between two
	# strings

	def compute_string_similarity(self, a, b):
	    return SequenceMatcher(None, a, b).ratio()

	# function to calculate similarity to all previously visited screens

	def compute_similarity_for(self, current_screen_hash):

		current_screen_page_source = self.screens[current_screen_hash]['page_source']

		for screen_hash, screen_info in self.screens.items():

			# for every screen except the current compute similarity to previous screens

			if screen_hash != current_screen_hash:

				self.screens[current_screen_hash]['similarity_list'].update\
					({screen_hash : self.compute_string_similarity(screen_info['page_source'],\
					 	current_screen_page_source)})

		self.screens[current_screen_hash]['similarity_check_performed'] = True

	# function to determine if current screen is similar to a past one

	def find_screen_similar_to(self, screen_hash_to_check):

		# use a lambda function to sort the similarity dict by value

		sorted_similarity_dict = sorted(self.screens[screen_hash_to_check]\
			['similarity_list'].items(), key = lambda x : x[1], reverse = True)

		best_match = sorted_similarity_dict[0]

		# check if the maximum similarity is greater then a threshold

		if best_match[1] > self.similarity_threshold:

			return best_match[0]

		return False


	# set element name if none provided in the app

	def set_element_name_for(self, element):

		element_name = element.get_attribute('name')

		if not element_name:

			element_name = self.random_interest_class + " - " + str(self.current_button_list.index(element))

		return element_name

	# function to check if screen has changed using hashing

	def has_screen_changed(self):

		new_xml_page_source = self.driver.page_source

		new_xml_hash = self.hashinshin(new_xml_page_source)

		if new_xml_hash != self.current_xml_page_hash:

			return True

		return False

	# function to set a new interest class

	def set_new_interest_class(self):

		unvisited_interest_classes = list(set(self.classes_of_interest) -\
		 set(self.screens[self.current_xml_page_hash]['visited_interest_classes']))

		if len(unvisited_interest_classes) == 0:

			return False

		self.random_interest_class = random.choice(unvisited_interest_classes)

		print('Current interest class is: ' + self.random_interest_class)

		return True

	# function to pull elements for a given interest class

	def pull_element_list_for(self, interest_class):

		self.current_button_list = self.driver.find_elements_by_class_name(interest_class)

	# reset the current page and current page's hash

	def reparse(self):

		# get the page source and compute the hash to use as key

		self.current_xml_page_source = self.driver.page_source

		new_xml_hash = self.hashinshin(self.current_xml_page_source)

		# for the old screen, connect the last next_button to the current screen it led to

		if self.screen_change_triggered:

			self.screens[self.current_xml_page_hash]['next_buttons'][-1][1] = new_xml_hash

			# clear the screen change

			self.screen_change_triggered = False

		# save old screen hash in case a similar screen will be later identified

		old_screen_hash = self.current_xml_page_hash

		# change the current screen hash

		self.current_xml_page_hash = new_xml_hash

		# setup dictionary entry for the current screen if neeed

		if self.current_xml_page_hash not in self.screens:

			self.setup_screen_dict()

		# save page source for future reference if first visit

		if self.screens[self.current_xml_page_hash].get('page_source') is None:

			self.screens[self.current_xml_page_hash]['page_source'] = self.current_xml_page_source

		# compute similarity list for the current screen

		if not self.screens[self.current_xml_page_hash]['similarity_check_performed']:

			self.compute_similarity_for(self.current_xml_page_hash)

		# find similar screen to current (if we have more than one screen)

		if len(self.screens) > 1:

			similar_screen_found = self.find_screen_similar_to(self.current_xml_page_hash)

			# if a valid candidate has been found, switch the current hash to the returned value

			if similar_screen_found:

				print("Screen " + self.current_xml_page_hash + " simiar to screen " + similar_screen_found)

				print("Switching screen to " + similar_screen_found)

				self.current_xml_page_hash = similar_screen_found

				# change next button entry for the previous screen if value different than 0 (placeholder)

				if self.screens[old_screen_hash]['next_buttons'][-1][1] != 0:

					self.screens[old_screen_hash]['next_buttons'][-1][1] = similar_screen_found


		# setup random interest class

		self.set_new_interest_class()

		# get a list of all the elements of interest (visible and invisible) on the screen

		self.pull_element_list_for(self.random_interest_class)


		self.needs_reparse = False

	def perform_action_on(self, element):

		element_name = self.set_element_name_for(element)

		# check if element is visible

		if not element.is_displayed():

			print(element_name + " : invisible element")

			return False

		# check if the button has already been explored

		if element_name in self.screens[self.current_xml_page_hash]['buttons']:

			print(element_name + " : visited element")

			return False

		print("Now Tapping: " + element_name)

		actions = TouchAction(self.driver)

		actions.tap(element)

		actions.perform()

		self.screens[self.current_xml_page_hash]['buttons'].append(element_name)

		# check if screen has changed to add to list of next buttons

		self.needs_reparse = self.has_screen_changed()

		if self.needs_reparse:

			# add tapped button to list of next_buttons for the current screen
			# 0 -> placeholder for the next screen we get into
			# should be (next_button, screen_it_leads_to)

			if not element_name in self.screens[self.current_xml_page_hash]['next_buttons']:

				self.screens[self.current_xml_page_hash]['next_buttons'].append([element_name, 0])

		return True

	# function to print the screens hashtable

	def print_screens_hashtable(self):

		print("Printing screen hashtable...", end = "\n\n")

		for hash, screen_info in self.screens.items():

			print("Screen : " + hash)

			for info_field, info_value in screen_info.items():

				if info_field not in self.blacklisted_info:

					print(info_field + " : " + str(info_value))

			print()

		print("Found %d screens" % len(self.screens), end= "\n\n")


	# setup a new dictionary entry for the current screen

	def setup_screen_dict(self):

		# initialize new screen dict entry

		if self.screens.get(self.current_xml_page_hash) is None:

			self.screens[self.current_xml_page_hash] = {}

		# initialize new button list for the screen

		if self.screens[self.current_xml_page_hash].get('buttons') is None:

			self.screens[self.current_xml_page_hash]['buttons'] = []

		# initialize transition list for the screen

		if self.screens[self.current_xml_page_hash].get('next_buttons') is None:

			self.screens[self.current_xml_page_hash]['next_buttons'] = []

		# initialize interest classes list for the screen

		if self.screens[self.current_xml_page_hash].get('visited_interest_classes') is None:

			self.screens[self.current_xml_page_hash]['visited_interest_classes'] = []

		# initialize similarity list

		if self.screens[self.current_xml_page_hash].get('similarity_list') is None:

			self.screens[self.current_xml_page_hash]['similarity_list'] = {}

		# field to let the script know a similarity check has been done for this screen

		if self.screens[self.current_xml_page_hash].get('similarity_check_performed') is None:

			self.screens[self.current_xml_page_hash]['similarity_check_performed'] = False

	# function to handle argument parsing

	def get_program_arguments(self):

		parser = ArgumentParser("iOS UI Exerciser Script")

		parser.add_argument('-c', '--classes', dest='class_list', nargs='+',\
			help='Classes of interest for the current script run. Possible classes are: \
			XCUIElementTypeButton XCUIElementTypeCell XCUIElementTypeLink XCUIElementTypeImage \
			XCUIElementTypeStaticText XCUIElementTypeOther', type=str, required=True)

		parser.add_argument('-t', '--timeout', dest='timeout', type=int, default=0,\
			help='Timeout in seconds for the script. Default: 0')

		parser.add_argument('-s', '--similarity', dest='similar', type=float, default=0.9,\
			help='The similarity percentage desired between screens. Default: 0.9')

		args = parser.parse_args()

		return args

	# function for the initial setup of the script

	def initial_setup(self):

		args = self.get_program_arguments()

		self.classes_of_interest = args.class_list

		self.similarity_threshold = args.similar

		print("\n\nThe desired classes of interest are: " + str(self.classes_of_interest))
		print("The desired similarity percentage is: " + str(self.similarity_threshold), end="\n\n")

		# internal info about a screen used in script logic
		# does not need to be printed out

		self.blacklisted_info = [
		"page_source",
		"similarity_check_performed"
		]

		self.needs_reparse = True

		self.screen_change_triggered = False

		self.screens = {}

		# set current xml hash to 0 for the first screen before reparsing

		self.current_xml_page_hash = 0

		# set max time to wait before ending script

		if args.timeout != 0:

			self.timeout = time.time() + args.timeout # s

			# marker for script to run indefinetly

			self.run_forever = False

		else:

			# set marker to let script know it will run indefinetly

			self.run_forever = True

	def test(self):

		self.initial_setup()

		while True:

			# if timeout is set, after given time, end the script and print the screen hashtable

			if not self.run_forever:

				if time.time() > self.timeout:

					print("Time limit excedeed.")

					self.print_screens_hashtable()

					break

			currently_untapped_in_list = 0

			currently_tapped_in_list = 0

			if self.needs_reparse:

				self.reparse()

			# if the button list is empty mark the interest class visited
			# and move on

			if self.current_button_list == []:

				print("Current button list empty")

				self.screens[self.current_xml_page_hash]['visited_interest_classes'].append(self.random_interest_class)

				if self.set_new_interest_class():

					print("Switching interest class...")

					# ask for a requery of the list of buttons

					self.pull_element_list_for(self.random_interest_class)

					continue

				else:

					print("No more classes to check")

					break

			else:

				print(self.random_interest_class + " : found " + str(len(self.current_button_list)) + " elements")

			# parse the list of elements for the current button list

			for element in self.current_button_list:

				if self.perform_action_on(element):

					# time delay to leave pages to load

					sleep(5)

					currently_tapped_in_list += 1

					print("Screen need reparsing: " + str(self.needs_reparse))

					# if current screen needs reparsing then we dont need to check
					# the other buttons

					if self.needs_reparse:

						# mark a screen change. Used to determine the screen the pressed button led to

						self.screen_change_triggered = True

						# check if last button pressed was last in class and triggered a screen change

						if currently_tapped_in_list + currently_untapped_in_list == len(self.current_button_list):

							# add interest class to list of visited classes

							self.screens[self.current_xml_page_hash]['visited_interest_classes'].append(self.random_interest_class)

						break

				else:

					currently_untapped_in_list += 1

					continue

			# if the screen has not changed and every button visited, add class to
			# visited list

			if currently_tapped_in_list + currently_untapped_in_list == len(self.current_button_list):

				print("Nothing in the current class left to tap")

				# add interest class to list of visited classes

				self.screens[self.current_xml_page_hash]['visited_interest_classes'].append(self.random_interest_class)

				# choose a different interest class and ask for a requery of the list of buttons

				if self.set_new_interest_class():

					print("Switching to a different interest class...")

					self.pull_element_list_for(self.random_interest_class)

				else:

				# all the interest classes for the current screen have been visited

					print("No more classes to check")

					self.print_screens_hashtable()

					break

		self.driver.close_app()

if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(LoginTests)
	unittest.TextTestRunner(verbosity=2).run(suite)
