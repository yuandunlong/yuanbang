# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request
from flask import json,Response
from database.models import OrderDetail,db

order_controller=Blueprint('order_controller',__name__)
@order_controller.route('/m1/private/get_order_detail_by_order_no',methods=['post'])
def get_order_detail_by_order_no():
    
    result={'code':'1','msg':'ok'}
    
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
    return Response(json.dumps(result))
        
    
    
    