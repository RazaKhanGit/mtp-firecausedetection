import cv2
import numpy as np
from skimage import io
from skimage.color import rgb2lab, rgb2ycbcr

def get_img(img_path):
    rgb = io.imread(img_path)
    lab = rgb2lab(rgb)
    ycbcr = rgb2ycbcr(rgb)
    l, a, b = cv2.split(lab)
    r, g, b = cv2.split(rgb)
    y, cb, cr = cv2.split(ycbcr)

    l_mean, a_mean, b_mean = cv2.mean(lab)[:-1]


    lab_rule_1 = l >= l_mean
    lab_rule_2 = a >= a_mean
    lab_rule_3 = b >= b_mean
    lab_rule_4 = b >= a_mean
    lab_satisfied = lab_rule_1 & lab_rule_2 & lab_rule_3 & lab_rule_4

    ycbcr_rule_1 = (r >= g) & (g > b)
    ycbcr_rule_2 = (r > 190) & (g > 100) & (b < 140)
    ycbcr_rule_3 = y >= cb
    ycbcr_rule_4 = cr >= cb
    ycbcr_satisfied = (ycbcr_rule_1 & ycbcr_rule_2) | (ycbcr_rule_3 & ycbcr_rule_4)



    lab_convert = np.uint8(lab_satisfied) * 255
    ycbcr_convert = np.uint8(ycbcr_satisfied) * 255

    converted = lab_convert & ycbcr_convert
    satisfied = lab_satisfied & ycbcr_satisfied

    return converted, satisfied, r

    # pixel_count = (lab_satisfied & ycbcr_satisfied).sum()
    # color = ((lab_satisfied & ycbcr_satisfied)*r).sum()/pixel_count
    # frame_copy = np.repeat(converted[:, :, np.newaxis], 3, axis=2)


def get_area(img_path): 
    _, satisfied, _ = get_img(img_path)
    total_area = satisfied.shape[0]*satisfied.shape[1]
    return 600*satisfied.sum()/total_area

def get_color(img_path):
    _, satisfied, r = get_img(img_path)
    if satisfied.sum() == 0:
        return 0
    return 300*(satisfied*r).sum()/(256*satisfied.sum())

