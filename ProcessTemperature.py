# coder print right @ wangbl@chzu.edu.cn
# -*- coding: utf-8 -*-
import os

import numpy as np
import pandas as pd

path = r'D:\Pycharm2020.3.3\PythonProject\workspace\TemRainYear\Tem'
# upath = unicode(path, 'utf-8')
os.chdir(path)
l = os.listdir(path)

# 如下读取可得到data列表 包括12个月份数据的dataframe,后面方便进行批处理
data = []
for i in range(len(l)):
    io = l[i]
    data.append(pd.read_csv(io, sep='\s+', header=None))
'''
            质量控制码	含义
                   0	数据正确
                   1	数据可疑
                   2	数据错误
                   8	数据缺测或无观测任务
                   9	数据未进行质量控制

                   11	平均地表气温质量控制码
                   8	平均地表气温	Number(7)	0.1℃
'''
# 根据第10列的质量控制码 筛选出正确数据
# for i in range(len(data)):
#     # 返回值满足，{12列含有数值[0,9]
#     data[i] = data[i][data[i][12].isin([0, 9])]
#     # data[i] = data[i][data[i][12].isin([0, 9])]
#     # 将原值32700替换为0.1 - 根据元数据描述32700 999990为微量  同时改变原数据
#     data[i].replace(32700, 0.001, inplace=True)
#     data[i].replace(999990, 0.001, inplace=True)

years = []
for i in range(len(data)):
    data[i] = data[i][data[i][10].isin([0, 9])]
    data[i] = data[i][~data[i][7].isin([32766])]
    # if data[i] == 32766:
    # a = data[i][i]
    # a = (data[i][data[i+1][7]] + data[i][data[i + 2][7]]) / 2
#
qa = 0
i = 0
# 逐月份读取1981-2019年每一个月的数据
for i in range(len(data)):
    if data[i][10].max() == 0 or data[i][10].max() == 9:
        qa = 1
    else:
        qa = 0  # 一旦出现不符合条件的，立刻终止
        break
if qa == 1:
    # 接下来按照台站号批量求每月降水总量   并转换为mm
    # 逐年统计气象站的降水数据
    year_lst = []
    for i in range(len(data)):
        # 针对气象站进行分组，并对每一组气象站求月累计降雨数据，同时保留年字段,第9列累计量 reset_index()重置索引
        year_lst.append(data[i].groupby(0).agg({1: 'max', 2: 'max', 3: 'max', 7: 'mean', 4: 'max'}).reset_index())
        # 以下代码将所有年、月的月累计降雨数据整合到一起！
        # year_lst = []
        # year_data = []
    year_data = year_lst[0]

    for i in range(len(year_lst)):
        if i > 0:
            # 所有的站点在所有年月的月累计降雨数据的集合
            # year_lst.append(year_lst[i])
            # year_data = year_data.append(year_lst[i])
            year_data = year_data.append(year_lst[i])
            # year_data = year_data.concat(year_lst[i])

        # 再次利用分组思想，将气象站进行分组，然后逐个分组提取各个气象站的数据
        # year_data2 = DataFrame(year_lst)
    year_data = year_data.groupby([0, 4]).agg({7: 'mean', 1: 'max', 2: 'max', 3: 'max'}).reset_index()
    # year_data = year_data.reindex()
    # month_data.query('0=55299')
    group = year_data.groupby(4)
    # 取出分组数据的index，并生成list
    year_index = group.size().index.tolist()
    # 循环station_index，取出相应的index对应的子数据集，然后进行其他的分析

    for each_station in year_index:
        station_data = group.get_group(each_station)
        # 重新定义
        station_data.columns = ['气象站', '年', '年平均温度', '纬度', '经度', '观测场拔海高度']
        order = ['气象站', '年', '年平均温度', '纬度', '经度', '观测场拔海高度']
        station_data = station_data[order]

        temp = station_data.copy()

        tt = temp.loc[:, '年平均温度'] * 0.1
        station_data.loc[:, '年平均温度'] = tt
        station_data["年平均温度"] = station_data["年平均温度"].round(1)

        t2 = temp.loc[:, '纬度'] * 0.010
        station_data.loc[:, '纬度'] = t2
        station_data["纬度"] = station_data["纬度"].round(3)

        t3 = temp.loc[:, '经度'] * 0.010
        station_data.loc[:, '经度'] = t3
        station_data["经度"] = station_data["经度"].round(4)

        t5 = temp.loc[:, '观测场拔海高度'] * 0.10
        station_data.loc[:, '观测场拔海高度'] = t5
        station_data["观测场拔海高度"] = station_data["观测场拔海高度"].round(5)

        t4 = temp.loc[:, '气象站'] * 1
        station_data.loc[:, '气象站'] = t4
        station_data["气象站"] = station_data["气象站"].round(2)
        # tt = temp.loc[:, ('月气温均值')] * 0.1
        # station_data.loc[:, ('月气温均值')] = tt
        # station_data["月气温均值"] = station_data["月气温均值"].round(1)
        # tt=station_data.loc[:, ('月气温均值')]*0.1
        # station_data.loc[:, ('月气温均值')]=tt
        # station_data.reset_index()
        station_data.to_csv(str(int(station_data.iloc[0, 1])) + '.txt',
                            columns=['气象站', '年', '年平均温度', '纬度', '经度', '观测场拔海高度'],
                            sep=' ',
                            index=0,
                            header=1)
        type(station_data)
        # station_data['7']= station_data['7']*0.1
    print('END!')
# 写出excel表格数据
else:
    for i in range(len(data)):
        if data[i][10].max() == 0:
            print('{}月数据合格'.format(i + 1))
        else:
            print('{}月数据不合格'.format(i + 1))
