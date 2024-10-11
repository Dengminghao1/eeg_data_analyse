import mysql.connector

from Eeg import eeg

# db_config = {"host": "10.131.164.180",  # 数据库服务器地址
#              "user": "root",  # 数据库用户名
#              "password": "123123",  # 数据库密码
#              "database": "ebmgpt"  # 要连接的数据库名称
#              }






def eeg_analyse():
    # 建立数据库连接
    conn = mysql.connector.connect(**db_config)

    # 创建游标对象
    # cursor = conn.cursor()
    try:
        with conn.cursor() as cursor:
            # 查询 id 列的不同值
            sql_distinct = "SELECT DISTINCT id FROM eeg"
            cursor.execute(sql_distinct)

            # 获取所有不同的连接设备 distinct_id是设备ip
            distinct_id = cursor.fetchall()
            print(distinct_id)
            # 将查询结果转换为列表
            eeg_machine_list = [row[0] for row in distinct_id]

            # 输出结果
            print("不同设备ip：", eeg_machine_list)

            # 查询不同设备的数量
            sql_count = "SELECT COUNT(DISTINCT id) AS unique_machine_count FROM eeg"
            cursor.execute(sql_count)

            # 获取结果
            result = cursor.fetchone()
            # print(result[0])
            print("不同设备的数量：", result[0])
            sql_different_machine = "SELECT * FROM eeg WHERE id = %s ORDER BY time DESC LIMIT 10"
            for machine in eeg_machine_list:
                # 执行SQL查询,查到每一个设备的十条脑电波值
                cursor.execute(sql_different_machine, (machine,))

            # 获取查询结果
            results = cursor.fetchall()

            # 打印查询结果
            for row in results:
                print(row)
                result = eeg.parse_packet(row[2])
                print(result)

    finally:
        conn.close()

    # 关闭游标和连接
    cursor.close()
    conn.close()


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    eeg_analyse()
