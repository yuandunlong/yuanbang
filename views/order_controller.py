# -*- coding: utf-8 -*-
from flask import Blueprint,current_app
from flask import request,copy_current_request_context
from flask import Response,json
from database.models import OrderDetail,db,Order,BuyerAddress,Purchase,Message,ShopCart,ShopInfo,Comment,Coupon
from utils import check_token,build_order_no,DecimalEncoder,row_map_converter,sub_map,result_set_converter,send_mail,rows_array_converter
from datetime import datetime
import string
import base64

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
        select a.OrderNo,a.ShopID,a.BuyerID,a.SaleMoney,a.SubmitTime,a.SendTime,a.ConfirmTime,a.Freight,a.AddressID,a.SendAddress,a.Receiver,a.Phone,a.Remark,a.Status,a.PayStatus,a.UpdateTime,a.PayType,
        c.ShopName
        from tb_order_s a 
        left join tb_shopinfo_s c on a.ShopID=c.ShopID 
        where BuyerID=%s order by a.SubmitTime desc
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

            sqlc='''select count(*) as count from tb_comment where CommentType=1 and OrderNo=%s'''

            #temp= db.engine.execute(sqlc,(order_map['order_no'])).fetchone()
            c=Comment.query.filter_by(comment_type='1',order_no=order_map['order_no']).first()
            if c:
                order_map['isAppraise']=1
            else:
                order_map['isAppraise']=0
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

