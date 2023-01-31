import codecs
import mmap
import os


def read_big(path, rw='rb', encoding='utf-8', buf_size=1024):
	"""
	:param path:
	:param rw:
	:param encoding:
	:param buf_size:
	:return:
	"""
	with codecs.open(path, rw, encoding=encoding, buffering=buf_size) as fHandle:
		data = mmap.mmap(fHandle.fileno(), os.path.getsize(path), access=mmap.ACCESS_READ)
		while True:
			line = data.readline()
			if not line:
				break
			yield line


def read_big_cache(path, rw='rb', encoding='utf-8', buf_size=1024, cache_size=10 ** 6):
	"""
	:param path:
	:param rw:
	:param encoding:
	:param buf_size:
	:param cache_size:
	:return:
	"""
	data = read_big(path, rw=rw, encoding=encoding, buf_size=buf_size)
	_cache = dict()
	_cache_size = 0
	for line in data:
		_cache[line] = 0
		_cache_size += 1
		if _cache_size >= cache_size:
			for _line in _cache.keys():
				yield _line
			_cache = dict()
			_cache_size = 0
	for _line in _cache:
		yield _line
	_cache = dict()
	_cache_size = 0


def read_big_buf(path, rw='rb', encoding=None, buf_size=1024):
	"""
	:param path:
	:param rw:
	:param encoding:
	:param buf_size:
	:return:
	"""
	with open(path, mode=rw, encoding=encoding, buffering=buf_size) as f:
		read_f = f.read
		while True:
			yield read_f(buf_size)


def write_big(items, path, rw='w+', ext='txt', encoding='utf-8'):
	"""
	:param items:
	:param path:
	:param rw:
	:param ext:
	:param encoding:
	:return:
	"""
	if not path.endswith('.' + ext):
		path += ".%s" % ext
	os.makedirs(os.path.dirname(path), exist_ok=True)
	new_line = '\n'
	if rw.find('b') != -1:
		new_line = b'\n'
		encoding = None
	elif encoding is None:
		rw += 'b'
		new_line = b'\n'
	with codecs.open(path, rw, encoding=encoding) as fHandle:
		for line in items:
			if not line:
				break
			fHandle.write(line + new_line)


def read_big_reverse(path, rw='rb'):
	"""
	:param path:
	:param rw:
	:return:
	"""
	with open(path, rw) as read_obj:
		# Move the cursor to the end of the file
		read_obj.seek(0, os.SEEK_END)
		# Get the current position of pointer i.e eof
		pointer_location = read_obj.tell()
		# Create a buffer to keep the last read line
		buffer = bytearray()
		# Loop till pointer reaches the top of the file
		while pointer_location >= 0:
			# Move the file pointer to the location pointed by pointer_location
			read_obj.seek(pointer_location)
			# Shift pointer location by -1
			pointer_location = pointer_location - 1
			# read that byte / character
			new_byte = read_obj.read(1)
			# If the read byte is new line character then it means one line is read
			if new_byte == b'\n':
				# Fetch the line from buffer and yield it
				yield buffer.decode()[::-1]
				# Reinitialize the byte array to save next line
				buffer = bytearray()
			else:
				# If last read character is not eol then add it in buffer
				buffer.extend(new_byte)
		
		# As file is read completely, if there is still data in buffer, then its the first line.
		if len(buffer) > 0:
			# Yield the first line too
			yield buffer.decode()[::-1]


def read_lines_from_file_as_data_chunks(file_name, chunk_size, callback, return_whole_chunk=False):
	"""
	read file line by line regardless of its size
	:param file_name: absolute path of file to read
	:param chunk_size: size of data to be read at at time
	:param callback: callback method, prototype ----> def callback(data, eof, file_name)
	:param return_whole_chunk: вернуть кусок в callback без обработки
	:return:
	"""
	
	def read_in_chunks(file_obj, _chunk_size=5000):
		"""
		https://stackoverflow.com/a/519653/5130720
		Lazy function to read a file
		Default chunk size: 5000.
		"""
		while True:
			data = file_obj.read(_chunk_size)
			if not data:
				break
			yield data
	
	fp = open(file_name)
	data_left_over = None
	
	# loop through characters
	for chunk in read_in_chunks(fp, chunk_size):
		
		# if uncompleted data exists
		if data_left_over:
			# print('\n left over found')
			current_chunk = data_left_over + chunk
		else:
			current_chunk = chunk
		
		# split chunk by new line
		lines = current_chunk.splitlines()
		
		# check if line is complete
		if current_chunk.endswith('\n'):
			data_left_over = None
		
		else:
			data_left_over = lines.pop()
		
		if return_whole_chunk:
			callback(data=lines, eof=False, file_name=file_name)
		
		else:
			
			for line in lines:
				callback(data=line, eof=False, file_name=file_name)
				pass
	
	if data_left_over:
		
		current_chunk = data_left_over
		if current_chunk is not None:
			
			lines = current_chunk.splitlines()
			
			if return_whole_chunk:
				callback(data=lines, eof=False, file_name=file_name)
			
			else:
				for line in lines:
					callback(data=line, eof=False, file_name=file_name)
					pass
	
	callback(data=None, eof=True, file_name=file_name)
