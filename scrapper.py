import time
import os
import io
import requests
from PIL import Image
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime


class GoogleImageScrapper:
    """
    Scraps image from google search and downloads it to 'Download' dir
    """
    def __init__(self, query):
        #  install webdriver
        self.opts = webdriver.ChromeOptions()
        self.opts.headless = True
        self.webdriver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=self.opts)

        #  params
        self.search_url = 'https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img'
        self.query = query
        self.img_urls = set()
        self.img_count = 0
        self.result_start = 0

    def get_img_urls(self, max_urls: int, sleep: int = 1, query: str = None) -> set:
        """
        Search Google for images by given query, return set of urls

        :param query: what to search
        :param max_urls: number of images
        :param sleep: sleep between interactions
        :return: set of urls
        """
        if query:
            self.query = query

        def scroll_to_end():
            self.webdriver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(sleep)

        self.webdriver.get(url=self.search_url.format(q=self.query))

        while self.img_count < max_urls:
            scroll_to_end()

            #  find all img tags
            thumbnail_imgs = self.webdriver.find_elements_by_css_selector('img.Q4LuWd')
            thumbnail_img_count = len(thumbnail_imgs)
            print(f'Found {thumbnail_img_count} thumbnail images! '
                  f'Extracting links from {self.result_start}:{thumbnail_img_count}...')

            #  try clicking on thumbnail
            for thumbnail_img in thumbnail_imgs[self.result_start:thumbnail_img_count]:
                try:
                    thumbnail_img.click()
                    time.sleep(sleep)
                except Exception as err:
                    print(err)
                    continue

                #  get full img url
                full_imgs = self.webdriver.find_elements_by_css_selector('img.n3VNCb')
                for full_img in full_imgs:
                    if full_img.get_attribute('src') and 'http' in full_img.get_attribute('src'):
                        self.img_urls.add(full_img.get_attribute('src'))
                self.img_count = len(self.img_urls)

                #  exit while loop
                if len(self.img_urls) >= max_urls:
                    print(f'Got {self.img_count} image links! Closing...')
                    break

            #  loads more images
            else:
                print(f'Found {len(self.img_urls)} image links, looking for more...')
                time.sleep(sleep)
                load_more_button = self.webdriver.find_element_by_css_selector('.mye4qd')
                if load_more_button:
                    self.webdriver.execute_script('document.querySelector(".mye4qd").click();')
            self.result_start = len(thumbnail_imgs)
        self.webdriver.quit()
        print('Bye!')
        return self.img_urls

    def download_image(self):
        if self.img_urls:
            #  create dirs
            dir_path = os.path.join(os.path.dirname(__file__), 'Download')
            sub_dir_path = os.path.join(dir_path, self.query.capitalize())
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            if not os.path.exists(sub_dir_path):
                os.makedirs(sub_dir_path)

            #  create image files
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
                    print(f'ERROR downloading {url} - {err}')


if __name__ == '__main__':
    my_parser = GoogleImageScrapper(query='cat')
    my_parser.get_img_urls(max_urls=1)
    my_parser.download_image()
