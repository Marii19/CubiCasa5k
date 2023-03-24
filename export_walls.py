import argparse
import numpy as np
from floortrans.loaders.svg_loader import FloorplanSVG
from tqdm import tqdm
import os
import cv2
from shutil import copy
import json



IMG_NAME_FORMAT = '{:08d}.png'

WALL_ID = 2
RAILING_ID = 8


def log(text, verbose=True):
    if verbose:
        print(text)

def polygonToArray(polygon, shape):
    array = np.zeros(shape)
    coords_array = np.array(polygon.exterior.coords)[:-1].astype(int)
    filled = cv2.fillPoly(array, [coords_array], 255.0)
    return filled

def draw_svg_walls(walls):
    for wall in walls:
        a = 10

def process_split(out_path, data_path, split, include_railing=True, verbose=True):
    split_path = os.path.join(out_path, split)
    img_path = os.path.join(split_path, 'images')
    mask_path = os.path.join(split_path, 'masks')
    rois_path = os.path.join(split_path, 'rois.json')

    os.makedirs(split_path, exist_ok=True)
    os.makedirs(img_path, exist_ok=True)
    os.makedirs(mask_path, exist_ok=True)

    txt_file = split + '.txt'
    rois_file = split + '.json'

    data = FloorplanSVG(data_path, txt_file, rois_file, format='txt', original_size=False)
    data_enum = tqdm(enumerate(data), desc='Processing example', total=len(data)) if verbose else enumerate(data)
    rois = {}
    for idx, example in data_enum:

        house = example['house']

        heatmaps = example["heatmaps"]
        tensor = house.get_tensor()
        walls = tensor[-2]

        heatmaps_mask = np.zeros(walls.shape)

        for heatmap in heatmaps:
            data = heatmaps[heatmap]
            for p in data:
                x, y = p
                heatmaps_mask[y-2:y+2, x-2:x+2] = 255

        cv2.imwrite(split + "heatmap.png", heatmaps_mask)
        

        # walls = (walls **2)
        # for i in range(walls.shape[0]):
        #     for j in range(walls.shape[1]):
        #         if(walls[i][j] != 0):
        #             walls[i][j] += 100
        # print("SUM: ", walls.sum())

        # heatmaps_mask = np.zeros(walls.shape)
        
        # heatmaps = example['heatmaps']
        # data = heatmaps[20]
        # for p in data:
        #     x, y = p
        #     heatmaps_mask[x-2:x+2, y-2:y+2] = 255
        # cv2.imwrite(split + "heatmap.png", heatmaps_mask)
        # # house = example['house']
        # # print("Folder is ", example['folder'])
        # # heatmaps = house.get_heatmaps()
        
  
        # # # walls = house.walls
        # mask = np.zeros(walls.shape, dtype=np.uint8)
        # mask[walls == WALL_ID] = 255
        # if include_railing:
        #     mask[walls == RAILING_ID] = 255
        # cv2.imwrite(split + "test_img.png", walls)
        # heatmap_mask = np.zeros(mask.shape) 

        # f_mask = os.path.join(mask_path, str(idx) + ".png")
        # cv2.imwrite(f_mask, mask)

        # src = data.data_folder + data.folders[idx] + data.image_file_name
        # dst = os.path.join(img_path, IMG_NAME_FORMAT.format(idx))
        # copy(src, dst)
        return


def export_walls(out_path, data_path, include_railing=True, verbose=True):
    splits = ('train', 'test',)
    for split in splits:
        log('Exporting [{}] data...'.format(split), verbose=verbose)
        process_split(out_path, data_path, split, include_railing=include_railing, verbose=verbose)






def get_args():
    parser = argparse.ArgumentParser(description='Script for exporting wall masks.')
    parser.add_argument('--data-path', nargs='?', type=str, default='data/cubicasa5k/',
                        help='Path to data directory')
    parser.add_argument('--out', type=str, default='wall_export/', help='Output directory')
    parser.add_argument('--quiet', action='store_true', help='Suppress verbose output')
    parser.add_argument('--ignore-railing', action='store_true', help='Do not consider railing as walls')



    args = parser.parse_args()
    return args




def main():
    args = get_args()
    export_walls(args.out, args.data_path, include_railing=(not args.ignore_railing), verbose=(not args.quiet))


if __name__ == '__main__':
    main()


