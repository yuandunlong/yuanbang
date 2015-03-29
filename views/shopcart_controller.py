# -*- coding: utf-8 -*-
from flask import json,Response,Blueprint,request
from utils import check_token
from datetime import datetime
from database.models import db,ShopCart
shopcart_controller=Blueprint('shopcart_controller',__name__)

@shopcart_controller.route('/m1/private/get_shopcart_list',methods=['GET','POST'])
@check_token
def get_shopcart_list(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
            sql='''
            SELECT
            x.ShopID,
            x.ShopName,
            a.GoodsID,
            a.CreateTime,
            c.PhotoPath,
            b.GoodsName,
            b.SalePrice,
            b.Discount,
            a.Quantity,
            a.IsSelected,
            b.SetNum,
            b.SetPrice,
            IF (
                a.Quantity >= b.SetNum,
                b.SetPrice,
                round(b.SalePrice * b.Discount, 2)
                ) AS DisPrice,
                IF (
                    a.Quantity >= b.SetNum,
                    round(b.SetPrice * a.Quantity, 2),
                    round(
                        round(b.SalePrice * b.Discount, 2) * a.Quantity,
                        2
                    )
                    ) AS Money,
                IFNULL(d.Quantity,0) AS SumQuantity
            FROM  tb_shoppingcart a
            LEFT JOIN tb_goodsinfo_s b ON a.GoodsID = b.GoodsID
            LEFT JOIN tb_photo c ON b.GoodsID = c.LinkID
            LEFT JOIN tb_shopinfo_s x ON b.ShopID = x.ShopID
            AND c.IsChecked = '1'
            AND c.IsVisable = '1'
            LEFT JOIN (
                SELECT
                GoodsID,
                SUM(Quantity) AS Quantity
                FROM
                tb_purchase_s
                GROUP BY
                GoodsID
                ) d ON a.GoodsID = d.GoodsID
            WHERE
                a.BuyerID = %s
            ORDER BY
                b.ShopID,a.GoodsID ;
            '''
            result_set=db.engine.execute(sql,[user_info.buyer_id])
            arr=[]
            for rows in result_set:
                temp={}
                temp['goods_id']=rows['GoodsID']
                temp['shop_id']=rows['ShopID']
                temp['shop_name']=rows['ShopName']
                temp['is_selected']=rows['IsSelected']
                temp['goods_name']=rows['GoodsName']
                temp['sale_price']=str(rows['SalePrice'])
                temp['photo_path']=rows['PhotoPath']
                temp['discount']=str(rows['Discount'])
                temp['quantity']=rows['Quantity']
                temp['set_num']=rows['SetNum']
                temp['set_price']=rows['SetPrice']
                arr.append(temp)
            
            shopcarts={}
            for item in arr:
                if item['shop_id']==None:
                    continue
                if shopcarts.has_key(item['shop_id']):
                    shopcarts[item.shop_id].append(item)
                else:
                    shopcarts[item['shop_id']]=[]
                    shopcarts[item['shop_id']].append(item)
            result['shopcarts']=shopcarts
    except Exception ,e:
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
        shop_cart=ShopCart()
        shop_cart.buyer_id=user_info.buyer_id
        shop_cart.goods_id=goods_id
        shop_cart.quantity=quantity
        shop_cart.create_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.session.add(shop_cart)
        db.session.commit()
    except Exception,e:
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
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type="application/json")
@shopcart_controller.route('/m1/private/add_or_update_goods_into_shopcart')
@check_token
def add_or_update_goods_into_shopcart(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        goods_id=data['goods_id']
        result_set=db.engine.execute('select * from tb_shoppingcart where BuyerID=%s and GoodsID=%s',(user_info.buyer_id,goods_id))
        if result_set.rowcount>=1:
            shop_cart=ShopCart.query.filter_by(goods_id=goods_id,buyer_id=user_info.buyer_id).first()
            if shop_cart:
                shop_cart.quantity=quantity  
        else:
            shop_cart=ShopCart()
            shop_cart.buyer_id=user_info.buyer_id
            shop_cart.goods_id=goods_id
            shop_cart.quantity=quantity
            shop_cart.create_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            db.session.add(shop_cart)            
        db.session.commit()
    except Exception,e:
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
        result['msg']=e.message
    
    return Response(json.dumps(result),content_type="application/json")
        
        
@shopcart_controller.route('/m1/private/clear_shopcart')
@check_token
def clear_shopcart(token_type,user_info):
    
    result={}
    
    try:
        db.engine.execute('delete from tb_shopingcart where BuyerID=%s',(user_info.buyer_id))
    except Exception,e:
        result['code']=0
        result['msg']=e.message
        
    return Response(json.dumps(result),content_type="application/json")
        
    