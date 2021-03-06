# -*- coding: utf-8 -*-
from flask import request,Response,json
from database.models import db,Token,Buyer,ShopInfo
from datetime import datetime
import time
import math
from decimal import Decimal
import threading
import urllib2
from email.mime.text import MIMEText
import smtplib
def check_token(func):
    def wrapper():
        response={'code':0,'msg':''}
        access_token=request.args.get('token','')
        
        if access_token=='':
            response['msg']='access denied,please provide token'
            return Response(json.dumps(response))
        else:
            token=Token.query.filter_by(access_token=access_token).first()
            if token:
                if token.token_type==1:
                    buyer=Buyer.query.get(token.user_id)
                    if not buyer:
                        response['msg']='wrong token'
                        return Response(json.dumps(response),content_type="application/json")
                    else:
                        info=buyer
                elif token.token_type==2:
                    shop_info=ShopInfo.query.get(token.user_id)
                    if shop_info==None:
                        response['msg']='wrong token'
                        return Response(json.dumps(response),content_type="application/json")
                    else:
                        info=shop_info
            else:
                response['msg']='token not exist'
                return Response(json.dumps(response),content_type="application/json")
        result = func(token.token_type,info)
        return result
    
    wrapper.__name__=func.__name__
    return wrapper

def result_set_converter(result_set):
    arr=[]
    if result_set:
        for result in result_set:
            arr.append(result.get_map())
    return arr
def rows_array_converter(rows):
    arr=[]
    for row in rows:
        arr.append(row_map_converter(row))
    return arr

def row_map_converter(row):
    temp={}
    for (k,v) in row.items():
        if isinstance(v,datetime) or isinstance(v,Decimal):
            v=str(v)
        if k.endswith('ID') or k.endswith('Id'):
            key=k.lower()[:-2]+'_id'
            if str.isdigit(str(v)):
                temp[key]=int(v)
            else:
                temp[key]=str(v)
        else:
            temp[camel_to_underline(k)]=v
    return temp
def sub_map(src,keys):
    result={}
    for key in keys:
        if src.has_key(key):
            result[key]=src[key]
    
    return result

def uniqid(prefix='', more_entropy=False):
    m = time.time()
    uniqid = '%8x%05x' %(math.floor(m),(m-math.floor(m))*1000000)
    if more_entropy:
        valid_chars = list(set(string.hexdigits.lower()))
        entropy_string = ''
        for i in range(0,10,1):
            entropy_string += random.choice(valid_chars)
        uniqid = uniqid + entropy_string
    uniqid = prefix + uniqid
    return uniqid


def build_order_no():
    uiq=uniqid()
    arr=[]
    for i in range(6):
        arr.append(str(ord(uiq[7+i])))
    temp=''.join(arr)
    
    return (datetime.now().strftime('%Y%m%d')+temp[:8])    


def camel_to_underline(camel_format):
    '''
        驼峰命名格式转下划线命名格式
    '''
    underline_format=''
    if isinstance(camel_format, str) or isinstance(camel_format,unicode):
        i=0
        for _s_ in camel_format:
            if _s_.islower() or i==0:
                underline_format += _s_.lower()
            else:
                underline_format +=('_'+_s_.lower())
            i=i+1
    return underline_format

def underline_to_camel(underline_format):
    '''
        下划线命名格式驼峰命名格式
    '''
    camel_format = ''
    if isinstance(underline_format, str):
        for _s_ in underline_format.split('_'):
            camel_format += _s_.capitalize()
    return camel_format


class DecimalEncoder(json.JSONEncoder):
    def _iterencode(self, o, markers=None):
        if isinstance(o, decimal.Decimal):
            # wanted a simple yield str(o) in the next line,
            # but that would mean a yield on the line with super(...),
            # which wouldn't work (see my comment below), so...
            return (str(o) for o in [o])
        return super(DecimalEncoder, self)._iterencode(o, markers)
    

def jw_2_mkt(jd,wd):
    response=urllib2.urlopen('http://api.map.baidu.com/geoconv/v1/?coords='+str(jd)+','+str(wd)+'&from=5&to=6&ak=XiCHxodqN1PXicr42Pw3WKVM').read()
    
    x=float(jd)*20037508.342789/180
    y=math.log(math.tan((90+float(wd))*math.pi/360))/(math.pi/180)
    y = y *20037508.34789/180
    return x,y


def send_mail(to_list,subject,content):  
    mail_user="yuanbangshop"
    mail_postfix="163.com"

    me="远邦邻里网"+"<"+mail_user+"@"+mail_postfix+">"  
    msg = MIMEText(content,_subtype='html',_charset='utf-8')  
    msg['Subject'] = subject  
    msg['From'] = me  
    msg['To'] = ";".join(to_list)  
    try:  
        server = smtplib.SMTP()  
        server.connect('smtp.163.com')  
        server.login('yuanbangshop@163.com',"123456yb")  
        server.sendmail(me, to_list, msg.as_string())  
        server.close()  
        return True  
    except Exception, e:  
        server.close() 
        print str(e)  
        return False  

        
    
        