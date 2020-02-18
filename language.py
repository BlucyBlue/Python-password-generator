import os
import re
import _pickle as pickle
from datetime import datetime, timedelta

import nltk
from pyhibp import pwnedpasswords as pw

from settings import ROOT_DIR, MODEL_DIR, TEMPLATE_DIR, MIN_PASS_LEN, EXCLUDED_WORDS, MAX_PASS_LEN


class ModelManager:
	"""
	Class in charge of making and deleting custom and already available nltk language models.
	"""

	def __init__(self, library_name):
		"""
		Args:
			library_name (str): Name of the library to be used by the manager. This will determine 
								the name of the template and model files the ModelManager will look for.	
		"""
		self.library_name = library_name

	def save(self, model):
		"""
		Saves nltk trigram model to a pickle file.

		Args:
			model (nltk.lm.MLE instance): trigram model to be saved.
		"""
		print(f'Saving model {self.library_name} to {self.library_name}.pk.')

		with open(f"{MODEL_DIR}/{self.library_name}.pk", 'wb') as f:
			pickle.dump(model, f)
		
		print(f'Model {self.library_name} saved to {self.library_name}.pk.')		

	def make_model(self, source):
		"""
		Generates an nltk trigram model based on a custom text file or already available nltk array of words.

		Args:
			source (str): Determines if the ModelManager will look for a local text file of an nltk resource.
		"""

		# Source is considered to be a local text file.
		if source == 'l':
			words = self.read_words_from_text(f'{TEMPLATE_DIR}/{self.library_name}.txt')
		
		# Source is considered to be an nltk resource.
		elif source == 'nltk':
			words = getattr(nltk.corpus, self.library_name)
			words = words.words()

		# Source not recognized.
		else:
			raise ValueError(f'Unknown source {source}')

		# We will be using the nltk.Text class to generate the trigram model, as it already comes with a method to do this.
		textClass = nltk.Text(words)

		print('Tokenizing sentences')
		# Tokenizing sentences means the frequency and relevance of words in a sentence are being determined and recorded.
		_tokenized_sents = [sent.split(" ") for sent in nltk.sent_tokenize(" ".join(textClass.tokens))] 
		
		print(f'Generating model for library {self.library_name}.')
		# Trigrams proved most convenient. Could implement option to modify from settings in the future.
		trigram_model = textClass._train_default_ngram_lm(_tokenized_sents, n=3)

		self.save(trigram_model)


	def delete(self):
		"""
		Already existing pickle file will be deteleted.
		"""
		os.remove(os.path.join(MODEL_DIR, self.library_name + '.pk'))

	@staticmethod
	def read_words_from_text(path_to_file):
		"""
		Convenience method for transfering contents of a file to a single string.

		Args:
			path_to_file (str): path to the file to be read.
		"""
		text = str()
		with open(path_to_file, 'r') as f:
			text = f.read()

		return text


