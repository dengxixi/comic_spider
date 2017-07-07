# -*- encoding: utf-8 -*-

__author__ = 'xgj1010'
__date__ = '2017/6/26 21:50'
import re
import os
from urllib import request, parse

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


browser = webdriver.PhantomJS()
wait = WebDriverWait(browser, 10)
browser.set_window_size(1400, 900)


user_agent = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.76 Mobile Safari/537.36'

map_url = 'http://www.fzdm.com/map'  # 入口


def get_page(url):
    # 开始请求
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else: return None
    except RequestException:
        return None


def get_comic_url(html):
    # 获取漫画url
    soup = BeautifulSoup(html, 'lxml')
    comic_urls = soup.select('#map ul li a')
    comic_url_dict = {}
    for comic_url in comic_urls:
        url = comic_url.get('href')
        title = comic_url.text
        comic_url_dict[title] = 'http:' + url
    return comic_url_dict


def get_comic_chapter_url(**kwargs):
    # 获取漫画每一话的url
    for key in kwargs:
        html = get_page(kwargs[key])
        soup = BeautifulSoup(html, 'lxml')
        comic_chapter_urls = soup.select('.pure-u-1-2 a')
        comic_chapter_url_dict = {}
        for comic_chapter_url in comic_chapter_urls:
            url = comic_chapter_url.get('href')
            title = comic_chapter_url.text
            comic_chapter_url_dict[title] = kwargs[key] + url
        return comic_chapter_url_dict


def parse_page(**kwargs):
    for key in kwargs:
        browser.get(kwargs[key])
        html = browser.page_source
        pattern = '.*?<a href="../">(.*?)</a> - (.*?)<h4.*?'
        path1 = re.search(pattern, html).group(1)
        path2 = re.search(pattern, html).group(2)
        path = 'F:\www.fzdm.com\\' + path1 + '\\' + path2
        make_file(path)

        next_page = re.search('下一頁', html).group()
        i = -1
        while next_page:
            i += 1
            offset = 'index_{}.html'.format(str(i))
            next_page_url = parse.urljoin(kwargs[key], offset)
            browser.get(next_page_url)
            html = browser.page_source

            title = str(i + 1)
            image_url = get_image()
            save_to_file(path, image_url, title)

            search_obj = re.search('下一頁', html)
            if search_obj == None:
                break


def get_image():
    # 获取图片link
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mhpic')))
    html = browser.page_source
    pattern = '.*?<img src="(.*?)" id="mhpic".*?'
    img_url = re.search(pattern, html).group(1)
    return img_url


def make_file(path):
    # 创建文件夹
    exists = os.path.exists(path)
    if not exists:
        os.makedirs(path)
        print('创建文件夹', path)
    else:
        print('文件夹已存在：', path)
        pass


def save_to_file(file_path, image_link, title):
    # 将图片保存至文件夹
    path = file_path + '\{0}.jpg'.format(title)
    opener = request.build_opener()
    opener.addheaders = [('User-agent', user_agent)]
    request.install_opener(opener)
    exists = os.path.exists(path)
    if not exists:
        request.urlretrieve(image_link, path)
        print('正在保存第{}张图片'.format(title))
    else:
        print('图片已经下载：', title)
        pass


def main():
    html = get_page(map_url)
    comic_url_dict = get_comic_url(html)
    comic_chapter_url_dict = get_comic_chapter_url(**comic_url_dict)
    parse_page(**comic_chapter_url_dict)


if __name__ == '__main__':
    main()