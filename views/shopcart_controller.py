# -*- coding: utf-8 -*-
from flask import json,Response,Blueprint,request,current_app
from utils import check_token,row_map_converter
from datetime import datetime
from database.models import db,ShopCart
from views.order_controller import GetGoodsListFromCart,GetShopListFromCart
shopcart_controller=Blueprint('shopcart_controller',__name__)

@shopcart_controller.route('/m1/private/get_shopcart_list',methods=['GET'])
@check_token
def get_shopcart_list(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        shop_list=GetShopListFromCart(None, None, user_info, 0)
        temp=[];
        for shop in shop_list:
            if str(shop['shop_id']).isdigit():
                temp.append(shop)
                arr=GetGoodsListFromCart(shop['shop_id'], user_info.buyer_id, 0)
                shop['goods']=arr

        result['shopcarts']=temp
    except Exception ,e:
        current_app.logger.exception(e)
        result['msg']=e.message
    return Response(json.dumps(result),content_type="application/json")
    
@shopcart_controller.route('/m1/private/add_goods_into_shopcart',methods=['POST'])
@check_token
def add_goods_into_shopcart(token_type,user_info):
    result={'code':1,"msg":'ok'}
    try:
        data=request.get_json()
        goods_id=data['goods_id']
        quantity=data['quantity']
        is_selected=data.get('is_selected','1')
        shop_cart=ShopCart.query.filter_by(goods_id=goods_id,buyer_id=user_info.buyer_id).first()
        if shop_cart:
            shop_cart.quantity+=int(quantity)
            db.session.commit()
        else:
            shop_cart=ShopCart()
            shop_cart.buyer_id=user_info.buyer_id
            shop_cart.goods_id=goods_id
            shop_cart.quantity=quantity
            shop_cart.is_selected=is_selected
            shop_cart.create_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            db.session.add(shop_cart)
            db.session.commit()
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type="application/json")
        
@shopcart_controller.route('/m1/private/delete_shopcart_goods_by_id',methods=['POST'])
@check_token
def delete_shopcart_goods_by_id(token_type,user_info):
    result={'code':1,'msg':"ok"}
    try:
        data=request.get_json()
        goods_id=data['goods_id']
        if goods_id:
            db.engine.execute('delete from tb_shoppingcart where BuyerID=%s and GoodsID=%s',(user_info.buyer_id,goods_id))
            
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    
    
    return Response(json.dumps(result),content_type="application/json")
        
@shopcart_controller.route('/m1/private/goods_exist_incart',methods=['POST'])
@check_token
def goods_exist_incart(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        goods_id=data['goods_id']
        if goods_id:
            result_set=db.engine.execute('select * from tb_shoppingcart where BuyerID=%s and GoodsID=%s',(user_info.buyer_id,goods_id))
            if result_set.rowcount>=1:
                result['exist']=True
            else:
                result['exist']=False
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type="application/json")
@shopcart_controller.route('/m1/private/add_or_update_goods_into_shopcart',methods=['POST'])
@check_token
def add_or_update_goods_into_shopcart(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        goods_id=data['goods_id']
        quantity=data['quantity']
        shop_cart=ShopCart.query.filter_by(goods_id=goods_id,buyer_id=user_info.buyer_id).first()
        if shop_cart:
            shop_cart.is_selected=data.get('is_selected',"1")
            shop_cart.quantity+=int(quantity)
                
        else:
            shop_cart=ShopCart()
            shop_cart.buyer_id=user_info.buyer_id
            shop_cart.goods_id=goods_id
            shop_cart.quantity=quantity
            shop_cart.is_selected=data.get('is_selected',"1")
            shop_cart.create_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            db.session.add(shop_cart)            
        db.session.commit()
    except Exception,e:
        current_app.logger.exception(e)
        result['msg']=e.message
    return Response(json.dumps(result),content_type="application/json")
        
    
@shopcart_controller.route('/m1/private/update_goods_quantity',methods=['POST'])   
@check_token
def update_goods_quantity(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        goods_id=data['goods_id']
        quantity=data['quantity']
        shop_cart=ShopCart.query.filter_by(goods_id=goods_id,buyer_id=user_info.buyer_id).first()
        if shop_cart:
            shop_cart.quantity=quantity
        db.session.commit()
        
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    
    return Response(json.dumps(result),content_type="application/json")
        
        
@shopcart_controller.route('/m1/private/clear_shopcart')
@check_token
def clear_shopcart(token_type,user_info):
    
    result={'code':1,'msg':'ok'}
    
    try:
        db.engine.execute('delete from tb_shoppingcart where BuyerID=%s',(user_info.buyer_id))
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
        
    return Response(json.dumps(result),content_type="application/json")
        

@shopcart_controller.route('/m1/private/select_shopcart_goods',methods=['POST'])
@check_token
def select_shopcart_goods(token_type,user_info):
    result={'code':1,'msg':'ok'}
    
    try:
        data=request.get_json()
        db.engine.execute('update tb_shoppingcart set IsSelected=1 where BuyerID=%s and GoodsID=%s',(user_info.buyer_id,data['goods_id']))
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')

@shopcart_controller.route('/m1/private/unselect_shopcart_goods',methods=['POST'])
@check_token
def unselect_shopcart_goods(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        db.engine.execute('update tb_shoppingcart set IsSelected=0 where BuyerID=%s and GoodsID=%s',(user_info.buyer_id,data['goods_id']))
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        
        
@shopcart_controller.route('/m1/private/unselect_all_shopcart_goods',methods=['POST','GET'])
@check_token
def unselect_all_shopcart_goods(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        db.engine.execute('update tb_shoppingcart set IsSelected=0 where BuyerID=%s ',(user_info.buyer_id))
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')

@shopcart_controller.route('/m1/private/select_all_shopcart_goods',methods=['POST','GET'])
@check_token
def select_all_shopcart_goods(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        db.engine.execute('update tb_shoppingcart set IsSelected=1 where BuyerID=%s ',(user_info.buyer_id))
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
    