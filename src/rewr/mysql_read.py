import csv
import os

from collections import defaultdict

import ipywidgets as widgets
from IPython.display import display

from .tools import Json

csv.field_size_limit(100000)


def ipython_display(*args, **kwargs):
	display(*args, **kwargs)


class Reader:
	def __init__(self, input_file, strict=False, parser_native=True):
		"""
		:param input_file:
		:param strict:
		:param parser_native:
		"""
		self.input_file = input_file
		self.strict = strict
		self.input_dir = os.path.dirname(os.path.abspath(input_file))
		
		self.tables = defaultdict(list)
		
		if parser_native:
			self._parse_values = self._parse_values_native
		else:
			self._parse_values = self._parse_values_csv
		
		pass
	
	@staticmethod
	def _line_to_values(
			line: str,
			delimiter: str = ',',
			quotechar: str = "'",
	):
		"""
		:param line:
		:param delimiter:
		:param quotechar:
		:return:
		"""
		line = line.strip(' ')
		values = []
		while True:
			_delimiter = str(delimiter)
			line = line.strip(' ')
			if not line:
				break
			if line.startswith(quotechar):
				_delimiter = f'{quotechar}{delimiter}'
				line = line[1:]
				_to = line.find(_delimiter)
				if _to > -1:
					value = line[:_to]
					line = line[_to:]
					line = line[len(_delimiter):]
				else:
					value = line.strip(_delimiter)
					line = ''
			else:
				_to = line.find(_delimiter)
				if _to > -1:
					value = line[:_to]
					line = line[_to:]
					line = line[len(_delimiter):]
				else:
					value = line
					line = ''
			
			values.append(fr'{value}')
		return values
	
	@staticmethod
	def _is_insert(line):
		"""
		Returns true if the line begins a SQL insert statement.
		:param line:
		:return:
		"""
		return (line.startswith('INSERT INTO') and not line.endswith('VALUES')) or False
	
	@staticmethod
	def _is_insert_multiline(line):
		"""
		Returns true if the line begins a SQL insert statement.
		:param line:
		:return:
		"""
		return (line.startswith('INSERT INTO') and line.endswith('VALUES')) or False
	
	@staticmethod
	def _is_create(line):
		"""
		Returns true if the line begins a SQL insert statement.
		:param line:
		:return:
		"""
		return line.startswith('CREATE TABLE') or False
	
	@staticmethod
	def _get_values(line):
		"""
		Returns the portion of an INSERT statement containing values
		:param line:
		:return:
		"""
		return line.partition('` VALUES ')[2]
	
	@staticmethod
	def _get_name(line):
		"""
		Return the name of the tables
		:param line:
		:return:
		"""
		dummy = line.partition('`')[2]
		return dummy.partition('`')[0]
	
	@staticmethod
	def _get_headers(header_lines):
		"""
		Return the header of the tables
		:param header_lines:
		:return:
		"""
		headers = []
		for headerline in header_lines:
			dummy = headerline.partition('`')[2]
			headers.append(dummy.partition('`')[0])
		return headers
	
	@staticmethod
	def _values_sanity_check(values):
		"""
		Ensures that values from the INSERT statement meet basic checks.
		:param values:
		:return:
		"""
		return values and values[0] == '('
	
	@staticmethod
	def columns_to_row(columns):
		"""
		:param columns:
		:return:
		"""
		row = []
		for column in columns:
			if len(column) == 0 or column == 'NULL' or column == 'null' or column == ' ':
				row.append('')
				continue
			row.append(column)
		return row
	
	# @staticmethod
	def _parse_values_native(self, values):
		"""
		:param values:
		:return:
		"""
		columns = self._line_to_values(
			values.strip('\t();,'),
			delimiter=',',
			quotechar="'",
		)
		return self.columns_to_row(columns)
	
	def _parse_values_csv(self, values):
		"""
		:param values:
		:return:
		"""
		reader = csv.reader(
			[values.strip('\t();,')],
			delimiter=',',
			doublequote=False,
			escapechar='\\',
			quotechar="'",
			strict=self.strict
		)
		
		return self.columns_to_row(next(reader))
	
	def parse(self):
		"""
		# Initialize an array to store the header_lines
		:return:
		"""
		header_lines = []
		
		get_headers_lines = False
		
		infile = open(self.input_file, 'r', encoding='utf-8')
		header_name = None
		multi_insert = False
		table_name = None
		for line in infile:
			# Check if lines have to be collected for extraction of the headers
			if get_headers_lines:
				if line.startswith('  `'):
					header_lines.append(line)
				else:
					headers = self._get_headers(header_lines)
					self.tables[header_name].append(headers)
					header_lines = []
					get_headers_lines = False
			# Look for a CREATE statement and parse it for the headers
			if self._is_create(line):
				header_name = self._get_name(line)
				get_headers_lines = True
				multi_insert = False
			
			clean_line = line.strip('\n\t\r ')
			# Look for an INSERT statement and parse it.
			
			if multi_insert:
				values = clean_line
				row = None
				if self._values_sanity_check(values):
					row = self._parse_values(values)
					self.tables[table_name].append(row)
				if not row:
					multi_insert = False
					table_name = None
			elif self._is_insert(line):
				table_name = self._get_name(clean_line)
				values = self._get_values(clean_line)
				if self._values_sanity_check(values):
					row = self._parse_values(values)
					self.tables[table_name].append(row)
			else:
				pass
			
			if multi_insert is False:
				multi_insert = self._is_insert_multiline(clean_line)
				table_name = self._get_name(line)
		
		return self


