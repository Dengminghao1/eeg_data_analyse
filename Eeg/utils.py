import pandas
import time
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from Eeg import eeg
import eeg_test
import mysql
import json
import pandas as pd

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号 #有中文出现的情况，需要u'内容'

path = r'eeg.txt'

db_config = {"host": "10.131.10.108",  # 数据库服务器地址
             "user": "root",  # 数据库用户名
             "password": "123123",  # 数据库密码
             "database": "ebmgpt"  # 要连接的数据库名称
             }
# db_config_tome= {"host": "10.131.222.134",  # 数据库服务器地址
#              "user": "root",  # 数据库用户名
#              "password": "123456",  # 数据库密码
#              "database": "ebmgpt"  # 要连接的数据库名称
#              }
start_time = (datetime.now() - timedelta(seconds=10)).strftime('%Y-%m-%d %H:%M:%S')
end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# start_time = (datetime.now()-timedelta(minutes=1))
# end_time = datetime.now()

test_start_time = '2024-10-12 17:39:48'
test_end_time = '2024-10-12 17:39:58'


def getTimestamp(realTime: str):
    # realTime = '2020-4-06 00:00:00'
    s_t = time.strptime(realTime, "%Y-%m-%d %H:%M:%S")  # 返回元祖
    mkt = int(time.mktime(s_t))
    return mkt


def eeg_calculate(start_time: str, end_time: str):
    all_dicts_list = []
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    sql = "SELECT * FROM eeg   WHERE time BETWEEN %s AND %s ORDER BY time DESC"
    cursor.execute(sql, (start_time, end_time))
    result = cursor.fetchall()
    with open(path, 'w', encoding='utf-8') as file:
        for row in result:
            # value = row[0]+" "+str(row[1])+str(eeg.parse_packet(row[2])).replace("{", " ").replace("}", "").replace(",", "")
            string_dict1 = {'id': row[0], 'time': str(row[1])}
            string_dict2 = eeg.parse_packet(row[2])
            merge_dict = string_dict1.copy()
            merge_dict.update(string_dict2)
            # value=string_dict2
            all_dicts_list.append(merge_dict)
            # print(merge_dict)

            file.write(str(merge_dict) + '\n')
    return all_dicts_list  # 返回一个列表,包含id,time,signal,delta,theta...(所有设备的)


def _get_diffent_machine(data: list):
    unique_machine = []
    for item in data:
        if 'id' in item:
            unique_machine.append(item['id'])
    return unique_machine


def get_eeg_file(path: str):
    f = open(path)
    line = f.readline()  # 每次读取一行内容
    out_data = []
    while line:
        # 移除行尾的换行符
        line.strip()
        # 将单引号替换为双引号
        corrected_json = line.replace("'", '"')

        # 将字符串转换为字典
        dictionary = json.loads(corrected_json)
        values = list(dictionary.values())
        # out_data.append(values)

        if len(values) == 13:  # 排除坏数据
            out_data.append(values)
        line = f.readline()
    f.close()

    out_res = pandas.DataFrame(
        data=np.array(out_data),
        columns=['id', 'time', 'signal',
                 'delta', 'theta', '低频alpha', '高频alpha', '低频beta', '高频beta', '低频gamma', '中频gamma',
                 'attention', 'Mediation']
    )

    return out_res


def get_eeg(all_data_list: list):
    index = 0
    out_data = []
    while index < len(all_data_list):

        line = all_data_list[index]
        values = list(line.values())
        if len(values) == 13:  # 排除坏数据
            out_data.append(values)
        index = index + 1
    out_res = pandas.DataFrame(
        data=np.array(out_data),
        columns=['id', 'time', 'signal',
                 'delta', 'theta', 'lowalpha', 'highalpha', 'lowbeta', 'highbeta', 'lowgamma', 'midgamma',
                 'attention', 'Mediation']
    )

    return out_res  # 转成dataframe


def get_diffent_machine(data: pandas.DataFrame):
    df = pd.DataFrame(data)
    unique_machine = df['id'].unique().tolist()
    # print(f'unique_machine: {unique_machine}')
    return unique_machine


