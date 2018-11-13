import pandas as pd
import numpy as np


def init_data_frame_matrix(df1, df2, columns_df1, columns_df2):
	matrix = {col: [] for col in columns_df1}
	for r in columns_df1:
		for col in columns_df2:
			val_cor = np.corrcoef(df1[r], df2[col])[0, 1]
			matrix[r].append(float(to_fixed(val_cor, 3)))
	data = pd.DataFrame(data=matrix)
	data.index = list(columns_df2)
	data.index.name = 'rows'
	data.columns.name = 'columns'
	df = pd.DataFrame(data.stack(), columns=['rate']).reset_index()
	return df


def to_fixed(num_obj, digits=0):
	return f"{num_obj:.{digits}f}"
