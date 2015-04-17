# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request
from flask import Response,json
from database.models import OrderDetail,db,Order,BuyerAddress
from utils import check_token,build_order_no,DecimalEncoder,row_map_converter,sub_map,result_set_converter
from datetime import datetime
order_controller=Blueprint('order_controller',__name__)

def get_order_listss(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        sql='''
        select a.OrderNo,a.ShopID,a.BuyerID,a.SaleMoney,a.SubmitTime,a.SendTime,a.ConfirmTime,a.Freight,a.AddressID,a.SendAddress,a.Receiver,a.Phone,a.Remark,a.Status,a.PayStatus,a.UpdateTime
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
        orders=[]
        for row in result_set:
            temp=row_map_converter(row)
            order=sub_map(temp,['order_no','shop_id','shop_name','buyer_id','sale_money','submit_time','send_time','confirm_time',\
                                'freight','send_address','receiver','phone','remark','status','update_time'])
           
            goods=sub_map(temp,['goods_id','batch_no','sale_price','quantity','discount_price','goods_name',\
                                'photo_id','photo_path','thumbnail_path','sort_no'])
            order['goods']=goods
            orders.append(order)
        result['orders']=orders
    except Exception,e:
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')

@order_controller.route('/m1/private/get_order_list',methods=['GET'])
@check_token
def get_order_list(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        sql='''
        select a.OrderNo,a.ShopID,a.BuyerID,a.SaleMoney,a.SubmitTime,a.SendTime,a.ConfirmTime,a.Freight,a.AddressID,a.SendAddress,a.Receiver,a.Phone,a.Remark,a.Status,a.PayStatus,a.UpdateTime,
        c.ShopName
        from tb_order_s a 
        left join tb_shopinfo_s c on a.ShopID=c.ShopID 
        where BuyerID=%s
        '''
        sql_detail='''

        select a.* ,b.GoodsName,
        c.PhotoID ,c.PhotoName,c.PhotoPath,c.ThumbnailPath,c.SortNo
        from tb_orderdetail_s a
        left join tb_goodsinfo_s b on b.GoodsID=a.GoodsID
        left join tb_photo c on c.LinkID=a.GoodsID and c.IsChecked=1 and c.IsVisable=1
        where OrderNo=%s
        '''
        print sql
        result_set=db.engine.execute(sql,(user_info.buyer_id))
        orders=[]
        for row in result_set:
            order_map=row_map_converter(row)
            order_detail_result_set=db.engine.execute(sql_detail,(order_map['order_no']))
            order_detail_arr=[]
            for item in order_detail_result_set:
                order_detail_arr.append(row_map_converter(item))
            order_map['goods']=order_detail_arr
            orders.append(order_map)
        result['orders']=orders
    except Exception, e:
        result['code']=0
        result['msg']=e.message
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
        freight=query['freight']
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

@order_controller.route('/m1/private/create_order_by_shopcart')
@check_token
def create_order_by_shopcart(token_type,user_info):
    try:
        result={'code':1,'msg':'ok'}
        data=request.get_json()
        address_id=data['address_id']
        buyerAddress=BuyerAddress.query.filter_by(address_id=address_id).first()
        carGrouptList=getOrderCartList(user_info.buyer_id, address_id)
        for ordr_info in carGrouptList:
            order=Order()
            order.order_no=build_order_no()
            order.shop_id=order_info['shop_id']
            order.buyer_id=user_info.buyer_id
            order.sale_money=order_info['sum_the_shop']
            order.freight=order_info['freight']
            order.submit_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            order.address_id=address_id
            order.send_address=buyerAddress.detail_address
            order.receiver=buyerAddress.consignee
            order.phone=buyerAddress.phone
            order.remark=data.get('remark','')
            db.session.add(order)
            #goods_list=
            
        
    except Exception,e:
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result))
    
        
def getOrderCartList(user_id,address_id):
    sql='''
    
        SELECT
            a.BuyerID,
            b.ShopID,
            d.ShopName,
            d.HasAlipay,
            d.HasOnlineBank,
                SUM(
        
                    IF (
                        a.Quantity >= b.SetNum,
                        round(b.SetPrice * a.Quantity, 2),
                        round(
                            round(b.SalePrice * b.Discount, 2) * a.Quantity,
                            2
                        )
                    )
                    ) AS sumTheShop,
        
            IF (
                ROUND(
                    SQRT(
                        POW(s.mktxzb - d.mktxzb, 2) + POW(s.mktyzb - d.mktyzb, 2)
                    )
                    ) > FreeDistance,
                ROUND(
                    SQRT(
                        POW(s.mktxzb - d.mktxzb, 2) + POW(s.mktyzb - d.mktyzb, 2)
                    ) 
                    ) - d.FreeDistance,
                0
                ) /1000* d.Freight AS Freight
            FROM
                tb_shoppingcart a
            LEFT JOIN tb_goodsinfo_s b ON a.GoodsID = b.GoodsID
            LEFT JOIN tb_shopinfo_s d ON d.ShopID = b.ShopID
            LEFT JOIN tb_buyeraddress s ON s.BuyerID = a.BuyerID
            AND s.AddressID = %s
            WHERE
                a.BuyerID = %s
            AND a.IsSelected = 1
            GROUP BY
                b.ShopID,
                a.BuyerID    
    '''
    result_set=db.engine.execute(sql,(address_id,user_id))
    
    arr=[]
    for row in result_set:
        row_map=row_map_converter(row)
        arr.append(row_map)
    return arr
    
def getGoodsList(shop_id,user_id):
    sql='''SELECT
    a.GoodsID,
    a.Quantity,
        b.SalePrice,
        b.SetNum,
        b.SetPrice,
        b.SalePrice,

    IF(
        a.Quantity >= b.SetNum,
        b.SetPrice,
        round(b.SalePrice * b.Discount, 2) 
        )AS DiscountPrice

    FROM
        tb_shoppingcart a
    INNER JOIN tb_goodsinfo_s b ON a.GoodsID = b.GoodsID
    INNER JOIN tb_shopinfo_s c ON c.ShopID = b.ShopID
    WHERE
        c.ShopID = %s
    AND a.BuyerID = %s
        AND a.Isselected = '1'''
    result_set=db.engine.execute(sql,(shop_id,user_id))
    arr=[]
    for row in result_set:
        row_map=row_map_converter(row)
        arr.append(row_map)
    return arr