def crop(data: pandas.DataFrame, start_time: str, end_time: str):  # 给定数据，去重；往有缺失的地方补0
    df = pd.DataFrame(data)
    new_data_all = pd.DataFrame()
    unique_machine = get_diffent_machine(data)
    processed_data_list = []
    for machine in unique_machine:
        filtered_data = df[df['id'] == machine]
        filtered_data_copy = filtered_data.copy()
        filtered_data_copy.drop_duplicates(subset=['time'], keep='first', inplace=True)  # 去重
        # print(filtered_data_copy)
        # 转换为 datetime 对象
        start_time = pd.to_datetime(start_time)
        end_time = pd.to_datetime(end_time)

        # 生成所有秒数的时间戳
        all_seconds = pd.date_range(start=start_time, end=end_time, freq='s')

        # 获取 DataFrame 中存在的时间戳
        existing_times = pd.to_datetime(data['time'])

        # 找出缺失的时间戳
        missing_times = all_seconds[~all_seconds.isin(existing_times)]
        missing_times_list = missing_times.strftime('%Y-%m-%d %H:%M:%S').tolist()
        # print('missing_times_list:' + str(missing_times_list))

        for i in missing_times_list:  # 在data里面查找没有的时间戳，补0
            zeroData = [machine] + [i] + [0] * 11
            zeroDataFrame = pandas.DataFrame([zeroData], columns=data.columns)
            filtered_data_copy = pd.concat([filtered_data_copy, zeroDataFrame], ignore_index=True)
        # 重新索引,按时间增序排列
        new_machine_data = filtered_data_copy.sort_values(by='time', ascending=True).reset_index(
            drop=True)  # 添加完成后，需要升序排
        # 打印每一个设备(去重且补0)后完整的数据
        # print(machine + '的补0数据')
        # print(new_machine_data)

        # 将这些属性变成int型
        trans_data = new_machine_data.astype({'signal': 'int',
                                              'delta': 'int', 'theta': 'int', 'lowalpha': 'int', 'highalpha': 'int',
                                              'lowbeta': 'int',
                                              'highbeta': 'int', 'lowgamma': 'int', 'midgamma': 'int',
                                              'attention': 'int', 'Mediation': 'int'})
        processed_data_list.append(trans_data)
        # 所有补充0后的数据拼接，形成一个大的dataframe(包含所有机器)
        new_data_all = pd.concat([new_data_all, trans_data], ignore_index=True)

    return processed_data_list  # 包含不同的机器，补0后的dataframe列表


def getCognitiveLoad(data):
    CognitiveLoad = []
    for i in range(2, data.shape[0]):
        CognitiveLoad_i = []
        for j in range(0, data.shape[1]):
            eeg_ij = data[i][j]
            if eeg_ij[2] == 0:
                CognitiveLoad_ij = 1
            else:
                CognitiveLoad_ij = eeg_ij[1] / ((eeg_ij[2] + eeg_ij[3]) / 2)
            CognitiveLoad_i.append(CognitiveLoad_ij)
        CognitiveLoad.append(CognitiveLoad_i)
    return np.array(CognitiveLoad)


def getCognitive_input_load(data):
    cog_input_list = []
    cog_load_list = []
    for index, row in data.iterrows():
        mean_theta = row['theta']
        mean_beta = (row['highbeta'] + row['lowbeta']) / 2
        mean_alpha = (row['highalpha'] + row['lowalpha']) / 2
        # if(mean_alpha + mean_theta)==0:
        #     print(row)
        #     continue
        cognitive_input = mean_beta / (mean_alpha + mean_theta)
        cognitive_load = mean_theta / mean_alpha
        cog_input_list.append(cognitive_input)
        cog_load_list.append(cognitive_load)
    per_machine_list = [cog_input_list, cog_load_list]

    return per_machine_list  # 列表中包含两个列表，第一个是cog_input_list，第二个是cog_load_list


def meanBytime(data, gap):
    reslut = []
    for i in range(0, len(data), gap):
        reslut.append(data[i:i + gap].mean())
    return reslut


def getMedian(data: pandas.DataFrame):  # 求总体的中位数
    df = pd.DataFrame(data)
    numeric_columns = df.select_dtypes(include=['int'])  # 选出int类型的数据
    medians = numeric_columns.median().astype(int)  # 求中位数
    return medians


# def replaceZero(data):
#     data.fillna(0, inplace=True)


