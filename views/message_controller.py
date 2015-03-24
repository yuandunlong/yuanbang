# -*- coding: utf-8 -*-
from flask import json,Response,Blueprint,request
from database.models import Message
from utils import check_token
message_controller=Blueprint('message_controller',__name__)
#查询消息信息
@message_controller.route('/m1/private/get_message_info',methods=['POST'])
@check_token
def get_message_info(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        m=Message.query.filter_by(message_id=data['message_id']).first()
        if m:
            result['message']=m.get_map()
    except Exception,e:
        result['code']=1
        result['msg']=e.message
    return Response(json.dumps(result),content_type="application/json")

@message_controller.route('/m1/private/revert_message_info')
@check_token
def revert_message_info(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        m=Message
    except Exception,e:
        result['msg']=e.message
        result['code']=0
    return Response(json.dumps(result),content_type="application/json")
        
    