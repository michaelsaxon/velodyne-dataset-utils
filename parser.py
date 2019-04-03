import sys, os, pcapy

class pcapIter:
	def __init__(self, fname):
		self.pcapy_obj = pcapy.open_offline(fname)

	def __iter__(self):
		return self

	def __next__(self):
		header, packet = self.pcapy_obj.next()
		if len(packet) == 0:
			raise StopIteration
		else:
			return packet

def pcap_to_dataset(pcap_file:str, scene_name:str):
	try:
		os.stat(scene_name)
	except:
		os.mkdir(scene_name)
	pc = pcapIter(pcap_file)
	azumith_prev = 0
	count = 0
	frame_count = 0
	current_frame = bytearray(0)
	for packet in pc:
		if len(packet) == 1248:
			for detection_index in range(12):
				detection_base = 42+detection_index*100
				azumith = packet[detection_base + 2:detection_base + 4]
				channel_data = azumith
				azumith_i = int.from_bytes(azumith, byteorder='little', signed=False)/100.0
				for channel_index in range(32):
					channel_base = detection_base + 4 + 3*channel_index
					channel_data += packet[channel_base:channel_base+2]
				if azumith_i < azumith_prev:
					#it flipped around
					count += 1
					newFile = open(scene_name+"/{}.dove".format(frame_count),"wb")
					newFile.write(bytes(current_frame))
					newFile.close()
					current_frame = bytearray(channel_data)
					#print("{}->{}".format(azumith_prev,azumith_i))
					#print("Completed count {}".format(count))
					print("Frame {} complete".format(frame_count))
					frame_count += 1				
					count = 0
				else:
					count += 1
					current_frame += channel_data
				#print(azumith_i-azumith_prev)
				azumith_prev = azumith_i
	return frame_count

def main():
	SCENE_NAME = "individual_files"
	count = pcap_to_dataset(pcap_file="output.pcap", scene_name=SCENE_NAME)
	with open("stats.csv","w+") as statfile:
		statfile.write(SCENE_NAME+","+str(count)+"\n")
		statfile.close()

if __name__ == "__main__":
    main()
