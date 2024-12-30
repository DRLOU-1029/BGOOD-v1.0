import pymysql

def connect_db():
    """连接数据库"""
    return pymysql.connect(
        host='localhost',        # 数据库主机
        user='root',             # 数据库用户名
        password='root',  # 数据库密码
        database='BGood',     # 数据库名称
        charset='utf8mb4'        # 字符集
    )

def create_database_and_table_main():
    """创建数据库和表"""
    # 连接到 MySQL 服务器（不指定数据库）
    connection = connect_db()

    try:
        with connection.cursor() as cursor:
            # 创建数据库
            cursor.execute("CREATE DATABASE IF NOT EXISTS BGood")
            print("数据库 'BGood' 创建成功或已存在！")

            # 选择数据库
            cursor.execute("USE BGood")

            # 创建表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS main (
                Bvid CHAR(20) NOT NULL,
                Date CHAR(10) NOT NULL,
                views CHAR(10),
                likes CHAR(10),
                coins CHAR(10),
                collects CHAR(10),
                shares CHAR(10),
                part CHAR(10),
                username CHAR(20),
                PRIMARY KEY (Bvid)
            )
            """)
            print("表 'main' 创建成功或已存在！")

            # 提交更改
            connection.commit()
    except Exception as e:
        print(f"错误: {e}")
    finally:
        # 关闭数据库连接
        connection.close()

def create_table_userGood():

    connection = connect_db()

    try:
        with connection.cursor() as cursor:
            # 选择数据库
            cursor.execute("USE BGood")

            # 创建表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS userGood (
                username CHAR(20) NOT NULL,
                fans CHAR(10),
                year CHAR(10),
                PRIMARY KEY (username, year)
            )
            """)
            print("表 'userGood' 创建成功或已存在！")

            # 提交更改
            connection.commit()
    except Exception as e:
        print(f"错误: {e}")
    finally:
        # 关闭数据库连接
        connection.close()

def create_table_userBad():

    connection = connect_db()

    try:
        with connection.cursor() as cursor:
            # 选择数据库
            cursor.execute("USE BGood")

            # 创建表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS userBad (
                username CHAR(20) NOT NULL,
                fans CHAR(10),
                year CHAR(10),
                PRIMARY KEY (username, year)
            )
            """)
            print("表 'userBad' 创建成功或已存在！")

            # 提交更改
            connection.commit()
    except Exception as e:
        print(f"错误: {e}")
    finally:
        # 关闭数据库连接
        connection.close()

def create_table_badmain():

    connection = connect_db()

    try:
        with connection.cursor() as cursor:
            # 选择数据库
            cursor.execute("USE BGood")

            # 创建表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS badmain (
                Bvid CHAR(20) NOT NULL,
                Date CHAR(10) NOT NULL,
                views CHAR(10),
                likes CHAR(10),
                coins CHAR(10),
                collects CHAR(10),
                shares CHAR(10),
                part CHAR(10),
                username CHAR(20),
                PRIMARY KEY (Bvid)
            )
            """)
            print("表 'badmain' 创建成功或已存在！")

            # 提交更改
            connection.commit()
    except Exception as e:
        print(f"错误: {e}")
    finally:
        # 关闭数据库连接
        connection.close()

def create_table_doneUsers():

    connection = connect_db()

    try:
        with connection.cursor() as cursor:
            # 选择数据库
            cursor.execute("USE BGood")

            # 创建表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS doneUser (
            username CHAR(20) NOT NULL,
            year CHAR(10) NOT NULL,
            PRIMARY KEY (username, year)
            )
            """)
            print("表 'doneUsers' 创建成功或已存在！")

            # 提交更改
            connection.commit()
    except Exception as e:
        print(f"错误: {e}")
    finally:
        # 关闭数据库连接
        connection.close()

def main():
    #create_database_and_table_main()
    #create_table_userGood()
    #create_table_userBad()
    create_table_badmain()
    #create_table_doneUsers()


if __name__ == "__main__":
    main()
