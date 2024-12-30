import random
import logging
from time import sleep
import re
import pymysql
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#正在开发中

def format_data(data: str) -> str:

    # 处理 "万" 的情况
    match1 = re.match(r"([0-9.]+)万", data)
    # 处理 "亿" 的情况
    match2 = re.match(r"([0-9.]+)亿", data)
    if match1:
        # 提取数字部分并转换为 float
        num = float(match1.group(1))
        # 转换为对应的整数值，乘以10000
        result = int(num * 10000)
        return str(result)
    elif match2:
        # 提取数字部分并转换为 float
        num = float(match2.group(1))
        # 转换为对应的整数值，乘以100000000
        result = int(num * 100000000)
        return str(result)
    else:
        return data

def connect_db():
    """连接数据库"""
    return pymysql.connect(
        host='localhost',        # 数据库主机
        user='root',             # 数据库用户名
        password='root',  # 数据库密码
        database='BGood',     # 数据库名称
        charset='utf8mb4'        # 字符集
    )

def get_all_bvids_from_db(connection):
    """获取数据库中的所有 Bvid"""
    try:
        with connection.cursor() as cursor:
            sql = "SELECT Bvid FROM badmain"# 从 main 或 badmain 表中获取 Bvid
            cursor.execute(sql)
            bvids = cursor.fetchall()
            return [bvid[0] for bvid in bvids]
    except Exception as e:
        print(f"获取Bvid失败: {e}")
        return []

def Update_video_details_in_db(connection, video_details: dict):
    """更新数据库中的视频信息"""
    try:
        with connection.cursor() as cursor:
            sql = """
                UPDATE main
                SET 
                    views = %s,
                    `likes` = %s, 
                    coins = %s, 
                    collects = %s, 
                    shares = %s, 
                    part = %s
                WHERE Bvid = %s
            """
            cursor.execute(sql, (
                video_details['views'],
                video_details['likes'],
                video_details['coins'],
                video_details['collects'],
                video_details['shares'],
                video_details['part'],
                video_details['Bvid']
            ))
            connection.commit()
            print(f"视频 {video_details['Bvid']} 更新成功")
    except Exception as e:
        print(f"更新数据库失败: {e}")
        #logging.error(f"保存 Bvid 数据失败: {e}")

def Get_video_details(driver, Bvid: str) -> dict:
    """获取每一页的视频数量"""
    video_url = f"https://www.bilibili.com/video/{Bvid}/"
    driver.get(video_url)
    print(f"正在打开 {Bvid} ")
    wait_time = random.uniform(2, 4)
    sleep(wait_time)
    retry_count = 3  # 设置最大重试次数
    attempt = 0  # 当前重试次数
    while attempt < retry_count:
        try:
            # 等待直到页面加载完成
            WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="arc_toolbar_report"]/div[1]/div/div[4]/div/span'))
            )
            video_detail = {}
            video_detail['Bvid'] = Bvid
            # 获取视频的标题
            title = driver.find_element(By.XPATH, '//*[@id="viewbox_report"]/div[1]/div/h1').text
            video_detail['title'] = title
            print(f"标题: {title}")
            # 获取视频的播放量
            views = driver.find_element(By.XPATH, '//*[@id="viewbox_report"]/div[2]/div/div[1]/div').text
            views = format_data(views)
            video_detail['views'] = views
            # 获取视频的点赞
            likes = driver.find_element(By.XPATH, '//*[@id="arc_toolbar_report"]/div[1]/div/div[1]/div/span').text
            likes = format_data(likes)
            video_detail['likes'] = likes
            print(f"点赞数: {likes}")
            # 获取视频的投币
            coins = driver.find_element(By.XPATH, '//*[@id="arc_toolbar_report"]/div[1]/div/div[2]/div/span').text
            coins = format_data(coins)
            video_detail['coins'] = coins
            print(f"投币数: {coins}")
            # 获取视频的收藏
            collects = driver.find_element(By.XPATH, '//*[@id="arc_toolbar_report"]/div[1]/div/div[3]/div/span').text
            collects = format_data(collects)
            video_detail['collects'] = collects
            print(f"收藏数: {collects}")
            # 获取视频的分享
            shares = driver.find_element(By.XPATH, '//*[@id="arc_toolbar_report"]/div[1]/div/div[4]/div/span').text
            shares = format_data(shares)
            video_detail['shares'] = shares
            print(f"分享数: {shares}")
            # 获得视频的分区
            part = driver.find_element(By.XPATH, '//*[@class="firstchannel-tag"]/a').text
            video_detail['part'] = part
            print(f"分区: {part}")

            return video_detail

        except Exception as e:
            print(f"加载超时或未找到元素, 第{attempt + 1}次重试: {e}")
            attempt += 1
            if attempt < retry_count:
                # 等待一段时间再重试，防止频繁请求
                sleep(3)
            else:
                print("最大重试次数已达到，无法获取总页数")
                return {}  # 最大重试次数后返回0表示失败

    return {}


def main():
    driver = webdriver.Edge()
    connection = connect_db()
    Bvids = get_all_bvids_from_db(connection)
    for Bvid in Bvids:
        video_details = Get_video_details(driver, Bvid)
        if video_details:
            Update_video_details_in_db(connection, video_details)
    connection.close()
    driver.quit()

if __name__ == "__main__":
    main()