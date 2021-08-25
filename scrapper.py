#! /usr/bin/env python3
import time
import os
import io
import requests
from PIL import Image
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from loggers import info_log, error_log
SE_DICT = {
    'Google': 'https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img'
}


class SearchEngineImageScrapper:
    """
    Scraps image from search engine and downloads it to 'Download' dir
    """

    def __init__(self, search_engine: str):
        #  install webdriver
        self.opts = webdriver.ChromeOptions()
        self.opts.headless = True
        self.webdriver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=self.opts)

        #  params
        self.search_engine = search_engine
        self.search_url = SE_DICT[search_engine]
        self.img_urls = set()
        self.img_count = 0
        self.result_start = 0
        self.query = None
        self.sub_dir_name = ''

    def get_img_urls(self, query: str, max_urls: int, sleep: int = 1) -> set:
        """
        Search Google for images by given query, return set of image urls

        :param query: what to search
        :param max_urls: number of images
        :param sleep: sleep between interactions
        :return: set of urls
        """

        def scroll_to_end():
            self.webdriver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(sleep)

        self.webdriver.get(url=self.search_url.format(q=query))
        self.query = query

        for char in self.query:
            if char not in r'<>:"/\|?*':
                self.sub_dir_name += char
            else:
                self.sub_dir_name += '_'

        while self.img_count < max_urls:
            scroll_to_end()

            #  find all img tags
            thumbnail_imgs = self.webdriver.find_elements_by_css_selector('img.Q4LuWd')
            thumbnail_img_count = len(thumbnail_imgs)
            info_log.info(f'Found {thumbnail_img_count} thumbnail images! '
                          f'Extracting links from {self.result_start}:{thumbnail_img_count}...')

            #  try clicking on thumbnail
            for thumbnail_img in thumbnail_imgs[self.result_start:thumbnail_img_count]:
                try:
                    thumbnail_img.click()
                    time.sleep(sleep)
                except Exception as err:
                    error_log.exception(err)
                    continue

                #  get full img url
                full_imgs = self.webdriver.find_elements_by_css_selector('img.n3VNCb')
                for full_img in full_imgs:
                    if full_img.get_attribute('src') and 'http' in full_img.get_attribute('src'):
                        self.img_urls.add(full_img.get_attribute('src'))
                self.img_count = len(self.img_urls)

                #  exit while loop
                if len(self.img_urls) >= max_urls:
                    info_log.info(f'Got {self.img_count} image links!')
                    break

            #  loads more images
            else:
                info_log.info(f'Found {len(self.img_urls)} image links, looking for more...')
                time.sleep(sleep)
                load_more_button = self.webdriver.find_element_by_css_selector('.mye4qd')
                if load_more_button:
                    self.webdriver.execute_script('document.querySelector(".mye4qd").click();')
            self.result_start = len(thumbnail_imgs)
        self.webdriver.quit()
        info_log.info('Success')
        return self.img_urls

    def download_image(self):
        if self.img_urls:
            #  create dirs
            dir_path = os.path.join(os.path.dirname(__file__), 'Download')
            sub_dir_path = os.path.join(dir_path, self.sub_dir_name.capitalize())
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            if not os.path.exists(sub_dir_path):
                os.makedirs(sub_dir_path)

            #  save image files
            for url in self.img_urls:
                file_name = str(datetime.now().strftime('%H-%M-%S.%f'))
                try:
                    file_path = os.path.join(sub_dir_path, file_name)
                    image_content = requests.get(url=url).content
                    image_file = io.BytesIO(image_content)
                    image = Image.open(image_file).convert('RGB')
                    with open(file=f'{file_path}.jpeg', mode='wb') as file:
                        image.save(file, 'JPEG')
                except Exception as err:
                    error_log.exception(f'ERROR downloading {url} - {err}')
            print(sub_dir_path)
            return sub_dir_path
        else:
            error_log.exception('No URLs found!')
            return None


if __name__ == '__main__':
    google_parser = SearchEngineImageScrapper(search_engine='Google')
    google_parser.get_img_urls(query='cat', max_urls=1)
    google_parser.download_image()
