import pandas as pd
import numpy as np
import os
from bokeh.models import Range1d

DEPT = 'DEPT'
DEPTH = 'DEPTH'


class MyDataFrames:
	def __init__(self):
		self.Y_COL = DEPT
		self.df1 = pd.DataFrame()
		self.df2 = pd.DataFrame()

	def read_data_frames(self, data_directory:str, file1:str, file2:str):
		self.df1 = pd.read_csv(os.path.join(data_directory, file1))
		self.df2 = pd.read_csv(os.path.join(data_directory, file2))

		ret_code = self.__rename_depth(self.df1)

		ret_code = self.__rename_depth(self.df2)
		self.df1,self.df2 = self.resize_depth(self.df1,self.df2)
		self.df1 = self.df1.astype(np.float32)
		df_describe = self.df1.describe().T
		self.df1 = self.df1[df_describe[df_describe['std'] > 0].index]

		self.df2 = self.df2.astype(np.float32)
		df_describe = self.df2.describe().T
		self.df2 = self.df2[df_describe[df_describe['std'] > 0].index]
		print("end read")
	def change_depth(self, attr, old, new):
		self.df1 = self.df1[
			(self.df1[self.Y_COL] >= new[0]) & (self.df1[self.Y_COL] <= new[1])]
		self.df2 = self.df2[
			(self.df2[self.Y_COL] >= new[0]) & (self.df2[self.Y_COL] <= new[1])]
		#self.update_page()

	def min_total_depth(self):
		return max(self.df1[self.Y_COL].min(), self.df2[self.Y_COL].min())

	def max_total_depth(self):
		return min(self.df1[self.Y_COL].max(), self.df2[self.Y_COL].max())

	def resize_depth(self, df1, df2):
		min_total_depth = self.min_total_depth()
		max_total_depth = self.max_total_depth()

		df1 = df1[(df1[self.Y_COL] >= min_total_depth) & (df1[self.Y_COL] <= max_total_depth)]
		df2 = df2[(df2[self.Y_COL] >= min_total_depth) & (df2[self.Y_COL] <= max_total_depth)]

		if (df1[self.Y_COL].size < df2[self.Y_COL].size):
			df2.drop_duplicates(self.Y_COL, inplace = True)
			df2.set_index([self.Y_COL], inplace=True)
			df2 = df2.reindex(df1[self.Y_COL], method='nearest')
			column_values = pd.Series(df2.index, index=df2.index)
			df2.insert(loc=0, column=self.Y_COL, value=column_values)
			df2.set_index(df1.index, inplace=True)
		else:
			df1.drop_duplicates(self.Y_COL, inplace = True)
			df1.set_index([self.Y_COL], inplace=True)
			df1 = df1.reindex(df2[self.Y_COL], method='nearest')
			column_values = pd.Series(df1.index, index=df1.index)
			df1.insert(loc=0, column=self.Y_COL, value=column_values)
			df1.set_index(df2.index, inplace=True)
		return df1, df2

	def __rename_depth(self, df):
		is_renamed_df = False
		unnamed = "Unnamed: 0"
		exist = 0
		not_exist = 1
		for col in df.columns:
			if (col.lower() == DEPTH.lower() or col.lower() == DEPT.lower()):
				df.rename(columns={col: self.Y_COL}, inplace=True)
				is_renamed_df = True
		if (not is_renamed_df):
			if (df.index.name == None and df.columns[0] == unnamed):
				df.rename(columns={unnamed: self.Y_COL}, inplace=True)
				return not_exist
			elif (df.index.name != None and df.index.name.lower().find(DEPT.lower()) != -1):
				column_values = pd.Series(df.index, index=df.index)
				df.insert(loc=0, column=self.Y_COL, value=column_values)
				return not_exist
			elif ((df.columns)[0] != unnamed and df.columns[0].lower().find(DEPT.lower()) != -1):
				df.rename(columns={unnamed: self.Y_COL}, inplace=True)
				return not_exist
			else:
				column_values = pd.Series(df.index, index=df.index)
				df.insert(loc=0, column=self.Y_COL, value=column_values)
				return not_exist
		return exist

	def get_data_frames(self):
		return (self.df1, self.df2)

	def get_name_dept(self):
		return self.Y_COL

	def get_columns_dataframes(self):
		return (self.df1.columns, self.df2.columns)

	def get_y_range(self, df):
		ymin = df[self.Y_COL].min()
		ymax = df[self.Y_COL].max()
		res = Range1d(ymin, ymax)
		return res

	def get_columns(self):
		columns_df1 = [col for col in self.df1.columns if self.is_number(col, self.df1)]
		columns_df2 = [col for col in self.df2.columns if self.is_number(col, self.df2)]
		return (columns_df1, columns_df2)

	def is_number(self, col, df):
		if type(df[col][df[col].index[0]]).__name__ == "int64" or type(df[col][df[col].index[0]]).__name__ == "float64":
			return True
		return False
