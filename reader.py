with open("individual_files/1.frame","rb") as f:
	frame = f.read()
	for i in range(int(len(frame)/66)):
		#this is a single column
		block = frame[i*66:i*66+66]
		azumith = int.from_bytes(block[0:2],byteorder='little',signed=False)
		print("Azumith: {}".format(azumith/100.0))
		#print("Channels:")
		for j in range(32):
			dist = int.from_bytes(frame[2+j*2:4+j*2],byteorder='little',signed=False)
			#print("{}: {} m".format(j,dist*2/1000.0))