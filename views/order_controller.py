# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request
from flask import Response,json
from database.models import OrderDetail,db,Order
from utils import check_token,build_order_no,DecimalEncoder,row_map_converter
from datetime import datetime
order_controller=Blueprint('order_controller',__name__)
@order_controller.route('/m1/private/get_order_list',methods=['GET'])
@check_token
def get_order_list(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        sql='''
        select a.OrderNo,a.ShopID,a.BuyerID,a.SaleMoney,a.SubmitTime,a.SendTime,a.ConfirmTime,a.Freight,a.AddressID,a.SendAddress,a.Receiver,a.Phone,a.Remark,a.status,a.PayStatus,a.UpdateTime
        ,b.GoodsID,b.BatchNo,b.SalePrice,b.Quantity,b.DiscountPrice,c.ShopName, 
        d.GoodsName,e.PhotoID,e.PhotoName,e.PhotoPath,e.ThumbnailPath,e.SortNo
        from tb_order_s a 
        left join tb_orderdetail_s b on a.OrderNo=b.OrderNo  
        left join tb_shopinfo_s c on a.ShopID=c.ShopID 
        left join tb_goodsinfo_s d on d.GoodsID=b.GoodsID
        left join tb_photo e on e.LinkID=d.GoodsID
        where buyerid=%s
        '''
        result_set=db.engine.execute(sql,(user_info.buyer_id))
        orders={}
        for row in result_set:
            temp=row_map_converter(row)
            if orders.has_key(row['ShopID']):
                orders[row['ShopID']].append(temp)
            else:
                orders[row['ShopID']]=[]
                orders[row['ShopID']].append(temp)
        result['orders']=orders
    except Exception,e:
        result['code']=0
        result['msg']=e.message
        json.dumps(obj)
    return Response(json.dumps(result),content_type='application/json')
        
@order_controller.route('/m1/private/get_order_detail_by_order_no',methods=['POST'])
@check_token
def get_order_detail_by_order_no(token_type,user_info):
    
    result={'code':1,'msg':'ok'}
    
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
    return Response(json.dumps(result),content_type="application/json")

@order_controller.route('/m1/private/create_order',methods=['POST'])
@check_token
def create_order(token_type,user_info):
    result={'code':1,'msg':'ok'}
    
    try:
        query=request.get_json()
        shop_id=query['shop_id']
        address_id=query['address_id']
        sale_money=query['sale_money']
        send_address=query['send_address']
        receiver=query['receiver']
        phone=query['phone']
        remark=query.get('remark')
        freight=query.get('freight')
        goods_id=query['goods_id']
        
        order=Order()
        order.order_no=build_order_no()
        order.shop_id=shop_id
        order.buyer_id=user_info.buyer_id
        order.freight=freight
        order.receiver=receiver
        order.send_address=send_address
        order.address_id=address_id
        order.sale_money=sale_money
        order.phone=phone
        order.submit_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.session.add(order)
        
        order_detail=OrderDetail()
        order_detail.order_no=order.order_no
        order_detail.goods_id=goods_id
        order_detail.quantity=data['quantity']
        db.session.add(order_detail)
        
        
        
    except Exception,e:        
        result['msg']=e.message
        
    return Response(json.dumps(result),content_type="application/json")
@order_controller.route('/m1/private/cancle_order',methods=['POST'])
@check_token
def cancle_order(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        order=Order.query.filter_by(order_no,data['order_no']).first()
        
        if order:
            #当订单状态!=3（交易取消）时
            if order.status!='3':
                order.status='3'
        sql='''UPDATE tb_purchase_s s
            INNER JOIN tb_orderdetail_s o ON s.GoodsID=o.GoodsID AND s.BatchNo=o.BatchNo
            SET s.Quantity = s.Quantity + o.Quantity
            WHERE o.OrderNo=%s'''
        db.engine.execute(sql,(data['order_no']))
        
        db.session.commit()
                
    except Exception,e:
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result))
        
    