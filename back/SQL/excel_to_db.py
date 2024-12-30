import pandas as pd
import mysql.connector


# 读取 Excel 文件
def read_excel(file_path):
    try:
        # 读取 Excel 文件的指定表单
        df = pd.read_excel(file_path)
        print(f"读取到的 Excel 数据：\n{df.head()}")
        return df
    except Exception as e:
        print(f"读取 Excel 文件失败: {e}")
        return None


# 连接到 MySQL 数据库
def create_connection():
    try:
        # 连接到 MySQL 数据库
        conn = mysql.connector.connect(
            host="localhost",  # 数据库主机地址
            user="root",  # 用户名
            password="root",  # 密码
            database="BGood"  # 数据库名称
        )
        print("数据库连接成功")
        return conn
    except mysql.connector.Error as err:
        print(f"数据库连接失败: {err}")
        return None

# 判断是否已存在数据
def record_exists(cursor, username, year):
    cursor.execute("SELECT 1 FROM userBad WHERE username = %s AND year = %s", (username, year))#选择userBad表
    return cursor.fetchone() is not None

# 将数据插入 MySQL 数据库
def insert_into_db(df):
    # 连接到数据库
    conn = create_connection()
    if conn is None:
        return

    cursor = conn.cursor()

    try:
        # 遍历 DataFrame 中的每一行并插入到数据库
        for index, row in df.iterrows():
            username = row['username']
            fans = row['fans']
            year = row['year']

            if not record_exists(cursor, username, year):
                sql = "INSERT INTO userBad (username, fans, year) VALUES (%s, %s, %s)"#插入userBad表
                values = (username, fans, year)
                cursor.execute(sql, values)
            else:
                print(f"用户 {username} 在 {year} 年的数据已存在，跳过插入")

        # 提交事务
        conn.commit()
        print(f"成功将 {len(df)} 条数据插入数据库")
    except mysql.connector.Error as err:
        print(f"插入数据失败: {err}")
        conn.rollback()  # 如果插入失败，回滚事务
    finally:
        cursor.close()
        conn.close()


def main():
    # Excel 文件路径
    file_path = "main.xls"  # 这里替换为你的文件路径
    df = read_excel(file_path)

    if df is not None:
        insert_into_db(df)


if __name__ == "__main__":
    main()