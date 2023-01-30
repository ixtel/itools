import os

import pandas as pd
from pandas import HDFStore


def _get_col_widths(dataframe):
	"""
	:param dataframe:
	:return:
	"""
	idx_max = max([len(str(s).strip()) for s in dataframe.index.values] + [len(str(dataframe.index.name).strip())])
	res = [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [len(col)]) for col in dataframe.columns]
	return res


def get_df_writer(path, strings_to_urls=False, strings_to_formulas=False, strings_to_numbers=False, nan_inf_to_errors=True):
	"""
	:param path:
	:param strings_to_urls:
	:param strings_to_formulas:
	:param strings_to_numbers:
	:param nan_inf_to_errors:
	:return:
	"""
	if not path.endswith('.xlsx'):
		path += '.xlsx'
	os.makedirs(os.path.dirname(path), exist_ok=True)
	writer = pd.ExcelWriter(
		path,
		options={
			'strings_to_urls': strings_to_urls,
			'strings_to_formulas': strings_to_formulas,
			'strings_to_numbers': strings_to_numbers,
			'nan_inf_to_errors': nan_inf_to_errors
		},
		engine='xlsxwriter'
	)
	return writer


def df_from_xlsx(path, sheet_name='report'):
	"""
	:param path:
	:param sheet_name:
	:return:
	"""
	df = pd.read_excel(path, sheet_name=sheet_name)
	return df


def df_to_xls(df, path=None, columns=None):
	"""
	:param df:
	:param path:
	:param columns:
	:return:
	"""
	if columns:
		_df = df[columns]
	else:
		_df = df[:]
	return df_to_xlsx(_df, path)


def df_sheets_to_xlsx(
		data, path, columns=None,
		strings_to_urls=False, strings_to_formulas=False, strings_to_numbers=False, nan_inf_to_errors=True,
		header=True, index=False
):
	"""
	:param data:
	:param path:
	:param columns:
	:param strings_to_urls:
	:param strings_to_formulas:
	:param strings_to_numbers:
	:param nan_inf_to_errors:
	:param header:
	:param index:
	:return:
	"""
	writer = get_df_writer(
		path=path,
		strings_to_urls=strings_to_urls,
		strings_to_formulas=strings_to_formulas,
		strings_to_numbers=strings_to_numbers,
		nan_inf_to_errors=nan_inf_to_errors
	)
	for sheet_name, sheet_data in data.items():
		sheet_name = str(sheet_name)
		if columns:
			df = pd.DataFrame(sheet_data, columns=columns)
		else:
			df = pd.DataFrame(sheet_data)
		df_to_xlsx_write(df=df, writer=writer, sheet_name=sheet_name, header=header, index=index)
	writer.save()
	return True


def df_sheet_to_xlsx(
		data, path, columns=None,
		strings_to_urls=False, strings_to_formulas=False, strings_to_numbers=False, nan_inf_to_errors=True,
		sheet_name='OutputData', header=True, index=False
):
	"""
	:param data:
	:param path:
	:param columns:
	:param strings_to_urls:
	:param strings_to_formulas:
	:param strings_to_numbers:
	:param nan_inf_to_errors:
	:param sheet_name:
	:param header:
	:param index:
	:return:
	"""
	writer = get_df_writer(
		path=path,
		strings_to_urls=strings_to_urls,
		strings_to_formulas=strings_to_formulas,
		strings_to_numbers=strings_to_numbers,
		nan_inf_to_errors=nan_inf_to_errors
	)
	
	if columns:
		df = pd.DataFrame(data, columns=columns)
	else:
		df = pd.DataFrame(data)
	
	df_to_xlsx_write(df=df, writer=writer, sheet_name=sheet_name, header=header, index=index)
	
	writer.save()
	return True


def df_to_xlsx(
		df,
		path,
		strings_to_urls=False, strings_to_formulas=False, strings_to_numbers=False, nan_inf_to_errors=True,
		sheet_name='OutputData',
		header=True, index=False
):
	"""
	:param df:
	:param path:
	:param strings_to_urls:
	:param strings_to_formulas:
	:param strings_to_numbers:
	:param nan_inf_to_errors:
	:param sheet_name:
	:param header:
	:param index:
	:return:
	"""
	writer = get_df_writer(
		path=path,
		strings_to_urls=strings_to_urls,
		strings_to_formulas=strings_to_formulas,
		strings_to_numbers=strings_to_numbers,
		nan_inf_to_errors=nan_inf_to_errors
	)
	df_to_xlsx_write(df=df, writer=writer, sheet_name=sheet_name, header=header, index=index)
	writer.save()
	return True


def df_to_xlsx_write(df, writer, sheet_name='OutputData', header=True, index=False):
	"""
	:param df:
	:param writer:
	:param sheet_name:
	:param header:
	:param index:
	:return:
	"""
	sheet_name = str(sheet_name)
	df.to_excel(writer, sheet_name=sheet_name, header=header, index=index, na_rep='')
	worksheet = writer.sheets[sheet_name]
	if header:
		worksheet.freeze_panes(1, 0)
	for idx, col in enumerate(df):
		series = df[col]
		max_len = max((
			series.astype(str).map(len).max(),
			len(str(series.name))
		)) + 3
		worksheet.set_column(idx, idx, max_len)
	return True


