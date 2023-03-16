

import argparse
import numpy as np
from floortrans.loaders.svg_loader import FloorplanSVG
from tqdm import tqdm
import os
import cv2
from shutil import copy
import json
from shapely.geometry import Polygon
from matplotlib import pyplot as plt



IMG_NAME_FORMAT = '{:08d}.png'

WALL_ID = 2
RAILING_ID = 8


def log(text, verbose=True):
    if verbose:
        print(text)

cap = cv2.VideoCapture(0)
def printImages(images, shape = (500, 700), window_name = "utils print image"):
    width, height = shape
    concat_images = np.array([])

    for img in images:
        tmp_img = img.copy()
        tmp_img = cv2.resize(tmp_img, (width, height))
        concat_images = tmp_img if not concat_images.any() else np.concatenate((concat_images, tmp_img), axis = 1)
    cv2.imshow(window_name, concat_images)
    cv2.waitKey(0)
    cap.release()
    cv2.destroyAllWindows()

def printPolygons(polygons, shape, fig_size = (5, 7), title = "polygons", reverse = True):
    plot_size = max(shape)
    plt.figure(figsize = fig_size)
    if reverse:
        plt.gca().invert_yaxis()

    for polygon in polygons:
        if(type(polygon) == Polygon):
            x, y = polygon.exterior.xy
        else:
            x, y = polygon.coords.xy
        plt.plot(x, y)
        plt.title(title)
        plt.xticks(np.arange(0, plot_size, 200))
        plt.yticks(np.arange(0, plot_size, 200))
        

    plt.show()

def polygonToArray(polygon, shape, color):
    array = np.zeros(shape)
    coords_array = np.array(polygon.exterior.coords)[:-1].astype(int)
    filled = cv2.fillPoly(array, [coords_array], color)
    return filled





def process_split(out_path, data_path, split, verbose=True):
    split_path = os.path.join(out_path, split)
    boxes_path = os.path.join(split_path, 'boxes')

    os.makedirs(split_path, exist_ok=True)
    os.makedirs(boxes_path, exist_ok=True)

    txt_file = split + '.txt'

    data = FloorplanSVG(data_path, txt_file, format='txt', original_size=False)
    data_enum = tqdm(enumerate(data), desc='Processing example', total=len(data)) if verbose else enumerate(data)
    
    for idx, example in data_enum:
        print(example)
        boxes = {}
        doors_boxes = []
        windows_boxes = []
        house = example['house']

        for poly in house.polys['only_doors']:
            doors_boxes.append(list(poly.exterior.coords))
        for poly in house.polys['only_windows']:
            windows_boxes.append(list(poly.exterior.coords))

        boxes["doors"] = doors_boxes
        boxes["windows"] = windows_boxes
        json_path = os.path.join(boxes_path, str(idx) + ".json")

        with open(json_path, 'w') as fo:
            json.dump(boxes, fo, indent=4)
        # f_mask = os.path.join(mask_path, IMG_NAME_FORMAT.format(idx))
        # cv2.imwrite(f_mask, rooms)


        # src = data.data_folder + data.folders[idx] + data.image_file_name
        # dst = os.path.join(img_path, IMG_NAME_FORMAT.format(idx))
        # copy(src, dst)






def export_walls(out_path, data_path,  verbose=True):
    splits = ('train', 'val',)
    for split in splits:
        log('Exporting [{}] data...'.format(split), verbose=verbose)
        process_split(out_path, data_path, split,  verbose=verbose)






def get_args():
    parser = argparse.ArgumentParser(description='Script for exporting windows and doors masks.')
    parser.add_argument('--data-path', nargs='?', type=str, default='data/cubicasa5k/',
                        help='Path to data directory')
    parser.add_argument('--out', type=str, default='door_windows_export/', help='Output directory')
    parser.add_argument('--quiet', action='store_true', help='Suppress verbose output')
    args = parser.parse_args()
    return args



def main():
    args = get_args()
    export_walls(args.out, args.data_path,  verbose=(not args.quiet))


if __name__ == '__main__':
    main()


