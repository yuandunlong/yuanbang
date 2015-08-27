# -*- coding: utf-8 -*-
from flask import Blueprint,current_app
from flask import request
from flask import json,jsonify,Response
from utils import check_token
from database.models import Order
import pingpp

pingpp.api_key = 'sk_test_y9azT8SKKWv9WDW9G4unTW9G'

pingpay_controller=Blueprint('pingpay_controller',__name__)

@pingpay_controller.route('/m1/private/order/begin_payfor_order',methods=['POST'])
@check_token
def get_order_charge(token_type,user_info):
    
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        order_no=data['order_no']
        amount=data['amount']
        channel=data['channel']
        buyer_id=user_info.buyer_id
        
        order=Order.query.filter_by(order_no=order_no).first()
        if order:
            
        #多个订单一起支付问题---》=速度有点慢目前不支持
            ch = pingpp.Charge.create(
            order_no=order_no,
            amount=sale_money, #订单总金额
            app=dict(id='app_1Gqj58ynP0mHeX1q'),
            channel=channel,
            currency='cny',
            client_ip=request.remote_addr,
            subject='Your Subject',
            body='Your Body',
        )
        
        result['charge']=ch
        
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')

@pingpay_controller.route('/m1/private/order/paynotify',methods=['POST'])   
def pay_notify_hooks():
    try:
        data=request.get_json()
        
    except Exception,e:
        current_app.logger.exception(e)
    return Response("ok")
    
    
    