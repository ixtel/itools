import csv

import xlrd
import xlsxwriter

from ..config import log

xlrd.xlsx.ensure_elementtree_imported(False, None)
xlrd.xlsx.Element_has_iter = True


def dict_to_csv(dic, path):
	"""
	:param dic:
	:param path:
	:return:
	"""
	with open(path, 'w') as fileobj:
		w = csv.writer(fileobj)
		w.writerows(dic.items())


def group_to_xls(d, path, colls=None):
	"""
	# dict-list-dict
	:param d:
	:param path:
	:param colls:
	:return:
	"""
	path += '.xlsx'
	workbook = xlsxwriter.Workbook(path)
	worksheet = workbook.add_worksheet()
	row = 0
	col = 0
	if colls:
		for i, c in enumerate(colls):
			worksheet.write(row, col + i, c)
	for key in d.keys():
		row += 1
		worksheet.write(row, col, key)
		data = d[key]
		for item in data:
			if not isinstance(item, dict):
				worksheet.write(row, col + 1, item)
				row += 1
			elif isinstance(item, dict):
				for i, k in enumerate(item.keys()):
					worksheet.write(row, col + 1 + i, item[k])
				row += 1
			else:
				log(item)
	workbook.close()


def xlsx_read(path=None, file_contents=None, drophead=False, sheetnum=0):
	"""
	:param path:
	:param file_contents:
	:param drophead:
	:param sheetnum:
	:return:
	"""
	if file_contents:
		wb_rd = xlrd.open_workbook(file_contents=file_contents)
	else:
		wb_rd = xlrd.open_workbook(filename=path)
	sheet = wb_rd.sheets()[sheetnum]
	rows = list(sheet.get_rows())
	colls = []
	if drophead:
		colls = [str(r.value).lower() for r in rows[0]]
		rows = rows[1:]
	return rows, colls


def xlsx_write(data, path, head=None, sheet_name=None):
	"""
	:param data:
	:param path:
	:param head:
	:param sheet_name:
	:return:
	"""
	if head is not None:
		data = [head] + data
	width = max(map(len, data))
	workbook = xlsxwriter.Workbook(path)
	worksheet = workbook.add_worksheet(sheet_name)
	worksheet.write_column(0, 0, data)
	worksheet.set_column(0, 0, width)
	workbook.close()
	return True


def proxy_read(name=None, file_contents=None, drophead=False):
	"""
	:param name:
	:param file_contents:
	:param drophead:
	:return:
	"""
	rows, colls = xlsx_read(name, file_contents, drophead)
	result = []
	for r in rows:
		if drophead:
			_d = {}
			for _i, _c in enumerate(colls):
				try:
					_v = int(float(r[_i].value))
				except Exception as _ex:
					_v = r[_i].value
				_d[_c] = _v
			result.append(_d)
		else:
			try:
				pas = str(int(r[4].value))
			except Exception as _ex:
				pas = str(r[4].value)
			result.append({
				'typ': str(r[0].value),
				'ip': str(r[1].value),
				'port': int(float(r[2].value)),
				'login': str(r[3].value),
				'pas': pas,
			})
	return result


def keyword_read(name=None, file_contents=None, drophead=False):
	"""
	:param name:
	:param file_contents:
	:param drophead:
	:return:
	"""
	rows = xlsx_read(name, file_contents, drophead)[0]
	result = []
	for r in rows:
		key = str(r[0].value)
		if key:
			try:
				count = int(r[1].value)
			except Exception as _ex:
				count = 1
			result.append({
				'keyword': key,
				'count': count,
			})
	return result


def keyword_read_with_coll(name=None, file_contents=None, drophead=False):
	"""
	:param name:
	:param file_contents:
	:param drophead:
	:return:
	"""
	rows, colls = xlsx_read(name, file_contents, drophead)
	# print(colls)
	result = []
	for i, r in enumerate(rows):
		_r = {}
		for n, e in enumerate(colls):
			try:
				_r[e] = str(r[n].value)
			except Exception as _ex:
				pass
		if _r:
			result.append(_r)
	return result


def keyword_read_with_coll_for_df(name=None, file_contents=None, drophead=False):
	"""
	:param name:
	:param file_contents:
	:param drophead:
	:return:
	"""
	rows, colls = xlsx_read(name, file_contents, drophead)
	# print(colls)
	result = []
	for i, r in enumerate(rows):
		_r = [str(e.value) for e in r]
		result.append(_r)
	return result, colls


def keyword_read_list(name=None, file_contents=None, drophead=False):
	"""
	:param name:
	:param file_contents:
	:param drophead:
	:return:
	"""
	rows = xlsx_read(name, file_contents, drophead)[0]
	result = []
	for r in rows:
		key = str(r[0].value)
		result.append(key)
	return result