def df_group_to_xlsx(
		grouping, path, columns, colls_out=False, coll_count=False,
		strings_to_urls=False, strings_to_formulas=False, strings_to_numbers=False, nan_inf_to_errors=True,
		sheet_name='OutputData', sort=False, spaces=1
):
	"""
	:param grouping:
	:param path:
	:param columns:
	:param colls_out:
	:param coll_count:
	:param strings_to_urls:
	:param strings_to_formulas:
	:param strings_to_numbers:
	:param nan_inf_to_errors:
	:param sheet_name:
	:param sort:
	:param spaces:
	:return:
	"""
	sheet_name = str(sheet_name)
	writer = get_df_writer(
		path=path,
		strings_to_urls=strings_to_urls,
		strings_to_formulas=strings_to_formulas,
		strings_to_numbers=strings_to_numbers,
		nan_inf_to_errors=nan_inf_to_errors
	)
	head_df = pd.DataFrame({}, columns=columns)
	head_df.to_excel(writer, sheet_name=sheet_name, header=True, index=False, startrow=0, startcol=1)
	row = 1
	df = None
	for k, df in grouping:
		df_size = df.shape[0]
		d = {
			'group': k,
			'size': df_size
		}
		if coll_count:
			d['count'] = df[coll_count].sum()
		group_df = pd.DataFrame.from_dict(d, orient='columns')
		group_df.to_excel(
			writer, sheet_name=sheet_name, columns=['group', 'size', 'count'], header=False, index=False,
			startrow=row, startcol=0
		)
		row += 1
		if colls_out:
			df = df[colls_out]
		if sort:
			df = df.sort_values(sort, ascending=False)
		df.to_excel(writer, sheet_name=sheet_name, header=False, index=False, startrow=row, startcol=1)
		row = row + len(df.index) + spaces + 1
	worksheet = writer.sheets[sheet_name]
	
	if df:
		for idx, col in enumerate(df):
			series = df[col]
			max_len = max((
				series.astype(str).map(len).max(),
				len(str(series.name))
			)) + 3
			worksheet.set_column(idx, idx, max_len)
		writer.save()
		return True
	return False


def df_grouper_write_to_sheet(
		writer, grouping, columns=None, colls_out=None, dfheader=True, sheet_name='OutputData', sort=False,
		spaces=1, cols_count=None, header=True, df_size_show=True
):
	"""
	:param writer:
	:param grouping:
	:param columns:
	:param colls_out:
	:param dfheader:
	:param sheet_name:
	:param sort:
	:param spaces:
	:param cols_count:
	:param header:
	:param df_size_show:
	:return:
	"""
	if columns is None:
		columns = ['group', 'size']
	sheet_name = str(sheet_name)
	_columns = columns.copy()
	if cols_count is not None:
		_columns.append(cols_count)
	head_df = pd.DataFrame({}, columns=_columns)
	head_df.to_excel(writer, sheet_name=sheet_name, header=header, index=False, startrow=0, startcol=0)
	row = 1
	widths = {}
	widths_group = len(columns[0]) + 3
	for group, df in grouping.items():
		widths_group = max(widths_group, len(group) + 3)
		_data = [group]
		if df_size_show:
			df_size = df.shape[0]
			_data.append(df_size)
		else:
			_data.append('')
		if cols_count is not None:
			count = df[cols_count].sum()
			df = df.sort_values(by=cols_count, ascending=False)
			if df_size_show:
				_data += [count]
			else:
				_data += ['']
		group_df = pd.DataFrame([_data], columns=_columns)
		group_df.to_excel(writer, sheet_name=sheet_name, header=False, index=False, startrow=row, startcol=0)
		if df_size_show:
			row += 1
		if colls_out is not None:
			df = df[colls_out]
		if sort:
			df = df.sort_values(sort, ascending=False)
		df.to_excel(writer, sheet_name=sheet_name, header=dfheader, index=False, startrow=row, startcol=1)
		row = row + len(df.index) + spaces + 1
		
		for idx, col in enumerate(df):
			series = df[col]
			max_len = max((
				series.astype(str).map(len).max(),
				len(str(series.name))
			)) + 3
			widths[idx] = max(widths.get(idx, 0), max_len)
	worksheet = writer.sheets[sheet_name]
	worksheet.set_column(0, 0, widths_group)
	for k, v in widths.items():
		worksheet.set_column(k + 1, k + 1, v)
	if header:
		worksheet.freeze_panes(1, 0)
	return True


