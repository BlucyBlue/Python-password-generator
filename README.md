# Python-password-generator

A module designed to generate passwords in form of a random string containing:

1) between 20 and 32 characters;
	
2) characters are only lower and upper case ascii letters, numbers or punctuation signs;
	
3) at least one of each char type from item 2) is contained withing the password string;
	
4) there are no sequences of same chars in the password string;
	
5) no char sequence is either an English word, nor does it belong to the list of sensitive words defined by user;
	
6) after implementing rules 1)-5), the password is checked against database from 'https://haveibeenpwned.com/Passwords',
 to ensure its not contained in the database of passwords previously exposed in data breaches.

Usage:
1) in scripts:
  from password import PyPass
  password_generator = PyPass()
  password_generator.generate_password([optional: number of passwords])  
  passwords = password_generator.passwords

2) from terminal (will create one PyPass instance with one password and print the resulting password):
  python3 password.py

Tests in test_password.py

Important: In case of issues with running nltk.core.wordnet, consult: 'http://www.velvetcache.org/2010/03/01/looking-up-words-in-a-dictionary-using-python'

