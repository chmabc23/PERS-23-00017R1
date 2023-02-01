#! python3
import os
import numpy as np
from osgeo import gdal
import math
from tkinter.filedialog import askdirectory
import sys

# 定义读取文件夹里的所有tif文件的函数
def get_fileN(path):
    filename = []
    for root, dirs, files in os.walk(path):  # 读所有文件,
        for i in files:
            file_dir = os.path.join(root, i)
            if os.path.splitext(i)[1] == '.tif':  # 筛选出文件夹里后缀为.tif的文件。分离文件名与扩展名；默认返回(fname,fextension)元组
                filename.append(file_dir)
                return filename
            # 筛选出文件夹里后缀为.tif的文件。分离文件名与扩展名；默认返回(fname,fextension)元组


# 定义数组转栅格函数
def array2raster(outpath, array, geoTransform, proj):
    cols = array.shape[1]
    rows = array.shape[0]
    driver = gdal.GetDriverByName('Gtiff')
    outRaster = driver.Create(outpath, cols, rows, 1, gdal.GDT_Float32)
    outRaster.SetGeoTransform(geoTransform)  # 输出tif的仿射矩阵
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(array)
    outRaster.SetProjection(proj)  # 输出tif的投影


# 读取“植被类型”数据
fn = r'D:\Desktop\500m\Type\2001\Type_2001.tif'
Veg = gdal.Open(fn)
width_Veg = Veg.RasterXSize  # 栅格矩阵的列数
# print('width_Veg:', width_Veg)
height_Veg = Veg.RasterYSize  # 栅格矩阵的行数
# print('height_Veg:', height_Veg)
bands_Veg = Veg.RasterCount  # 波段数
im_geotrans = Veg.GetGeoTransform()  # 仿射矩阵，左上角像素的大地坐标和像素分辨率
im_proj = Veg.GetProjection()  # 地图投影信息，字符串表示
Data1 = Veg.ReadAsArray(0, 0, width_Veg, height_Veg)
Data1 = (Data1 > 0) * Data1

path0 = askdirectory(title=r'D:\Desktop\500m\NDVI\2001\ndvi2001.tif')
path1 = askdirectory(title=r'D:\Desktop\500m\Radiation\2001\Radiation_2001.tif')
path2 = askdirectory(title=r'D:\Desktop\500m\ASU_Tem_500m\2001\Tem2001.tif')
path3 = askdirectory(title=r'D:\Desktop\500m\ASU_Rain_500m\2001\Rain2001.tif')
# path5 = askdirectory(title=r'D:\Pycharm2020.3.3\PythonProject\workspace\Topt')

fileNDVI = get_fileN(path0)
fileSolar = get_fileN(path1)
fileTem = get_fileN(path2)
fileRain = get_fileN(path3)
# fileTopt = get_fileN(path5)

print('NDVI:\n', fileNDVI)
print('太阳辐射：\n', fileSolar)
print('气温：\n', fileTem)
print('降水:\n', fileRain)
# 最适温度为NDVI取得最大值时的当月平均气温 当某月气温小于等于－10度，第一胁迫因子取0
# print('最适温度：\n', fileTopt)

