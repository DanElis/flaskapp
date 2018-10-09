import pandas as pd
from bokeh.io import output_file, show, curdoc
from bokeh.models import BasicTicker,Select,Button,Range1d, ColorBar, ColumnDataSource, LinearColorMapper, PrintfTickFormatter
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.transform import transform,dodge
from bokeh.events import Tap,Press
from bokeh.models.widgets import Panel, Tabs, RadioButtonGroup,CheckboxGroup
from bokeh.models.widgets.sliders import RangeSlider
import os 
import numpy

class Page():
	
	def __init__(self):
		self.WIDTH_MATRIX = 1
		self.HEIGHT_MATRIX = 1	
		self.tabs =  RadioButtonGroup(labels = ['Page1','Page2'],active = 0)
		self.tabs.on_change('active', lambda attr, old, new: self.change_page())

		self.data_directory = '/home/wer/diplom/flaskapp/flaskapp/data'
		self.data_files = os.listdir(self.data_directory) 

		self.select_data_files1 = Select(title="Data files 1:",value = "df1", options=["df1"]+self.data_files)
		self.select_data_files2 = Select(title="Data files 2:",value = "df2", options=["df2"]+self.data_files)

		self.select_data_files1.on_change('value',lambda attr, old,new:self.init_dataframes())
		self.select_data_files2.on_change('value',lambda attr, old,new:self.init_dataframes())
		self.refresh_button = Button(label="Refresh", button_type="success", width=100)
		self.refresh_button.on_click(self.update_directory)

		self.layout = column(self.tabs,row(self.select_data_files1,self.select_data_files2),
						self.refresh_button)
		curdoc().add_root(self.layout)
		#show(self.layout)

	def change_page(self):
		if(self.select_data_files1.value == "df1" or self.select_data_files2.value == "df2"):
			self.tabs.active = 0;
			return
		if(self.tabs.active == 0):
			self.layout.children = [self.tabs,
			row(self.select_data_files1,self.select_data_files2),
						self.refresh_button,
						self.slider_depth,
						self.plot_matrix]
		elif(self.tabs.active == 1):
			self.layout.children = [self.tabs,
			#self.sel_well,self.pred_button,
			self.plots_rock,
			row(column(self.select_df1_corr, self.checkbox_df1),
				column(self.select_df2_corr,self.checkbox_df2)),
			self.plot_correlation]
	def init_dataframes(self):
		if(self.select_data_files1.value == "df1" or self.select_data_files2.value == "df2"):
			return
		if(not self.select_data_files1.value.endswith('.csv') or not self.select_data_files2.value.endswith('.csv')):
			print("incorrect data, expected format csv")
			return

		self.Y_COL = 'Depth'
		self.main_df1,self.main_df2 = self.read_dataframe()
		self.change_case_depth(self.main_df1,self.main_df2)

		self.df1 = self.main_df1.copy()
		self.df2 = self.main_df2.copy()

		self.slider_depth = RangeSlider(start = self.min_total_depth(self.main_df1,self.main_df2), 
				end = self.max_total_depth(self.main_df1,self.main_df2),step =1,
				value = (self.min_total_depth(self.main_df1,self.main_df2),self.max_total_depth(self.main_df1,self.main_df2)))
		self.slider_depth.on_change('value', self.change_depth)
		self.update_page(True)

	def update_page(self,is_change):
		

		self.columns_df1 = [col for col in self.df1.columns if self.is_number(col,self.df1)]
		self.columns_df2 = [col for col in self.df2.columns if self.is_number(col,self.df2)]
		#self.select_plots = [-1 for i in range(len(self.columns_df1) + len(self.columns_df1))]
		self.select_plots = []

	#	wells = self.df1['Well Name'].unique().tolist()
	#	wells = [well for well in wells if well not in ['Recruit F9']]
		
		#self.sel_well = Select(title="Well name:", value=wells[0], options=wells)
		#self.pred_button = Button(label="Predict", button_type="success", width=100)
		#self.pred_button.on_click(self.update_predict)

		#self.plots_rock = self.init_plots_rock()

		self.plots_rock = column()
		self.source_correlation_plot = None
		self.plot_correlation = self.init_corr()
		
		self.select_df1_corr = Select(title="Data frame 1:", value=self.columns_df1[0], options=self.columns_df1)
		self.select_df2_corr = Select(title="Data frame 2:", value=self.columns_df2[1], options=self.columns_df2)
	
		self.select_df1_corr.on_change('value',lambda attr, old, new:self.update_set_data())
		self.select_df2_corr.on_change('value',lambda attr, old, new:self.update_set_data())
		
		self.checkbox_df1 = CheckboxGroup(labels = ["log10"],active = [])
		self.checkbox_df2 = CheckboxGroup(labels = ["log10"],active = [])
		self.checkbox_df1.on_change('active',lambda attr, old, new:self.update_set_data())
		self.checkbox_df2.on_change('active',lambda attr, old, new:self.update_set_data())

		data_matrix = self.init_data_matrix(self.df1,self.df2)
		self.plot_matrix = self.draw_matrix(data_matrix)
		self.plot_matrix.on_event(Tap, self.update_plots)

		self.layout.children = [self.tabs,row(self.select_data_files1,self.select_data_files2),
							self.refresh_button,
							self.slider_depth,
							self.plot_matrix]
	
	def change_depth(self, attr, old, new):
		self.df1 = self.df1[(self.df1[self.Y_COL] >= self.slider_depth.value[0]) & (self.df1[self.Y_COL] <= self.slider_depth.value[1])]
		self.df2 = self.df2[(self.df2[self.Y_COL] >= self.slider_depth.value[0]) & (self.df2[self.Y_COL] <= self.slider_depth.value[1])]
		self.update_page(False)
	def min_total_depth(self,df1,df2):
		return df1[self.Y_COL].min()
	def max_total_depth(self,df1,df2):
		return df1[self.Y_COL].max()
	def change_case_depth(self,df1,df2):
		for col in df1.columns:
			if(col.lower() == self.Y_COL.lower()):
				df1.rename(columns={col:self.Y_COL}, inplace=True)
		for col in df2.columns:
			if(col.lower() == self.Y_COL.lower()):
				df2.rename(columns={col:self.Y_COL}, inplace=True)

	def is_number(self,col,df):
		if(type(df[col][0]).__name__ == "int64" or type(df[col][0]).__name__ == "float64"):
			return True
		return False

	def update_directory(self):
		self.data_directory = '/home/wer/diplom/flaskapp/flaskapp/data'
		self.data_files = os.listdir(self.data_directory) 
		self.select_data_files1 = Select(title="Data files 1:",value = "df1", options=["df1"]+self.data_files)
		self.select_data_files2 = Select(title="Data files 2:",value = "df2", options=["df2"]+self.data_files)
		self.layout.children[1] = row(self.select_data_files1,self.select_data_files2)

	def init_corr(self):
		plot_correlation = figure(plot_width = 800, plot_height = 500, title = 'correlation graph')
		data = pd.DataFrame(data = {'x':self.df1[self.columns_df1[0]],'y':self.df2[self.columns_df2[1]]})
		self.source_correlation_plot = ColumnDataSource(data)
		plot_correlation.scatter(x='x', y='y', source=self.source_correlation_plot, line_color='red', size=2)
		
		return plot_correlation

	def toFixed(self,numObj, digits=0):
	    return f"{numObj:.{digits}f}"
		
	def get_y_range(self,df):
		ymin = df[self.Y_COL].min()
		ymax = df[self.Y_COL].max()
		res = Range1d(ymin, ymax)
		return res

	def update_plots(self,event):
		length_columns_df1 = len(self.columns_df1)
		length_columns_df2 = len(self.columns_df2) 
		x = int((event.x)/self.WIDTH_MATRIX)
		y = int((event.y)/self.HEIGHT_MATRIX)
		if(self.select_plots.count(((1,self.columns_df1[x]),(2,self.columns_df2[length_columns_df2-y-1]))) == 1): 
			self.select_plots.remove(((1,self.columns_df1[x]),(2,self.columns_df2[length_columns_df2-y-1])))
			self.delete_select_cell(name = self.columns_df1[x]+self.columns_df2[length_columns_df2 - y - 1])

		elif(event.x<0 or event.x > length_columns_df1 or event.y<0 or event.y > length_columns_df2):
			return
		else:
			self.draw_select_cell(name = self.columns_df1[x]+self.columns_df2[length_columns_df2 - y - 1],x=x+0.5,y = y+0.5,width = 1, height =1)
			self.select_plots.append(((1,self.columns_df1[x]),(2,self.columns_df2[length_columns_df2-y-1])))
		
		self.plots_rock.children = [self.draw_plot_rock(self.df1,self.df2,self.select_plots)]
	
	def draw_select_cell(self,name,x,y,height,width):
		self.plot_matrix.rect(x=x,y=y,width=width,height=height,fill_alpha=0,line_color="blue",name=name)
	
	def delete_select_cell(self,name):
		self.plot_matrix.select(name=name).visible = False

	def update_set_data(self):
		r = self.df1[self.select_df1_corr.value]
		col = self.df2[self.select_df2_corr.value]
		if(self.checkbox_df2.active == [0]):
			col = col.apply(numpy.log10)
		if(self.checkbox_df1.active == [0]):
			r = r.apply(numpy.log10)
		data = {'x':r,'y':col}
		self.source_correlation_plot.data = data

	def update_predict(self):
		return
		
	def draw_plot_rock(self,df1,df2, select_plots):
		list_plots = []
		source_df1 = ColumnDataSource(data=df1)
		source_df2 = ColumnDataSource(data = df2)
		yrange = self.get_y_range(df1)
		for pair_data in self.select_plots:
			
			list_plots.append(self.init_plot_rock(pair_data[0][1],pair_data[0][1],self.Y_COL,source_df1,yrange,'#0000ff'))
			
			list_plots.append(self.init_plot_rock(pair_data[1][1],pair_data[1][1],self.Y_COL,source_df2,yrange,'#008000'))
		return row(list_plots)
	def init_plot_rock(self, title, x , y, source, yrange,color_title):
		plot = figure(plot_width=200, plot_height=400, title=title, toolbar_location=None,tools = 'ywheel_zoom', active_scroll='ywheel_zoom')
		plot.line(x, y, source=source, line_width=2)
		plot.y_range = yrange
		plot.title.text_color = color_title

		return plot
	def init_data_matrix(self,df1,df2):
		matrix = {col:[] for col in self.columns_df1}
		for r in self.columns_df1:
			for col in self.columns_df2:
				matrix[r].append(float(self.toFixed(numpy.corrcoef(df1[r], df2[col])[0,1],3)))
		data = pd.DataFrame(data = matrix)
		data.index = list(self.columns_df2)
		data.index.name = 'rows'
		data.columns.name = 'columns'

		return data

	def draw_matrix(self, data):
		df = pd.DataFrame(data.stack(), columns=['rate']).reset_index()
		
		source = ColumnDataSource(df)
		colors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]
		mapper = LinearColorMapper(palette=colors, low=df.rate.min(), high=df.rate.max())

		plot_matrix = figure(plot_width=800, plot_height=300, title="",
				   x_range=list(self.columns_df2), y_range=list(reversed(self.columns_df1)),
				   toolbar_location=None, tools="", x_axis_location="above")
		plot_matrix.rect(x="rows", y="columns", width=self.WIDTH_MATRIX, height=self.HEIGHT_MATRIX, source=source,
			   line_color=None, fill_color=transform('rate', mapper))
		plot_matrix.xaxis.major_label_text_color = '#0000ff' #blue
		plot_matrix.yaxis.major_label_text_color = '#008000' #green
		self.r = plot_matrix.text(x=dodge("rows",-0.1,range = plot_matrix.x_range), y=dodge("columns",-0.2,range = plot_matrix.y_range), text="rate", **{"source":df})
		self.r.glyph.text_font_size="9pt"
		
		plot_matrix.axis.axis_line_color = None
		plot_matrix.axis.major_tick_line_color = None
		return plot_matrix
	def read_dataframe(self):
		df1 = pd.read_csv('data/'+self.select_data_files1.value)
		df2 = pd.read_csv('data/'+self.select_data_files2.value)

		return (df1,df2)
table = Page()
