
from flask import Blueprint,Response,json,request,current_app
from rong import ApiClient
from views.utils import uniqid,check_token,row_map_converter
from database.models import Buyer,ShopInfo,db
import hashlib
import logging
import os
rong_token_controller=Blueprint("rong_token_controller",__name__)
logging.basicConfig(level=logging.INFO)
#os.environ.setdefault('rongcloud_app_key', 'c9kqb3rdkhm3j')
#os.environ.setdefault('rongcloud_app_secret', 'phsiqN68xW')
os.environ.setdefault('rongcloud_app_key', '6tnym1brnsc17')
os.environ.setdefault('rongcloud_app_secret', 'MdQzqnbm2ice')
limter='-~-'
@rong_token_controller.route('/m1/private/get_chat_token',methods=['POST','GET'])
@check_token
def get_chat_token(token_type,user_info):
    result={'code':1,'msg':'ok'}
    
    nonce=uniqid()
    try:
        if token_type==1:
            token_id='buyer'+limter+str(user_info.buyer_id)+limter+user_info.account
        elif token_type==2:
            token_id='shop'+limter+str(user_info.shop_id)+limter+user_info.account
        
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
        current_app.logger.exception(e)
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
                result['userId']='shop'+limter+str(shop_info.shop_id)+limter+shop_info.account
                result['name']=shop_info.shop_name
        elif data['user_type']=='buyer':
            buyer=Buyer.query.filter_by(buyer_id=to_id).first()
            if buyer:
                result['userId']='buyer'+limter+str(buyer.buyer_id)+limter+buyer.account
                if buyer.nick_name:
                    result['name']=buyer.nick_name
                elif buyer.real_name:
                    result['name']=buyer.real_name
                
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        
        
        
@rong_token_controller.route('/m1/private/get_chat_info_by_userId',methods=['POST'])
@check_token        
def get_chat_info_by_userId(token_type,user_info):
    
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        
        user_ids=data['user_ids']
        
        shop_accounts=[]
        buyer_accounts=[]
        for user_id in user_ids:
            temp=user_id.split(limter)
            if temp[0]=='shop':
                shop_accounts.append(temp[2])
            elif temp[0]=='buyer':
                buyer_accounts.append(temp[2])
        arr=[]
        if len(shop_accounts)>0:
            
                
            shop_sql=''' select ShopName,Account ,ShopID from tb_shopinfo_s where Account in ( '''
            
            for shop_account in shop_accounts:
                shop_sql+= "'"+shop_account+"'"+','
            shop_sql=shop_sql[:-1]+")"
            shop_result_set=db.engine.execute(shop_sql)
            arr=[]
            for shop_row in shop_result_set:
                temp=row_map_converter(shop_row)
                temp['userId']='shop'+limter+str(temp['shop_id'])+limter+temp['account']
                arr.append(temp)
        if len(buyer_accounts)>0:
            buyer_sql='''select NickName,RealName,Account,BuyerID from tb_buyer where account in ( '''
            for buyer_account in buyer_accounts:
                buyer_sql+="'"+buyer_account+"'"+','
            buyer_sql=buyer_sql[:-1]+")"
            buyer_result_set=db.engine.execute(buyer_sql)
            
            for buyer_row in buyer_result_set:
                temp=row_map_converter(buyer_row)
                temp['userId']='buyer'+limter+str(temp['buyer_id'])+limter+temp['account']
                arr.append(temp)
            
        result['user_infos']=arr
            
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')        
        
        
    