# II = 37.6983
# II = [40.6117, 41.2696, 38.0396, 36.3984, 38.2347, 39.8085, 39.0088, 41.7375, 39.0179,
#       39.5570, 39.6312, 39.6312, 38.6132, 37.7971, 38.0434, 38.5681, 37.6983]  # 热量总和 2000-2016年
# T = 23.1658
# T = [23.859, 23.3539, 22.3898, 21.0718, 21.6974, 22.5692, 21.91, 22.6075, 22.8175, 22.15,
#      23.9447, 23.8316, 22.0263, 21.9921, 22.1395, 22.1895, 23.1658, ]  # 最适温度  2000-2016年
for m in range(len(fileNDVI)):

    # 读取“NDVI”数据
    NDVI = gdal.Open(fileNDVI[m])
    Data = NDVI.ReadAsArray(0, 0, width_Veg, height_Veg)
    Data = (Data > -1) * Data
    # 读取“太阳辐射”数据
    Solar = gdal.Open(fileSolar[m])
    Data2 = Solar.ReadAsArray(0, 0, width_Veg, height_Veg)
    Data2 = (Data2 > 0) * Data2
    # 读取“温度”数据
    Tem = gdal.Open(fileTem[m])
    Data3 = Tem.ReadAsArray(0, 0, width_Veg, height_Veg)
    Data3 = (Data3 > 0) * Data3
    # 读取“降水”数据
    rain = gdal.Open(fileRain[m])
    Data4 = rain.ReadAsArray(0, 0, width_Veg, height_Veg)
    Data4 = (Data4 > 0) * Data4

    # print(m + 2000, '年')
    # 返回固定形状的数据
    # c = np.zeros((173, 256))
    RData = np.zeros((436, 647))
    FPARe = np.zeros((436, 647))
    eFPAR = np.zeros((436, 647))
    for i in range(1, 15):
        if 4 <= i <= 17:
            # 返回元素，可以是x或y，具体取决于where后条件
            index = np.where(Data1 == i)
            indexArr = np.array(index[0])
            indexArr2 = np.array(index[1])
            c = Data[indexArr, indexArr2]
            d = (c > -1) * c  # 此处为了使得统计NDVI值的最小值为>-1的数
            SR = (1 + d) / (1 - d)
            maN = np.max(d)
            miN = np.min(d)
            maR = np.max(SR)
            miR = np.min(SR)
            FPAR_NDVI = (d - miN) * (0.95 - 0.001) / (maN - miN) + 0.001
            FPAR_SR = (SR - miR) * (0.95 - 0.001) / (maR - miR) + 0.001
            FPAR = (FPAR_NDVI + FPAR_SR) / 2  # 植被层对入射光合有效辐射的吸收比例

            # 在此处乘每种植被类型的最大光能利用率
            if i == 1:
                print('常绿针叶林')
                FPARe = FPAR * 0.389
            elif i == 2:
                print('常绿阔叶林')
                FPARe = FPAR * 0.985
            elif i == 3:
                print('落叶针叶林')
                FPARe = FPAR * 0.485
            elif i == 4:
                print('落叶阔叶林')
                FPARe = FPAR * 0.692
            elif i == 5:
                print('混交林')
                # FPARe = FPAR * 0.475
                FPARe = FPAR * 0.768
            elif i == 6 or i == 7:
                print('灌木林')
                FPARe = FPAR * 0.494
            elif i == 8 or i == 10:
                print('草地')
                FPARe = FPAR * 0.542
            elif i == 9:
                print('草原')
                FPARe = FPAR * 0.542
            elif i == 11:
                print('湿地')
                FPARe = FPAR * 0.542
            elif i == 12:
                print('农田')
                FPARe = FPAR * 0.542
            elif i == 14:
                print('农田与自然植被镶嵌体')
                FPARe = FPAR * 0.542
            else:
                print('其他冰雪、裸地、水体等非植被类型')
                FPARe = FPAR * 0.542
            # if i == 4:
            #     print('落叶阔叶林')
            #     FPARe = FPAR * 0.692
            # elif i == 5:
            #     print('混交林')
            #     FPARe = FPAR * 0.768
            # elif i == 10:
            #     print('草地')
            #     FPARe = FPAR * 0.542
            # else:
            #     print('其他')
            #     FPARe = FPAR * 0.542

            print('   NDVI最大值:', maN, '\n   NDVI最小值:', miN)
            print('   SR最大值:', maR, '\n   SR最小值:', miR)
            RData[indexArr, indexArr2] = FPAR
            eFPAR[indexArr, indexArr2] = FPARe

    APAR = np.zeros((436, 647))
    # 未算 2018年平均气温
    Topt = 29.907709495931 # 某一区域一年内NDVI值达到最高时当月平均气温

    Te1 = 0.8 + 0.02 * Topt - 0.0005 * Topt ** 2  # 温度胁迫系数1
    Te = np.zeros((436, 647))
    Te2 = np.zeros((436, 647))
    # H热量总和
    H = (Topt / 5) ** 1.514
    #  Thornthwaite法（简称TW法）A参数
    a = (0.675 * H ** 3 - 77.1 * H ** 2 + 17920 * H + 492390) * 10 ** -6  # 因地而异的常数

    Ep0 = np.zeros((436, 647))
    Rn = np.zeros((436, 647))
    E = np.zeros((436, 647))
    Ep = np.zeros((436, 647))
    W = np.zeros((436, 647))
    NPP = np.zeros((436, 647))
    for xi in range(height_Veg):
        for yj in range(width_Veg):
            APAR[xi][yj] = RData[xi, yj] * Data2[xi, yj] * 0.5  # APAR植被所吸收的光合有效辐射
            Te2[xi][yj] = 1.184 / (1 + math.exp(0.2 * (Topt - 10 - Data3[xi, yj]))) * 1 \
                          / (1 + math.exp(0.3 * (-Topt - 10 + Data3[xi, yj])))  # 温度胁迫系数2
            Te[xi][yj] = Te2[xi][yj] * Te1  # 温度胁迫因子
            Ep0[xi, yj] = 16 * (10 * Data3[xi, yj] / H) ** a  # 局地潜在蒸散量
            Rn[xi, yj] = ((Ep0[xi, yj] * Data4[xi, yj]) ** 0.5) * (
                    0.369 + 0.589 * ((Ep0[xi, yj] / Data4[xi, yj]) ** 0.5))
            E[xi, yj] = Data4[xi, yj] * Rn[xi, yj] * (Data4[xi, yj] ** 2 + Rn[xi, yj] ** 2 + Data4[xi, yj] * Rn[xi, yj]) \
                        / ((Data4[xi, yj] + Rn[xi, yj]) * (Data4[xi, yj] ** 2 + Rn[xi, yj] ** 2))  # 区域实际蒸散量
            Ep[xi, yj] = (E[xi, yj] + Ep0[xi, yj]) / 2  # 区域潜在蒸散量
            W[xi, yj] = 0.5 + (0.5 * E[xi, yj]) / Ep[xi, yj]  # 水分胁迫因子

            NPP[xi, yj] = Data2[xi, yj] * eFPAR[xi, yj] * 0.5 * Te[xi][yj] * W[xi, yj]  # NPP
    # APARname = r"H:\\graduation\code\APAR\APAR%04d.tif" % (m + 2000)
    # Temstress = r"H:\\graduation\code\TemStress\Temstress%04d.tif" % (m + 2000)
    # waterStress = r"H:\\graduation\code\waterStress\waterStress%04d.tif" % (m + 2000)
    # array2raster(APARname, NPP, im_geotrans, im_proj)
    # array2raster(Temstress, NPP, im_geotrans, im_proj)
    # array2raster(waterStress, NPP, im_geotrans, im_proj)

    NPPname = r"D:\Desktop\right\NPP2001.tif"
    # 调用数组转栅格函数 转为tif数据
    array2raster(NPPname, NPP, im_geotrans, im_proj)

# path4 = askdirectory(title = r'D:\Desktop\data\graduation\NPP')
# fileNPP = get_fileN(path4)
# print('NPP:\n', fileNPP)
# sumNPP = file_add(path4)
# meanNPP = sumNPP / len(fileNPP)
# array2raster(r"H:\\graduation\code\Mean\NPPmean.tif", meanNPP, im_geotrans, im_proj)
#
# end = time.clock()
# print('Running time: %s Seconds' % (end - start))
