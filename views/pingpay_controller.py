# -*- coding: utf-8 -*-
from flask import Blueprint,current_app
from flask import request
from flask import json,Response
from utils import check_token
from database.models import Order,ShopInfo,db
import pingpp

pingpp.api_key = 'pk_live_uDCWT44Wn1S8SuTiz5yzTWzP'

pingpay_controller=Blueprint('pingpay_controller',__name__)

@pingpay_controller.route('/m1/private/order/get_order_charge',methods=['POST'])
@check_token
def get_order_charge(token_type,user_info):
    
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        order_no=data['order_no']
        channel=data['channel']
        buyer_id=user_info.buyer_id
        
        order=Order.query.filter_by(order_no=order_no).first()
        if order:
            
            shop_info=ShopInfo.query.filter_by(shop_id=order.shop_id).first()
            subject='mysbject'
            if shop_info:
                subject=shop_info.shop_name+" 订单"
        #多个订单一起支付问题---》=速度有点慢目前不支持
            ch = pingpp.Charge.create(
            order_no=order_no,
            amount=int(order.sale_money*100), #订单总金额
            app=dict(id='app_HCur9S9iLGG0a58i'),
            channel=channel,
            currency='cny',
            client_ip=request.remote_addr,
            subject=subject,
            body='no body',
        )
        
        result['charge']=ch
        
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')

@pingpay_controller.route('/m1/public/order/paynotify',methods=['POST'])
def pay_notify_hooks():
    try:
        data=request.get_json()
        if data['type']=='charge.succeeded':
            result=data['data']['object']
            order_no=result['order_no']
            order=Order.query.filter_by(order_no=order_no).first()
            if order:
                order.pay_status='1' #已支付
                db.session.commit()
    except Exception,e:
        current_app.logger.exception(e)
    return Response(status=200)
    
    
    