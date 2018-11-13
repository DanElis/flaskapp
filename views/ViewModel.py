import pandas as pd
from bokeh.models import Range1d
from bokeh.models import Select
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.layouts import column,row
import pickle
from sklearn import ensemble
import os
import numpy as np

class ViewModel():
	def __init__(self):
		self.select_plot_rock = Select()
		self.select_model = Select()
		self.plot_rock  = column(figure(plot_width=200, plot_height=400, title='', toolbar_location=None, tools='ywheel_zoom',
					  active_scroll='ywheel_zoom'))
		self.df1 = pd.DataFrame()
		self.__init_select_model()
		self.h_bar = column(figure())
		self.dict_model = {}
	def __init_plot_rock(self, x, y, source, yrange): 
		plot = figure(plot_width=200, plot_height=400, title='', toolbar_location=None, tools='ywheel_zoom',
					  active_scroll='ywheel_zoom')
		plot.line(x, y, source=source, line_width=2)
		plot.y_range = yrange
		return plot
	def change_select(self,attr, old, new):
		x = new
		source = ColumnDataSource(data=self.df1)
		self.plot_rock = column(self.__init_plot_rock(x,'DEPT',source, self.get_y_range(self.df1)))

	def init_select(self,columns,df1,df2):
		self.select_plot_rock = Select(title="PLots:", options=columns.tolist())
		self.df1 = df1
		self.df2 = df2
		self.load_model()
	def get_y_range(self, df):
		ymin = df['DEPT'].min()
		ymax = df['DEPT'].max()
		res = Range1d(ymin, ymax)
		return res
	def get_select(self):
		return self.select_plot_rock
	def get_layout(self):
		return column(row(self.select_plot_rock,self.select_model),
			self.plot_rock)
	def __init_select_model(self):
		model_list = ['0-25%','0-50%', '0-75%', '0-100%', '25-100%', '50-100%', '75-100%' ]
		self.select_model = Select(title="Predict:", options=model_list)
	def change_model(self,attr,old,new):
	
		df_merged = self.gen_merged(y_col='GR')

		X_test, y_test = self.get_sample(df_merged, y_col='GR')
		print(X_test)
		y_pred = self.dict_model[new].predict(X_test)
		#source = ColumnDataSource(data=self.df1)
		self.plot_rock.children[0].line(y_pred, self.df1['DEPT'], line_width=2, line_color = 'red')
		self.plot_rock.children[0].y_range = self.get_y_range(self.df1)
	def get_select_model(self):
		return self.select_model
	def load_model(self):
		path_to_dir = '/home/wer/diplom/flaskapp/flaskapp/data/models'
		for file in os.listdir(path_to_dir):
			
			if not file.endswith('.pickle'):
				continue
			print(file)
			with open(file, 'rb') as f:

				clf = pickle.load(f)
				self.dict_model[f.name[0:-7:]] = clf
				print(f.name[0:-7:])

	def get_sample(self,df_merged, y_col=['GR']):
		x_cols = np.setdiff1d(df_merged.columns, [y_col,'Unnamed: 0']).tolist()
		x, y = df_merged[x_cols].values, df_merged[y_col].values
		return x, y
	def gen_merged(self,y_col=['GR']):
		df_gis = self.df1
		df_gti = self.df2
		if len(df_gti.columns):
			df_gti = df_gti[df_gti.columns]
			
		if len(df_gis.columns)>0:
			df_gis = df_gis[df_gis.columns]
		
		df_gti = self.reindex_gti_depth(df_gis, df_gti, depth_col='DEPT')
		print('reindex')
		return self.merge_gti_gis(df_gis, df_gti, y_col=y_col)
	def merge_gti_gis(self,df_gis, df_gti, depth_col=['DEPT'], y_col=['GR'], set_size=1024):
		df_gis = pd.DataFrame(df_gis.set_index(depth_col)[y_col])
		df_gti = df_gti.set_index(depth_col)
		
		df_merged = pd.merge(df_gis, df_gti, left_index=True, right_index=True)
		print('merge')
		df_merged = df_merged.reset_index()
		df_merged = df_merged[df_merged[y_col].notnull()]
		df_merged = df_merged.fillna(0)
		
	#     df_describe = df_merged.describe().T
	#     df_merged = df_merged[df_describe[df_describe['std'] > 0].index]

		return df_merged
	def reindex_gti_depth(self,df_gis, df_gti, depth_col='DEPT'):
		df_gti = df_gti.set_index(depth_col).copy()
		df_gti = df_gti.reindex(df_gis['DEPT'], method='nearest')
		return df_gti.reset_index()