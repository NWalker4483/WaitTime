import pandas as pd 
# https://www.crowdhuman.org
class BOXLoader():
    def __init__(self, fname):
        self.data = pd.read_csv(fname)
        self.frame_num = 0 

    def update(self, frame = None):
        results = self.data.loc[self.data['frame_num'] == self.frame_num]
        self.frame_num += 1 
        boxes = [[int(float(i.strip())) for i in result[1:][:-1].split()] for result in results["bbox"]]  
        return list(zip(boxes,results["class"], results["id"]))
