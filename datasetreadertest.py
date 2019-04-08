from torch.utils.data import DataLoader
import dove_dataset
import time
from datetime import timedelta

d = dove_dataset.DOVeDataset('.',raw=False)
print("1")
loader = DataLoader(d,batch_size=32,shuffle=True,num_workers=3)
print("2")
start = time.time()
print("3")
fstart = time.time()
for x in loader:
	print(len(x))
	fend = time.time()
	print(timedelta(seconds=fend-fstart))
	fstart = time.time()
end = time.time()

print(timedelta(seconds=end-start))