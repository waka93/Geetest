from config import *
from bilibili_geetest import BilibiliGeetestCracker

import time


def main():
    xpath_to_slider = '//*[@id="gc-box"]/div/div[3]/div[2]'
    xpath_to_image = '//*[@id="gc-box"]/div/div[1]/div[2]/div[1]/a[2]'
    xpath_to_slice = '//*[@id="gc-box"]/div/div[1]/div[2]/div[1]/a[1]/div[2]'
    cracker = BilibiliGeetestCracker(url=URL, xpath_to_slider=xpath_to_slider, xpath_to_image=xpath_to_image, xpath_to_slice=xpath_to_slice)
    cracker.crack()
    time.sleep(1)
    cracker.close()


if __name__ == '__main__':
    main()

