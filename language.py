import os
import re
import _pickle as pickle
from datetime import datetime, timedelta

import nltk
from pyhibp import pwnedpasswords as pw

from settings import ROOT_DIR, MODEL_DIR, TEMPLATE_DIR, MIN_PASS_LEN, EXCLUDED_WORDS


class ModelManager:
	"""
	Class in charge of making and deleting nltk language models.
	"""

	def __init__(self, library_name):
		self.library_name = library_name

	def save(self, model):
		print(f'Saving model {self.library_name} to {self.library_name}.pk.')

		with open(MODEL_DIR + self.library_name + '.pk', 'wb') as f:
			pickle.dump(model, f)
		
		print(f'Model {self.library_name} saved to {self.library_name}.pk.')		

	def make_model(self, source):
		"""
		LOADING WORDS
		"""

		# Source is local.
		if source == 'l':
			words = self.read_words_from_text(TEMPLATE_DIR + self.library_name + '.txt')
		
		# Source is remote.
		elif source == 'nltk':
			words = getattr(nltk.corpus, self.library_name)
			words = words.words()

		# Source not recognized.
		else:
			raise ValueError(f'Unknown source {source}')

		"""
		GENERATING AND SAVING THE MODEL
		"""
		textClass = nltk.Text(words)
		print('Tokenizing sentences')
		_tokenized_sents = [sent.split(" ") for sent in nltk.sent_tokenize(" ".join(textClass.tokens))] 
		print(f'Generating model for library {self.library_name}.')
		
		# Trigrams proved most convenient. Could implement option to modify from settings in the future.
		trigram_model = textClass._train_default_ngram_lm(_tokenized_sents, n=3)

		self.save(trigram_model)


	def delete(self):
		os.remove(os.path.join(MODEL_DIR, self.library_name + '.pk'))


class Language:
	"""
	Class in charge of generating sentences based on nltk models.
	"""

	def __init__(self, library=None, min_sentence_length=None, check_breached=True):
		self.library_name = library
		self.min_sentence_length = min_sentence_length or MIN_SENT_LENGTH
		self.check_breached = check_breached
		self.specials = list("""./,<>?\\';|":}{][=-+_)(*&^%$#@!~`""")

	@staticmethod
	def format_words(words):
		# Removing tabs, new lines and double spacings from string.
		return re.sub(r"\s+", " ", words)

	def read_words_from_text(self, text_file):
		with open(text_file, 'r') as f:
			return [word for word in self.format_words(f.read()).spli(' ') if word not in EXCLUDED_WORDS]

	@staticmethod
	def add_spice(sentence):
		pass

	def get_words(self, library_name=None):
		library_name = library_name or self.library_name

		local_file_name = TEMPLATE_DIR + library_name + '.txt'
		local_model_name = MODEL_DIR + library_name + '.pk'

		# Lookup if the library is in local templates.
		if local_file_name in os.listdir(TEMPLATE_DIR):
			# If a model does not exist, make one.
			if local_model_name not in os.listdir(MODEL_DIR):
				ModelManager(library_name).make_model('l')

			return self.read_words_from_text(local_file_name)

		# If no local template is provided, try nltk.
		try:
			# Try if nltk library was already downloaded.
			# If not, download and save a model.
			words = getattr(nltk.corpus, library_name)

		except AttributeError:
			ModelManager(library_name).make_model('nltk')
			words = getattr(nltk.corpus, library_name)

		return words.words()


	def form_sentece(self):
		print(f'Generating random text with length {length}.')
		
		today = datetime.now()
		sentence = [i for i in sent_generator.generate(length=self.min_sentence_length, 
			random_seed=int(today.second + today.minute)) if i not in specials]

		sentence = self.format_words(''.join([i for i in sentence if i != ' ']))

		if len(sentence) < MIN_PASS_LEN:
			sentence = self.make_sentece()

		if self.check_breached:
			if pw.is_password_breached(password=sentence) != 0:
				sentence = self.make_sentece()

		return sentence

	def gen_random(self, library_name=None, spice=False):
		library_name = library_name or self.library_name

		words = self.get_words(library_name)

		print('Instantiating generator.')
		self.sent_generator = nltk.Text(words)
		print(f'Loading model {library_name}.pk')
		with open(MODEL_DIR + library_name + '.pk', 'rb') as f:
			self.sent_generator._trigram_model = self.sent_generator.trigram_model = pickle.load(f)

		sentence = self.form_sentece()

		if spice:
			sentence = self.add_spice(sentence)

		return sentence


if __name__ == "__main__":
	pass