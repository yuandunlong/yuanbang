# -*- coding: utf-8 -*-
from flask import Blueprint,current_app
from flask import request
from flask import Response,json
from database.models import OrderDetail,db,Order,BuyerAddress,Purchase,Message,ShopCart
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
        current_app.logger.exception(e)
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
        current_app.logger.exception(e)
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
        current_app.logger.exception(e)
        result['code']='0'
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
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')

@order_controller.route('/m1/private/submit_order_by_shopcart',methods=['POST'])
@check_token
def submit_order_by_shopcart(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        buyerAddress=BuyerAddress.query.filter_by(buyer_id=user_info.buyer_id,is_default='1').first()
        if not buyerAddress:
            raise Exception('user dont have default address')
        carGrouptList=getOrderCartList(user_info.buyer_id, buyerAddress.address_id)
        
        for order_info in carGrouptList:
            order=Order()
            order.order_no=build_order_no()
            order.shop_id=order_info['shop_id']
            order.buyer_id=user_info.buyer_id
            order.sale_money=order_info['sum_the_shop']
            order.freight=order_info['freight']
            order.submit_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            order.address_id=buyerAddress.address_id
            order.send_address=buyerAddress.detail_address
            order.receiver=buyerAddress.consignee
            order.phone=buyerAddress.phone
            order.remark=data.get('remark','')
            order.status='0' #已提交
            db.session.add(order)
            goods_list=getGoodsList(order.shop_id,order.buyer_id)
            
            for goods_info in goods_list:
                purchase=Purchase.query.filter_by(goods_id=goods_info['goods_id']).order_by(Purchase.batch_no).first()
                quantity=goods_info['quantity']
                if purchase:
                    purchase_info.quantity-=quantity
                    db.session.commit()
                order_detail=OrderDetail()
                order_detail.order_no=order.order_no
                order_detail.goods_id=goods_info['goods_id']
                if purchase:
                    order_detail.batch_no=purchase.batch_no
                order_detail.sale_price=goods_info['sale_price']
                order_detail.quantity=quantity
                order_detail.discount_price=goods_info['discount_price'] 
                db.session.add(order_detail)
            message=Message()
            message.sender_type='3'
            message.sender_name='系统消息'
            message.receiver_type='1' #商铺
            message.receiver=order_info['shop_id']
            message.receiver_name=order_info['shop_name']
            message.send_title=r'您有一个新订单：'+order.order_no
            message.send_content=r'''您有一个新的订单：<a style='text-decoration:underline' href='index.php/Display/OrderDetailPage?OrderNo=".$OrderNo."'>".$OrderNo."</a><br/><div class='date'>点击订单编号查看详细信息！</div> '''
            message.send_time=datetime.now()
                
            db.session.add(message)
            db.session.commit()
            
        #删除购物车
        delete_cart_sql='''
        delete from tb_shoppingcart where BuyerID=%s and IsSelected=1
        '''
        db.engine.execute(delete_cart_sql,(user_info.buyer_id))
        db.session.commit()
        
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
    
#下单前的界面get_preview_orders_by_shopcart
@order_controller.route('/m1/private/get_preview_orders_by_shopcart',methods=['POST'])
@check_token
def get_preview_orders_by_shopcart(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        buyer_address=BuyerAddress.query.filter_by(buyer_id=user_info.buyer_id,is_default='1').first()
        if not buyer_address:
            raise Exception('user dont have default address')
        xzb=buyer_address.xzb
        yzb=buyer_address.yzb
        is_selected=data.get('is_selected',None)
        
        sql='''
        SELECT
        a.* ,
        c.ShopID,
        c.ShopName,
        b.GoodsName,
        b.SalePrice,
        b.Discount,
        b.SetNum,
        b.SetPrice,
        c.FarthestDistance/1000 as FarthestDistance,
        c.FreeDistance,
        c.Freight as FreightPerKilometre,
        
        d.PhotoPath,
        d.ThumbnailPath,
        d.PhotoID,
        d.PhotoName,
        '''
        
        if xzb and yzb:
            sql+='''ROUND(SQRT(POW(%s - c.mktxzb, 2) + POW(%s- c.mktyzb, 2))/1000,2) AS Distance,'''
            sql+='''
            
                IF (
                    ROUND(
                        SQRT(
                            POW(%s - c.mktxzb, 2) + POW(%s - c.mktyzb, 2)
                            ),
                        2
                        ) > c.FreeDistance,
                    CEIL(
                        ROUND(
                            SQRT(
                                POW(%s - c.mktxzb, 2) + POW(%s - c.mktyzb, 2)
                                ),
                            2
                            ) - FreeDistance
                        ) /1000* Freight,
                    0
                    ) AS TotalFreight,sum(
                
                    IF (
                        a.Quantity >= b.SetNum,
                        round(b.SetPrice * a.Quantity, 2),
                        round(
                            round(b.SalePrice * b.Discount, 2) * a.Quantity,
                            2
                        )
                    )
                    )AS Money
                    FROM
                        tb_shoppingcart a
                    LEFT JOIN tb_goodsinfo_s b ON a.GoodsID = b.GoodsID
                    LEFT JOIN tb_shopinfo_s c ON b.ShopID = c.ShopID
                    LEFT JOIN tb_photo d ON b.GoodsID = d.LinkID
                    WHERE
                        a.BuyerID = %s
            '''
        if is_selected=='1' or is_selected==1:
            sql+='and a.IsSelected=1'
        sql+='''
                    GROUP BY
                    c.ShopID,
                    c.ShopName
                    ORDER BY
                        c.ShopID
            '''
        if xzb and yzb:
            result_set=db.engine.execute(sql,(xzb,yzb,xzb,yzb,xzb,yzb,user_info.buyer_id))
        else:
            result_set=db.engine.execute(sql,(user_info.buyer_id))
        arr=[]
        for row in result_set:
            temp=row_map_converter(row)
            arr.append(temp)
        orders=[]
        for item in arr:
            if item['shop_id']==None or item['shop_id']=='None':
                continue  
            temp_shop={
                'shop_id':item['shop_id'],
                'shop_name':item['shop_name'],
                'free_distance':item['free_distance'],
                'freight':item['freight_per_kilometre']
        
            }
        
            count=0            
            for order in orders:
                count=count+1
                if order['shop_id']==item['shop_id']:
                    order['goods'].append(item)
                    break
            if count==len(orders):
                temp_arr=[]
                temp_arr.append(item)
                temp_shop['goods']=temp_arr
                orders.append(temp_shop)            
        result['orders']=orders
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
        
    return Response(json.dumps(result),content_type='application/json')
        
        
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
        AND a.IsSelected = 1 '''
    result_set=db.engine.execute(sql,(shop_id,user_id))
    arr=[]
    for row in result_set:
        row_map=row_map_converter(row)
        arr.append(row_map)
    return arr
