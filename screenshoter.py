from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from typing import Tuple
from datetime import datetime
import time
import os
import json
import enum

CRED_PATH = 'credentials.txt'

class QuestionType(enum.Enum):
	''' enum for question types.
		More information in README.md
	'''

	unknown, multichoice, gapselect, shortanswer = \
		range(4)

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

def remove_extra_whitespaces(original : str) -> str:
	''' this function removes extra whitespaces inside string '''
	# replace newlines with spaces
	original = original.replace('\n', ' ')

	# remove dublicated spaces
	while original.find(' ' * 2) != -1:
		original = original.replace(' ' * 2, ' ')

	return original

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

def get_question_type(question_elem : WebElement) -> QuestionType:
	# getting the classes of question WebElement
	classes = question_elem.get_attribute('class').split(' ')

	if 'multichoice' in classes: return QuestionType.multichoice
	if 'gapselect' in classes: return QuestionType.gapselect
	if 'shortanswer' in classes: return QuestionType.shortanswer

	# failed to determite the type of question
	return QuestionType.unknown

def main():
	# preparing JSON (in case we need it)
	serialized = {}
	serialized['multichoice'] = []

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
	time.sleep(0.1)
	driver.find_element(By.ID, 'password').send_keys(password)
	time.sleep(0.1)
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
		one_page_link.click()

	# looking for questions
	questions = driver.find_elements(By.CLASS_NAME, 'que')

	# create the directory for screenshots of current session
	results_path = 'results/%s' % \
		datetime.now().strftime('%d.%m.%Y, %T')
	os.makedirs(results_path, exist_ok = True)

	# dump everything
	for q_pair in enumerate(questions):
		# question number
		q_n = q_pair[0] + 1

		# question element
		q_e = q_pair[1]

		# get the question type
		q_type = get_question_type(q_e)

		# multichoice?
		if q_type == QuestionType.multichoice:
			# create the dict for multichoice
			multichoice_dict = { }
			# set the title
			multichoice_dict['title'] = \
				remove_extra_whitespaces(
					q_e.find_element(By.CSS_SELECTOR, 'div.qtext').text.strip())

			# add correct answers
			multichoice_dict['answers'] = []
			for a in q_e.find_elements(By.CSS_SELECTOR, 'div.rightanswer'):
				multichoice_dict['answers'].append(
					remove_extra_whitespaces(a.text.replace('Правильный ответ:', '').strip()))
			
			# add serialized multichoice to list
			serialized['multichoice'].append(multichoice_dict)

		# ************************
		# save the screenshot now
		# ************************

		# check if tabled answer
		table_elements = q_e. \
			find_elements(By.CSS_SELECTOR, 'table.answer')

		# yes!
		if table_elements:
			# iterate through all rows
			for tr in enumerate(table_elements[0].find_elements(By.TAG_NAME, 'tr')):
				# screenshot name
				sc_name = '%s_%s.png' % (q_n, tr[0])

				# log
				print(
					'Screenshoting row of question #%s to %s' % \
					(q_n, sc_name),
					end='... ')

				# try to save the screenshot
				screenshot_element(tr[1], '%s/%s' % \
					(results_path, sc_name))
		# no!
		else:
			# log
			print(
				'Screenshoting question #%s to %s.png' % \
				(q_n, q_n),
				end='... ')

			# try to save the screenshot
			screenshot_element(q_e, '%s/%s.png' % (results_path, q_n))

	# done, close the driver
	driver.close()

	# write json
	with open('%s/serialized.json' % results_path, 'w') as f:
		f.write(json.dumps(serialized, indent = 2, ensure_ascii = False))
		print('Saved serialized data to %s/serialized.json' % results_path)



# entry point
if __name__ == '__main__':
	main()