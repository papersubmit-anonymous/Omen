# coding=utf-8
import os
import pickle
import re
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
import psutil
import requests
import sys
import urllib
import time
import socket
from bs4 import BeautifulSoup
sleep_time = 1
socket.setdefaulttimeout(30)
sys.path.append("..")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename='runtime.log',
    filemode='a+'
)
proxy = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}
logger = logging.getLogger()
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'}


def parser_apks(root_url, count=1):
    '''
    apkpure
    '''
    # 伪装浏览器
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent',
                          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36')]
    urllib.request.install_opener(opener)
    _root_url = root_url
    res_parser = {}
    page_num = 1  # 设置爬取的页面，从第一页开始爬取，第一页爬完爬取第二页，以此类推
    while count:
        time.sleep(sleep_time)
        wbdata = requests.get(_root_url + "?sort=download&page=" + str(page_num),
                              headers=header, proxies=proxy).text
        soup = BeautifulSoup(wbdata, "html.parser")
        download_links = soup.body.contents[9].find_all('a', href=re.compile("/download?"))
        for download_link in download_links:
            try:
                download_link = download_link.get('href')
                time.sleep(3)  # 等待3s 海外网站防止连续性登录
                detail_link = urllib.parse.urljoin(_root_url, download_link)
                package_name = download_link.split('/')[3]
                s = requests.session()
                s.keep_alive = False  # 关闭多余连接
                time.sleep(3)

                def loop(detail_link=detail_link):
                    '''
                    重复5次获取网页内容，防止网络波动
                    '''
                    try:
                        detail_data = requests.get(detail_link, headers=header, proxies=proxy).text
                        return detail_data
                    except Exception as e:
                        count = 1
                        while count <= 5:
                            try:
                                detail_data = requests.get(detail_link, headers=header, proxies=proxy).text
                                return detail_data
                            except Exception as e:
                                count += 1
                        if count > 5:
                            print("网络超时" + str(e))

                detail_data = loop(detail_link)
                soup = BeautifulSoup(detail_data, "html.parser")
                download = soup.find(id="download_link")["href"]
                if download not in res_parser.values():
                    res_parser[package_name] = download
                    print(f"{package_name}: {download}")
                    with open("apkpure_url.txt", "a", encoding="utf-8") as f:
                        f.write(f"{package_name}: {download}" + "\n")
                    count = count - 1
                if count == 0:
                    break
            except:
                pass
        if count > 0:
            page_num = page_num + 1
    return res_parser


def testparse():
    # 伪装浏览器
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent',
                          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36')]
    urllib.request.install_opener(opener)
    _root_url = 'https://apkpure.com/cn/app'
    wbdata = requests.get(_root_url,
                          headers=header, proxies=proxy).text
    soup = BeautifulSoup(wbdata, "html.parser")
    divs = soup.find_all('div', class_='apk-name-list')
    # print(divs)
    app_list = []
    # 提取所有a元素的href属性，并打印出来
    for div in divs:
        for a in div.find_all('a'):
            # print(a['href'])
            app_list.append("https://apkpure.com" + a['href'])
    print(app_list)
    return app_list


def craw_apks(count=10, path="./apkpure"):
    '''
    爬取方法
    在获取的map里面循环下载apk
    '''
    # 确保目录存在
    os.makedirs(path, exist_ok=True)
    # 在log内增加日期分割
    apk_address = 'APKPureTopAPK' + "\\"
    app_list = testparse()
    return app_list

    # res_dic = {}

    # for app_url in app_list:
    # res_parser_list = self.parser_apks(app_url, count)
    # res_dic.update(res_parser_list)
    # break

    # for filename, url in res_dic.items():
    # print(filename)
    # print(url)
    # self.auto_down(url, filename)

    # 将字典对象序列化为字节流并写入文件
    # with open('apkpure.pkl', 'wb') as f:
    # pickle.dump(res_dic, f)
    # 从文件中读取字节流并反序列化为 Python 对象
    # with open('apkpure.pkl', 'rb') as f:
    # res_dic = pickle.load(f)

    # 创建进程池
    # with ProcessPoolExecutor(max_workers=true_cpu_cores) as executor:
    # for filename, url in res_dic.items():
    # executor.submit(self.auto_down, url, filename)
    # executor.map(self.auto_down, res_dic.values(), os.path.join(path, res_dic.keys() + ".apk"))
    # for apk in res_dic.keys():
    # executor.submit(self.auto_down, res_dic[apk], os.path.join(path, apk + ".apk"))

    # res_dic = self.parser_apks(count)
    # print(res_dic)

    # for apk in res_dic.keys():
    # self.auto_down(res_dic[apk], os.path.join(path, apk + ".apk"))


