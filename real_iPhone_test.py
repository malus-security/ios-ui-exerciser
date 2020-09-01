import unittest
import os
from appium import webdriver
from time import sleep
from appium.webdriver.common.touch_action import TouchAction

class LoginTests(unittest.TestCase):

	def setUp(self):
		self.driver = webdriver.Remote(
			command_executor='http://127.0.0.1:4723/wd/hub',
			desired_capabilities={
				'platformName': 'iOS',
				'platformVersion': '13.6.1',
				'udid': 'your phone udid here',
				'deviceName': 'your phone name here',
				'bundleId': 'com.google.chrome.ios -- wanted app bundle id for testing'
			}
		)

	def tearDown(self):
		self.driver.quit()

	def test(self):
		element = self.driver.find_element_by_accessibility_id('Google Account')
		actions = TouchAction(self.driver)
		actions.tap(element)
		actions.perform()
		sleep(3)

	def test2(self):
		actions = TouchAction(self.driver)
		actions.tap(None, 90, 272,1)
		actions.perform()
		sleep(3)

	def test3(self):
		actions = TouchAction(self.driver)
		actions.tap(None, 90, 272,1)
		actions.perform()
		sleep(3)
		self.driver.execute_script("mobile: scroll", {"direction": "down"})
		sleep(3)


if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(LoginTests)
	unittest.TextTestRunner(verbosity=2).run(suite)
