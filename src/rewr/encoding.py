import codecs


def get_file_bom_encodig(filename):
	"""
	:param filename:
	:return:
	"""
	with open(filename, 'rb') as openfileobject:
		line = str(openfileobject.readline())
		if line[2:14] == str(codecs.BOM_UTF8).split("'")[1]:
			return 'utf_8'
		if line[2:10] == str(codecs.BOM_UTF16_BE).split("'")[1]:
			return 'utf_16'
		if line[2:10] == str(codecs.BOM_UTF16_LE).split("'")[1]:
			return 'utf_16'
		if line[2:18] == str(codecs.BOM_UTF32_BE).split("'")[1]:
			return 'utf_32'
		if line[2:18] == str(codecs.BOM_UTF32_LE).split("'")[1]:
			return 'utf_32'
	return ''


def get_all_file_encoding(filename):
	"""
	:param filename:
	:return:
	"""
	encoding_list = []
	encodings = (
		'utf_8', 'utf_16', 'utf_16_le', 'utf_16_be',
		'utf_32', 'utf_32_be', 'utf_32_le',
		'cp850', 'cp437', 'cp852', 'cp1252', 'cp1250', 'ascii',
		'utf_8_sig', 'big5', 'big5hkscs', 'cp037', 'cp424', 'cp500',
		'cp720', 'cp737', 'cp775', 'cp855', 'cp856', 'cp857',
		'cp858', 'cp860', 'cp861', 'cp862', 'cp863', 'cp864',
		'cp865', 'cp866', 'cp869', 'cp874', 'cp875', 'cp932',
		'cp949', 'cp950', 'cp1006', 'cp1026', 'cp1140', 'cp1251',
		'cp1253', 'cp1254', 'cp1255', 'cp1256', 'cp1257',
		'cp1258', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213',
		'euc_kr', 'gb2312', 'gbk', 'gb18030', 'hz', 'iso2022_jp',
		'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_2004',
		'iso2022_jp_3', 'iso2022_jp_ext', 'iso2022_kr', 'latin_1',
		'iso8859_2', 'iso8859_3', 'iso8859_4', 'iso8859_5',
		'iso8859_6', 'iso8859_7', 'iso8859_8', 'iso8859_9',
		'iso8859_10', 'iso8859_13', 'iso8859_14', 'iso8859_15',
		'iso8859_16', 'johab', 'koi8_r', 'koi8_u', 'mac_cyrillic',
		'mac_greek', 'mac_iceland', 'mac_latin2', 'mac_roman',
		'mac_turkish', 'ptcp154', 'shift_jis', 'shift_jis_2004',
		'shift_jisx0213'
	)
	for e in encodings:
		try:
			fh = codecs.open(filename, 'r', encoding=e)
			fh.readlines()
		except Exception as _ex:
			pass
		else:
			encoding_list.append([e])
			fh.close()
			continue
	return encoding_list


def get_file_encoding(filename):
	"""
	:param filename:
	:return:
	"""
	file_encoding = get_file_bom_encodig(filename)
	if file_encoding != '':
		return file_encoding
	encoding_list = get_all_file_encoding(filename)
	file_encoding = str(encoding_list[0][0])
	if file_encoding[-3:] == '_be' or file_encoding[-3:] == '_le':
		file_encoding = file_encoding[:-3]
	return file_encoding


def get_codepage(text=None):
	"""
	Определение кодировки текста
	:param text:
	:return:
	"""
	encodings = {
		'UTF-8': 'utf-8',
		'CP1251': 'windows-1251',
		'KOI8-R': 'koi8-r',
		'IBM866': 'ibm866',
		'ISO-8859-5': 'iso-8859-5',
		'MAC': 'mac',
	}
	uppercase = 1
	lowercase = 3
	utfupper = 5
	utflower = 7
	codepages = {}
	for enc in encodings.keys():
		codepages[enc] = 0
	if text is not None and len(text) > 0:
		last_simb = 0
		for simb in text:
			simb_ord = ord(simb)
			
			"""non-russian characters"""
			if simb_ord < 128 or simb_ord > 256:
				continue
			
			"""UTF-8"""
			if last_simb == 208 and (143 < simb_ord < 176 or simb_ord == 129):
				codepages['UTF-8'] += (utfupper * 2)
			if (last_simb == 208 and (simb_ord == 145 or 175 < simb_ord < 192)) \
					or (last_simb == 209 and (127 < simb_ord < 144)):
				codepages['UTF-8'] += (utflower * 2)
			
			"""CP1251"""
			if 223 < simb_ord < 256 or simb_ord == 184:
				codepages['CP1251'] += lowercase
			if 191 < simb_ord < 224 or simb_ord == 168:
				codepages['CP1251'] += uppercase
			
			"""KOI8-R"""
			if 191 < simb_ord < 224 or simb_ord == 163:
				codepages['KOI8-R'] += lowercase
			if 222 < simb_ord < 256 or simb_ord == 179:
				codepages['KOI8-R'] += uppercase
			
			"""IBM866"""
			if 159 < simb_ord < 176 or 223 < simb_ord < 241:
				codepages['IBM866'] += lowercase
			if 127 < simb_ord < 160 or simb_ord == 241:
				codepages['IBM866'] += uppercase
			
			"""ISO-8859-5"""
			if 207 < simb_ord < 240 or simb_ord == 161:
				codepages['ISO-8859-5'] += lowercase
			if 175 < simb_ord < 208 or simb_ord == 241:
				codepages['ISO-8859-5'] += uppercase
			
			"""MAC"""
			if 221 < simb_ord < 255:
				codepages['MAC'] += lowercase
			if 127 < simb_ord < 160:
				codepages['MAC'] += uppercase
			
			last_simb = simb_ord
		
		idx = ''
		max_ = 0
		for item in codepages:
			if codepages[item] > max_:
				max_ = codepages[item]
				idx = item
		return idx
