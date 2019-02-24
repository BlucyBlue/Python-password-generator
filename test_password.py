import unittest
import itertools

from password import PyPass


class TestPassword(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		print('Setting up class')

	@classmethod
	def tearDownClass(cls):
		print('Tearing down class')

	def setUp(self):
		print('Setting up test')

		self.p1 = PyPass()
		self.p2 = PyPass()
		self.p3 = PyPass()
		self.p4 = PyPass()

		self.hmp1 = PyPass(excluded_chars=['6','g','+','K'])
		self.hmp2 = PyPass(excluded_chars=['8', 'v','1', '/', 'F'])
		self.hmp3 = PyPass(excluded_chars=['7', '3', ')'])
		self.hmp4 = PyPass(excluded_chars=['^', '7','e', 'K'])

		self.p1.generate_human_password()
		self.pass1 = self.p1.human_passwords[0]

		self.p2.generate_human_password()
		self.pass2 = self.p2.human_passwords[0]

		self.p3.generate_human_password()
		self.pass3 = self.p3.human_passwords[0]

		self.p4.generate_human_password()
		self.pass4 = self.p4.human_passwords[0]

		self.my_dict1 = {'0':1,'1':3,'2':0,'3':6}
		self.my_dict2 = {'0':0,'1':9,'2':5,'3':34536}
		self.my_dict3 = {'0':721,'1':6,'2':2,'3':14}
		self.my_dict4 = {'0':177,'1':8989,'2':10,'3':29}

	def tearDown(self):
		print('Dismantling test')

	"""
	Defining testing functions
	"""

	def has_touching_duplicates(self,test_str):
		for char in range(len(test_str[-1])):
			if test_str[char] == test_str[char+1]:
				return True
		return False

	"""
	Quick function for joining multiple lists into one.
	"""
	def join_l(self, lists_to_join):
		joined_list_elements = []
		for l in lists_to_join:
			joined_list_elements += l
		return joined_list_elements

	"""
	Testing generate_human_password()
	"""
	def test_pass_has_touching_duplicates(self):
		self.assertFalse(self.has_touching_duplicates(self.pass1))
		self.assertFalse(self.has_touching_duplicates(self.pass2))
		self.assertFalse(self.has_touching_duplicates(self.pass3))
		self.assertFalse(self.has_touching_duplicates(self.pass4))

	def test_maintains_proportions(self):
		self.assertTrue(self.p1.confirm_proportions(self.p1.generate_new_dict(self.pass1)))
		self.assertTrue(self.p2.confirm_proportions(self.p2.generate_new_dict(self.pass2)))
		self.assertTrue(self.p3.confirm_proportions(self.p3.generate_new_dict(self.pass3)))
		self.assertTrue(self.p4.confirm_proportions(self.p4.generate_new_dict(self.pass4)))


	"""
	Testing remove_touching_duplicates()
	"""
	def test_remove_touching_duplicates(self):
		self.assertFalse(self.has_touching_duplicates(self.p1.remove_touching_duplicates(['j','j','j','s','s','s',\
																						  4,4,4,'.','.','.',])))
		self.assertFalse(self.has_touching_duplicates(self.p2.remove_touching_duplicates([3,3,4,3,'+','+','+',\
																						  'C','C','C',])))
		self.assertFalse(self.has_touching_duplicates(self.p3.remove_touching_duplicates(['&','&','&','H','H','H',\
																				3,3,3,'b','b','b','o','o','o','o',])))
		self.assertFalse(self.has_touching_duplicates(self.p4.remove_touching_duplicates([0,0,0,0,6,5,6,4,5,5,4,'m',\
																'm','m','m','s','s','s','?','?','?','?','Q','Q','Q',])))

	"""
	Testing confirm_proportions()
	"""

	def test_confirm_proportions(self):
		self.assertFalse(self.p1.confirm_proportions(self.my_dict1))
		self.assertFalse(self.p2.confirm_proportions(self.my_dict2))
		self.assertTrue(self.p3.confirm_proportions(self.my_dict3))
		self.assertTrue(self.p4.confirm_proportions(self.my_dict4))

	"""
	Testing removal of excluded_characters from usable_chars lists.
	"""

	def test_confirm_excluded_removal(self):
		self.assertFalse(self.hmp1.excluded_chars in self.join_l(self.hmp1.usable_chars))
		self.assertFalse(self.hmp2.excluded_chars in self.join_l(self.hmp2.usable_chars))
		self.assertFalse(self.hmp3.excluded_chars in self.join_l(self.hmp3.usable_chars))
		self.assertFalse(self.hmp4.excluded_chars in self.join_l(self.hmp4.usable_chars))




if __name__ == '__main__':
	unittest.main()