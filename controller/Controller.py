import pandas as pd
from bokeh.io import show, curdoc
from bokeh.models import Select, Button, ColumnDataSource
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.events import Tap
from bokeh.models.widgets import RadioButtonGroup, CheckboxGroup
from bokeh.models.widgets.sliders import RangeSlider
import os
import numpy
import models.MyDataFrames
import models.df_matrix
import models.df_corr_plot
import views.PlotMatrix
import views.plot_corr
import views.plot_rock
import views.ViewModel

WIDTH_MATRIX = 1
HEIGHT_MATRIX = 1
DATA_DIR = 'data/mydata'

class Controller():

	def __init__(self):

		self.WIDTH_MATRIX = WIDTH_MATRIX
		self.HEIGHT_MATRIX = HEIGHT_MATRIX
		self.DATA_DIRIRECTORY = DATA_DIR
		self.plots_rock = column()
		self.source_correlation_plot = None
		self.select_plots = []

		self.view_model = views.ViewModel.ViewModel()
		

		self.data_files = os.listdir(self.DATA_DIRIRECTORY)
		self.my_data_frames = models.MyDataFrames.MyDataFrames()
		self.Y_COL = self.my_data_frames.get_name_dept()
		self.tabs = RadioButtonGroup(labels=['Page1', 'Page2'], active=0)
		self.tabs.on_change('active', lambda attr, old, new: self.change_page())

		self.select_data_files1 = Select(title="Data files 1:", value="df1", options=["df1"]+(self.data_files))
		self.select_data_files2 = Select(title="Data files 2:", value="df2", options=["df2"]+(self.data_files))

		self.select_data_files1.on_change('value', lambda attr, old, new: self.change_dataframes())
		self.select_data_files2.on_change('value', lambda attr, old, new: self.change_dataframes())
		self.refresh_button = Button(label="Refresh", button_type="success", width=100)
		self.refresh_button.on_click(self.update_directory)

		self.plot_matrix = views.PlotMatrix.PlotMatrix()
		self.layout = column(self.tabs, row(self.select_data_files1, self.select_data_files2),
							 self.refresh_button)
		curdoc().add_root(self.layout)

		# show(self.layout)

	def change_page(self):
		if (self.select_data_files1.value == "df1" or self.select_data_files2.value == "df2"):
			self.tabs.active = 0
			return
		if (self.tabs.active == 0):
			self.layout.children = [self.tabs,
									row(self.select_data_files1, self.select_data_files2),
									self.refresh_button,
									self.slider_depth,
									self.plot_matrix.figure()]
		elif (self.tabs.active == 1):
			self.layout.children = [self.tabs,
									self.plots_rock,
									self.view_model.get_layout(),
									row(column(self.select_df1_corr, self.checkbox_df1),
										column(self.select_df2_corr, self.checkbox_df2)),
									views.plot_corr.get_figure_corr_plot(self.source_correlation_plot)]
	def change_dataframes(self):
		if (self.select_data_files1.value == "df1" or self.select_data_files2.value == "df2"):
			return
		if (not self.select_data_files1.value.endswith('.csv') or not self.select_data_files2.value.endswith('.csv')):
			print("incorrect data, expected format csv")
			return
		try:
			self.my_data_frames.read_data_frames(data_directory=self.DATA_DIRIRECTORY,
											  file1=self.select_data_files1.value,
											  file2=self.select_data_files2.value)
		except(BaseException):
			print("exception")

		self.df1, self.df2 = self.my_data_frames.get_data_frames()
		self.df1,self.df2 = self.my_data_frames.resize_depth(self.df1,self.df2)
		print(0)
		self.slider_depth = RangeSlider(start=self.my_data_frames.min_total_depth(),
										end=self.my_data_frames.max_total_depth(), step=1,
										value=(self.my_data_frames.min_total_depth(),
											   self.my_data_frames.max_total_depth()))
		print(1)
		self.slider_depth.on_change('value', lambda attr, old, new: self.change_depth(attr, old, new))
		self.view_model.init_select(self.df1.columns,self.df1, self.df2)
		print(self.df1[self.df1.columns],self.df2.columns)
		self.view_model.get_select().on_change('value', lambda attr, old, new: self.change_select(attr, old, new))
		self.view_model.get_select_model().on_change('value', lambda attr, old, new:self.change_model(attr,old,new))
		print(2)
		self.update_page()
	def change_depth(self,attr, old, new):
		self.my_data_frames.change_depth(attr, old, new)
		self.df1,self.df2 = self.my_data_frames.get_data_frames()
		self.update_page()
	def change_select(self,attr, old, new):
		self.view_model.change_select(attr,old,new)
		print("change select")
		self.layout.children = [self.tabs,
									self.plots_rock,
									self.view_model.get_layout(),
									row(column(self.select_df1_corr, self.checkbox_df1),
										column(self.select_df2_corr, self.checkbox_df2)),
									views.plot_corr.get_figure_corr_plot(self.source_correlation_plot)]

	def change_model(self,attr,old,new):
		print('change model0')
		self.view_model.change_model(attr,old,new)
		print('change model1')
		self.layout.children = [self.tabs,
									self.plots_rock,
									self.view_model.get_layout(),
									row(column(self.select_df1_corr, self.checkbox_df1),
										column(self.select_df2_corr, self.checkbox_df2)),
									views.plot_corr.get_figure_corr_plot(self.source_correlation_plot)]
		print('change model2')
		

	def update_page(self):

		self.columns_df1, self.columns_df2 = self.df1.columns.tolist(),self.df2.columns.tolist()#self.my_data_frames.get_columns()
		self.select_plots = []
		self.source_correlation_plot = models.df_corr_plot.get_source_corr(df1 = self.df1,df2 = self.df2,val1 = self.columns_df1[0], val2 = self.columns_df2[1] )
		print(4)
		self.select_df1_corr = Select(title="Data frame 1:", value=self.columns_df1[0], options=self.columns_df1)
		self.select_df2_corr = Select(title="Data frame 2:", value=self.columns_df2[1], options=self.columns_df2)

		self.select_df1_corr.on_change('value', lambda attr, old, new: self.update_set_data())
		self.select_df2_corr.on_change('value', lambda attr, old, new: self.update_set_data())

		self.checkbox_df1 = CheckboxGroup(labels=["log10"], active=[])
		self.checkbox_df2 = CheckboxGroup(labels=["log10"], active=[])
		self.checkbox_df1.on_change('active', lambda attr, old, new: self.update_set_data())
		self.checkbox_df2.on_change('active', lambda attr, old, new: self.update_set_data())
		data_matrix = models.df_matrix.init_data_frame_matrix(self.df1, self.df2,self.columns_df1,self.columns_df2)
		
		self.plot_matrix.draw_matrix(data_matrix,
									 self.columns_df1,
									 self.columns_df2,
									 self.WIDTH_MATRIX,
									 self.HEIGHT_MATRIX)

		self.plot_matrix.figure().on_event(Tap, self.update_plots)

		self.layout.children = [self.tabs, row(self.select_data_files1, self.select_data_files2),
								self.refresh_button,
								self.slider_depth,
								self.plot_matrix.figure()]
		print('end')
	def update_directory(self):
		self.DATA_DIRIRECTORY = 'data'
		self.data_files = os.listdir(self.DATA_DIRIRECTORY)
		self.select_data_files1 = Select(title="Data files 1:", value="df1", options=["df1"] + self.data_files)
		self.select_data_files2 = Select(title="Data files 2:", value="df2", options=["df2"] + self.data_files)
		self.layout.children[1] = row(self.select_data_files1, self.select_data_files2)

	def init_corr(self):
	   
		data = pd.DataFrame(data={'x': self.df1[self.columns_df1[0]], 'y': self.df2[self.columns_df2[1]]})
		self.source_correlation_plot = ColumnDataSource(data)
		plot_correlation = figure(plot_width=800, plot_height=500, title='correlation graph')
		plot_correlation.scatter(x='x', y='y', source=self.source_correlation_plot, line_color='red', size=2)

		return plot_correlation

	def update_plots(self, event):
		length_columns_df1 = len(self.columns_df1)
		length_columns_df2 = len(self.columns_df2)
		x = int((event.x) / self.WIDTH_MATRIX)
		y = int((event.y) / self.HEIGHT_MATRIX)
		if (self.select_plots.count(
				((1, self.columns_df1[x]), (2, self.columns_df2[length_columns_df2 - y - 1]))) == 1):
			self.select_plots.remove(((1, self.columns_df1[x]), (2, self.columns_df2[length_columns_df2 - y - 1])))
			self.plot_matrix.delete_select_cell(name=self.columns_df1[x] + self.columns_df2[length_columns_df2 - y - 1])

		elif (event.x < 0 or event.x > length_columns_df1 or event.y < 0 or event.y > length_columns_df2):
			return
		else:
			self.plot_matrix.draw_select_cell(name=self.columns_df1[x] + self.columns_df2[length_columns_df2 - y - 1],
											  x=x + 0.5,
											  y=y + 0.5, width=1, height=1)
			self.select_plots.append(((1, self.columns_df1[x]), (2, self.columns_df2[length_columns_df2 - y - 1])))

		self.plots_rock.children = [views.plot_rock.get_plots_rock(self.df1,
															 self.df2,
															 self.select_plots,
															 self.my_data_frames.get_y_range(self.df1),
															 self.Y_COL)]

	def update_set_data(self):
		r = self.df1[self.select_df1_corr.value]
		col = self.df2[self.select_df2_corr.value]
		if (self.checkbox_df2.active == [0]):
			col = col.apply(numpy.log10)
		if (self.checkbox_df1.active == [0]):
			r = r.apply(numpy.log10)
		data = {'x': r, 'y': col}
		self.source_correlation_plot.data = data
