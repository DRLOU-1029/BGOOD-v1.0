import pandas as pd
import mysql.connector
from mysql.connector import Error

def insert_csv_to_mysql(csv_file_path, db_config):
    try:
        # 读取 CSV 文件
        df = pd.read_csv(csv_file_path, dtype={'username': str, 'fans': int, 'year': int})
        total_csv_records = df.shape[0]
        print(f"CSV 文件总共有 {total_csv_records} 条数据。")

        # 连接到 MySQL 数据库
        connection = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            charset='utf8mb4'
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # 准备插入语句
            insert_query = """
            INSERT INTO userbad (username, fans, year)
            VALUES (%s, %s, %s)
            """

            # 将 DataFrame 转换为列表的元组
            data_to_insert = list(df.itertuples(index=False, name=None))

            # 执行批量插入
            cursor.executemany(insert_query, data_to_insert)
            connection.commit()

            inserted_rows = cursor.rowcount
            print(f"成功插入了 {inserted_rows} 条数据。")

    except FileNotFoundError:
        print(f"错误：文件 {csv_file_path} 未找到。")
    except pd.errors.EmptyDataError:
        print("错误：CSV 文件为空。")
    except mysql.connector.Error as e:
        print(f"MySQL 错误：{e}")
    except Exception as e:
        print(f"发生错误：{e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL 连接已关闭。")

if __name__ == "__main__":
    # 配置数据库连接信息
    db_config = {
        'host': 'localhost',
        'user': 'root',      # 替换为您的MySQL用户名
        'password': 'root',  # 替换为您的MySQL密码
        'database': 'BGood'   # 替换为您的数据库名
    }

    # CSV 文件路径
    csv_file_path = 'userbad_data.csv'  # 替换为您的CSV文件路径

    # 执行插入操作
    insert_csv_to_mysql(csv_file_path, db_config)
