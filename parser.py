import sys  
import pcapy
import base64

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


pc = pcapIter('output.pcap')
counts = []
trimmed = bytearray(0)
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
			trimmed += channel_data
			if azumith_i < azumith_prev:
				#it flipped around
				count += 1
				counts.append(count)
				newFile = open("individual_files/{}.frame".format(frame_count),"wb")
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
trimmed_file = open("trimmed.bin","wb")
trimmed_file.write(bytes(trimmed))
trimmed_file.close()