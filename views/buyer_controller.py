# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request
from flask import json,jsonify,Response
from database.models import Buyer,BuyerAddress,Order,Message,db
from utils import check_token
buyer_controller=Blueprint("buyer_controller",__name__)
@buyer_controller.route('/test',methods=['GET', 'POST'])
def test():
    
    buyer=Buyer.query.filter().first()
    ba=BuyerAddress.query.filter_by(buyer_id=9)[0]
    result={"hello":"world"}
    return Response(json.dumps(result),mimetype='application/json')

@buyer_controller.route('/m1/private/get_buyer_info',methods=['POST'])
@check_token
def get_buyer_info(token_type,info):
    result={'code':0,'msg':''}
    try:
        query=request.get_json()
        what=query['what']
        if what.count('user')>0:
            result['buyer_info']=info.get_map()
        if what.count('my_orders')>=0:
            orders=Order.query.filter_by(buyer_id=info.buyer_id).all()
            orders_arr=[]
            for order in orders:
                orders_arr.append(order.get_map())
            result['my_orders']=orders_arr
        if what.count('attention_shops')>=0:

            pass
        if what.count('my_msg')>=0:
            messages=Message.query.filter_by(receiver=info.buyer_id).all()
            msg_arr=[]
            for msg in messages:
                msg_arr.append(msg.get_map())
            result['my_msg']=msg_arr
        if what.count('attention_goods')>=0:
            pass
        if what.count('buyer_address')>0:
            pass
            
    except Exception,e:
        result['msg']=e.message
    return Response(json.dumps(result))
        
        
        
    
