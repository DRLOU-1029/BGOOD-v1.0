from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.parse  # 用于 URL 编码

def Get_space(driver,username: str) -> str:
    # 指定新的搜索用户名
    new_keyword = username  # 替换成你想搜索的用户

    # 将新的搜索关键词进行 URL 编码
    encoded_keyword = urllib.parse.quote(new_keyword)

    # 构造新的 URL，替换原来 keyword 参数的值
    new_url = f"https://search.bilibili.com/upuser?keyword={encoded_keyword}&from_source=webtop_search&spm_id_from=333.1007&search_source=5"

    # 打开Bilibili的搜索页面
    driver.get(new_url)
    retry_count = 3  # 设置最大重试次数
    attempt = 0  # 当前重试次数
    while attempt < retry_count:
        try:
            # 检查是否存在没有结果的提示
            no_data_element = driver.find_elements(By.XPATH,
                                                   '//*[@id="i_cecream"]/div/div[2]/div[2]/div/div/div[2]/div')[0].text
            if no_data_element == "今天真是寂寞如雪啊~":
                return "NONE"
            else:
                # 等待直到页面中某个元素加载完成，例如第一个用户的头像
                WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located(
                        (By.XPATH,
                         '//*[@id="i_cecream"]/div/div[2]/div[2]/div/div/div[2]/div[1]/div[1]/div/a/div/div/div/div/img'))
                )

                print("页面加载完成！")

                # 获取第一个用户的昵称
                username = driver.find_element(By.XPATH,
                                               '//*[@id="i_cecream"]/div/div[2]/div[2]/div/div/div[2]/div[1]/div[1]/div/div/h2/a').text
                print("用户昵称:", username)

                # 获取第一个用户的空间链接
                space_link = driver.find_element(By.XPATH,
                                                 '//*[@id="i_cecream"]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div/h2/a').get_attribute(
                    "href").split("?")[0]
                print("用户空间链接:", space_link)
                return space_link

        except Exception as e:
            print(f"加载超时或未找到元素, 第{attempt + 1}次重试: {e}")
            attempt += 1
            if attempt < retry_count:
                # 等待一段时间再重试，防止频繁请求
                sleep(1)
            else:
                print("最大重试次数已达到，无法获取总页数")
                return "ERROR"  # 最大重试次数后返回0表示失败
    return "ERROR"


if __name__ == "__main__":
    # 创建 WebDriver 实例
    driver = webdriver.Edge()
    # 搜索用户
    username = "DRLOU1029"
    space_link = Get_space(username)
    if space_link == "NONE":
        print("未找到用户！")
    elif space_link == "ERROR":
        print("加载超时或未找到元素！")
    else:
        print(f"用户 {username} 的空间链接为: {space_link}")

