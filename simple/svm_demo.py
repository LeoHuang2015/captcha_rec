#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A simple captcha recognition demo by svm"""

import os
import urllib2
import svmlight
from PIL import Image, ImageDraw, ImageEnhance,ImageFilter


headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}


def get_batch_pic(url, dir):
    for i in range(100):
        print "download", i
        filename = "%d.jpg" %(i)
        picfile = os.path.join(dir, filename)

        req = urllib2.Request(url,headers = headers)
        file(picfile, "wb").write( urllib2.urlopen(req).read() )

def binaryzation(input_dir, output_dir, resize=False):
    '''
    比较简单通用的二值化算法，resize模式会放大，方便精确识别，但是识别成本会增加（cpu）
    '''
    for f in os.listdir(input_dir):
        if f.endswith(".jpg"):
            img = Image.open( os.path.join(input_dir,f) )
            img = img.convert("RGBA")
            pixdata = img.load()
            #二值化
            for y in xrange(img.size[1]):
                for x in xrange(img.size[0]):
                    if pixdata[x, y][0] < 90:
                        pixdata[x, y] = (0, 0, 0, 255)
            for y in xrange(img.size[1]):
                for x in xrange(img.size[0]):
                    if pixdata[x, y][1] < 136:
                        pixdata[x, y] = (0, 0, 0, 255)
            for y in xrange(img.size[1]):
                for x in xrange(img.size[0]):
                    if pixdata[x, y][2] > 0:
                        pixdata[x, y] = (255, 255, 255, 255)
            output_file = os.path.join(output_dir, f)
            #img = img.convert("L")
            if not resize:
                img.save( output_file )
            else:
                x,y = img.size
                big = img.resize((x*5, y*5), Image.NEAREST)
                big.save( output_file )

def get_point(im):
    '''
    获取垂直投影图
    '''
    x,y = im.size

    Lim = im.convert('L')
    threshold = 80
    table = []
    for i in range(256):
        if i > threshold:
            table.append(0)
        else:
            table.append(1)

    # convert to binary image by the table
    bim = Lim.point(table, '1')
    bdata=bim.load()

    vertical_projection = {}
    for b in range(x):
        vertical_projection[b] = 0

    for a in range(y):
        for b in range(x):
            #print bdata[b,a],
            if bdata[b,a] == 1:
                vertical_projection[b] += 1
        #print

    '''
    y = 0
    for x in vertical_projection:
        #print x, vertical_projection[x]
        if y < vertical_projection[x]: y = vertical_projection[x]

    #print "[vertical projection]", len(vertical_projection), y
    for a in range(y, 0, -1):
        for x in vertical_projection:
            #print x, vertical_projection[x],a
            if vertical_projection[x]>a:
                print 1,
            else:
                print " ",

        print
    #'''

    return vertical_projection

def locate_troughs(vertical_projection, num=4):
    '''
    根据垂直投影图，确定切割的8个波谷值
    '''
    c = 0
    up_trough_list = []
    down_trough_list = []
    vp_length = len(vertical_projection)
    for x in range(vp_length-1):
        if vertical_projection[x]<vertical_projection[x+1]:
            if x==0:
                up_trough_list.append(x)
            else:
                if vertical_projection[x]<=vertical_projection[x-1]:
                    up_trough_list.append(x)

    for x in range(1, vp_length-1):
        if vertical_projection[x]<vertical_projection[x-1] and vertical_projection[x]<=vertical_projection[x+1]:
            down_trough_list.append(x)

    #print len(up_trough_list),up_trough_list
    #print len(down_trough_list),down_trough_list

    tmp_list = up_trough_list + down_trough_list
    # 需要的波谷，过滤条件：波谷值为0
    my_trough_list = []

    for x in tmp_list:
        #print vertical_projection[x]
        if 0 == vertical_projection[x]:
            my_trough_list.append(x)

    my_trough_list.sort()
    #print len(my_trough_list),my_trough_list
    if len(my_trough_list) != 8:
        print "[notice]troughs info:", len(my_trough_list),my_trough_list,vertical_projection

    return my_trough_list

def get_auto_division(filename):
    '''
    使用垂直投影法切割字符
    '''
    font=[]
    img = Image.open( filename )
    #img = img.convert("1")
    width,height=img.size

    vp = get_point(img)
    troughs = locate_troughs(vp)

    for i in range(0, 8, 2):
        start_x, end_x = troughs[i], troughs[i+1]
        #print start_x, end_x
        y = 0
        #if img.mode != "RGB": img = img.convert("RGB")

        big = img.crop((start_x, y, end_x, y+height))
        big = big.resize((60, 100), Image.NEAREST)

        font.append( big )

    #print "font:", font
    return font

def auto_division(dir, font_dir):
    '''
    切割字符图片，保存到文件
    '''
    for f in os.listdir(dir):
        if f.endswith(".jpg"):
            #print f
            fonts = get_auto_division(os.path.join(dir, f))
            i = 0
            for font in fonts:
                i += 1
                file_name = "%s_%s.jpg" %(f.split(".")[0], i)
                font.save(os.path.join(font_dir, file_name))


