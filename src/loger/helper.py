import os
import codecs


def text_to_file(text, path, rw='w', encoding='utf-8'):
	"""
	:param text:
	:param path:
	:param rw:
	:param encoding:
	:return:
	"""
	os.makedirs(os.path.dirname(path), exist_ok=True)
	with codecs.open(path, rw, encoding=encoding) as f:
		f.write(text)
	f.close()
