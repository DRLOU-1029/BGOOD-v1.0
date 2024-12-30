import pandas as pd
import mysql.connector
from mysql.connector import Error
from sqlalchemy import create_engine
import joblib


def connect_mysql(host, database, user, password):
    """
    连接到 MySQL 数据库并返回连接对象。
    """
    try:
        connection = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        if connection.is_connected():
            print("成功连接到 MySQL 数据库")
            return connection
    except Error as e:
        print(f"连接 MySQL 时出错: {e}")
        return None


def create_sqlalchemy_engine(db_type, user, password, host, port, database):
    """
    创建一个 SQLAlchemy 引擎。
    """
    if db_type == 'mysql':
        connection_string = f'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}'
    elif db_type == 'postgresql':
        connection_string = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'
    else:
        raise ValueError("Unsupported database type")

    engine = create_engine(connection_string)
    return engine


def export_view_to_csv(connection, view_name, output_csv_path):
    """
    从数据库视图中查询数据并导出为 CSV 文件。
    """
    query = f"SELECT * FROM {view_name};"
    try:
        if isinstance(connection, mysql.connector.connection_cext.CMySQLConnection):
            # 使用 mysql-connector-python
            df = pd.read_sql(query, connection)
        else:
            # 使用 SQLAlchemy
            df = pd.read_sql(query, connection)

        df.to_csv(output_csv_path, index=False)
        print(f"数据已成功导出到 {output_csv_path}")
    except Exception as e:
        print(f"导出数据时出错: {e}")


def main():
    # 配置数据库连接信息
    user = 'root'  # 数据库用户名
    password = 'root'  # 数据库密码
    host = 'localhost'  # 数据库主机
    database = 'BGood'  # 数据库名称
    view_name = 'baduserdetail'  # 视图名称

    # 输出文件路径
    output_csv = 'baduser_detail.csv'

    # 选择连接方式：MySQL Connector 或 SQLAlchemy
    # 方法一：使用 mysql-connector-python
    connection = connect_mysql(host, database, user, password)

    if connection:
        # 导出为 CSV
        export_view_to_csv(connection, view_name, output_csv)

        # 关闭连接
        connection.close()

    # 方法二：使用 SQLAlchemy
    # engine = create_sqlalchemy_engine(db_type, user, password, host, port, database)
    # export_view_to_csv(engine, view_name, output_csv)
    # export_view_to_excel(engine, view_name, output_excel)
    # engine.dispose()


if __name__ == "__main__":
    main()
