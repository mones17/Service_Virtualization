from curses.ascii import *
import re

specialRegex = "[ `',+@_!#$%^&*()<>?/\\|}{~:\[\]-]"

def ValidatePassword(password):
	if not 8 <= len(password) <= 20:
		return False, "Password must contain at least 8 characters and maximum 20."
	num = 0
	upper = 0
	alphabet = 0
	special = 0
	for char in password:
		matchChar = re.match(specialRegex, char)
		if matchChar is not None:
			special += 1
		elif char.isdigit():
			num += 1
		elif char.isupper():
			upper += 1
		elif char.isalpha():
			alphabet += 1
	if num >= 1 and upper >= 1 and alphabet >= 1 and special >= 1:
		return True, "Password complexity as expected."
	message = ""
	if num < 1:
		message = message + "Password must contain at least 1 number. "
	if upper < 1:
		message = message + "Password must contain at least 1 upper case. "
	if alphabet < 1:
		message = message + "Password must contain at least 1 alphabetic character. "
	if special < 1:
		message = message + "Password must contain at least 1 special character."
	return False, message