@order_controller.route('/m1/private/delete_order',methods=['POST'])
@check_token
def delete_order(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        sql='''delete from tb_order_s where OrderNo=%s'''
        detail_sql='''delete from tb_orderdetail_s where OrderNo=%s'''
        db.engine.execute(sql,(data['order_no']))
        db.engine.execute(detail_sql,(data['order_no']))
        db.session.commit()
        
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        
        

@order_controller.route('/m1/private/cancle_order',methods=['POST'])
@check_token
def cancle_order(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        cancel_reason=data.get('cancel_reason','')
        # order=Order.query.filter_by(order_no=data['order_no']).first()
        #
        # if order:
        #     #当订单状态!=3（交易取消）时
        #     if order.status!='3':
        #         order.status='3'
        #         order.cancel_reason=cancel_reason

        sql1='''update tb_order_s set Status=3,CancelReason =%s where OrderNo=%s'''
        db.engine.execute(sql1,(cancel_reason,data['order_no']))
        db.session.commit()
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
        pay_type=data.get('pay_type',0)#0货到付款 1在线支付
        use_coupons=data.get('use_coupons',None)
        get_coupons=data.get('get_coupons',None)
        buyerAddress=BuyerAddress.query.filter_by(buyer_id=user_info.buyer_id,is_default='1').first()

        rv=[]
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
            order.pay_type=pay_type
            get_coupon_money=0
            if use_coupons:
                for use_coupon in use_coupons:
                    if int(use_coupon['shop_id'])==int(order.shop_id):
                        sql='''insert into tb_coupon (CouponType,ShopID,BuyerID,OrderNO,CouponMoney) values(%s,%s,%s,%s,%s)'''
                        db.engine.execute(sql,('1',order.shop_id,user_info.buyer_id,order.order_no,use_coupon['coupon_money']))
                        order.use_coupon=use_coupon['coupon_money']
            if get_coupons:
                for get_coupon in get_coupons:
                    if int(get_coupon['shop_id']==int(order.shop_id)):
                        get_coupon_money=get_coupon['coupon_money']
            order.get_coupon=get_coupon_money
            if not order.use_coupon:
                order.use_coupon=0
            order.sale_money=float(order.sale_money)-float(order.use_coupon)

            db.session.add(order)
            goods_list=getGoodsList(order.shop_id,order.buyer_id)
            
            for goods_info in goods_list:
                purchase=Purchase.query.filter_by(goods_id=goods_info['goods_id']).order_by(Purchase.batch_no).first()
                quantity=goods_info['quantity']
                if purchase:
                    purchase.quantity-=quantity
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
            r_map={}
            r_map['order_no']=order.order_no
            r_map['shop_id']=order.shop_id
            r_map['sale_money']=str(order.sale_money)
            r_map['use_coupon']=str(order.use_coupon)
            r_map['get_coupon']=str(order.get_coupon)
            r_map['freight']=str(order.freight)
            r_map['has_alipay']=order_info['has_alipay']
            r_map['has_online_bank']=order_info['has_online_bank']
            rv.append(r_map)

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
            send_email_2_shop(order.shop_id, order.order_no)
        #删除购物车
        delete_cart_sql='''
        delete from tb_shoppingcart where BuyerID=%s and IsSelected='1'
        '''
        db.engine.execute(delete_cart_sql,(user_info.buyer_id))
        db.session.commit()
        result['orders']=rv
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')


@order_controller.route('/m1/private/complete_order',methods=['POST'])
@check_token
def complete_order(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        data=request.json
        order_no=data['order_no']
        sql='''update tb_order_s set Status=2 where OrderNo=%s'''
        db.engine.execute(sql,(order_no))
        db.session.commit()
        order=Order.query.filter_by(order_no=order_no).first()

        get_coupon=order.get_coupon

        if get_coupon>0:
            coupon=Coupon()
            coupon.buyer_id=order.buyer_id
            coupon.order_no=order_no
            coupon.coupon_money=get_coupon
            coupon.coupon_type='0'
            coupon.remark=''
            coupon.shop_id=order.shop_id
            db.session.add(coupon)
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
        xzb=None
        yzb=None
        mktxzb=None
        mktyzb=None        
        if  buyer_address:
            xzb=buyer_address.xzb
            yzb=buyer_address.yzb
            mktxzb=buyer_address.mktxzb
            mktyzb=buyer_address.mktyzb
        is_selected=data.get('is_selected',None)
        
        shop_list=GetShopListFromCart(mktxzb, mktyzb, user_info, is_selected)
        temp=[]
        for shop in shop_list:

            if not str(shop['shop_id']).isdigit():
                continue

            temp.append(shop)

            ##判断用户是否是第一次下单
            orders= Order.query.filter_by(buyer_id=user_info.buyer_id,shop_id=shop['shop_id']).first()
            if orders:
                shop['first_order']=False
            else:
                shop['first_order']=True

            #获取已经有的商铺优惠券
            sql='''
            SELECT
						IFNULL(
							sum(
								CASE
								WHEN CouponType = '0' THEN
									CouponMoney
								ELSE
									-CouponMoney
								END
							),
							0
						) AS CouponMoney
					FROM
						tb_coupon
					WHERE
						ShopID = %s
					AND BuyerID =%s'''
            shopCoupons = db.engine.execute(sql,(shop['shop_id'], user_info.buyer_id))
            shop['shopCoupons']=rows_array_converter(shopCoupons)
            goods=GetGoodsListFromCart(shop['shop_id'], user_info.buyer_id, is_selected)
            shop['goods']=goods
        result['orders']=temp
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
        
    return Response(json.dumps(result),content_type='application/json')


@order_controller.route('/m1/private/get_orders_count',methods=['GET'])
@check_token
def get_orders_count(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        sql="select count(OrderNo) as count,status from tb_order_s where BuyerID='%s' group by status";
        rows= db.engine.execute(sql,(user_info.buyer_id))
        result['orders_counts']=rows_array_converter(rows)
    except Exception,e:
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')


        
@order_controller.route('/m1/private/buy_again_by_order_no',methods=['POST'])
@check_token
def buy_again_by_order_no(token_type,user_info):
    
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        order_no=data['order_no']
        
        order_details=OrderDetail.query.filter_by(order_no=order_no).all()
        if order_details:
            db.engine.execute('update tb_shoppingcart set IsSelected=0 where BuyerID=%s',(user_info.buyer_id))
        for order_detail in order_details:
            shop_cart=ShopCart.query.filter_by(buyer_id=user_info.buyer_id,goods_id=order_detail.goods_id).first()
            if shop_cart:
                db.engine.execute("update tb_shoppingcart set IsSelected=1 where BuyerID=%s and  GoodsID= %s",(user_info.buyer_id,order_detail.goods_id))
                db.session.commit()
            else:
                shop_cart=ShopCart()
                shop_cart.buyer_id=user_info.buyer_id
                shop_cart.quantity=order_detail.quantity
                shop_cart.goods_id=order_detail.goods_id
                shop_cart.is_selected='1'
                shop_cart.create_time=datetime.now()
                db.session.add(shop_cart)
                db.session.commit()
        db.session.commit()
        result=get_preview_orders_by_shopcart_for_buyer_again(token_type, user_info)
        
    except Exception,e:
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        
      
def getOrderCartList(user_id,address_id):
    sql='''
       SELECT tmp.BuyerID,tmp.ShopID,tmp.ShopName,tmp.HasAlipay,tmp.HasOnlineBank,tmp.sumTheShop,
    IF (
        tmp.Distance > tmp.FreeDistance,
        CEIL(
            tmp.Distance - tmp.FreeDistance
            ) * tmp.Freight +
        IF (
            tmp.sumTheShop < tmp.ExtraOrderAmount,
            tmp.ExtraFreight,
            0
            ),
        0 + IF ( tmp.sumTheShop < tmp.ExtraOrderAmount, tmp.ExtraFreight, 0 )
        ) AS Freight
    FROM (SELECT a.BuyerID,c.ShopID,
        c.ShopName,
        c.HasAlipay,
        c.HasOnlineBank,
        c.OrderAmount,
        c.FreeDistance / 1000 AS FreeDistance,
        c.Freight,
        c.FarthestDistance / 1000 AS FarthestDistance,
        ROUND(
            SQRT(
                POW(s.mktxzb - c.mktxzb, 2) + POW(s.mktyzb - c.mktyzb, 2)
                ) / 1000,
            2
            ) AS Distance,
        c.ExtraOrderAmount,
        c.ExtraFreight,
        SUM(
            IF (
                a.Quantity >= b.SetNum,
                round(b.SetPrice * a.Quantity, 2),
                round(
                    round(b.SalePrice * b.Discount, 2) * a.Quantity,
                    2
                )
            )
            ) AS sumTheShop

        FROM
        tb_shoppingcart a
        LEFT JOIN tb_goodsinfo_s b ON a.GoodsID = b.GoodsID
        LEFT JOIN tb_shopinfo_s c ON b.ShopID = c.ShopID
        LEFT JOIN tb_buyeraddress s ON s.BuyerID = a.BuyerID
        AND s.AddressID = %s
        WHERE
        a.BuyerID = %s
        AND a.IsSelected = '1'
        GROUP BY
        a.BuyerID,
        c.ShopID,
        c.ShopName,
        c.HasAlipay,
        c.HasOnlineBank,
        c.OrderAmount,
        FreeDistance,
        c.Freight,
        FarthestDistance,
        Distance,
        c.ExtraOrderAmount,
        c.ExtraFreight ) tmp
    '''
    result_set=db.engine.execute(sql,(address_id,user_id))
    
    arr=[]
    for row in result_set:
        row_map=row_map_converter(row)
        arr.append(row_map)
    return arr

def GetShopListFromCart(mktxzb,mktyzb,user_info,is_selected):
    arr=[]
    try:
        if mktxzb and mktyzb:
            sql='''

            SELECT
						tmp.ShopID,
						tmp.ShopName,
						tmp.OrderAmount,
						tmp.FreeDistance,
						tmp.FarthestDistance,
						tmp.Distance,
        				tmp.Freight as BaseFreight,
						tmp.ExtraOrderAmount,
						tmp.ExtraFreight,
						tmp.Money,
        				tmp.CouponMoney,
        				IFNULL(tmp.OrderCount,0) as OrderCount,
        				tmp.FirstGiveCoupon,
        				tmp.GiveLimit,
        				tmp.GiveCoupon,
        				tmp.UseLimit,
        				tmp.CanUseCoupon,
						IF (
							tmp.Distance > tmp.FreeDistance,
							CEIL(
								tmp.Distance - tmp.FreeDistance
							) * tmp.Freight + IF(tmp.Money < tmp.ExtraOrderAmount,tmp.ExtraFreight,0),
							0 + IF(tmp.Money < tmp.ExtraOrderAmount,tmp.ExtraFreight,0)
						) AS Freight
				FROM (
					SELECT
						c.ShopID,
						c.ShopName,
						c.OrderAmount,
						c.FreeDistance / 1000 AS FreeDistance,
						c.Freight,
						c.FarthestDistance / 1000 AS FarthestDistance,
						ROUND(
							SQRT(
								POW(%s - c.mktxzb, 2) + POW(%s - c.mktyzb, 2)
							) / 1000,
							2
						) AS Distance,
						c.ExtraOrderAmount,
						c.ExtraFreight,
						sum(
							IF (
								a.Quantity >= b.SetNum,
								round(b.SetPrice * a.Quantity, 2),
								round(
									round(b.SalePrice * b.Discount, 2) * a.Quantity,
									2
								)
							)
						) AS Money,
        				sum(
        					case when b.CanGetCoupon = 1 then
							IF (
								a.Quantity >= b.SetNum,
								round(b.SetPrice * a.Quantity, 2),
								round(
									round(b.SalePrice * b.Discount, 2) * a.Quantity,
									2
								)
							)
        					else 0 end
						) AS CouponMoney,
        				d.OrderCount,
        				c.FirstGiveCoupon,
        				c.GiveLimit,
        				c.GiveCoupon,
        				c.UseLimit,
        				c.CanUseCoupon
					FROM
						tb_shoppingcart a
					LEFT JOIN tb_goodsinfo_s b ON a.GoodsID = b.GoodsID
					LEFT JOIN tb_shopinfo_s c ON b.ShopID = c.ShopID
        			LEFT JOIN (select count(1) as OrderCount,ShopID,BuyerID from tb_order_s group by ShopID,BuyerID) d
        			on d.ShopID = c.ShopID and d.BuyerID = a.BuyerID
					WHERE
						a.BuyerID = %s
            '''

            if int(is_selected)==1:
        			sql=sql+" and a.IsSelected=1 "
            sql=sql+'''GROUP BY
						c.ShopID,
						c.ShopName,
						c.OrderAmount,
						FreeDistance,
						c.Freight,
						FarthestDistance,
						Distance,
						c.ExtraOrderAmount,
						c.ExtraFreight) tmp'''
            result_set=db.engine.execute(sql,(mktxzb,mktyzb,user_info.buyer_id))

            arr=rows_array_converter(result_set)
        else:
            sql='''
            SELECT
						c.ShopID,
						c.ShopName,
						c.OrderAmount,
						c.FreeDistance / 1000 AS FreeDistance,
						c.Freight,
						c.FarthestDistance / 1000 AS FarthestDistance,
						c.ExtraOrderAmount,
						c.ExtraFreight,
						sum(
							IF (
								a.Quantity >= b.SetNum,
								round(b.SetPrice * a.Quantity, 2),
								round(
									round(b.SalePrice * b.Discount, 2) * a.Quantity,
									2
								)
							)
						) AS Money,
        				c.FirstGiveCoupon,
        				c.GiveLimit,
        				c.GiveCoupon,
        				c.UseLimit,
        				c.CanUseCoupon,
        				0 as CouponMoney
					FROM
						tb_shoppingcart a
					LEFT JOIN tb_goodsinfo_s b ON a.GoodsID = b.GoodsID
					LEFT JOIN tb_shopinfo_s c ON b.ShopID = c.ShopID
					WHERE
						a.BuyerID = %s'''

            if int(is_selected)==1:
	        	sql=sql+" and a.IsSelected=1 "
            else:
			    sql=sql+'''	GROUP BY
						c.ShopID,
						c.ShopName,
						c.OrderAmount,
						FreeDistance,
						c.Freight,
						FarthestDistance,
						c.ExtraOrderAmount,
						c.ExtraFreight'''
            result_set=db.engine.execute(sql,(user_info.buyer_id))
            arr=rows_array_converter(result_set)
            print "==============================="
            current_app.logger.info("==================")
        for row in arr:

                if int(row['use_limit'])==0:
                    row['coupon_money']='0.00'
                else:
                    row['coupon_money']=int(float(row['money'])/float(row['use_limit']))*float(row['can_use_coupon'])
                    row['coupon_money']=str(row['coupon_money'])
    except Exception,e:
        current_app.logger.exception(e)
    return arr
   
   
def GetGoodsListFromCart(shop_id,buyer_id,is_selected):
    arr=[]
    try:
        sql='''
        SELECT
                	a.GoodsID,
                	c.PhotoPath,
                        c.ThumbnailPath,
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
                	IFNULL(d.Quantity, 0) AS SumQuantity
                FROM
                	tb_shoppingcart a
                INNER JOIN tb_goodsinfo_s b ON a.GoodsID = b.GoodsID
                AND b.ShopID = %s
                INNER JOIN tb_photo c ON b.GoodsID = c.LinkID
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
        
        '''
        
        if is_selected==1 or is_selected=='1':
            sql+='and a.IsSelected=1'
        sql+=' ORDER BY a.CreateTime desc'
        
        result_set=db.engine.execute(sql,(shop_id,buyer_id))
        for row in result_set:
            arr.append(row_map_converter(row))
    except Exception,e:
        current_app.logger.exception(e)
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



def get_preview_orders_by_shopcart_for_buyer_again(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        
        buyer_address=BuyerAddress.query.filter_by(buyer_id=user_info.buyer_id,is_default='1').first()
        xzb=None
        yzb=None
        mktxzb=None
        mktyzb=None        
        if  buyer_address:
            xzb=buyer_address.xzb
            yzb=buyer_address.yzb
            mktxzb=buyer_address.mktxzb
            mktyzb=buyer_address.mktyzb
        is_selected='1'
        
        shop_list=GetShopListFromCart(mktxzb, mktyzb, user_info, is_selected)
        temp=[]
        for shop in shop_list:
            # goods=GetGoodsListFromCart(shop['shop_id'], user_info.buyer_id, is_selected)
            # shop['goods']=goods
            if not str(shop['shop_id']).isdigit():
                continue

            temp.append(shop)

            ##判断用户是否是第一次下单
            orders= Order.query.filter_by(buyer_id=user_info.buyer_id,shop_id=shop['shop_id']).first()
            if orders:
                shop['first_order']=False
            else:
                shop['first_order']=True

            #获取已经有的商铺优惠券
            sql='''
            SELECT
						IFNULL(
							sum(
								CASE
								WHEN CouponType = '0' THEN
									CouponMoney
								ELSE
									-CouponMoney
								END
							),
							0
						) AS CouponMoney
					FROM
						tb_coupon
					WHERE
						ShopID = %s
					AND BuyerID =%s'''
            shopCoupons = db.engine.execute(sql,(shop['shop_id'], user_info.buyer_id))
            shop['shopCoupons']=rows_array_converter(shopCoupons)
            goods=GetGoodsListFromCart(shop['shop_id'], user_info.buyer_id, is_selected)
            shop['goods']=goods
        result['orders']=temp
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return result

@order_controller.route('/m1/email',methods=['GET'])
def test_email():
    #thr = Thread(target=send_email_2_shop, args=[current_app, 21,'2015052097995551'])
   # thr.start()    
    send_email_2_shop(21, '2015052097995551')
    return Response('ok')

def send_email_2_shop(shop_id,order_no):
    try:
	order_sql='''
        
        
        SELECT
                o.OrderNo,
                o.SubmitTime,
                o.SendTime,
                o.ConfirmTime,
                o.Freight,
                o.Receiver,
                o.SendAddress,
                o.Phone,
                o.Remark,
                (o.SaleMoney + o.Freight) AS SaleMoney,
                o.ShopID,
                b.Account,
                b.NickName,
                s.ShopName,
                s.ShopPhone,
                s.LinkMan,
                s.Mobile,
                s.ShopAddress,
                s.Email,
                c.ItemName AS Status
        FROM
                tb_order_s o
        LEFT JOIN tb_shopinfo_s s on o.ShopID = s.ShopID
        LEFT JOIN TB_BUYER b on b.BuyerID = o.BuyerID
        LEFT JOIN TB_CONSTENT_M c on c.TypeID = '009' and o.Status = c.ItemID
        WHERE
                o.OrderNo = %s	
        '''
	order_row=db.engine.execute(order_sql,order_no).fetchone()
	order=row_map_converter(order_row)
	
	    
	detail_sql='''
        SELECT
                    o.OrderNo,
                    o.SalePrice,
                    o.DiscountPrice,
                    SUM(o.Quantity) AS Quantity,
                    o.GoodsID,
                    g.GoodsName,
                    g.ShopID,
                    p.ThumbnailPath AS PhotoPath
            FROM
                    TB_GOODSINFO_S g,
                    TB_ORDERDETAIL_S o
    
            INNER JOIN TB_PHOTO p ON p.LinkID = o.GoodsID
            AND p.IsVisable = 1 AND p.IsChecked = 1
            WHERE
                    o.OrderNo = %s
            AND o.GoodsID = g.GoodsID
            GROUP BY
                    o.OrderNo,
                    o.SalePrice,
                    o.DiscountPrice,
                    o.GoodsID,
                    g.GoodsName,
                    PhotoPath '''
	order_details= db.engine.execute(detail_sql,order_no)
	arr=[]
	for row in order_details:
	    arr.append(row_map_converter(row))
	
	order['order_detail']=arr
	
	temp_template=string.Template(''' 尊敬的${shop_name}店主：<br />&nbsp;&nbsp;&nbsp;&nbsp;您的店铺有新的订单，订单编号为:${order_no}
        
        <table width='100%' border='1' cellspacing='0' cellpadding='5' style='margin-bottom:5px;' bgcolor='#FFFFFF'>
                                    <tbody>
                                       <tr>
                                                <td width='80' class='biaoti' >收货人：
                                                        ${reciever}
                                                </td>
                                                <td width='80' class='biaoti' >联系电话：
                                                        ${phone}
                                                </td>
                                                <td width='80' class='biaoti' >配送地址：
                                                        ${send_address}
                                                </td>
                                        </tr>
                                    </tbody>
                                </table>
                                        <table width='100%' border='1' cellspacing='0' cellpadding='5' class='ordergl ordersearch'>
                                    <tbody>
                                         <tr>
                                            <td width='280' class='biaoti' align='center' colspan='2'>商品</td>
                                            <td width='70' class='biaoti'>单价(元)</td>
                                            <td width='50' height='26' class='biaoti'>数量</td>
                                            <td width='120' class='biaoti'>合计(元)</td>
                                        </tr>
        ''')
	
	mail_body=temp_template.substitute(shop_name=order['shop_name'],order_no=order['order_no'],reciever=order['receiver'],phone=order['phone'],send_address=order['send_address'])
	
	temp_template=''
	i=0
	for order_detail in order['order_detail']:
	    
	    temp_template=string.Template('''<tr>
	                        <td width='80' class='orderpic hang'><a href='${base_url}/Display/ShopGoodsInfoPage?ShopID=${shop_id}&GoodsID=${goods_id}'><img src='${base_url}/${photo_path}' width='80px' height='80px' /></a></td>
	                            <td width='200' class='hang' style='text-align: left'><a href='${base_url}/Display/ShopGoodsInfoPage?ShopID=${shop_id}&GoodsID=${goods_id}'>${goods_name}</a></td>
	                            <td width='70' class='hang'><s>${sale_price}</s><br/>${discount_price}</td>
	                            <td width='50' class='hang'>${quantity}</td>" ''')
	    mail_body+=temp_template.substitute(base_url='http://www.yuanbangshop.com',shop_id=order['shop_id'],goods_id=order_detail['goods_id'],photo_path=order_detail['photo_path'],goods_name=order_detail['goods_name'],sale_price=order_detail['sale_price'],discount_price=order_detail['discount_price'],quantity=order_detail['quantity'])
	    
	    if i==0:
		temp_template=string.Template(''' <td width='120' class='rowspan' rowspan='${count}'>${sale_money}<br/>(含运费：${freight})</td>''')
		mail_body+=temp_template.substitute(count=len(order['order_detail']),sale_money=order['sale_money'],freight=order['freight'])
	    
		
	    i=i+1
	    mail_body+='</tr>'
	
	mail_body+='''</tbody>
                            </table><table width='100%' border='1' cellspacing='0' cellpadding='5' style='margin-bottom:5px;' bgcolor='#FFFFFF'><tbody>
                                       <tr><td width='80' class='biaoti' >备注:'''
	if order['remark']:
	    
	    mail_body+=order['remark']
	else:
	    mail_body+="无"
	param=base64.encodestring(order['email']+order['shop_name'])
	temp_template=string.Template('''</td></tr></tbody></table>
                                请点击下列链接进行操作。<a href='${base_url}/ShopCenterManage/OrderListPage?p=${param}'>${base_url}/ShopCenterManage/OrderListPage?p=${param}</a>
                                <br>(如果上面不是链接形式，请将地址手工粘贴到浏览器地址栏再访问)<br><br>此邮件为系统邮件，请勿直接回复''')
	mail_body+=temp_template.substitute(base_url='http://www.yuanbangshop.com',param=param)
	
	send_mail([order['email']], '[远邦邻里网] 订单提醒邮件', mail_body)
	
	
    except Exception,e:
	current_app.logger.exception(e)
   
    
    