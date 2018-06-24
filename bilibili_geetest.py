from selenium.webdriver.common.by import By

from PIL import Image

from config import *
from geetest_cracker import GeetestCracker

import numpy as np

import re
import requests
import io
import uuid


class BilibiliGeetestCracker(GeetestCracker):
    def get_slice(self):
        slice_element = self.driver.find_element(By.XPATH, self.xpath_to_slice)
        style = slice_element.get_attribute('style')
        url = re.findall('url\("(.*?)"\)',style)[0]
        resp = requests.get(url, headers=HEADERS)
        self.slice_image = Image.open(io.BytesIO(resp.content))
        return self

    def get_steps(self):
        gt_image = self.gt_image.convert('L')  # convert to grayscale
        sliced_gt_image = self.sliced_gt_image.convert('L')
        slice_image = self.slice_image.convert('L')

        gt_image.save('{}.png'.format(uuid.uuid4().hex))
        sliced_gt_image.save('{}.png'.format(uuid.uuid4().hex))
        slice_image.save('{}.png'.format(uuid.uuid4().hex))

        gt_image = np.array(gt_image.getdata()).reshape(self.size['height'], self.size['width'])
        sliced_gt_image = np.array(sliced_gt_image.getdata()).reshape(self.size['height'], self.size['width'])
        slice_image = np.array(slice_image.getdata()).reshape(slice_image.size[1], slice_image.size[0])

        diff = np.abs(gt_image - sliced_gt_image)
        diff[diff < PIXEL_THRESHOLD] = 0
        diff_img = Image.fromarray(diff, 'L')
        diff_img.save('{}.png'.format(uuid.uuid4().hex))
        diff = np.sum(diff, axis=0)
        slice_image[slice_image < 5] = 0
        slice_image = np.sum(slice_image, axis=0)
        boundary = [i for i in range(len(slice_image)-1) if slice_image[i] > 0 and slice_image[i+1] == 0]

        edge = [i for i in range(1, len(diff)-1) if diff[i-1] > 0 and diff[i] > 0 and diff[i+1] == 0]

        print(diff)
        print(boundary[0])
        print(edge)
        if len(edge) > 2 or len(boundary) > 1:
            print('Cracking Failed. Please Try Again.')
            return 0

        return edge[-1] - boundary[0] - 3

