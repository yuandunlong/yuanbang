# -*- coding: utf-8 -*-
from flask import Blueprint,current_app
from flask import request
from flask import json,Response
import urllib2
import random
from database.models import Buyer,db
from werkzeug.contrib.cache import SimpleCache
from datetime import datetime
signup_controller=Blueprint('signup_controller',__name__)

tempate='''http://106.ihuyi.cn/webservice/sms.php?method=Submit&account={0}&password={1}&mobile={2}&content=您的验证码是：【{3}】。请不要把验证码泄露给其他人。'''

cache = SimpleCache(threshold=5000, default_timeout=300)
@signup_controller.route('/m1/public/get_mobile_check_code',methods=['POST'])
def get_mobile_check_code():
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        mobile=data['mobile']
        check_code=''.join(random.sample('123467890',6))
        result['check_code']=check_code
        cache.set(mobile,check_code)
        page=urllib2.urlopen(tempate.format(current_app.config['SMS_ACCOUNT'],current_app.config['SMS_PWD'],mobile,check_code)).read()
        current_app.logger.debug(page)
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        
        
@signup_controller.route('/m1/public/check_mobile_exist',methods=['POST'])        
def check_mobile_exist():
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        buyer=Buyer.query.filter_by(account=data['mobile']).first()
        if buyer:
            result['exist']=True
        else:
            result['exist']=False
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')

@signup_controller.route('/m1/public/buyer_sign_up',methods=['POST'])
def buyer_sign_up():
    result={'code':1,'msg':"ok"}
    try:
        data=request.get_json()
        
        check_code=data['check_code']
        mobile=data['mobile']
        cache_check_code= cache.get(mobile)
        if cache_check_code==check_code:
            passwd=data['passwd']
            buyer=Buyer()
            buyer.account=mobile
            buyer.password=passwd
            buyer.is_validate='1'
            buyer.is_visable='1'
            buyer.create_time=datetime.now()
            buyer.status='0'
            db.session.add(buyer)
            db.session.commit()
        else:
            result['code']=0
            result['msg']='wrong check code'
        
        
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=1
        result['msg']=e.message
        
    return Response(json.dumps(result),content_type='application/json')
    