def binary(im):
    '''
    图片转化为二进制的点
    PS:这里要注意背景，背景用0表示，验证码字符用1表示
    '''

    x, y = im.size

    #'''
    Lim = im.convert('L')
    threshold = 80
    table = []
    for i in range(256):
        if i > threshold:
            table.append(0)
        else:
            table.append(1)

    #print table
    #'''
    # convert to binary image by the table
    bim = Lim.point(table, '1')
    bdata = bim.load()
    out = ""
    for a in range(y):
        for b in range(x):
            out = out + str(bdata[b,a])
    #    out = out + '\n'
    #print out
    return out

def totrain(x):
    '''

    :param x:
    :return:
    '''

    path = "simple_font/"
    f = []
    filelist = os.listdir(path)

    for sub in filelist:
        subpath = path + sub
        if os.path.isdir( subpath ):
            ff = os.listdir( subpath )
            for one in ff:
                if not one.endswith(".jpg"):continue
                im = Image.open(subpath + "/" + one)
                a = binary(im)
                d = []
                c = 1

                for b in a:
                    d.append((c,int(b)))
                    c = c + 1

                if str(x) == str(sub):
                    e = (1,d)
                else:
                    e = (-1,d)

                f.append(e)
    return f

def trainall():
    '''
    使用svm训练0-9 10个数字样本
    :return:
    '''
    for i in range(10):
        print "training ", i
        training_data = totrain(i)
        model = svmlight.learn(training_data, type='classification', verbosity=0)
        model_name = 'model/'+str(i)
        svmlight.write_model(model, model_name)  #write model

        '''
        # 训练结果测试
        model=svmlight.read_model(model_name)
        # 读取指定字体样本，直接检验训练结果
        test_im = Image.open("simple_font/1/65_1.jpg")
        test_data =  binary(test_im)
        test_data = chformat(test_data)
        predictions = svmlight.classify(model, test_data)
        if predictions[0] >0:
            print "yes",predictions
        #'''

def chformat(x):
    f = []
    d = []
    c = 1
    for b in x:
        d.append((c, int(b)))
        c = c + 1
    e = (1, d)
    f.append(e)
    return f

def rec_char(div_img):
    '''
    切割后的单个字符识别
    '''
    result = ""
    test = binary(div_img)
    test = chformat(test)
    for i in range(10):
        model = svmlight.read_model("model/"+str(i))
        prediction = svmlight.classify(model, test)
        #print prediction
        if prediction[0] >0:
            result = str(i)
            #print prediction[0]

    return result

def rec_pic(filename):
    '''
    验证码图片识别
    '''
    result = ""
    for div_img in get_auto_division(filename):
        result = result + rec_char(div_img)

    return result


def svm_rec(input_dir):
    p = 0
    c = 0
    for f in os.listdir(input_dir):
        if f.endswith(".jpg"):
            p += 1
            mImgFile = os.path.join(input_dir, f)
            result = rec_pic(mImgFile)

            if len(result)==4:
                    c += 1
                    print "rec:",f,result
            else:
                print "----", f, result
                pass

    print "check %d pics, recognise %d pics, rate:%0.2f%%" %( p, c, float(c)/p*100 )

def print_xy(file):
    im = Image.open(file)
    x, y = im.size

    #'''
    Lim = im.convert('L')
    threshold = 80
    table = []
    for i in range(256):
        if i > threshold:
            table.append(0)
        else:
            table.append(1)

    # convert to binary image by the table
    bim = Lim.point(table, '1')
    bdata=bim.load()

    for a in range(y):
        for b in range(x):
            print  bdata[b,a],
        print

def vp_demo(pic_dir):
    '''
    垂直投影展示demo
    :return:
    '''

    tmp_dir1 = "vp_tmp1"
    if not os.path.exists(tmp_dir1):os.makedirs(tmp_dir1)
    #binaryzation(pic_dir, tmp_dir1)

    imgf = "vp_tmp1/0.jpg"
    print_xy(imgf)
    im = Image.open(imgf)
    get_point(im)

def check_svm(pic_dir):
    '''
    开始使用了固定距标准切割，识别效果一般，识别率70%左右；
    直接垂直投影切割，识别率98%左右（没有进行降噪处理）
    '''

    ## 二值化
    tmp_dir1 = "simple_tmp1"
    if not os.path.exists(tmp_dir1):os.makedirs(tmp_dir1)
    binaryzation(pic_dir, tmp_dir1, True)

    ## 切割字符到字符库
    tmp_dir2 = "simple_tmp2"
    if not os.path.exists(tmp_dir2):os.makedirs(tmp_dir2)
    #使用垂直投影法切割
    #auto_division(tmp_dir1, tmp_dir2)

    ## 切割后, 需要人工挑选样本到样本库，每个字符10个样本
    font_dir = "simple_font"
    model_dir = "model"
    if not os.path.exists(model_dir):os.makedirs(model_dir)

    ## 进行训练
    trainall()

    ## 识别二值化后的图片效果
    svm_rec(tmp_dir1)


if __name__ == '__main__':


    url = "http://csp.csm.org.cn/umt/servlet/validcode"

    pic_dir = "simple_pic"
    if not os.path.exists(pic_dir):os.makedirs(pic_dir)
    #get_batch_pic(url, pic_dir)


    #vp_demo(pic_dir)

    # 使用svm算法识别
    check_svm(pic_dir)

