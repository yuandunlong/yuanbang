# -*- coding: utf-8 -*-
from flask import Blueprint,current_app
from flask import request
from flask import json,Response
from database.models import BuyerAddress,db,Community
from utils import check_token,jw_2_mkt,result_set_converter,rows_array_converter
from decimal import Decimal
buyer_address_controller=Blueprint('buyer_address_controller',__name__)
@buyer_address_controller.route('/m1/private/add_address',methods=['POST'])
@check_token
def add_address(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        buyer_address=BuyerAddress()
        buyer_address.buyer_id=user_info.buyer_id
        buyer_address.consignee=data.get('consignee')
        buyer_address.phone=data.get('phone')
        buyer_address.detail_address=data.get('detail_address')
        community_id=data.get('community_id',None)
        xzb=data.get('xzb','')
        if xzb=='':
            xzb=0
        yzb=data.get('yzb','')
        if yzb=='':
            yzb=0
        buyer_address.xzb=Decimal(xzb)
        buyer_address.yzb=Decimal(yzb)
        
        buyer_address.mktxzb=Decimal(data['mktxzb'])
        buyer_address.mktyzb=Decimal(data['mktyzb'])
        buyer_address.is_default=str(data.get('is_default'))
        if community_id:
            buyer_address.community_id=community_id

        #如果是默认地址
        if buyer_address.is_default=="1" or buyer_address.is_default==1:
            db.engine.execute('update tb_buyeraddress set IsDefault=0 where BuyerID=%s',(user_info.buyer_id))
        db.session.add(buyer_address)
        db.session.commit()
        result['buyer_address']=buyer_address.get_map();  
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type="application/json")

@buyer_address_controller.route('/m1/private/update_address',methods=['POST'])
@check_token        
def update_address(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        address_id=data['address_id']
        buyer_address=BuyerAddress.query.filter_by(address_id=address_id,buyer_id=user_info.buyer_id).first()
        if buyer_address:
            if data.get('detail_address'):
                buyer_address.detail_address=data.get('detail_address')
            if data.get('consignee'):
                buyer_address.consignee=data.get('consignee')
            if data.get('phone'):
                buyer_address.phone=data.get('phone')
            xzb=data.get('xzb','')
            if xzb=='':
                xzb=0
                buyer_address.xzb=Decimal(xzb)
            yzb=data.get('yzb','')
            if yzb=='':
                yzb=0
                buyer_address.yzb=Decimal(yzb)
            if data.get('is_default'):
                buyer_address.is_default=str(data.get('is_default'))
                if buyer_address.is_default=='1' or buyer_address.is_default==1:
                    db.engine.execute('update tb_buyeraddress set IsDefault=0 where BuyerID=%s',(user_info.buyer_id))
            mktxzb=data.get('mktxzb',None)
            mktyzb=data.get('mktyzb',None)
            if mktxzb and mktyzb:
                buyer_address.mktxzb=Decimal(mktxzb)
                buyer_address.mktyzb=Decimal(mktyzb)
            community_id=data.get('community_id',None)
            if community_id:
                buyer_address.community_id=community_id
            db.session.commit()
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type="application/json")
        
@buyer_address_controller.route('/m1/private/get_addresses_by_user',methods=['GET'])
@check_token
def get_addresses_by_user(token_type,info):
    
    result={'code':1,'msg':'ok'}
    
    try:
        result_set=BuyerAddress.query.filter_by(buyer_id=info.buyer_id).all()
        buyer_addresses=[]
        if result:
            for buyer_address in result_set:
                communityId=buyer_address.community_id
                c=Community.query.filter_by(community_id=communityId).first()
                tmp=buyer_address.get_map()
                tmp['community']=tmp
                buyer_addresses.append(tmp)

        result['buyer_addresses']=buyer_addresses
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type="application/json")

@buyer_address_controller.route('/m1/private/set_default_address',methods=['POST']) 
@check_token
def set_default_address(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        query=request.get_json()
        address_id=query['address_id']
        sql1='update tb_buyeraddress set IsDefault=0 where BuyerID=%s';
        sql2='update tb_buyeraddress set IsDefault=1 where BuyerID=%s and AddressID=%s'
        db.engine.execute(sql1,(user_info.buyer_id))
        db.engine.execute(sql2,(user_info.buyer_id,address_id))        
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type="application/json")   

@buyer_address_controller.route('/m1/private/delete_address',methods=['POST'])
@check_token
def delete_address(token_type,user_info):
    result={'code':1,'msg':'ok'}
    
    try:
        data=request.get_json()
        address_id=data['address_id']
        db.engine.execute('delete from tb_buyeraddress where AddressID =%s',(address_id))
    except Exception,e:
        current_app.logger.exception(e)
        result['msg']=e.message
        result['code']=0
        
    return Response(json.dumps(result),content_type="application/json")
        
@buyer_address_controller.route('/m1/private/get_all_communities',methods=['GET'])
@check_token
def get_all_communities(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        result_set=Community.query.all()
        result['communities']=result_set_converter(result_set)
    except Exception,e:
        current_app.logger.exception(e)
        result['msg']=e.message
        result['code']=0
    return Response(json.dumps(result),content_type="application/json")

@buyer_address_controller.route('/m1/private/get_communities_by_xyzb',methods=['POST'])
@check_token
def get_communities_by_xyzb():

    result={'code':1,'msg':'ok'}
    data= request.json
    mktxzb=data.get('mktxzb',None)
    mktyzb=data.get('mktyzb',None)
    try:
        sql='''select c.communityId,c.communityName,ROUND(SQRT(POW(%s - c.mktxzb, 2) + POW(%s- c.mktyzb, 2)),2) AS Distance from tb_community_m c where ROUND(SQRT(POW(%s - c.mktxzb, 2) + POW(%s- c.mktyzb, 2)),2)<=500 order by Distance'''

        if mktyzb and mktxzb:
            rows=db.engine.execute(sql,(mktxzb,mktyzb,mktxzb,mktyzb))
            result['communities']=rows_array_converter(rows)
        else:
            result['communities']=[]
    except Exception,e:
        current_app.logger.exception(e)
        result['msg']=e.message
        result['code']=0
    return Response(json.dumps(result),content_type='application/json')