def medianCompletion(data: pandas.DataFrame):
    medianAll = getMedian(data)  # 有效数据的中位数
    # newData = []
    # for i in range(0, len(data), gap):
    #     if i - gap <= 0 & i==0:  # 在所有数据里，把0数据替换成中位数数据，每gap时间里检索一次
    #         data_i = data[i - gap:i]  # 截取到一段时间的数据
    #     if sum(map(sum, data_i)) == 0:  # 该时间段的数据全是空缺
    #         print(0)
    #         for j in range(0, gap, 1):
    #             newData.append(medianAll)
    #     else:
    #         median_i = getMedian(data_i)
    #         for j in data_i:
    #             if sum(j) == 0:
    #                 newData.append(median_i)
    #             else:
    #                 newData.append(j)
    # return newData
    # 假设 df 是一个 Pandas DataFrame

    for index, row in data.iterrows():  # 遍历每一行
        for col in data.columns:  # 遍历每一列
            if row[col] == 0:  # 如果元素为 0
                data.at[index, col] = medianAll[col]  # 替换为对应列的中位数
    return data


def drawImg(data):
    x = [i for i in range(1, len(data) + 1, 1)]
    plt.plot(x, data, 'b*--', alpha=0.5, linewidth=1,
             label='Cognitive Load'
             )  # 'bo-'表示蓝色实线，数据点实心原点标注
    ## plot中参数的含义分别是横轴值，纵轴值，线的形状（'s'方块,'o'实心圆点，'*'五角星   ...，颜色，透明度,线的宽度和标签 ，
    plt.legend()  # 显示上面的label
    plt.axhline(y=sum(data) / len(data),
                color='red',
                ls='--'
                )
    plt.title('groupNine')
    # plt.xlabel('time')  # x_label
    # plt.ylabel('number')  # y_label
    plt.savefig('result.jpg')
    plt.show()


def calculate_cognitive(start_time: str, end_time: str):

    eeg_list = eeg_calculate(start_time, end_time)
    eeg_get = get_eeg(eeg_list)  # dataframe
    unique_machine = get_diffent_machine(eeg_get)
    # print(f'unique_machine: {unique_machine}')
    all_cog_list = []
    eeg_crop = crop(eeg_get, start_time, end_time)  # 分别填了0的数据列表
    for index, i in enumerate(eeg_crop):
        median = getMedian(i)
        media = medianCompletion(i)
        cog = getCognitive_input_load(media)

        # print(f"这是{get_diffent_machine(eeg_get)[index]}\n{cog}")
        all_cog_list.append(cog)
    return all_cog_list, unique_machine


def trans_to_json(data: list,machine_name: list):
    unique_machine = machine_name
    print(f'unique_machine: {unique_machine}')
    for i in range(len(machine_name)):
        unique_machine[i] = f"machine{i+1}"
    # unique_machine=['machine1','machine2']
    result = {}
    # 遍历每个机器的数据
    for i, machine_data in enumerate(data):
        machine_name = unique_machine[i]
        machine_info = {
            "cognitive_input": machine_data[0],
            "cognitive_load": machine_data[1]
        }

        # 添加到结果字典中
        result[machine_name] = machine_info

    # 将结果字典转换为 JSON 字符串
    json_result = json.dumps(result, indent=4, ensure_ascii=False)

    return json_result


if __name__ == '__main__':
    # 显示所有列
    pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_colwidth', 100)  # 设置最大列宽为无穷大
    # 显示所有行
    pd.set_option('display.max_rows', None)

    # 如果还需要调整其他显示选项，例如宽度等，也可以在这里设置
    pd.set_option('display.width', 1500)  # 设置显示宽度

    #     while True:
    #         eeg_list = eeg_calculate(test_start_time, test_end_time)
    #         eeg_get = get_eeg(eeg_list)#dataframe
    #         # print(eeg_get)
    #         eeg_crop = crop(eeg_get, test_start_time, test_end_time)#分别填了0的数据列表
    #
    #         for index,i in enumerate(eeg_crop):
    #              # print('shuju')
    #              # print(i)
    #              median = getMedian(i)
    #              # print('中位数\n', median)
    #              media = medianCompletion(i)
    #              cog = getCognitive_input_load(media)
    #              # print(media)
    #              event_stream()
    #              print(f"这是{get_diffent_machine(eeg_get)[index]}\n{cog}")
    #          # aa=getCognitiveLoad(media)
    #          # print(aa)
    #
    #         time.sleep(10)
    # # # eeg_crop.replace(to_replace=0, value=median, inplace=False)
    # # print(eeg_crop)
    # a, b = calculate_cognitive(start_time, end_time)
    a, b = calculate_cognitive(test_start_time, test_end_time)
    result=trans_to_json(a, b)
    print(result)
