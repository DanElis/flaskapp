from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.layouts import row
def get_plots_rock(df1, df2, select_plots, yrange,Y_COL):
	list_plots = []
	source_df1 = ColumnDataSource(data=df1)
	source_df2 = ColumnDataSource(data=df2)
	for pair_data in select_plots:
		list_plots.append(
			__init_plot_rock(pair_data[0][1], pair_data[0][1], Y_COL, source_df1, yrange, '#0000ff'))
		list_plots.append(
			__init_plot_rock(pair_data[1][1], pair_data[1][1], Y_COL, source_df2, yrange, '#008000'))
	return row(list_plots)

def __init_plot_rock(title, x, y, source, yrange, color_title):
	
	plot = figure(plot_width=200, plot_height=400, title=title, toolbar_location=None, tools='ywheel_zoom',
				  active_scroll='ywheel_zoom')
	plot.line(x, y, source=source, line_width=2)
	plot.y_range = yrange
	plot.title.text_color = color_title
	return plot
