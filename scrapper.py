#! /usr/bin/env python3
import time
import os
import io
import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from loggers import info_log, error_log

SE_DICT = {
    'Google': 'https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img',
    'Yandex': 'https://yandex.ru/images/search?text={q}'
}


class ImageScrapper:
    """
    Scraps image from search engine and downloads it to 'Download' dir
    """

    def __init__(self):
        # install webdriver
        self.opts = webdriver.ChromeOptions()
        self.opts.headless = True
        self.opts.add_argument('start-maximized')
        self.opts.add_argument('--disable-blink-features=AutomationControlled')
        self.opts.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.opts.add_experimental_option('useAutomationExtension', False)
        self.webdriver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=self.opts)
        self.webdriver.execute_script('Object.defineProperty(navigator, "webdriver", {get: () => undefined})')
        self.webdriver.execute_cdp_cmd('Network.setUserAgentOverride',
                                       {
                                           "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                                        '(KHTML, like Gecko) '
                                                        'Chrome/83.0.4103.53 Safari/537.36'})

        #  params
        self.search_engine = None
        self.query = None
        self.img_urls = set()
        self.img_count = 0
        self.result_start = 0
        self.sub_dir_name = ''

    def scroll_to_end(self, sleep: int = 2) -> None:
        """
        Scrolls to the bottom

        :param sleep: wait between interactions
        :return: None
        """
        self.webdriver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(sleep)

    def scrape_google(self, query: str, max_urls: int, sleep: int = 2) -> set:
        """
        Search Google for images by given query, return set of image urls

        :param query: what to search
        :param max_urls: number of images
        :param sleep: wait between interactions
        :return: set of urls
        """
        self.search_engine = 'Google'
        search_url = SE_DICT[self.search_engine]
        self.webdriver.get(url=search_url.format(q=query))
        self.query = query

        for char in self.query:
            if char not in r'<>:"/\|?*':
                self.sub_dir_name += char
            else:
                self.sub_dir_name += '_'

        while self.img_count < max_urls:
            self.scroll_to_end()

            #  find all img tags
            thumbnail_images = self.webdriver.find_elements_by_css_selector('img.Q4LuWd')
            thumbnail_img_count = len(thumbnail_images)
            info_log.info(f'Found {thumbnail_img_count} thumbnail images! '
                          f'Extracting links from {self.result_start}:{thumbnail_img_count}...')

            #  try clicking on thumbnail
            for thumbnail_img in thumbnail_images[self.result_start:thumbnail_img_count]:
                try:
                    thumbnail_img.click()
                    time.sleep(sleep)
                except Exception as err:
                    error_log.exception(f'{err}\n')
                    continue

                #  get full img url
                full_images = self.webdriver.find_elements_by_css_selector('img.n3VNCb')
                for full_img in full_images:
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
            self.result_start = len(thumbnail_images)
        # close browser
        self.webdriver.quit()
        return self.img_urls

    def scrape_yandex(self, query: str, max_urls: int, sleep: int = 2) -> set:
        """
        Search Yandex for images by given query, return set of image urls

        :param query: what to search
        :param max_urls: number of images
        :param sleep: wait between interactions
        :return: set of urls
        """
        self.search_engine = 'Yandex'
        search_url = SE_DICT[self.search_engine]
        self.webdriver.get(url=search_url.format(q=query))
        self.query = query

        for char in self.query:
            if char not in r'<>:"/\|?*':
                self.sub_dir_name += char
            else:
                self.sub_dir_name += '_'

        while self.img_count < max_urls:
            time.sleep(sleep)
            #  try clicking on first image
            thumbnail_img = self.webdriver.find_element_by_css_selector('div.serp-item__preview')
            try:
                thumbnail_img.click()
                html_elem = self.webdriver.find_element_by_tag_name('html')  # where to send ARROW_DOWN key call
                for _ in range(max_urls):
                    time.sleep(sleep)
                    full_img = self.webdriver.find_element_by_css_selector('img.MMImage-Origin')
                    if full_img.get_attribute('src') and 'http' in full_img.get_attribute('src'):
                        self.img_urls.add(full_img.get_attribute('src'))
                    self.img_count = len(self.img_urls)
                    html_elem.send_keys(Keys.ARROW_DOWN)
                info_log.info(f'Got {self.img_count} image links!')
            except Exception as err:
                error_log.exception(f'{err}\n')
        # close browser
        self.webdriver.quit()
        return self.img_urls

    def download_image(self) -> str or None:
        """
        Download images from found urls
        :return:  path to subdir to open it in GUI or None if there if no urls found
        """
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
                    error_log.exception(f'ERROR downloading {url} - {err}\n')
            info_log.info(f'Successfully downloaded images by query "{self.query}" from {self.search_engine}\n')
            return sub_dir_path
        else:
            error_log.exception(f'No URLs found by given query {self.query}!\n')
            return None


if __name__ == '__main__':
    scrapper = ImageScrapper()
    scrapper.scrape_google(query='cat', max_urls=2)
    # scrapper.scrape_yandex(query='cat', max_urls=2)
    # scrapper.download_image()
