# -*- coding: utf-8 -*-
from flask import Blueprint,current_app
from flask import request
from flask import json, jsonify, Response
from database.models import Buyer, BuyerAddress, Order, Message, Attention, db,Member,DeliveryMan
from utils import check_token, result_set_converter,rows_array_converter
from datetime import datetime
buyer_controller = Blueprint("buyer_controller", __name__)


@buyer_controller.route('/test', methods=['GET', 'POST'])
def test():
    result = {}
    sql = 'select BuyerID from tb_buyer where BuyerID=%s'
    result_set = db.engine.execute(sql, (12))
    for row in result_set:
        print row['BuyerID']
    return Response(json.dumps(result), content_type="application/json")


@buyer_controller.route('/m1/private/get_buyer_info', methods=['POST'])
@check_token
def get_buyer_info(token_type, info):
    result = {'code': 1, 'msg': ''}
    try:
        query = request.get_json()
        what = query['what']
        if what.count('buyer') > 0:
            result['buyer'] = info.get_map()
        if what.count('my_orders') > 0:
            orders = Order.query.filter_by(buyer_id=info.buyer_id).all()
            orders_arr = []
            for order in orders:
                orders_arr.append(order.get_map())
            result['my_orders'] = orders_arr
        if what.count('attention_shops') > 0:
            attentions_shops = Attention.query.filter_by(attention_type='0', buyer_id=info.buyer_id).all()
            arr = []
            if attentions_shops:
                for attention_shop in attentions_shops:
                    arr.append({'shop_id': attention_shop.attention_id, 'id': attention_shop.id})
            result['attention_shops'] = arr
        if what.count('my_msg') > 0:
            messages = Message.query.filter_by(receiver=info.buyer_id).all()
            msg_arr = []
            for msg in messages:
                msg_arr.append(msg.get_map())
            result['my_msg'] = msg_arr
        if what.count('attention_goods') > 0:
            attentions_goods = Attention.query.filter_by(attention_type='1', buyer_id=info.buyer_id).all()
            if attentions_goods:
                goods_arr = []
                for attention_good in attentions_goods:
                    goods_arr.append({'id': attention_good.id, 'goods_id': attention_good.attention_id})
                result['attention_goods'] = goods_arr
        if what.count('buyer_address') > 0:
            result_set = BuyerAddress.query.filter_by(buyer_id=info.buyer_id).all()
            result['buyer_address'] = result_set_converter(result_set)
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type="application/json")
        
        
@buyer_controller.route('/m1/private/be_memeber', methods=['POST'])
@check_token       
def be_memeber(token_type,buyer):
    
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        if not Member.query.filter_by(shop_id=data['shop_id'],buyer_id=buyer.buyer_id).first():
            memeber=Member(shop_id=data['shop_id'],buyer_id=buyer.buyer_id,create_time=datetime.now())
            db.session.add(memeber)
            db.session.commit()
        
    except Exception,e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type="application/json") 

@buyer_controller.route('/m1/private/be_delivery_man', methods=['POST'])       
@check_token           
def be_delivery_man(token_type,buyer):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        shop_id=data['shop_id']
        if not DeliveryMan.query.filter_by(shop_id=shop_id,buyer_id=buyer.buyer_id).first():
            delivery_man=DeliveryMan()
            delivery_man.shop_id=shop_id
            delivery_man.buyer_id=buyer.buyer_id
            db.session.add(delivery_man)
            db.session.commit()
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type="application/json")
        

@buyer_controller.route('/m1/private/get_all_my_coupons', methods=['GET'])       
@check_token
def get_all_my_coupons(token_type,buyer):
    result={'code':1,'msg':'ok'}
    try:
        sql='''
        SELECT
    c.ShopID,
    s.ShopName,
    IFNULL(
        sum(
            CASE
            WHEN CouponType = '0' THEN
            CouponMoney
            ELSE
            - CouponMoney
            END
            ),
        0
        ) AS CanUseCouponSum,
    IFNULL(
        sum(
            CASE
            WHEN CouponType = '0' THEN
            CouponMoney
            ELSE
            0
            END
            ),
        0
        ) AS GetCouponSum,
    IFNULL(
        sum(
            CASE
            WHEN CouponType = '1' THEN
            CouponMoney
            ELSE
            0
            END
            ),
        0
        ) AS UsedCouponSum
    FROM
        tb_coupon c
    INNER JOIN tb_shopinfo_s s on s.ShopID = c.ShopID
    WHERE
        BuyerID = %s
    GROUP BY c.ShopID,s.ShopName
        '''
        rows=db.engine.execute(sql,(buyer.buyer_id))
        result['coupons']=rows_array_converter(rows)
    
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')


@buyer_controller.route('/m1/private/query_coupons_by_shop_id', methods=['POST'])       
@check_token
def query_coupons_by_shop_id(token_type,buyer):
    result={'code':1,'msg':'ok'}
    
    try:
        data=request.get_json()
        sql='''SELECT
            s.ShopName,
            CASE c.CouponType
                WHEN '0' THEN
                    '收入'
                WHEN '1' THEN
                    '支出'
            END AS CouponTypeName,
            c.OperateTime,
            c.OrderNO,
            c.ShopID,
            CASE c.CouponType
                WHEN '0' THEN
                    c.CouponMoney
                WHEN '1' THEN
                    -c.CouponMoney
                END AS CouponMoney,
            c.Remark
            FROM
                tb_coupon c
            LEFT JOIN tb_shopinfo_s s ON c.ShopID = s.ShopID
            WHERE c.BuyerID = %s
            AND c.ShopID = %s    ''' 
        
        rows=db.engine.execute(sql,(buyer.buyer_id,data['shop_id']))
        result['coupons']=rows_array_converter(rows)
        
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        
@buyer_controller.route('/m1/private/update_buyer_info', methods=['POST'])       
@check_token      
def update_buyer_info(token_type,buyer):
    result={"code":1,'msg':'ok'}
    
    try:
        data=request.get_json()
        buyer_id=int(data.get(buyer_id,0))
        buyer=Buyer.query.get(buyer_id)
        avatar=data.get('avatar',None)
        real_name=data.get('real_name',None)
        nick_name=data.get('nick_name',None)
        sex=data.get('sex',None)
        
        if avatar:
            buyer.avatar=avatar
        if real_name:
            buyer.real_name=real_name
        if nick_name:
            buer.nick_name=nick_name
        if sex:
            buyer.sex=sex
        db.session.commit()
            
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type="application/json")
        
    
     