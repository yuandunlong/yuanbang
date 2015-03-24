# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request
from flask import json,Response
from database.models import OrderDetail,db,Order
from utils import check_token,build_order_no
from datetime import datetime
order_controller=Blueprint('order_controller',__name__)
@order_controller.route('/m1/private/get_order_detail_by_order_no',methods=['POST'])
@check_token
def get_order_detail_by_order_no():
    
    result={'code':1,'msg':'ok'}
    
    try:
        query=request.get_json()
        order_no=query['order_no']
        order_detail=OrderDetail.query.filter_by(order_no=order_no).first()
        if order_detail:
            result['order_detail']=order_detail.get_map()
        else:
            result['order_detail']={}
    except Exception,e:
        result['code']='0'
        result['msg']=e.message
    return Response(json.dumps(result),content_type="application/json")

@order_controller.route('/m1/private/create_order',methods=['POST'])
@check_token
def create_order(token_type,user_info):
    result={'code':1,'msg':'ok'}
    
    try:
        query=request.get_json()
        shop_id=query['shop_id']
        address_id=query['address_id']
        sale_money=query['sale_money']
        send_address=query['send_address']
        receiver=query['receiver']
        phone=query['phone']
        remark=query.get('remark')
        freight=query.get('freight')
        
        order=Order()
        order.order_no=build_order_no()
        order.shop_id=shop_id
        order.buyer_id=user_info.buyer_id
        order.freight=freight
        order.receiver=receiver
        order.send_address=send_address
        order.address_id=address_id
        order.sale_money=sale_money
        order.phone=phone
        order.submit_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.session.add(order)
        
        order_detail=OrderDetail()
        order_detail.order_no=''
        
        
    except Exception,e:        
        result['msg']=e.message
        
    return Response(json.dumps(result),content_type="application/json")
        
    
    
    