class Saver:
	def __init__(self, output_dir, tables, saver='json'):
		"""
		Save mysql dump parsed tables
		:param tables: dict of tables
		:param saver: json or csv
		"""
		self.output_dir = output_dir
		os.makedirs(self.output_dir, exist_ok=True)
		self.tables = tables
		self.tables_names = list(tables.keys())
		self.tables_total = len(tables)
		self.tables_done = 0
		self.row_index = 0
		if saver == 'json':
			self._write_values = self._write_values_json
			self._result_prepare = self._result_prepare_json
		else:
			self._write_values = self._write_values_csv
			self._result_prepare = self._result_prepare_csv
	
	def _write_values_csv(self, table_name, rows):
		"""
		:param table_name:
		:param rows:
		:return:
		"""
		if len(rows) > 1:
			outfile = open(f'{self.output_dir}/{table_name}.csv', mode='w', encoding='utf-8', newline='')
			writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
			writer.writerows(rows)
		return
	
	def _write_values_json(self, table_name, rows):
		"""
		:param table_name:
		:param rows:
		:return:
		"""
		if len(rows) > 0:
			Json(f'{self.output_dir}/{table_name}.json').write(rows)
		return
	
	def write(self):
		"""
		:return:
		"""
		for _table_name, _rows in self.tables.items():
			print(_table_name, len(_rows) - 1)
			self._write_values(table_name=_table_name, rows=_rows)
		return self
	
	@staticmethod
	def _result_prepare_csv(header, header_result, enabled, table):
		"""
		:param header:
		:param header_result:
		:param enabled:
		:param table:
		:return:
		"""
		result_table = [header_result]
		for _row in table:
			result_row = []
			for i, _col in enumerate(header):
				if enabled[i]:
					result_row.append(_row[i])
			result_table.append(result_row)
		return result_table
	
	@staticmethod
	def _result_prepare_json(header, _header_result, enabled, table):
		"""
		:param header:
		:param _header_result:
		:param enabled:
		:param table:
		:return:
		"""
		result_table = []
		for _row in table:
			result_row = {}
			for i, _col in enumerate(header):
				if enabled[i]:
					result_row[_col] = _row[i]
			result_table.append(result_row)
		return result_table
	
	def _save_table(self, header_widgets, column_enabled):
		"""
		:param header_widgets:
		:param column_enabled:
		:return:
		"""
		table_name = self.tables_names[self.tables_done]
		table = self.tables[table_name]
		_enabled = []
		_header = []
		_header_result = []
		enable = False
		for i, column in enumerate(header_widgets):
			_enable = column_enabled[i].value
			_enabled.append(_enable)
			_header.append(column.value)
			if _enable:
				enable = True
				_header_result.append(column.value)
		if enable is False:
			return
		
		result_table = self._result_prepare(_header, _header_result, _enabled, table)
		self._write_values(table_name, result_table)
		return table_name, result_table
	
	def _next_table(self, orient, row_widgets):
		"""
		:param orient:
		:param row_widgets:
		:return:
		"""
		for _box in row_widgets:
			_box.close()
		self.tables_done += orient
		return self.next_table()
	
	def _next_values(self, orient, table, label_widgets):
		"""
		:param orient:
		:param table:
		:param label_widgets:
		:return:
		"""
		self.row_index += orient
		for i, label in enumerate(label_widgets):
			try:
				label.value = table[self.row_index][i]
			except Exception as _ex:
				pass
	
	def next_table(self, *_args, **__kwargs):
		"""
		:param _args:
		:param __kwargs:
		:return:
		"""
		if self.tables_done == self.tables_total:
			print('all tables_done')
			return
		table_name = self.tables_names[self.tables_done]
		table = self.tables[table_name]
		
		_columns = table.pop(0)
		_header_widgets = []
		_column_widgets = []
		_label_widgets = []
		_row_widgets = []
		self.row_index = 0
		
		_label_table = widgets.Label(value=f'{table_name}, {len(table)}')
		ipython_display(_label_table)
		_row_widgets.append(_label_table)
		
		if not table:
			return self._next_table(+1, _row_widgets)
		
		_save_next_table_button = widgets.Button(
			description='Save & Next Table',
			disabled=False,
			button_style='',
			tooltip='Click me',
			icon='check'
		)
		_prev_table_button = widgets.Button(
			description='Prev Table',
			disabled=False,
			button_style='',
			tooltip='Click me',
			icon='check'
		)
		_next_table_button = widgets.Button(
			description='Next Table',
			disabled=False,
			button_style='',
			tooltip='Click me',
			icon='check'
		)
		_save_table_button = widgets.Button(
			description='Save Table',
			disabled=False,
			button_style='',
			tooltip='Click me',
			icon='check'
		)
		_prev_values_button = widgets.Button(
			description='Prev Values',
			disabled=False,
			button_style='',
			tooltip='Click me',
			icon='check'
		)
		_next_values_button = widgets.Button(
			description='Next Values',
			disabled=False,
			button_style='',
			tooltip='Click me',
			icon='check'
		)
		_box_button = widgets.GridBox(
			[
				_save_next_table_button,
				_next_table_button,
				_prev_table_button,
				_save_table_button,
				_prev_values_button,
				_next_values_button,
			],
			layout=widgets.Layout(grid_template_columns="repeat(6, auto auto auto auto)")
		)
		_row_widgets.append(_box_button)
		ipython_display(_box_button)
		
		for i, _column in enumerate(_columns):
			_header = widgets.Text(
				value=_column,
				placeholder=_column,
				description='',
				disabled=False,
				layout=widgets.Layout(width='auto', height='auto')
			)
			_header_widgets.append(_header)
			_column_enabled = widgets.Checkbox(
				value=False,
				description='',
				disabled=False,
				indent=False
			)
			_column_widgets.append(_column_enabled)
			
			_label = widgets.Label(value=table[self.row_index][i])
			_label_widgets.append(_label)
			
			_box = widgets.GridBox(
				[
					_column_enabled,
					_header,
					_label
				],
				layout=widgets.Layout(grid_template_columns="repeat(1, 30px 200px auto)")
			)
			_row_widgets.append(_box)
			ipython_display(_box)
		
		_save_next_table_button.on_click(lambda *a, **kw: (
			self._save_table(_header_widgets, _column_widgets),
			self._next_table(+1, _row_widgets)
		))
		_prev_table_button.on_click(lambda *a, **kw: self._next_table(-1, _row_widgets))
		_next_table_button.on_click(lambda *a, **kw: self._next_table(+1, _row_widgets))
		_save_table_button.on_click(lambda *a, **kw: self._save_table(_header_widgets, _column_widgets))
		_prev_values_button.on_click(lambda *a, **kw: self._next_values(-1, table, _label_widgets))
		_next_values_button.on_click(lambda *a, **kw: self._next_values(+1, table, _label_widgets))
	
	def start(self, *_args, **__kwargs):
		"""
		:param _args:
		:param __kwargs:
		:return:
		"""
		button_start = widgets.Button(
			description='Start',
			disabled=False,
			button_style='',  # 'success', 'info', 'warning', 'danger' or ''
			tooltip='Click me',
			icon='check'  # (FontAwesome names without the `fa-` prefix)
		)
		ipython_display(button_start)
		button_start.on_click(lambda *a, **kw: (
			self.next_table(),
			button_start.close()
		))
		
		pass
