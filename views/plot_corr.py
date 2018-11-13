from bokeh.plotting import figure
def get_figure_corr_plot(source_correlation_plot):
	plot_correlation = figure(plot_width=800, plot_height=500, title='correlation graph')
	plot_correlation.scatter(x='x', y='y', source=source_correlation_plot, line_color='red', size=2)
	print('plot corr')
	return plot_correlation
