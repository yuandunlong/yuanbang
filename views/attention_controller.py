# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request
from flask import json,Response
from database.models import Attention,db
from datetime import datetime
from utils import check_token
attention_controller=Blueprint('attention_controller',__name__)
@attention_controller.route('/m1/private/add_attention_shop',methods=['POST'])
@check_token
def add_attention_shop(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        attention=Attention()
        attention.buyer_id=user_info.buyer_id
        attention.attention_id=data['shop_id']
        attention.attention_type='0'
        attention.attention_time=datetime.today()
        db.session.add(attention)
        db.session.commit()
        
    except Exception,e:
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
@attention_controller.route('/m1/private/cancle_attention_shop',methods=['POST'])  
@check_token
def cancle_attention_shop(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        Attention.query.filter_by(buyer_id=user_info.buyer_id,attention_id=data['shop_id'],attention_type='0').first().delete()
    except Exception,e:
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        
@attention_controller.route('/m1/private/add_attention_goods',methods=['POST'])    
@check_token
def add_attention_goods(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        attention=Attention()
        attention.attention_id=data['goods_id']
        attention.buyer_id=user_info.buyer_id
        attention.attention_time=datetime.today()
        attention.attention_type='3'
        db.session.add(attention)
        db.session.commit()
    except Exception,e:
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')

@attention_controller.route('/m1/private/cancle_attention_goods')   
@check_token
def cancle_attention_goods(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        Attention.query.filter_by(buyer_id=user_info.buyer_id,attention_id=data['goods_id'],attention_type='3').first().delete()
    except Exception,e:
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        