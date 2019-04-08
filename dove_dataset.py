from torch.utils.data import Dataset
import numpy as np

class DOVeDataset(Dataset):
	"""Distance-Only Velodyne Dataset"""

	def __init__(self, root_dir, frames_per_clip = 10, raw:bool=True, granularity:int = 3):
		sf = open(root_dir+"/stats_file.csv", "r")
		self.basepath = root_dir
		self.folders = []
		self.framecounts = []
		self.raw = raw
		self.granularity = granularity
		cumsum = 0
		cumclips = 0
		self.cumulcounts = [0]
		self.cumulclips = [0]
		self.n_folder_clips = []
		self.frames_per_clip = frames_per_clip
		stats_lines = sf.readlines()
		sf.close()
		for line in stats_lines:
			folder, framecount = line.split(",")
			framecount = int(framecount)
			this_n_folder_clips = int(np.ceil(framecount/frames_per_clip))
			self.n_folder_clips.append(this_n_folder_clips)
			cumsum += framecount
			cumclips += this_n_folder_clips
			self.folders.append(folder)
			self.framecounts.append(framecount)
			self.cumulcounts.append(cumsum)
			self.cumulclips.append(cumclips)
			#folder_clip_indices = [j*frames_per_clip+cumsum for j in range(this_n_folder_clips)]
			#folder_clip_lens = [frames_per_clip]*(this_n_folder_clips-1) + [framecount-folder_clip_indices[-1]]


	def readfile(self, fname):
		f = open(fname, "rb")
		frame = f.read()
		n = int(len(frame)/66)
		azumiths = np.empty(n,np.float32)
		distances = np.empty([n,32],np.uint32)
		for i in range(n):
			#this is a single column
			block = frame[i*66:i*66+66]
			azumith = int.from_bytes(block[0:2],byteorder='little',signed=False)
			#print("Azumith: {}".format(azumith/100.0))
			#print("Channels:")
			azumiths[i] = azumith
			for j in range(32):
				dist = int.from_bytes(block[2+j*2:4+j*2],byteorder='little',signed=False)*2
				#print("{}: {} m".format(j,dist))
				distances[i,j] = dist
		if self.raw:
			return {'azumiths' : azumiths, 'distances' : distances}
		else:
			# we create a consistent frame
			# first create output frame
			output = np.full((360*self.granularity,32),4294967295,dtype=np.uint32)
			# convert azumiths to our range
			azumith_inds = np.mod(np.round(azumiths/100*self.granularity),360*self.granularity)
			for az_i in range(len(azumith_inds)):
				az = int(azumith_inds[int(az_i)])
				output[az,:] = np.minimum(output[az,:],distances[az_i,:])
			return output





	def __len__(self):
		return sum(self.n_folder_clips)


	def __getitem__(self, idx):
		#find which folder this index falls in
		for fidx in range(len(self.folders)):
			if self.cumulclips[fidx+1] > idx:
				folder_to_read = self.folders[fidx]
				in_folder_idx_base = (idx-self.cumulclips[fidx])*self.frames_per_clip 
				n_frames = min(self.frames_per_clip, self.framecounts[fidx]-in_folder_idx_base)
				if self.raw:
					clip = []
				else:
					clip = np.empty((n_frames,360*self.granularity,32),dtype=np.uint32)
				for clip_frame_idx in range(n_frames):
					fname = self.basepath+"/"+folder_to_read+"/"+str(in_folder_idx_base+clip_frame_idx)+".dove"
					frame = self.readfile(fname)
					if self.raw:
						clip.append(frame)
					else:
						clip[clip_frame_idx,:,:] = frame
				return clip
