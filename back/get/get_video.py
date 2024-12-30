from time import sleep
from datetime import datetime, timedelta
import re
import pymysql
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from get_space import Get_space

def connect_db():
    """连接数据库"""
    return pymysql.connect(
        host='localhost',        # 数据库主机
        user='root',             # 数据库用户名
        password='root',  # 数据库密码
        database='BGood',     # 数据库名称
        charset='utf8mb4'        # 字符集
    )

def format_publish_time(publish_time: str) -> str:
    """将发布时间格式化为标准日期格式"""

    # 处理 "昨天"
    if publish_time == "昨天":
        return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # 处理 "月-日"
    match = re.match(r"(\d{1,2})-(\d{1,2})", publish_time)
    if match:
        month = int(match.group(1))
        day = int(match.group(2))
        return datetime.now().replace(month=month, day=day).strftime("%Y-%m-%d")

    # 处理 "n小时前"
    match = re.match(r"(\d+)小时前", publish_time)
    if match:
        # 直接返回当天日期
        return datetime.now().strftime("%Y-%m-%d")

    # 处理 "n分钟前"
    match = re.match(r"(\d+)分钟前", publish_time)
    if match:
        # 直接返回当天日期
        return datetime.now().strftime("%Y-%m-%d")

    # 处理 "2020-12-9" 格式的日期
    match = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})", publish_time)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        return datetime(year, month, day).strftime("%Y-%m-%d")

def save_to_db(username:str, data:list):
    """将数据保存到 db 文件"""
    connection = connect_db()
    cursor = connection.cursor()
    for video in data:
        Bvid = video.get('Bvid')
        date = video.get('date')
        username = username
        # 插入数据到表 main
        try:
            cursor.execute("""
                    INSERT INTO main (Bvid, Date, views, likes, coins, collects, shares, part, username)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (Bvid, date, "", "", "", "", "", "", username))
            connection.commit()
            print(f"已保存视频 {Bvid} 的数据到数据库")
        except Exception as e:
            print(f"插入数据失败: {e}")
            connection.rollback()

        # 关闭数据库连接
    cursor.close()
    connection.close()

def get_total_page(driver, space_url: str) -> int:
    """获取用户发布视频的总页数"""
    driver.get(space_url)
    print(f"正在打开空间链接: {space_url}")
    sleep(2)
    retry_count = 3  # 设置最大重试次数
    attempt = 0  # 当前重试次数
    while attempt < retry_count:
        try:
            # 等待直到分页元素加载完成
            WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="submit-video-list"]/ul[3]/span[1]'))
            )

            # 获取总页数文本并提取页数
            total_pages_text = driver.find_element(By.XPATH, '//*[@id="submit-video-list"]/ul[3]/span[1]').text
            total_pages = total_pages_text.split(" ")[1]
            print(f"总页数: {total_pages}")
            return int(total_pages)

        except Exception as e:
            print(f"加载超时或未找到元素, 第{attempt + 1}次重试: {e}")
            attempt += 1
            if attempt < retry_count:
                # 等待一段时间再重试，防止频繁请求
                sleep(3)
            else:
                print("最大重试次数已达到，无法获取总页数")
                return 1  # 最大重试次数后返回0表示失败

    return 0  # 返回 0 表示未找到或出错

def get_video_per_page(driver, space_url: str, page: int,year: int) -> list:
    """获取每一页的视频数量"""
    s_url = space_url + f"?tid=0&special_type=&pn={page}&keyword=&order=pubdate"
    driver.get(s_url)
    print(f"正在打开第 {page} 页: {s_url}")
    sleep(3)
    retry_count = 3  # 设置最大重试次数
    attempt = 0  # 当前重试次数

    while attempt < retry_count:
        try:
            # 等待直到页面加载完成
            WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="submit-video-list"]/ul[3]/span[1]'))
            )
            video_details = []
            # 定位到指定的 ul 元素
            ul_element = driver.find_element(By.XPATH, '//*[@id="submit-video-list"]/ul[1]')
            #ul_element = driver.find_element(By.XPATH, '//*[@id="submit-video-list"]/ul[2]')#临时
            # 获取所有 li 元素
            li_elements = ul_element.find_elements(By.TAG_NAME, 'li')
            # 遍历所有 li 元素
            for i, li in enumerate(li_elements, start=1):
                # 获取每个 li 元素中的链接//*[@id="submit-video-list"]/ul[2]/li[i]/div/span[2]
                link_element = li.find_element(By.TAG_NAME, 'a')  # 获取 li 中的 a 标签
                link_url = link_element.get_attribute("href")  # 获取 a 标签的 href 属性
                try:
                    time_element = li.find_element(By.XPATH, '//li[' + str(i) + ']/div/span[2]')
                    publish_time = format_publish_time(time_element.text)
                    video_year = int(publish_time.split("-")[0])
                    if video_year > year and year != 0:
                        continue
                except Exception as e:
                    publish_time = "未获取到时间"  # 如果没有获取到时间，返回默认值
                Bvid = link_url.split("/")[4]
                video_details.append({"Bvid": Bvid, "date": publish_time})
                print(f"第 {i} 个视频的Bvid: {Bvid}")

            return video_details

        except Exception as e:
            print(f"加载超时或未找到元素, 第{attempt + 1}次重试: {e}")
            attempt += 1
            if attempt < retry_count:
                # 等待一段时间再重试，防止频繁请求
                sleep(3)
            else:
                print("最大重试次数已达到，无法获取总页数")
                return [] # 最大重试次数后返回0表示失败
    return []

def Get_video(driver,username: str,year: int,) -> list:
    # 获取空间链接
    space_url = Get_space(driver, username)
    space_url = space_url.split("?")[0]  # 去掉 URL 中的参数部分
    space_url = space_url + "/video"  # 拼接成视频页面的 URL
    # 获取总页数
    total_pages = get_total_page(driver, space_url)
    #total_pages = 1
    if total_pages == 0:
        #driver.quit()
        print(f"获取{username}总页数失败！")
        return []
    # 初始化一个列表
    all_video_details = []
    #total_pages = 1#测试用
    # 遍历每一页获取视频数量
    for page in range(1, total_pages + 1):
            video_details = get_video_per_page(driver, space_url, page, year)
            if video_details:
                all_video_details.extend(video_details)

    # 保存数据到 DB 文件
    save_to_db(username, all_video_details)
    return all_video_details


def main():
    driver = webdriver.Edge()
    username = "老番茄"
    year = 0
    Get_video(driver, username, year)

    driver.quit()

if __name__ == "__main__":
    main()