def dic_sheets_df_grouper_to_xlsx(
		dic, path, columns=None, colls_out=None, dfheader=True,
		strings_to_urls=False, strings_to_formulas=False, strings_to_numbers=False, nan_inf_to_errors=True,
		sort=False, spaces=1, cols_count=None, header=True, df_size_show=True
):
	"""
	:param dic:
	:param path:
	:param columns:
	:param colls_out:
	:param dfheader:
	:param strings_to_urls:
	:param strings_to_formulas:
	:param strings_to_numbers:
	:param nan_inf_to_errors:
	:param sort:
	:param spaces:
	:param cols_count:
	:param header:
	:param df_size_show:
	:return:
	"""
	writer = get_df_writer(
		path=path,
		strings_to_urls=strings_to_urls,
		strings_to_formulas=strings_to_formulas,
		strings_to_numbers=strings_to_numbers,
		nan_inf_to_errors=nan_inf_to_errors
	)
	for k, grouping in dic.items():
		sheet_name = k
		df_grouper_write_to_sheet(
			writer=writer, grouping=grouping, columns=columns, colls_out=colls_out, dfheader=dfheader,
			sheet_name=sheet_name, sort=sort, spaces=spaces, cols_count=cols_count, header=header, df_size_show=df_size_show
		)
	writer.save()
	return True


def df_grouper_to_xlsx(
		grouping, path, columns=None, colls_out=False, dfheader=True,
		strings_to_urls=False, strings_to_formulas=False, strings_to_numbers=False, nan_inf_to_errors=True,
		sheet_name='outData', sort=False, spaces=1, cols_count=None
):
	"""
	:param grouping:
	:param path:
	:param columns:
	:param colls_out:
	:param dfheader:
	:param strings_to_urls:
	:param strings_to_formulas:
	:param strings_to_numbers:
	:param nan_inf_to_errors:
	:param sheet_name:
	:param sort:
	:param spaces:
	:param cols_count:
	:return:
	"""
	if columns is None:
		columns = ['group', 'size']
	writer = get_df_writer(
		path=path,
		strings_to_urls=strings_to_urls,
		strings_to_formulas=strings_to_formulas,
		strings_to_numbers=strings_to_numbers,
		nan_inf_to_errors=nan_inf_to_errors
	)
	df_grouper_write_to_sheet(
		writer=writer, grouping=grouping, columns=columns, colls_out=colls_out, dfheader=dfheader,
		sheet_name=sheet_name, sort=sort, spaces=spaces, cols_count=cols_count
	)
	writer.save()
	return True


def df_to_csv(df, path):
	"""
	:param df:
	:param path:
	:return:
	"""
	df.to_csv(path)


def df_to_hdf(df, key, path):
	"""
	:param df:
	:param key:
	:param path:
	:return:
	"""
	with HDFStore(path) as store:
		store[key] = df


def list_dic_to_df(list_dict):
	"""
	:param list_dict:
	:return:
	"""
	df = pd.DataFrame.from_dict(list_dict)
	return df


def list_to_df(data, columns=None):
	"""
	:param data:
	:param columns:
	:return:
	"""
	if columns is None:
		columns = []
	df = pd.DataFrame(data, columns=columns)
	return df


def dic_to_df(d):
	"""
	:param d:
	:return:
	"""
	df = pd.DataFrame.from_dict(d, orient='index')
	return df


def list_dic_to_xls(list_dict, path):
	"""
	:param list_dict:
	:param path:
	:return:
	"""
	df = list_dic_to_df(list_dict)
	df_to_xlsx(df, path)


def dic_to_xls(d, path):
	"""
	:param d:
	:param path:
	:return:
	"""
	df = dic_to_df(d)
	df_to_xlsx(df, path, header=False, index=True)


def hdf_save(key, data, path, append=True):
	"""
	:param key:
	:param data:
	:param path:
	:param append:
	:return:
	"""
	f = None
	if append is False:
		f = 'fixed'
	if isinstance(data, list):
		data = pd.Series(data)
	with pd.HDFStore(path) as hdf:
		data.to_hdf(hdf, key, format=f, append=append)
	return True


def hdf_read(path):
	"""
	:param path:
	:return:
	"""
	res = {}
	with pd.HDFStore(path) as hdf:
		for key in hdf.keys():
			res[str(key)] = hdf[key]
	return res


def set_relate_tables_hdf(key, path, data, append=True):
	"""
	:param key:
	:param path:
	:param data:
	:param append:
	:return:
	"""
	f = None
	if append is False:
		f = 'fixed'
	with pd.HDFStore(path) as hdf:
		if isinstance(data, dict):
			for k, data in data.items():
				if data:
					if isinstance(data, (list, tuple, set)):
						data = pd.Series(data)
					data.to_hdf(hdf, '{}/{}'.format(key, k), format=f, append=append, complib='blosc')
		else:
			data.to_hdf(hdf, key, format=f, append=append, complib='blosc')


def get_relate_tables_hdf(keys, path):
	"""
	:param keys:
	:param path:
	:return:
	"""
	res = {}
	with pd.HDFStore(path) as hdf:
		for k in keys:
			res[str(k)] = hdf[k]
	return res
