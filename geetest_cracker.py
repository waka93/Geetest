from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains

from PIL import Image

from config import *
from errors import *

import numpy as np

import time
import io
import uuid


class GeetestCracker:
    """
    Geetest Cacker Base Class
    Action Order: open_page -> view_gt_image -> get_gt_image -> click_and_hold
    -> get_sliced_gt_image -> get_slice -> drag_slider
    """
    def __init__(self, driver='Chrome', url=None, xpath_to_slider=None, xpath_to_image=None, xpath_to_slice=None):
        """
        :param driver: browser driver, default Chrome
        :param url: url to login page
        :param xpath_to_slider: xpath to the slider button
        :param xpath_to_image: xpath to the geetest captcha image
        :param xpath_to_image: xpath to the geetest moving slice
        """
        self.driver = eval('webdriver.{}()'.format(driver))
        self.url = url
        self.xpath_to_slider = xpath_to_slider
        self.xpath_to_image = xpath_to_image
        self.xpath_to_slice = xpath_to_slice
        self.element = None
        self.action_chains = ActionChains(self.driver)
        self.location = None
        self.size = None
        self.gt_image = None
        self.sliced_gt_image = None
        self.slice_image = None

    def open_page(self):
        """
        open page with driver and wait until geetest captcha has been loaded
        :return:
        """
        if not self.url or not self.xpath_to_slider or not self.xpath_to_image:
            raise ParameterNotSetError

        self.driver.get(self.url)
        self.element = WebDriverWait(self.driver, PAGE_LOADING_TIME).until(
            EC.presence_of_element_located((By.XPATH, self.xpath_to_slider))
        )

        return self

    def view_gt_image(self):
        """
        view the whole geetest image by moving cursor to slider
        """
        if not self.element:
            raise ElementNotLocatedError
        self.action_chains.move_to_element(self.element)
        self.action_chains.perform()

        time.sleep(IMAGE_LOADING_TIME)

        return self

    def get_gt_image(self):
        """
        get two geetest images, one full image and one with a slice on the image
        :return:
        """
        gt_image_element = self.driver.find_element(By.XPATH, self.xpath_to_image)
        self.location = gt_image_element.location
        self.size = gt_image_element.size

        left = self.location['x']
        top = self.location['y']
        right = left + self.size['width']
        bottom = top + self.size['height']

        full_page = self.driver.get_screenshot_as_png()
        full_page = Image.open(io.BytesIO(full_page))
        self.gt_image = full_page.crop((left, top, right, bottom))
        # self.gt_image.save('{}.png'.format(uuid.uuid4().hex))

        return self

    def click_and_hold(self):
        """
        click and hold the slider button to view the image with slice
        :return:
        """
        time.sleep(IMAGE_LOADING_TIME)

        self.action_chains.click_and_hold(self.element)
        self.action_chains.perform()

        return self

    def get_sliced_gt_image(self):
        left = self.location['x']
        top = self.location['y']
        right = left + self.size['width']
        bottom = top + self.size['height']
        full_page = self.driver.get_screenshot_as_png()
        full_page = Image.open(io.BytesIO(full_page))
        self.sliced_gt_image = full_page.crop((left, top, right, bottom))
        # self.sliced_gt_image.save('{}.png'.format(uuid.uuid4().hex))

        return self

    def get_slice(self):
        raise NotImplementedError('Method {} Is Not Defined'.format(self.get_slice.__qualname__))

    def drag_slider(self):
        self.action_chains.drag_and_drop_by_offset(self.element, xoffset=self.get_steps(), yoffset=0)
        self.action_chains.perform()

        return self

    def get_steps(self):
        """
        calculate how many pixels the slider has to move to complete the geetest
        :param full_image: Image
        :param sliced_image: Image
        :return: int
        """
        gt_image = self.gt_image.convert('L')  # convert to grayscale
        sliced_gt_image = self.sliced_gt_image.convert('L')
        slice_image = self.slice_image.convert('L')

        # gt_image.save('{}.png'.format(uuid.uuid4().hex))
        # sliced_gt_image.save('{}.png'.format(uuid.uuid4().hex))
        # slice_image.save('{}.png'.format(uuid.uuid4().hex))

        gt_image = np.array(gt_image.getdata()).reshape(self.size['height'], self.size['width'])
        sliced_gt_image = np.array(sliced_gt_image.getdata()).reshape(self.size['height'], self.size['width'])
        slice_image = np.array(slice_image.getdata()).reshape(slice_image.size[1], slice_image.size[0])

        diff = np.abs(gt_image - sliced_gt_image)
        diff[diff < PIXEL_THRESHOLD] = 0
        diff_img = Image.fromarray(diff, 'L')
        # diff_img.save('{}.png'.format(uuid.uuid4().hex))
        diff = np.sum(diff, axis=0)
        slice_image[slice_image < 5] = 0
        slice_image = np.sum(slice_image, axis=0)
        boundary = [i for i in range(len(slice_image)-1) if slice_image[i] > 0 and slice_image[i+1] == 0]

        edge = [i for i in range(1, len(diff)-1) if diff[i-1] > 0 and diff[i] > 0 and diff[i+1] == 0]

        if len(edge) > 2 or len(boundary) > 1:
            print('Cracking Failed. Please Try Again.')
            return 0

        return edge[1]-boundary[0]

    def crack(self):
        self.open_page().view_gt_image().get_gt_image().click_and_hold().get_sliced_gt_image().get_slice().drag_slider()

    def close(self):
        self.driver.quit()