import re
import os 

log_file_path = ""

counter = 0
flag = 0
path_counter = 1 
startpoint = ''
endpoint = ''
destName = ''
fileList = ["", ""]
for file in os.listdir('.'):
	if "timing_by_pairs" in str(file):
		if(len(file.split('_')) > 2 ):
			destName = file.split('.')[0] + '.csv'
       		print("Running on file: " + str(file))
        	with open (file, "r") as file:				
				print("Running on file: " + str(file))
				for line in file: 
					file = open(destName, 'a+')
					if re.search(r'Startpoint:', line):
						startpoint = line.split()[2]
					if re.search(r'Endpoint:', line):
						endpoint = line.split()[2]
					if re.search(r'Data Path', line):
						delay = line.split()[2]
						path_delay = "Path " + str(path_counter) + "," + startpoint + "," + endpoint + "," + delay + "\n"
						#print(path_delay)
						file.write(path_delay)
					if (line[:1] == '#'):
						counter = counter + 1
						if(counter<=4):
							flag = 1
							continue
					elif (counter == 4 or (counter == 0 and flag == 1)):
						counter = 0
						interval = line.split()
						edge = interval[3]
						cell = interval[4]
						fanout = interval[5]
						load = interval[6]
						trans = interval[7]
						delay = interval[8]
						if(cell != "(arrival)" and cell != "(port)" and cell != "(net)"):
							line = edge + "," + cell + "," + fanout + "," + load + "," + delay + "," + trans  + "\n"   
							#print(line)
							file.write(line)
					elif (counter == 1):
						path_counter = path_counter + 1 
						counter = 0
						flag = 0

				file.close()
