import pymysql
import pandas as pd
import json

def create_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="root",  # 修改为你的数据库密码
        database="BGood",
        charset="utf8mb4"
    )

def get_bvid_year_and_user():
    connection = create_connection()
    try:
        with connection.cursor() as cursor:# 删除main或者badmain表中views为空的数据
            query = """SELECT bvid, date, username FROM badmain
                            WHERE (views IS NULL OR views = '')"""
            df = pd.read_sql(query, connection)
            df['year'] = df['date'].str[:4]
            # 按照 username 分组，生成每个 username 对应的 (bvid, year) 数据
            grouped = df.groupby('username').apply(
                lambda group: group[['bvid', 'year']].to_dict(orient='records')).to_dict()
            bvid_list = df['bvid'].tolist()
            print(f"已获取 {len(bvid_list)} 条需要处理的记录。")
            return grouped, bvid_list

    except Exception as e:
        print(f"获取用户数据失败: {e}")
        return {}, []
    finally:
        connection.close()

def delete_records(bvid_list):
    if not bvid_list:
        print("没有需要删除的记录。")
        return
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            # 为了防止参数过多导致 SQL 语句失败，分批删除
            batch_size = 1000
            total_deleted = 0
            for i in range(0, len(bvid_list), batch_size):
                batch = bvid_list[i:i+batch_size]
                format_strings = ','.join(['%s'] * len(batch))
                sql = f"DELETE FROM badmain WHERE bvid IN ({format_strings})"
                cursor.execute(sql, batch)
                deleted = cursor.rowcount
                total_deleted += deleted
                print(f"已删除第 {i//batch_size +1} 批，共 {deleted} 条记录。")
            connection.commit()
            print(f"总共删除了 {total_deleted} 条记录。")
    except Exception as e:
        connection.rollback()
        print(f"删除记录时出错: {e}")
    finally:
        connection.close()

def save_to_json(grouped_data):
    for username, data in grouped_data.items():
        # 文件名为 username.json
        filename = f"user_none/{username}.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"数据已保存到 {filename}")
        except Exception as e:
            print(f"保存文件 {filename} 时出错: {e}")

def main():
    # 获取所有用户和年份
    data, bvid_list = get_bvid_year_and_user()
    # 删除需要处理的记录
    delete_records(bvid_list)
    # 保存数据到 JSON 文件
    #save_to_json(data)

if __name__ == '__main__':
    main()

