import lmdb
import pickle
import torch
from torch.utils.data import Dataset
import cv2
import numpy as np
from numpy import genfromtxt
from floortrans.loaders.house import House
import os
import json


class FloorplanSVG(Dataset):
    def __init__(self, data_folder, data_file, rois_file, is_transform=True,
                 augmentations=None, img_norm=True, format='txt',
                 original_size=False, lmdb_folder='cubi_lmdb/'):
        self.img_norm = img_norm
        self.is_transform = is_transform
        self.augmentations = augmentations
        self.get_data = None
        self.original_size = original_size
        self.image_file_name = '/F1_scaled.png'
        self.org_scaled_image_file_name = '/F1_scaled_orig.png'
        self.org_image_file_name = '/F1_original.png'
        self.svg_file_name = '/model.svg'
        self.roi_file_path = os.path.join(data_folder, rois_file)

        if format == 'txt':
            self.get_data = self.get_txt
        if format == 'lmdb':
            self.lmdb = lmdb.open(data_folder+lmdb_folder, readonly=True,
                                  max_readers=8, lock=False,
                                  readahead=True, meminit=False)
            self.get_data = self.get_lmdb
            self.is_transform = False

        self.data_folder = data_folder
        # Load txt file to list
        self.folders = genfromtxt(data_folder + data_file, dtype='str')

        with open(self.roi_file_path, 'r') as f:
            self.rois = json.load(f)


    def __len__(self):
        """__len__"""
        return len(self.folders)

    def __getitem__(self, index):
        sample = self.get_data(index)

        if self.augmentations is not None:
            sample = self.augmentations(sample)
            
        if self.is_transform:
            sample = self.transform(sample)

        return sample

    def get_txt(self, index):
        fplan = cv2.imread(self.data_folder + self.folders[index] + self.image_file_name)
        fplan = cv2.cvtColor(fplan, cv2.COLOR_BGR2RGB)  # correct color channels
        fplan_orig = cv2.imread(self.data_folder + self.folders[index] + self.org_scaled_image_file_name)
        fplan_orig = cv2.cvtColor(fplan_orig, cv2.COLOR_BGR2RGB)  # correct color channels
        height, width, nchannel = fplan_orig.shape
        fplan = np.moveaxis(fplan, -1, 0)

        # Getting labels for segmentation and heatmaps
        roi = self.rois[self.folders[index]+ '\n']
        house = House(self.data_folder + self.folders[index] + self.svg_file_name, height, width, roi)
        # Combining them to one numpy tensor
        label = torch.tensor(house.get_segmentation_tensor().astype(np.float32))
        
        heatmaps = house.get_heatmap_dict()

        coef_width = 1
        if self.original_size:
            print("--------------------------original_size---------------------------------")
            fplan = cv2.imread(self.data_folder + self.folders[index] + self.org_image_file_name)
            fplan = cv2.cvtColor(fplan, cv2.COLOR_BGR2RGB)  # correct color channels
            height_org, width_org, nchannel = fplan.shape
            fplan = np.moveaxis(fplan, -1, 0)
            label = label.unsqueeze(0)
            label = torch.nn.functional.interpolate(label,
                                                    size=(height_org, width_org),
                                                    mode='nearest')
            label = label.squeeze(0)

            coef_height = float(height_org) / float(height)
            coef_width = float(width_org) / float(width)
            for key, value in heatmaps.items():
                heatmaps[key] = [(int(round(x*coef_width)), int(round(y*coef_height))) for x, y in value]

        img = torch.tensor(fplan.astype(np.float32))

        heatmaps = self.fix_heatmaps(heatmaps, roi, height, width)
        sample = {'image': img, 'label': label, 'folder': self.folders[index],
                  'heatmaps': heatmaps, 'scale': coef_width, 'house': house}

        return sample

    def fix_heatmaps(self, heatmaps, roi, height, width):
        xmin, ymin, w, h = roi
        xmax, ymax = xmin + w, ymin + h


        for heatmap in heatmaps:
            heatmap_mask = np.zeros((height, width))
            data = heatmaps[heatmap]
            data_new = []
            for p in data:
                y, x = p
                heatmap_mask[x, y] = 255
            
            heatmap_mask = heatmap_mask[ymin:ymax, xmin:xmax]
            non_zero = np.where(heatmap_mask != 0)
            if(len(non_zero[0]) != 0):
                for idx, x in enumerate(non_zero[0]):
                    new_point = (non_zero[1][idx], x)
                    data_new.append(new_point)
            heatmaps[heatmap] = data_new

        return heatmaps



    def get_lmdb(self, index):
        key = self.folders[index].encode()
        with self.lmdb.begin(write=False) as f:
            data = f.get(key)

        sample = pickle.loads(data)
        return sample

    def transform(self, sample):
        fplan = sample['image']
        # Normalization values to range -1 and 1
        fplan = 2 * (fplan / 255.0) - 1

        sample['image'] = fplan

        return sample
