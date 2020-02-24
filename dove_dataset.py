from torch.utils.data import Dataset
import numpy as np

class DOVeDataset(Dataset):
	"""Distance-Only Velodyne Dataset"""

	def __init__(self, root_dir, idxmapping, length, cpf, ccpf, folders, framecounts, frames_per_clip = 10, raw:bool=True, granularity:int = 3, d_max: float = 50):
		self.length = length
		self.idxmapping = idxmapping
		self.basepath = root_dir
		self.folders = folders
		self.framecounts = framecounts
		self.raw = raw
		self.granularity = granularity
		self.cumulclips = ccpf
		self.n_folder_clips = cpf
		self.frames_per_clip = frames_per_clip
		self.d_max = d_max
		self.order = [31,29,27,25,23,21,19,17,15,13,11,9,7,5,3,1,30,28,26,24,22,20,28,16,14,12,10,8,6,4,2,0]
		
	def readfile(self, fname):
		f = open(fname, "rb")
		frame = f.read()
		n = int(len(frame)/66)
		azumiths = np.empty(n,np.float32)
		distances = np.empty([n,32],np.int32)
		for i in range(n):
			#this is a single column
			block = frame[i*66:i*66+66]
			azumith = int.from_bytes(block[0:2],byteorder='little',signed=False)
			#print("Azumith: {}".format(azumith/100.0))
			#print("Channels:")
			azumiths[i] = azumith
			for o,j in zip(self.order,range(32)): #range(32):
				#dist = int.from_bytes(block[2+j*2:4+j*2],byteorder='little',signed=False)*2
				dist = int.from_bytes(block[2+o*2:4+o*2],byteorder='little',signed=False)*2
				#print("{}: {} m".format(j,dist))
				distances[i,j] = dist
		if self.raw:
			return {'azumiths' : azumiths, 'distances' : distances}
		else:
			# we create a consistent frame
			# first create output frame
			output = np.full((360*self.granularity,32),int(self.d_max*1000),dtype=np.uint32)
			# convert azumiths to our range
			azumith_inds = np.mod(np.round(azumiths/100*self.granularity),360*self.granularity)
			for az_i in range(len(azumith_inds)):
				az = int(azumith_inds[int(az_i)])
				output[az,:] = np.minimum(output[az,:],distances[az_i,:])
				#print((np.min(output[az,:]),np.min(distances[az_i,:])))
			return output


	def __len__(self):
		return self.length


	def __getitem__(self, idx):
		#by performing the index mapping right away all the other math stays the same as normal
		idx = int(self.idxmapping[idx])
		#find which folder this index falls in
		for fidx in range(len(self.folders)):
			if self.cumulclips[fidx+1] > idx:
				folder_to_read = self.folders[fidx]
				in_folder_idx_base = (idx-self.cumulclips[fidx])*self.frames_per_clip 
				n_frames = min(self.frames_per_clip, self.framecounts[fidx]-in_folder_idx_base)
				if self.raw:
					clip = []
				else:
					clip = np.zeros((10,360*self.granularity,32),dtype=np.int32)
				for clip_frame_idx in range(n_frames):
					fname = self.basepath+"/"+folder_to_read+"/"+str(in_folder_idx_base+clip_frame_idx)+".dove"
					frame = self.readfile(fname)
					if self.raw:
						clip.append(frame)
					else:
						clip[clip_frame_idx,:,:] = frame
				return clip


def CreateDOVeDatasets(root_dir, frames_per_clip = 10, raw:bool=False, granularity:int = 3, train_pct:float = 0.8, val_pct:float = 0.1, test_pct:float = 0.1):
	if not train_pct+val_pct+test_pct == 1.0:
		raise Exception('Percents don\'t sum to 1!')
	else:
		#we need to evaluate the same set of folders and stuff.
		sf = open(root_dir+"/stats.csv", "r")
		stats_lines = sf.readlines()
		sf.close()
		folders = []
		framecounts = []
		raw = raw
		granularity = granularity
		cumclips = 0
		cumulclips = [0]
		n_folder_clips = []
		frames_per_clip = frames_per_clip
		for line in stats_lines:
			folder, framecount = line.split(",")
			framecount = int(framecount)
			this_n_folder_clips = int(np.ceil(framecount/frames_per_clip))
			n_folder_clips.append(this_n_folder_clips)
			cumclips += this_n_folder_clips
			folders.append(folder)
			framecounts.append(framecount)
			cumulclips.append(cumclips)
		#now we have
		#in cumulclips, the start clip index for each
		#in n_folder_clips = the number of clips in each folder
		total_clips = sum(n_folder_clips)
		indices = np.array(range(total_clips),dtype=np.int32)
		np.random.shuffle(indices)
		n_train = int(total_clips*train_pct)
		n_val = int(total_clips*val_pct)
		s_test = n_train + n_val
		n_test = int(total_clips*test_pct)
		#root_dir, idxmapping, length, cpf, ccpf, folders, framecounts, frames_per_clip, raw, granularity
		train_dataset = DOVeDataset(root_dir, indices[:n_train], n_train, n_folder_clips, cumulclips, folders, framecounts, frames_per_clip, raw, granularity)
		val_dataset = DOVeDataset(root_dir, indices[n_train:s_test], n_val, n_folder_clips, cumulclips, folders, framecounts, frames_per_clip, raw, granularity)
		test_dataset = DOVeDataset(root_dir, indices[s_test:], n_test, n_folder_clips, cumulclips, folders, framecounts, frames_per_clip, raw, granularity)
		return (train_dataset, val_dataset, test_dataset)
