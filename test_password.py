import unittest
import password
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
	Testing generate_password()
	"""
	def test_pass_has_touching_duplicates(self):
		self.assertFalse(self.has_touching_duplicates(self.pass1[0]))
		self.assertFalse(self.has_touching_duplicates(self.pass2[0]))
		self.assertFalse(self.has_touching_duplicates(self.pass3[0]))
		self.assertFalse(self.has_touching_duplicates(self.pass4[0]))

	def test_maintains_proportions(self):
		self.assertTrue(self.p1.confirm_proportions(self.p1.generate_new_dict(self.pass1[0])))
		self.assertTrue(self.p2.confirm_proportions(self.p2.generate_new_dict(self.pass2[0])))
		self.assertTrue(self.p3.confirm_proportions(self.p3.generate_new_dict(self.pass3[0])))
		self.assertTrue(self.p4.confirm_proportions(self.p4.generate_new_dict(self.pass4[0])))


	"""
	Testing remove_touching_duplicates()
	"""
	def test_remove_touching_duplicates(self):
		self.assertFalse(self.has_touching_duplicates(self.p1.remove_touching_duplicates('jjjsss444...')))
		self.assertFalse(self.has_touching_duplicates(self.p2.remove_touching_duplicates('3343+++CCC')))
		self.assertFalse(self.has_touching_duplicates(self.p3.remove_touching_duplicates('&&&HHH333bbboooo')))
		self.assertFalse(self.has_touching_duplicates(self.p4.remove_touching_duplicates('00006564554mmmmsss????QQQ')))

	"""
	Testing confirm_proportions()
	"""

	def test_confirm_proportions(self):
		self.assertFalse(self.p1.confirm_proportions(self.my_dict1))
		self.assertFalse(self.p2.confirm_proportions(self.my_dict2))
		self.assertTrue(self.p3.confirm_proportions(self.my_dict3))
		self.assertTrue(self.p4.confirm_proportions(self.my_dict4))


if __name__ == '__main__':
	unittest.main()