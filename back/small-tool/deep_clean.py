import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError


def get_existing_bvids(engine, table_name='main'):
    """
    从MySQL数据库的指定表中获取所有已存在的Bvid。

    参数:
    - engine: SQLAlchemy的数据库引擎对象
    - table_name: str, 数据库中的表名

    返回:
    - 一个包含已存在Bvid的集合
    """
    query = f"SELECT Bvid FROM {table_name}"
    try:
        df_existing = pd.read_sql(query, engine)
        existing_bvids = set(df_existing['Bvid'].dropna().unique())
        print(f"已从数据库中获取到 {len(existing_bvids)} 个现有的 Bvid。")
        return existing_bvids
    except SQLAlchemyError as e:
        print(f"获取现有Bvid时发生数据库错误: {e}")
        return set()
    except Exception as e:
        print(f"获取现有Bvid时发生未知错误: {e}")
        return set()


def filter_duplicates(input_csv, output_duplicates_csv, table_existing_bvids):
    """
    比较CSV文件中的Bvid与数据库中的Bvid，删除重复的Bvid并保存到新CSV文件。

    参数:
    - input_csv: str, 原始CSV文件路径
    - output_duplicates_csv: str, 保存重复记录的CSV文件路径
    - table_existing_bvids: set, 数据库中已存在的Bvid集合

    返回:
    - df_filtered: pandas DataFrame, 过滤后的新记录
    - df_duplicates: pandas DataFrame, 重复的记录
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(input_csv, dtype=str)
        print(f"成功读取CSV文件 '{input_csv}'，共有 {len(df)} 条记录。")

        # 检查 'Bvid' 列是否存在
        if 'Bvid' not in df.columns:
            print("错误: CSV文件中未找到 'Bvid' 列。")
            return None, None

        # 标准化 'Bvid'（去除前后空格并转换为大写）
        df['Bvid'] = df['Bvid'].str.strip().str.upper()

        # 查找重复的Bvid
        df_duplicates = df[df['Bvid'].isin(table_existing_bvids)]
        duplicate_count = len(df_duplicates)

        if duplicate_count > 0:
            print(f"发现 {duplicate_count} 条重复的 Bvid，正在保存到 '{output_duplicates_csv}'。")
            try:
                df_duplicates.to_csv(output_duplicates_csv, index=False, encoding='utf-8-sig')
                print(f"重复的记录已成功保存到 '{output_duplicates_csv}'。")
            except Exception as e:
                print(f"保存重复记录到CSV文件时发生错误: {e}")
        else:
            print("没有发现重复的 Bvid。")

        # 过滤掉重复的Bvid，保留新记录
        df_filtered = df[~df['Bvid'].isin(table_existing_bvids)]
        new_count = len(df_filtered)
        print(f"过滤后，保留 {new_count} 条新记录。")

        return df_filtered, df_duplicates

    except FileNotFoundError:
        print(f"错误: CSV文件 '{input_csv}' 未找到。请检查文件路径是否正确。")
        return None, None
    except pd.errors.EmptyDataError:
        print(f"错误: CSV文件 '{input_csv}' 是空的。")
        return None, None
    except pd.errors.ParserError:
        print(f"错误: 解析CSV文件 '{input_csv}' 时发生错误。请检查文件格式。")
        return None, None
    except Exception as e:
        print(f"发生未知错误: {e}")
        return None, None


def save_filtered_csv(df_filtered, output_filtered_csv):
    """
    保存过滤后的新记录到新的CSV文件。

    参数:
    - df_filtered: pandas DataFrame, 过滤后的新记录
    - output_filtered_csv: str, 保存新记录的CSV文件路径
    """
    try:
        df_filtered.to_csv(output_filtered_csv, index=False, encoding='utf-8-sig')
        print(f"新记录已成功保存到 '{output_filtered_csv}'。")
    except Exception as e:
        print(f"保存新记录到CSV文件时发生错误: {e}")


def main():
    # 配置参数
    input_csv = 'main_data_cleaned.csv'  # 原始清理后的CSV文件
    output_duplicates_csv = 'duplicates.csv'  # 保存重复记录的CSV文件
    output_filtered_csv = 'main_data_deep_cleaned.csv'  # 保存过滤后的新记录的CSV文件

    # 配置数据库连接
    # 请根据你的数据库配置修改以下连接字符串
    # 格式: 'mysql+pymysql://<username>:<password>@<host>/<database>'
    db_username = 'root'  # 数据库用户名
    db_password = 'root'  # 数据库密码
    db_host = 'localhost'  # 数据库主机
    db_name = 'BGood'  # 数据库名称
    table_name = 'main'  # 数据库中的表名

    connection_string = f'mysql+pymysql://{db_username}:{db_password}@{db_host}/{db_name}'

    # 创建数据库引擎
    try:
        engine = create_engine(connection_string, echo=False)
        print("成功连接到数据库。")
    except SQLAlchemyError as e:
        print(f"数据库连接失败: {e}")
        return
    except Exception as e:
        print(f"发生未知错误: {e}")
        return

    # 获取数据库中已存在的Bvid
    existing_bvids = get_existing_bvids(engine, table_name)

    if not existing_bvids:
        print("没有获取到任何已存在的Bvid，可能是数据库中表为空或发生了错误。")

    # 过滤CSV中的重复记录
    df_filtered, df_duplicates = filter_duplicates(input_csv, output_duplicates_csv, existing_bvids)

    if df_filtered is not None:
        # 保存过滤后的新记录
        save_filtered_csv(df_filtered, output_filtered_csv)

    print("\n操作完成。")


if __name__ == "__main__":
    main()
