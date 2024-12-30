import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker
import logging

def list_tables(engine):
    try:
        tables = engine.table_names()
        print(f"数据库中的表: {tables}")
    except SQLAlchemyError as e:
        print(f"列出表时发生数据库错误: {e}")
    except Exception as e:
        print(f"列出表时发生未知错误: {e}")


def get_existing_bvids(engine, table_name='main'):
    query = f"SELECT Bvid FROM {table_name}"
    try:
        df_existing = pd.read_sql(query, engine)
        existing_bvids = set(df_existing['Bvid'].dropna())
        print(f"已从数据库中获取到 {len(existing_bvids)} 个现有的 Bvid。")
        return existing_bvids
    except SQLAlchemyError as e:
        print(f"获取现有Bvid时发生数据库错误: {e}")
        return set()
    except Exception as e:
        print(f"获取现有Bvid时发生未知错误: {e}")
        return set()


def filter_csv(input_csv, existing_bvids):
    try:
        df = pd.read_csv(input_csv, dtype=str)
        print(f"成功读取CSV文件 '{input_csv}'，共有 {len(df)} 条记录。")

        if 'Bvid' not in df.columns:
            print("错误: CSV文件中未找到 'Bvid' 列。")
            return None, None

        # 保持Bvid的原始大小写
        df['Bvid'] = df['Bvid'].str.strip()

        # 移除CSV内部的重复Bvid，保留第一条
        initial_count = len(df)
        df = df.drop_duplicates(subset='Bvid', keep='first')
        cleaned_count = len(df)
        duplicates_in_csv = initial_count - cleaned_count
        if duplicates_in_csv > 0:
            print(f"在CSV内部发现并移除了 {duplicates_in_csv} 条重复的Bvid。")
        else:
            print("CSV文件中没有内部重复的Bvid。")

        # 查找与数据库中已存在的Bvid重复的记录
        df_duplicates = df[df['Bvid'].isin(existing_bvids)]
        duplicate_count = len(df_duplicates)

        if duplicate_count > 0:
            print(f"发现 {duplicate_count} 条重复的 Bvid，准备移除这些记录。")
        else:
            print("没有发现重复的 Bvid。")

        # 过滤掉重复的Bvid，保留新记录
        df_filtered = df[~df['Bvid'].isin(existing_bvids)]
        new_count = len(df_filtered)
        print(f"准备插入的新记录数: {new_count}。")

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


def save_duplicates(df_duplicates, output_duplicates_csv):
    if df_duplicates.empty:
        print("没有重复的记录需要保存。")
        return

    try:
        df_duplicates.to_csv(output_duplicates_csv, index=False, encoding='utf-8-sig')
        print(f"重复的记录已成功保存到 '{output_duplicates_csv}'。")
    except Exception as e:
        print(f"保存重复记录到CSV文件时发生错误: {e}")


def insert_new_records_with_transaction(engine, df_new, table_name='main'):
    if df_new.empty:
        print("没有新记录需要插入。")
        return 0

    insert_stmt = f"""
        INSERT INTO {table_name} (Bvid, Date, views, likes, coins, collects, shares, part, username)
        VALUES (:Bvid, :Date, :views, :likes, :coins, :collects, :shares, :part, :username)
        ON DUPLICATE KEY UPDATE Bvid = Bvid
    """

    records = df_new.to_dict(orient='records')

    # 打印每条记录的Bvid
    for record in records:
        print(f"准备插入Bvid: {record['Bvid']}")

    Session = sessionmaker(bind=engine)
    session = Session()
    total_inserted = 0

    try:
        session.execute(text(insert_stmt), records)
        session.commit()
        total_inserted = len(records)
        print(f"成功插入 {total_inserted} 条新记录。")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"插入新记录时发生数据库错误: {e}")
    except Exception as e:
        session.rollback()
        print(f"插入新记录时发生未知错误: {e}")
    finally:
        session.close()

    return total_inserted


def insert_single_record(engine, record, table_name='main'):
    insert_stmt = f"""
        INSERT INTO {table_name} (Bvid, Date, views, likes, coins, collects, shares, part, username)
        VALUES (:Bvid, :Date, :views, :likes, :coins, :collects, :shares, :part, :username)
        ON DUPLICATE KEY UPDATE Bvid = Bvid
    """

    try:
        with engine.connect() as conn:
            conn.execute(text(insert_stmt), record)
            print(f"成功插入Bvid: {record['Bvid']}")
    except SQLAlchemyError as e:
        print(f"插入记录时发生数据库错误: {e}")
    except Exception as e:
        print(f"插入记录时发生未知错误: {e}")


def main():

    input_csv = 'badmain_data_cleaned.csv'  # 过滤后的CSV文件
    duplicates_csv = 'badduplicates.csv'  # 重复记录的CSV文件
    db_username = 'root'  # 数据库用户名
    db_password = 'root'  # 数据库密码
    db_host = 'localhost'  # 数据库主机
    db_name = 'BGood'  # 数据库名称
    table_name = 'badmain'  # 数据库表名

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

    # 列出数据库中的表，确认连接正确
    list_tables(engine)

    # 获取已存在的Bvid
    existing_bvids = get_existing_bvids(engine, table_name)

    # 过滤CSV中的重复记录
    df_new, df_duplicates = filter_csv(input_csv, existing_bvids)

    if df_new is not None:
        # 保存重复记录，插入main和badmain表可启用，插入user和baduser表可注释
        #save_duplicates(df_duplicates, duplicates_csv)

        # 插入新记录
        inserted = insert_new_records_with_transaction(engine, df_new, table_name)
        print(f"总插入记录数: {inserted}")


    print("\n操作完成。")


if __name__ == "__main__":
    main()

