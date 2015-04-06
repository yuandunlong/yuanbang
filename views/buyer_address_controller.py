# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request
from flask import json,Response
from database.models import BuyerAddress,db
from utils import check_token
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
        xzb=data.get('xzb','')
        if xzb=='':
            xzb=0
        yzb=data.get('yzb','')
        if yzb=='':
            yzb=0
        buyer_address.xzb=Decimal(xzb)
        buyer_address.yzb=Decimal(yzb)
        buyer_address.is_default=data.get('is_default')
        #如果是默认地址
        if buyer_address.is_default=="1" or buyer_address.is_default==1:
            db.engine.execute('update tb_buyeraddress set IsDefault=0 where BuyerID=%s',(user_info.buyer_id))
        db.session.add(buyer_address)
        db.session.commit()
        result['buyer_address']=buyer_address.get_map();  
    except Exception,e:
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
            if data.get('xzb'):
                buyer_address.xzb=Decimal(data.get('xzb'))
            if data.get('yzb'):
                buyer_address.yzb=Decimal(data.get('yzb'))
            if data.get('is_default'):
                buyer_address.is_default=data.get('is_default')
                if buyer_address.is_default=='1':
                    db.engine.execute('update tb_buyeraddress set IsDefault=0 where BuyerID=%s',(user_info.buyer_id))
            db.session.commit()
    except Exception,e:
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
                buyer_addresses.append(buyer_address.get_map())
        result['buyer_addresses']=buyer_addresses
    except Exception,e:
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
        result['msg']=e.message
        result['code']=0
        
    return Response(json.dumps(result),content_type="application/json")
        
     
   