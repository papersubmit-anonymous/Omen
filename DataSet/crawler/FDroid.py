import time
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import psutil
# ... 其他函数定义
# 代理配置
proxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890',
    # 'http': 'socks5://127.0.0.1:1080',
    # 'https': 'socks5://127.0.0.1:1080',
}

# 获取应用列表
def get_app_list(url):
    response = requests.get(url, proxies=proxies)
    soup = BeautifulSoup(response.text, 'lxml')
    app_list = soup.find_all('a', class_='package-header')
    return [urljoin(url, app['href']) for app in app_list]

# 下载APK文件
def download_apk(apk_url, save_path, timeout=60):
    try:
        if os.path.exists(save_path):
            print(f"File already exists: {save_path}. Skipping download.")
            return True

        response = requests.get(apk_url, stream=True, timeout=timeout, proxies=proxies)
        response.raise_for_status()

        with open(save_path, 'wb') as apk_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    apk_file.write(chunk)

        print(f"Downloaded {apk_url} to {save_path}")
        return True
    except Exception as e:
        print(f"Error downloading {apk_url}: {e}")
        return False

def download_app_versions(app_url, download_folder, failed_log_path):
    app_response = requests.get(app_url, proxies=proxies)
    app_soup = BeautifulSoup(app_response.text, 'lxml')

    # 获取应用包名
    package_name = app_url.split('/')[-2]

    # 获取所有版本的APK下载链接
    all_version_sections = app_soup.find_all('li', class_='package-version')

    if all_version_sections:
        # 创建以包名命名的文件夹
        app_download_folder = os.path.join(download_folder, package_name)
        os.makedirs(app_download_folder, exist_ok=True)

        for version_section in all_version_sections:
            apk_button = version_section.find('p', class_='package-version-download')

            if apk_button:
                apk_link = apk_button.find('a', href=True)

                if apk_link:
                    apk_url = apk_link['href']
                    apk_name = apk_url.split('/')[-1]
                    save_path = os.path.join(app_download_folder, apk_name)
                    if not download_apk(apk_url, save_path):
                        with open(failed_log_path, 'a') as log_file:
                            log_file.write(f"{apk_url}\n")
                else:
                    print(f"APK download link not found for {app_url}")
            else:
                print(f"APK download button not found for {app_url}")
    else:
        print(f"No version sections found for {app_url}")

def retry_failed_downloads(failed_log_path, download_folder):
    if not os.path.exists(failed_log_path):
        return []

    with open(failed_log_path, "r") as log_file:
        failed_apk_urls = log_file.readlines()

    # 清空失败记录文件
    open(failed_log_path, 'w').close()

    remaining_failed_apks = []

    for apk_url in failed_apk_urls:
        apk_url = apk_url.strip()
        package_name = apk_url.split('/')[-2]
        apk_name = apk_url.split('/')[-1]

        app_download_folder = os.path.join(download_folder, package_name)
        os.makedirs(app_download_folder, exist_ok=True)

        save_path = os.path.join(app_download_folder, apk_name)
        if not download_apk(apk_url, save_path):
            remaining_failed_apks.append(apk_url)
            with open(failed_log_path, 'a') as log_file:
                log_file.write(f"{apk_url}\n")

    return remaining_failed_apks

def get_subcategory_links(url):
    response = requests.get(url, proxies=proxies)
    soup = BeautifulSoup(response.text, 'lxml')

    subcategories = soup.find('nav', class_='app-categories')
    subcategory_links = []

    if subcategories:
        for link in subcategories.find_all('a', href=True):
            subcategory_links.append(urljoin(url, link['href']))

    return subcategory_links

def fdroid_spider_multiprocess(url, download_folder, failed_log_path, retry_limit=3):
    subcategory_links = get_subcategory_links(url)

    # 将主页面链接添加到子页面链接列表中
    subcategory_links.append(url)

    for subcategory_url in subcategory_links:
        app_list = get_app_list(subcategory_url)

        # 获取真实CPU核心数
        true_cpu_cores = psutil.cpu_count(logical=False)

        # 创建进程池
        with ProcessPoolExecutor(max_workers=true_cpu_cores) as executor:
            for app_url in app_list:
                executor.submit(download_app_versions, app_url, download_folder, failed_log_path)

    retries = 0
    retry_limit = 10
    while retries < retry_limit:
        remaining_failed_apks = retry_failed_downloads(failed_log_path, download_folder)
        if not remaining_failed_apks:
            break
        print(f"Retrying failed downloads (attempt {retries + 1})")
        with ProcessPoolExecutor(max_workers=true_cpu_cores) as executor:
            for apk_url in remaining_failed_apks:
                executor.submit(download_apk, apk_url, download_folder)
        retries += 1



# ... 其他函数定义

if __name__ == "__main__":
    base_url = "https://f-droid.org/en/packages/"
    download_folder = "apk_downloads"
    failed_log_path = "failed_downloads.txt"

    fdroid_spider_multiprocess(base_url, download_folder, failed_log_path)
