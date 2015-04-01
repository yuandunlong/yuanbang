# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request
from flask import json,Response
from database.models import Attention,db
from datetime import datetime
from utils import check_token,row_map_converter
attention_controller=Blueprint('attention_controller',__name__)
@attention_controller.route('/m1/private/get_attention_shops',methods=['GET'])
@check_token
def get_attention_shops(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        sql='''
        select a.* ,b.*from tb_attention a,tb_shopinfo_s b where a.AttentionID=b.ShopID and a.AttentionType=0 and a.BuyerID=%s
        '''
        result_set=db.engine.execute(sql,(user_info.buyer_id))
        shops=[]
        for row in result_set:
            shops.append(row_map_converter(row))
        result['shops']=shops
    except Exception,e:
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
@attention_controller.route('/m1/private/get_attention_goods',methods=['GET'])
@check_token
def get_attention_goods(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        sql='''
        select a.*,b.* ,
        c.PhotoID,c.PhotoName,c.PhotoPath,c.ThumbnailPath
        from tb_attention a 
        inner join tb_goodsinfo_s b on a.AttentionID=b.GoodsID and a.AttentionType=3
        left join tb_photo c on c.LinkID=b.GoodsID and c.IsChecked=1 and c.IsVisable=1
        where BuyerID=%s
        '''
        result_set=db.engine.execute(sql,(user_info.buyer_id))
        
        goods=[]
        for row in result_set:
            goods.append(row_map_converter(row))
        result['goods']=goods
    except Exception ,e:
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        
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
        