import pymysql
from selenium import webdriver
from get_video import Get_video
from video import Get_video_details
from time import sleep
import random

# 连接到数据库
def create_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="BGood",
        charset="utf8mb4"
    )

# 从 userGood 表中获取 username 和 year
def get_user_and_year():
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            #cursor.execute("SELECT username, year FROM userGood")# 从 userGood 表中获取 username 和 year
            cursor.execute("SELECT username, year FROM userBad")# 从 userBad 表中获取 username 和 year
            result = cursor.fetchall()  # 获取所有记录
            return result  # [(username1, year1), (username2, year2), ...]
    except Exception as e:
        print(f"获取用户数据失败: {e}")
        return []
    finally:
        connection.close()

def get_done_user():
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT username, year FROM doneUser")
            result = cursor.fetchall()  # 获取所有记录
            return result  # [(username1, year1), (username2, year2), ...]
    except Exception as e:
        print(f"获取用户数据失败: {e}")
        return []
    finally:
        connection.close()

# 将 Bvid 和 Date 插入 main 表
def save_bvid_to_main(username, bvid_data):
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            for video in bvid_data:
                Bvid = video["Bvid"]
                Date = video["date"]
                # 插入 Bvid 和 Date，忽略重复的 Bvid,可以选择main表或者badmain表
                sql = """
                    INSERT IGNORE INTO badmain (Bvid, Date, username)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(sql, (Bvid, Date, username))
        connection.commit()
    except Exception as e:
        print(f"保存 Bvid 数据失败: {e}")
    finally:
        connection.close()

# 更新 main 表中的详细信息
def save_video_details_to_main(Bvid, details):
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            # 更新 main 表中的详细信息，可以选择main表或者badmain表
            sql = """
                UPDATE badmain
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
                details['views'], details['likes'], details['coins'], details['collects'],
                details['shares'], details['part'], Bvid
            ))
        connection.commit()
    except Exception as e:
        print(f"更新视频详细信息失败: {e}")
    finally:
        connection.close()

def save_done_user(username: str, year: int):
    """将已完成的用户和年份记录到 doneUser 数据表"""
    connection = create_connection()
    try:
        cursor = connection.cursor()
        query = "INSERT INTO doneUser (username, year) VALUES (%s, %s) ON DUPLICATE KEY UPDATE year = year"
        cursor.execute(query, (username, year))
        connection.commit()  # 提交事务
        print(f"已记录完成用户: {username}, 年份: {year}")
    except Exception as e:
        print(f"记录完成用户失败: {e}")
    finally:
        cursor.close()
        connection.close()

# 主函数
def main():
    driver = webdriver.Edge()  # 初始化 Selenium WebDriver
    users = get_user_and_year()  # 从 userGood 表中获取用户名和年份
    done_users = get_done_user()  # 从 doneUser 表中获取已处理的用户名和年份
    users = [user for user in users if user not in done_users]  # 过滤已处理的用户
    for username, year in users:
        print(f"开始处理用户: {username}，年份: {year}")
        wait_time = random.uniform(2, 5)
        sleep(wait_time)
        # 调用 Get_video 函数获取 Bvid 和 Date
        bvid_data = Get_video(driver, username, int(year))
        if bvid_data:
            print(f"获取到 {len(bvid_data)} 个视频，正在保存到数据库...")
            save_bvid_to_main(username, bvid_data)  # 保存 Bvid 和 Date

            # 遍历每个 Bvid，获取详细信息并保存
            for video in bvid_data:
                Bvid = video["Bvid"]
                print(f"获取 {Bvid} 的详细信息...")
                details = Get_video_details(driver, Bvid)
                if details:
                    save_video_details_to_main(Bvid, details)  # 保存详细信息
            save_done_user(username, year)  # 记录已处理的用户
        else:
            print("未获取到视频信息")

    driver.quit()  # 关闭 WebDriver
    print("所有用户数据处理完成！")

if __name__ == "__main__":
    main()
