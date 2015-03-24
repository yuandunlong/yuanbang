# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request
from flask import json,jsonify,Response
from database.models import Buyer,BuyerAddress,Order,Message,Attention,db
from utils import check_token,result_set_converter
buyer_controller=Blueprint("buyer_controller",__name__)
@buyer_controller.route('/test',methods=['GET', 'POST'])
def test():
    result={}
    sql='select BuyerID from tb_buyer where BuyerID=%s'
    result_set=db.engine.execute(sql,(12))
    for row in result_set:
        print row['BuyerID']
    return Response(json.dumps(result),content_type="application/json")

@buyer_controller.route('/m1/private/get_buyer_info',methods=['POST'])
@check_token
def get_buyer_info(token_type,info):
    result={'code':0,'msg':''}
    try:
        query=request.get_json()
        what=query['what']
        if what.count('user')>0:
            result['buyer_info']=info.get_map()
        if what.count('my_orders')>0:
            orders=Order.query.filter_by(buyer_id=info.buyer_id).all()
            orders_arr=[]
            for order in orders:
                orders_arr.append(order.get_map())
            result['my_orders']=orders_arr
        if what.count('attention_shops')>0:
            attentions_shops=Attention.query.filter_by(attention_type='0',buyer_id=info.buyer_id).all()
            arr=[]
            if attentions_shops:
                for attention_shop in attentions_shops:
                    arr.append({'shop_id':attention_shop.attention_id,'id':attention_shop.id})
            result['attention_shops']=arr
        if what.count('my_msg')>0:
            messages=Message.query.filter_by(receiver=info.buyer_id).all()
            msg_arr=[]
            for msg in messages:
                msg_arr.append(msg.get_map())
            result['my_msg']=msg_arr
        if what.count('attention_goods')>0:
            attentions_goods=Attention.query.filter_by(attention_type='1',buyer_id=info.buyer_id).all()
            if attentions_goods:
                goods_arr=[]
                for attention_good in attentions_goods:
                    goods_arr.append({'id':attention_good.id,'goods_id':attention_good.attention_id})
                result['attention_goods']=goods_arr
        if what.count('buyer_address')>0:
            result_set=BuyerAddress.query.filter_by(buyer_id=info.buyer_id).all()
            result['buyer_address']=result_set_converter(result_set)
    except Exception,e:
        result['msg']=e.message
    return Response(json.dumps(result),content_type="application/json")
        
        
        
    
