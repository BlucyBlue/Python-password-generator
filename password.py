import secrets
import string
import re

from nltk.corpus import wordnet
from pyhibp import pwnedpasswords as pw

from settings import EXCLUDED_WORDS, USABLE_CHARS, EXCLUDED_CHARS, MAX_PASS_LEN, MIN_PASS_LEN, FIXED_LEN, PSWRD_NO


"""
Class used for storing and generating passwords.

One or more passwords are generated with self.generate_password() [stored in the self.passwords] 
or self.generate_human_password() [stored in the self.human_passwords].
"""
class PyPass:

	def __init__(self, usable_chars=USABLE_CHARS, excluded_chars=EXCLUDED_CHARS, min_pass_len=MIN_PASS_LEN,
				 max_pass_len=MAX_PASS_LEN, excluded_words=EXCLUDED_WORDS, remove_repeating=False,
				 remove_english=False, ensure_proportions=False):

		self.excluded_chars = excluded_chars

		"""
		Usable chars are checked against the excluded characters, and any matching chars are removed before
		initializing usable_chars property.
		"""

		for excl_char in excluded_chars:
			for usable_char_list in usable_chars:
				if excl_char in usable_char_list:
					usable_char_list.remove(excl_char)

		self.usable_chars = usable_chars
		self.excluded_words = excluded_words

		# Setting the minimum and maximum length of the generated passwords.
		self.min_pass_len = min_pass_len
		self.max_pass_len = max_pass_len

		# Passwords generated with self.generate_human_password will be stored here
		self.human_passwords = []
		# Passwords generated with self.generate_password will be stored here
		self.passwords = []


	def __str__(self):
		return ' '.join(self.all_passwords)

	# Returns combined "human" and "random" passwords.
	@property
	def all_passwords(self):
		return self.passwords + self.human_passwords


	# Generates a random string of chars from types available in usable_chars
	def generate_random(self, pass_length):
		return ''.join([secrets.choice(secrets.choice(self.usable_chars)) for i in range(pass_length)])



	# This function removes two same characters which are placed one after the other,
	# replacing them with random char from a randomly chosen usable_char list.
	def remove_touching_duplicates(self, my_string):
		new_string = ''
		# The -1 range was chosen to avoid index out of range error.
		for char in range(len(my_string[:-1])):
			if my_string[char] == my_string[char+1]:
				new_string += secrets.choice(secrets.choice(self.usable_chars))
			else:
				new_string += my_string[char]

		new_string += my_string[-1]

		return(new_string)


	# Checks if a string contains any of the words or other char sequences marked as excluded in 'excluded.py'.
	@staticmethod
	def contains_excluded(my_string):
		for word in excluded_words:
			if word in my_string:
				return True
		return False


	# Finds sequences of letters in the password string.
	#
	# Once found, it checks if the letter sequence corresponds to an English word, or is an excluded word.
	#
	# If such sequences are found, they are replaced with a random set of characters.
	def find_letter_sequences(self, my_string):
		pass_string = my_string
		pattern = re.compile('[a-zA-Z]+')

		# Replaces English words with new random strings.
		#
		# The process is repeated if the newly generated random string, is also an English word.
		finds = 1

		while finds == 1:
			matches = pattern.findall(pass_string)
			if len(matches) > 0:
				for m in matches:
					if wordnet.synsets(m.lower() or self.contains_excluded(m)) and len(m) > 3:
						pass_string = pass_string.replace(m, self.remove_touching_duplicates(self.generate_random(len(m))))
						finds = 1

					else:
						finds = 0
			else:
				finds = 0

		return pass_string


	# Examines if there is at least one character from each usable_chars list.
	#
	# Returns True if the proportion is fulfilled, and False if not.
	@staticmethod
	def confirm_proportions(list_dict):
		for key in list_dict.keys():
			if list_dict[key] < 1:
				return False

		return True


	# Generates a new dictionary reflecting the number of each char type from usable_chars in the password string.
	def generate_new_dict(self, string_members):

		string_proportions = {
					'0':0,
					'1':0,
					'2':0,
					'3':0,
					}

		for char in string_members:
			if char in self.usable_chars[0]:
				string_proportions['0'] += 1
			elif char in self.usable_chars[1]:
				string_proportions['1'] += 1
			elif char in self.usable_chars[2]:
				string_proportions['2'] += 1
			else:
				string_proportions['3'] += 1

		return string_proportions


	# Checks if there is at least one of each types of usable_chars in the password string using the confirm_proportions().
	#
	# If the proportion is not fulfilled, it replaces a random character in the password string, with a randomly chosen
	# char from the missing usable_chars type.
	#
	# It continues this check until the confirm_proportions() returns True.
	def ensure_proportions(self, my_string):
		string_members = list(my_string)

		string_proportions = self.generate_new_dict(string_members)

		while self.confirm_proportions(string_proportions) == False:
			for item in string_proportions.keys():

				if string_proportions[item] < 1:
					index = secrets.choice(list(range(len(string_members))))
					string_members[index] = secrets.choice(self.usable_chars[int(item)])

				string_proportions = self.generate_new_dict(string_members)

		return ''.join(string_members)

		"""
	The function will generate a password conforming to most common rules recommended for passwords generation. 
	The idea is to generate passwords which are resistant to breaking attempts where the malicious actor presumes 
	that the password wa generated by a person and not a randomizing program.
	
	Therefore, it should be noted that, because the function implements the rules listed below, the number of possible
	combinations this function generates is lower that a more pure randomization function (see generate_password()). 
	So, once again, using this function is recommended only if the user wishes to protect themselves particularly from 
	cracking attempts modified to presume a person generated a password.
		
	Implements other functions in order to generate a random string containing:
		1) characters are only lower and upper case ascii letters, numbers or punctuation signs;
		2) at least one of each char type from item 1) is contained withing the password string;
		3) there are no sequences of same chars in the password string;
		4) no char sequence is either an English word, nor does it belong to the list of sensitive words defined by user;
		5) after implementing rules 1)-4), the password is checked against database from 
			'https://haveibeenpwned.com/Passwords', to ensure its not contained in the database of passwords previously 
			exposed in data breaches.
	
	Argument 'pass_number' designates how many passwords are to be created. If left blank, will generate one password.
	
	Argument 'fixed_len' will designate a fixed length of the generated password.
	
	Generated passwords are appended to self.human_passwords
	
	"""

	def generate_human_password(self, pass_number=PSWRD_NO, fixed_len=FIXED_LEN):

		# Prevents setting password number below 1.
		if pass_number < 1:
			pass_number = 1

		for number in range(pass_number):

			if fixed_len:
				pass_string_list = self.generate_random(fixed_len)

			else:
				pass_len_range = list(range(self.min_pass_len,self.max_pass_len+1))
				pass_string_list = self.generate_random(secrets.choice(pass_len_range))


			# Removing touching duplicate chars.
			my_pass = self.find_letter_sequences(self.remove_touching_duplicates(pass_string_list))

			# Ensuring at least one member of each type from usable_chars is contained in the password string.
			my_pass = self.ensure_proportions(my_pass)

			my_pass = ''.join(my_pass)

			# Checking if the generated password was exposed in data breaches. If so, the process is repeated.
			if pw.is_password_breached(password=my_pass) != 0:
				self.generate_password()

			self.human_passwords.append(my_pass)

    """
	The function will generate a password string from the set of usable characters described by the user in settings.py.

	Argument 'pass_number' designates how many passwords are to be created. If left blank, will generate one password.
	
	Argument 'remove_repeating' designates if consecutive duplicate chars will be removed from the password. 
	If left blank, duplicates will not be removed.
	
	Argument 'remove_english' designates if English words will be removed from the password. If left blank, 
	English words will not be removed.
	
	Argument 'ensure_proportions' designates if the password will contain at least one char form each list 
	in usable_chars. If left blank, these proportions will not be enforced.
		
	Argument 'fixed_len' will designate a fixed length of the generated password.

	Generated passwords are appended to self.human_passwords
	"""
	def generate_password(self, pass_number=PSWRD_NO, remove_repeating=False, remove_english=False, check_proportions=False,
					  fixed_len=FIXED_LEN):

	# Prevents setting password number below 1.
	if pass_number<1:
		pass_number = 1

	for number in range(pass_number):
		if fixed_len:
			pass_string_list = self.generate_random(fixed_len)

		else:
			pass_len_range = list(range(self.min_pass_len,self.max_pass_len+1))
			pass_string_list = self.generate_random(secrets.choice(pass_len_range))

		# Removing touching duplicate chars, in case the user chose so.
		if remove_repeating:
			pass_string_list = self.remove_touching_duplicates(pass_string_list)

		# Removing English words and excluded words, if the user chose so.
		if remove_english:
			pass_string_list = self.remove_english(pass_string_list,remove_repeating)

		# Removing excluded words, if they are designated by the user.
		if len(self.excluded_words) > 0:
			pass_string_list = self.remove_excluded(pass_string_list, remove_repeating)

		# If the user chose so, ensuring at least one member of each group of characters
		# from the usable characters lists has been included.
		if check_proportions:
			pass_string_list = self.ensure_proportions(pass_string_list)

		my_pass = ''.join(pass_string_list)

		if pw.is_password_breached(password=my_pass) != 0:
			self.generate_password(pass_number=pass_number, remove_repeating=remove_repeating,
								   remove_english=remove_english, ensure_proportions=check_proportions)

		self.passwords.append(my_pass)
