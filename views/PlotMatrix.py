from bokeh.models import ColumnDataSource, LinearColorMapper
from bokeh.plotting import figure
from bokeh.transform import transform, dodge

BLUE = '#0000ff'
GREEN = '#008000'
class PlotMatrix():
    def __init__(self):
        self.plot_matrix = figure()
    def draw_matrix(self, df, columns_df1, columns_df2, WIDTH_MATRIX, HEIGHT_MATRIX):
        source = ColumnDataSource(df)
        colors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]
        mapper = LinearColorMapper(palette=colors, low=df.rate.min(), high=df.rate.max())

        self.plot_matrix = figure(plot_width=800, plot_height=300, title="",
                                  x_range=list(columns_df2), y_range=list(reversed(columns_df1)),
                                  toolbar_location=None, tools="", x_axis_location="above")
        self.plot_matrix.rect(x="rows", y="columns", width= WIDTH_MATRIX, height= HEIGHT_MATRIX, source=source,
                              line_color=None, fill_color=transform('rate', mapper))
        self.plot_matrix.xaxis.major_label_text_color = BLUE
        self.plot_matrix.yaxis.major_label_text_color = GREEN
        r = self.plot_matrix.text(x=dodge("rows", -0.1, range=self.plot_matrix.x_range),
                                  y=dodge("columns", -0.2, range=self.plot_matrix.y_range), text="rate",
                                  **{"source": df})
        r.glyph.text_font_size = "9pt"

        self.plot_matrix.axis.axis_line_color = None
        self.plot_matrix.axis.major_tick_line_color = None

    def figure(self):
        return self.plot_matrix

    def draw_select_cell(self, name, x, y, height, width):
        self.plot_matrix.rect(x=x, y=y, width=width, height=height, fill_alpha=0, line_color="blue", name=name)

    def delete_select_cell(self, name):
        self.plot_matrix.select(name=name).visible = False
