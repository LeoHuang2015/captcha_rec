#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A simple captcha recognition demo by python-tesseract"""

import os
import tesseract
import urllib2
from PIL import Image, ImageDraw, ImageEnhance,ImageFilter


headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',
           'Referer':""}


def get_batch_pic(url, dir):
    for i in range(100):
        print "download", i
        filename = "%d.jpg" %(i)
        picfile = os.path.join(dir, filename)

        req = urllib2.Request(url,headers = headers)
        file(picfile, "wb").write( urllib2.urlopen(req).read() )

def binaryzation(input_dir, output_dir):
    for f in os.listdir(input_dir):
        if f.endswith(".jpg"):
            #if f!="1.jpg":continue
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
            #img = img.convert("RGBA")
            img.save( output_file )

def rec(input_dir):
    api = tesseract.TessBaseAPI()
    api.Init(".","eng",tesseract.OEM_DEFAULT)
    #api.SetVariable("tessedit_char_whitelist", "abcdefghijklmnopqrstuvwxyz")
    api.SetVariable("tessedit_char_whitelist", "0123456789")
    api.SetPageSegMode(tesseract.PSM_AUTO)
    p = 0
    c = 0

    for f in os.listdir(input_dir):
        if f.endswith(".jpg"):
            p += 1
            #if f!="1.jpg":continue
            imfile = os.path.join( input_dir, f )
            im = open(imfile,"rb").read()
            result = tesseract.ProcessPagesBuffer(im, len(im), api)
            if result:
                result = ''.join(result.split())
                if len(result)==4:
                    c += 1
                    print 'result:',f,result
                else:
                    print "[recognise error]", f, result
                    pass
            else:
                print "[tesseract error]", f
                pass

    print "check %d pics, recognise %d pics, rate:%0.2f%%" %( p, c, float(c)/p*100 )


if __name__ == '__main__':


    url = "http://csp.csm.org.cn/umt/servlet/validcode"

    pic_dir = "simple_pic"
    if not os.path.exists(pic_dir):os.makedirs(pic_dir)
    get_batch_pic(url, pic_dir)

    # 二值化能提升tesseract的识别率
    tmp_dir1 = "tesseract_tmp1"
    if not os.path.exists(tmp_dir1):os.makedirs(tmp_dir1)
    binaryzation(pic_dir, tmp_dir1)

    # 调用tesseract识别， 接近100%的识别率
    rec(tmp_dir1)




    
 