class Language:
	"""
	Class in charge of generating sentences based on nltk models.
	"""

	def __init__(self, library=None, min_sentence_length=None, max_sentence_length=None, check_breached=True, include_whitespace=True):
		"""
		Args:
			library (str): Name of the library to be used for generating sentences.
			min_sentence_length (int): Minimal length of the sentece to be generated.
			max_sentence_length (int): Maximum length of the sentece to be generated.
			check_breached (bool): Determines if the genreated sentences will be checked against breached passwords database.
			include_whitespace (bool): Determines if white spaces will be removed from the generated sentences.
		"""
		self.library_name = library
		self.min_sentence_length = min_sentence_length or MIN_SENT_LENGTH
		self.max_sentence_length = max_sentence_length or MAX_PASS_LEN
		self.check_breached = check_breached
		self.specials = list("""./,<>?\\';|":}{][=-+_)(*&^%$#@!~`""")
		self.include_whitespace = include_whitespace

	@staticmethod
	def format_words(words):
		"""
		Removing tabs, new lines and double spacings from string.

		Args:
			words (str): String to be formatted.
		"""
		return re.sub(r"\s+", " ", words)

	def read_words_from_text(self, text_file):
		"""
		Convenience method for transfering contents of a file to a single string. Will remove 
		words listed in the EXCLUDED_WORDS variable of settings.py

		Args:
			text_file (str): path to the file to be read.
		"""
		with open(text_file, 'r') as f:
			return [word for word in self.format_words(f.read()).split(' ') if word not in EXCLUDED_WORDS]

	def get_words(self, library_name=None):
		"""
		Extracts words from nltk resources or custom text files.

		Args:
			library (str): Name of the nltk resources or custom text file to be used.
		"""
		library_name = library_name or self.library_name

		local_file_name = library_name + '.txt'
		local_model_name = f"{MODEL_DIR}/{self.library_name}.pk"

		# If the library is in local templates, proceed with extracting from text file.
		if local_file_name in os.listdir(TEMPLATE_DIR):
			# If a model does not exist, make one.
			if local_model_name not in os.listdir(MODEL_DIR):
				ModelManager(library_name).make_model('l')

			return self.read_words_from_text(os.path.join(TEMPLATE_DIR, local_file_name))

		# If no local template is provided, try locating an nltk resource.
		try:
			# Try if nltk library was already downloaded.
			# If not, download and save a model.
			words = getattr(nltk.corpus, library_name)

		except AttributeError:
			ModelManager(library_name).make_model('nltk')
			words = getattr(nltk.corpus, library_name)

		return words.words()

	def get_trigram(self, library_name=None):
		"""
		Loads already existing trigram model.

		Args:
			library (str): Name of model, used to locate the pickle file in the MODEL_DIR.
		"""
		library_name = library_name or self.library_name
		local_model_name = f"{MODEL_DIR}/{self.library_name}.pk"

		pickle_file = None

		with open(os.path.join(MODEL_DIR, local_model_name), 'rb') as f:
			pickle_file = pickle.load(f)
		return pickle_file

	def form_sentece(self):
		"""
		Method for generating random sentences, taking into account params of this class instance.
		"""
		print(f'Generating random text with length {self.min_sentence_length}.')
		
		today = datetime.now()
		self.sent_generator = nltk.Text(self.get_words())
		# Existing model is loaded instead of making a new one each time a sentence is generated.
		self.sent_generator._trigram_model = self.get_trigram()

		sentence = self.sent_generator.generate(length=self.min_sentence_length, random_seed=int(today.second + today.minute))
		
		# Removes special characters from the sentence.
		sentence = self.format_words(''.join([i for i in sentence if i not in self.specials]))
		if not self.include_whitespace:
			sentence = "".join([i for i in sentence if i != " "])

		my_pass_len = len(sentence)

		# Logic for enforcing min and max length sentence requirements.
		if my_pass_len < self.min_sentence_length:
			sentence = self.form_sentece()
		elif my_pass_len > self.max_sentence_length:
			sentence = sentence[:self.max_sentence_length]
			# Making sure that the last characther is not a whitespace, which would could make it difficult to see when copying.
			if sentence[-1] == " ":
				sentence = sentence[:-1]

		if self.check_breached:
			if pw.is_password_breached(password=sentence) != 0:
				sentence = self.form_sentece()

		return sentence

	def gen_random(self, library_name=None):
		"""
		Method for generating random sentences from a designated library, without taking into account (other) params of this class instance.

		Args:
			library (str): Name of model, used to locate the pickle file in the MODEL_DIR.
		"""
		library_name = library_name or self.library_name

		words = self.get_words(library_name)

		print('Instantiating generator.')
		self.sent_generator = nltk.Text(words)
		print(f'Loading model {library_name}.pk')
		# Existing model is loaded instead of making a new one each time a sentence is generated.
		with open(MODEL_DIR + library_name + '.pk', 'rb') as f:
			self.sent_generator._trigram_model = self.sent_generator.trigram_model = pickle.load(f)

		sentence = self.form_sentece()

		return sentence


if __name__ == "__main__":
	pass