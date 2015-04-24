# -*- coding: utf-8 -*-
from flask import json,Response,Blueprint,request,json
from views.utils import check_token
shopcenter_controller=Blueprint('shopcenter_controller',__name__)
@shopcenter_controller.route('/m1/private/shopcenter/get_shop_info',methods=['GET'])
@check_token
def get_shop_info(token_type,shop):
    result={'code':1,'msg':'ok'}
    try:
        result['shop_info']=shop.get_map()
    except Exception,e:
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type="application/json")
@shopcenter_controller.route('/m1/private/shopcenter/get_goods',methods=['GET'])
@check_token
def get_goods(token_type,shop):
    
    result={'code':1,'msg':'ok'}
    
    try:
        
    except Exception,e:
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        
@shopcenter_controller.route('/m1/private/shopcenter/get_orders')
@check_token
def get_orders(token_type,shop):
    result={'code':1,'msg':'ok'}
    try:
        
    except Exception,e:
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        
    
    
@shopcenter_controller.route('/m1/private/shopcenter/get_msgs')    
@check_token
def get_msgs(token_type,shop):
    
    result={'code':1,'msg':'ok'}
    try:
        
    except Exception,e:
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        