def auto_down(url, filename):
    '''
    自动尝试5次下载
    未下载的app记录在log/pure_undown_apk_info.txt文件内
    '''
    print("URL: ", url)
    print("filename: ", filename)
    filename = os.path.join("./apkpure", filename + ".apk")
    if os.path.exists(filename):
        return
    try:
        print("正在下载: " + filename.split("\\")[-1])
        logger.info("正在下载: " + filename.split("\\")[-1])
        proxy_handler = urllib.request.ProxyHandler({'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'})
        # 伪装浏览器
        opener = urllib.request.build_opener(proxy_handler)
        opener.addheaders = [('User-Agent',
                              'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(url, filename)
        # 下载完整包后才会加载下载完成log
        print("下载完成: " + filename.split("\\")[-1])
        logger.info("下载完成: " + filename.split("\\")[-1])
    except (socket.timeout, Exception) as e:
        # 重试2次
        count = 2
        while count <= 2:
            try:
                proxy_handler = urllib.request.ProxyHandler(
                    {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'})
                # 伪装浏览器
                opener = urllib.request.build_opener(proxy_handler)
                opener.addheaders = [('User-Agent',
                                      'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36')]
                urllib.request.install_opener(opener)
                urllib.request.urlretrieve(url, filename)
            except (socket.timeout, Exception) as e:
                count += 1
        if count > 2:
            print("应用下载5次失败：" + filename)
            logger.info("应用下载5次失败：" + filename)
            with open("apkpure_failed.txt", "a", encoding="utf-8") as f:
                f.write(url + "\n")


if __name__ == "__main__":
    with open("apkpure_failed.txt", "w", encoding="utf-8") as f:
        f.write("")
    path = "./apkpure"
    # 确保目录存在
    os.makedirs(path, exist_ok=True)
    # 在log内增加日期分割
    apk_address = 'APKPureTopAPK' + "\\"
    app_list = testparse()
    print(app_list)
    # 获取真实CPU核心数
    true_cpu_cores = psutil.cpu_count(logical=False)
    count = 12
    # 使用 ProcessPoolExecutor 开启多进程
    # app_url = app_list[0]
    res_dic = {}
    
    with ProcessPoolExecutor(max_workers=true_cpu_cores) as executor:
        # 遍历 app_list 列表，提交任务到进程池
        futures = [executor.submit(parser_apks, app_url, count) for app_url in app_list]
        # futures = [executor.submit(ApkPure.parser_apks, app_url, count) for app_url in app_list]

    for future in as_completed(futures):
        result = future.result()
        res_dic.update(result)
        print(result)
    # print(res_dic)
    # 将字典对象序列化为字节流并写入文件
    with open('apkpure.pkl', 'wb') as f:
        pickle.dump(res_dic, f)
    # 从文件中读取字节流并反序列化为 Python 对象
    #with open('apkpure.pkl', 'rb') as f:
        #res_dic = pickle.load(f)
    with ProcessPoolExecutor(max_workers=true_cpu_cores) as executor:
        #time.sleep(sleep_time)
        futures = [executor.submit(auto_down, url, filename) for filename, url in res_dic.items()]
        # for filename, url in res_dic.items():
        # executor.submit(auto_down, url, filename)
