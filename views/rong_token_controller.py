
from flask import Blueprint,Response,json,request
from rong import ApiClient
from views.utils import uniqid,check_token
from database.models import Buyer,ShopInfo
import hashlib
import logging
import os
rong_token_controller=Blueprint("rong_token_controller",__name__)
logging.basicConfig(level=logging.INFO)
os.environ.setdefault('rongcloud_app_key', 'c9kqb3rdkhm3j')
os.environ.setdefault('rongcloud_app_secret', 'phsiqN68xW')
@rong_token_controller.route('/m1/private/get_chat_token',methods=['POST','GET'])
@check_token
def get_chat_token(token_type,user_info):
    result={'code':1,'msg':'ok'}
    
    nonce=uniqid()
    try:
        if token_type==1:
            token_id='buyer'+str(user_info.buyer_id)+user_info.account
        elif token_type==2:
            token_id='shop'+str(user_info.shop_id)+user_info.account
        
        api=ApiClient()
        token=api.call_api(
        action="/user/getToken",
        params={
            "userId":token_id,
            "name":user_info.account,
            "portraitUri":"p1"
        }
        )
        
        result['token']=token
    except Exception ,e:
        result['code']=1
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
@rong_token_controller.route('/m1/private/get_chat_userId',methods=['POST'])
@check_token
def get_chat_userId(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        to_id=data['to_id']
        if data['user_type']=='shop':
            shop_info=ShopInfo.query.filter_by(shop_id=to_id).first()
            if shop_info:
                result['userId']='shop'+str(shop_info.shop_id)+shop_info.account
        elif data['user_type']=='buyer':
            buyer=Buyer.query.filter_by(buyer_id=to_id).first()
            if buyer:
                result['userId']='shop'+str(buyer.buyer_id)+buyer.account
                
        
    except Exception,e:
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        
        