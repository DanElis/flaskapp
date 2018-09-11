import lasio
import csv
import os

data_directory = '/home/wer/diplom/flaskapp/flaskapp/data/newlaslogs'
data_files = os.listdir(data_directory) 
path_to_las_files = "data/newlaslogs/"
path_to_csv_files = "data/newlaslogs/newcsvlogs/"
for las_file in data_files :
	print(1)
	if(las_file.find(".las") != -1):
		las = lasio.read(path_to_las_files + las_file)
		data = las.data.tolist()
		data.insert(0,las.keys())
		file = las_file[:len(las_file)-4]+".csv"
		with open(path_to_csv_files+file, "w", newline="") as csv_file:
			writer = csv.writer(csv_file)
			writer.writerows(data)


 

