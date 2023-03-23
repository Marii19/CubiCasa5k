import json
import os
import cv2

data_path = r"C:\Users\treciakiewicz\Documents\Datasets\cubicasa5k_cropped"
data_path_crop = r"C:\Users\treciakiewicz\Documents\Datasets\cubicasa5k"


with open(os.path.join(data_path,"test.json" ), 'r') as f:
    data = json.load(f)
    for idx, p in enumerate(data):
        
        roi = data[p]
        if idx == 399:
            p = p
        else:
            p = p[:-1]
        print(p)
        img = cv2.imread(data_path + p.replace("/", "\\")+"F1_scaled.png")

        cv2.imwrite(data_path_crop + p.replace("/", "\\")+"F1_scaled_orig.png", img)
