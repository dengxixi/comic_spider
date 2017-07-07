# -*- encoding: utf-8 -*-
__author__ = 'xgj1010'
__date__ = '2017/6/25 20:10'

import os
import re
from urllib import parse, request

import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup

user_agent = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.76 Mobile Safari/537.36'


base_url = 'http://www.xeall.com/'
urls = ['http://www.xeall.com/xieemanhua/p{}.html'.format(str(i)) for i in range(1, 20)]


def get_page(url):
    # 请求主页面
    try:
        response = requests.get(url)
        if response.status_code == 200:
            response.encoding = 'gb2312'
            return response.text
        else:
            return None
    except RequestException:
        return None


def get_comic_url(html):
    # 获取每一页所有漫画的url
    soup = BeautifulSoup(html, 'lxml')
    links = soup.select('a.pic.show')
    comic_list = []
    for link in links:
        link = link.get('href')
        comic_url = parse.urljoin(base_url, link)
        comic_list.append(comic_url)
    return comic_list
        # parse_comic_page(comic_url)


def parse_comic_page(url):
    # 解析漫画详情页获取漫画标题和图片url
    response = get_page(url)
    soup = BeautifulSoup(response, 'lxml')
    first_image = soup.select('.left img')[0].get('src')
    title = soup.select('h1')[0].text
    page_num = soup.select('ul.pagelist a')[0].text
    page_num = re.sub("\D", "",  page_num)
    image_list = []
    image_list.append(first_image)
    for i in range(2, int(page_num) + 1):
        image_url = url.rstrip('.html') + '_{}.html'.format(str(i))
        response = requests.get(image_url)
        soup = BeautifulSoup(response.text, 'lxml')
        last_image = soup.select('.left img')[0].get('src')
        image_list.append(last_image)
    return title, image_list


def save_pic(filename, *args):
    # 保存漫画图片到文件夹
    dir = 'F:\comic_image\{}\\'.format(filename)
    exists = os.path.exists(dir)
    if not exists:
        os.mkdir(dir)
        print('创建文件夹', filename)
    else:
        print('文件夹已存在：', filename)
        pass
    dir_path = os.path.dirname(dir)
    for i in args[0]:
        title = i[-8:-4]
        path = dir_path + '\{0}.jpg'.format(title)
        opener = request.build_opener()
        opener.addheaders=[('User-agent',user_agent)]
        request.install_opener(opener)
        exists = os.path.exists(path)
        if not exists:
            request.urlretrieve(i, path)
            print('保存图片：', title)
        else:
            print('图片已经下载：', title)
            pass


def main():
    for url in urls:
        index = get_page(url)
        comic_urls = get_comic_url(index)
        for comic_url in comic_urls:
            title, pic_list = parse_comic_page(comic_url)
            save_pic(title, pic_list)

if __name__ == '__main__':
    main()