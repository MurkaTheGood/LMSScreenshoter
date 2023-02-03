from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from typing import Tuple
from datetime import datetime
import time
import os

CRED_PATH = 'credentials.txt'

def screenshot_element(el : WebElement, path : str) -> None:
	''' screenshot the WebElement and save the .png to path '''

	# try to screenshot
	try:
		with open(path, 'wb') as f:
			f.write(el.screenshot_as_png)
		print('OK')
	except:
		# :-(
		print('FAIL')

def get_auth_data() -> Tuple[str, str]:
	''' returns the saved auth data for the LMS user.
		will ask for credentials interactively and save them if they aren't present
	'''
	try:
		# try to read from file
		with open(CRED_PATH, 'r') as f:
			cred = [s.strip() for s in f.readlines()]
			return (cred[0], cred[1])
	except:
		# failed to read from file, ask for credentials
		login, password = \
			input('LMS login: '), input('LMS password: ')

		# save
		with open(CRED_PATH, 'w') as f:
			cred = '%s\n%s' % (login, password)
			f.write(cred)

		# return
		return (login, password)

def main():
	# getting the credentials
	login, password = get_auth_data()

	# log
	print('Starting the driver...')

	# open the headless gecko driver
	opts = webdriver.FirefoxOptions()
	opts.headless = True
	driver = webdriver.Firefox(options=opts)

	# naviagate to LMS main page
	print('Navigating to the LMS login page...')
	driver.get('https://online.mospolytech.ru/login/index.php')

	# authorizing
	print('Authorizing...')

	# type the credentials
	driver.find_element(By.ID, 'username').send_keys(login)
	time.sleep(1)
	driver.find_element(By.ID, 'password').send_keys(password)
	time.sleep(1)
	driver.find_element(By.ID, 'loginbtn').click()

	# asking to paste the overview URL
	driver.get(input('URL of answers overview: '))

	# check if questions are on different pages
	if driver.find_elements(By.CLASS_NAME, 'multipages'):
		print('Making the LMS show all questions on one page...')
		# show all questions on one page
		one_page_link = \
			driver.find_element(By.CLASS_NAME, 'othernav').find_elements(By.TAG_NAME, 'a')[0]

		# navigate to the wanteed page
		driver.get(one_page_link.get_attribute('href'))

		# sleep
		time.sleep(5)

	# looking for questions
	questions = driver.find_elements(By.CLASS_NAME, 'que')

	# create the directory for screenshots of current session
	screenshots_path = 'screenshots/%s' % \
		datetime.now().strftime('%d.%m.%Y, %T')
	os.makedirs(screenshots_path, exist_ok = True)

	# screenshot everything
	for q_e in enumerate(questions):
		# question number
		q_n = q_e[0] + 1

		# log
		print(
			'Screenshoting question #%s to %s/%s.png' % \
			(q_n, screenshots_path, q_n),
			end='... ')

		# try to save the screenshot
		screenshot_element(q_e[1], '%s/%s.png' % (screenshots_path, q_n))

	# done, close the driver
	driver.close()


# entry point
if __name__ == '__main__':
	main()