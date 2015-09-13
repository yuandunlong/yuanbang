# -*- coding: utf-8 -*-
from flask import json,Response,Blueprint,request,json,current_app
from database.models import db
from views.utils import check_token,row_map_converter
shopcenter_controller=Blueprint('shopcenter_controller',__name__)
@shopcenter_controller.route('/m1/private/shopcenter/get_shop_info',methods=['GET'])
@check_token
def get_shop_info(token_type,shop):
    result={'code':1,'msg':'ok'}
    try:
        result['shop_info']=shop.get_map()
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type="application/json")
@shopcenter_controller.route('/m1/private/shopcenter/get_goods_by_page',methods=['POST'])
@check_token
def get_goods_by_page(token_type,shop):
    
    result={'code':1,'msg':'ok'}
    
    try:
        data=request.get_json()
        page=int(data.get('page',1))
        page_size=int(data.get('page_size',20))
        
        order_by=data.get('order_by','summarydesc')
        
        
        
        sql='''
            SELECT
            g.GoodsID,
            g.ShopID,
            g.SortNo,
            IFNULL(p.ThumbnailPath,'./Content/images/web/nowprinting2.jpg') AS ThumbnailPath,
            g.BarCode,
            m.GoodsTypeName,
            g.GoodsName,
            g.GoodsSpec,
            g.GoodsLocality,
            g.GoodsBrand,
            g.SalePrice,
            IFNULL(a.Quantity, 0) AS Quantity,
            g.WarningNum,
            g.Discount,
            t.ItemName AS Status
    FROM
            tb_goodsinfo_s g
    LEFT JOIN tb_goodstype_m m ON g.GoodsTypeID = m.GoodsTypeID
    INNER JOIN tb_photo p ON g.GoodsID = p.LinkID
    AND p.IsVisable = 1
    LEFT JOIN (
            SELECT
                    GoodsID,
                    sum(Quantity) AS Quantity
            FROM
                    tb_purchase_s
            GROUP BY
                    GoodsID
    ) a ON g.GoodsID = a.GoodsID
    LEFT JOIN tb_constent_m t ON t.TypeID=14 AND g.Status=t.ItemID
    WHERE
            g.ShopID =%s 
        '''
        
        if order_by=='saleasc':
            sql+='order by Quantity asc'
        if order_by=='saledesc':
            sql+='order by Quantity desc'
        if order_by=='priceasc':
            sql+='order by SalePrice asc'
        if order_by=='pricedesc':
            sql+='order by SalePrice desc'
        if order_by=='summarydesc':
            sql+='order by Saleprice,Quantity desc'
        if order_by=='summaryasc':
            sql+='order by Saleprice,Quantity asc'
        sql+=' limit %s,%s'
        result_set=db.engine.execute(sql,(shop.shop_id,page-1,page_size))
        arr=[]
        for row in result_set:
            temp=row_map_converter(row)
            arr.append(temp)
            result['goods']=arr
        count_sql='''
        select count(*) as TotalCount from tb_goodsinfo_s g
    LEFT JOIN tb_goodstype_m m ON g.GoodsTypeID = m.GoodsTypeID
    INNER JOIN tb_photo p ON g.GoodsID = p.LinkID
    AND p.IsVisable = 1
    LEFT JOIN (
            SELECT
                    GoodsID,
                    sum(Quantity) AS Quantity
            FROM
                    tb_purchase_s
            GROUP BY
                    GoodsID
    ) a ON g.GoodsID = a.GoodsID
    LEFT JOIN tb_constent_m t ON t.TypeID=14 AND g.Status=t.ItemID
    WHERE
            g.ShopID =%s ORDER BY g.SortNo DESC 
        '''
        row=db.engine.execute(count_sql,(shop.shop_id)).fetchone()
        total_count=0
        if row:
            result['total_count']=int(row['TotalCount'])
        result['page']=page
        result['page_size']=page_size
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        
@shopcenter_controller.route('/m1/private/shopcenter/get_orders_by_page',methods=['POST'])
@check_token
def get_orders_by_page(token_type,shop):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        page=int(data.get('page',1))
        page_size=int(data.get('page_size',20))        
        sql='''
        SELECT
                TOS.OrderNo,
                TOS.ShopID,
                TOS.BuyerID,
                TOS.SaleMoney,
                TOS.SubmitTime,
                TOS.SendTime,
                TOS.ConfirmTime,
                TOS.Freight,
                TOS.AddressID,
                TOS.SendAddress,
                TOS.Receiver,
                TOS.Phone,
                TOS.Remark,
                TOS.Status,
                TCM.ItemName AS StatusName,
                TOS.PayStatus,
                TOS.UpdateTime,
                PCM.ItemName AS PayStatusName
        FROM
                tb_order_s TOS
        LEFT JOIN  tb_constent_m TCM ON TCM.TypeID = '009'
        AND TOS. STATUS = TCM.ItemID
        LEFT JOIN tb_constent_m PCM ON PCm.TypeID = '010'
        AND TOS.PayStatus = PCM.ItemID
        WHERE
                TOS.ShopID = %s  ORDER BY SubmitTime desc limit %s,%s
        '''
        result_set=db.engine.execute(sql,(shop.shop_id,page-1,page_size))
        arr=[]
        for row in result_set:
            temp=row_map_converter(row)
            arr.append(temp)
        result['orders']=arr
        count_Sql='''
        
        select count(*) as TotalCount  FROM
                tb_order_s TOS
        LEFT JOIN  tb_constent_m TCM ON TCM.TypeID = '009'
        AND TOS. STATUS = TCM.ItemID
        LEFT JOIN tb_constent_m PCM ON PCm.TypeID = '010'
        AND TOS.PayStatus = PCM.ItemID
        WHERE
                TOS.ShopID = %s  ORDER BY SubmitTime desc 
        '''
        row=db.engine.execute(count_Sql,(shop.shop_id)).fetchone()
        if row:
            result['total_count']=row['TotalCount']
        result['page']=page
        result['page_size']=page_size
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        
@shopcenter_controller.route('/m1/private/shopcenter/up_goods_by_id',methods=['POST'])    
@check_token
def up_goods_by_id(token_type,shop):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        sql='update tb_goodsinfo_s set Status=1 where GoodsID = %s'
        db.engine.execute(sql,(data['goods_id']))
        db.session.commit()
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
@shopcenter_controller.route('/m1/private/shopcenter/down_goods_by_id',methods=['POST'])    
@check_token
def down_goods_by_id(token_type,shop):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        sql='update tb_goodsinfo_s set Status=0 where GoodsID = %s'
        db.engine.execute(sql,(data['goods_id']))
        db.session.commit()        
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=1
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        
@shopcenter_controller.route('/m1/private/shopcenter/get_msgs_by_page',methods=['POST'])    
@check_token
def get_msgs_by_page(token_type,shop):
    data=request.get_json()
    page=int(data.get('page',1))
    page_size=int(data.get('page_size',20))      
    result={'code':1,'msg':'ok'}
    try:
        sql=''' select
                m.MessageID,
                m.SenderType,
                m.Sender,
                m.SenderName,
                m.SendTitle,
                m.SendTime,
                m.SendContent,
                m.ReplyTime,
                m.ReplyContent,
                c.ItemName as ReadState
                from tb_message_w m
                left join tb_constent_m c on m.IsRead =c.ItemID and c.typeID=015
                where m.ReceiverType=1 and m.Receiver=%s order by m.SendTime desc limit %s,%s
        '''
        result_set=db.engine.execute(sql,(shop.shop_id,page-1,page_size))
        arr=[]
        for row in result_set:
            temp=row_map_converter(row)
            arr.append(temp)
        result['msgs']=arr
        count_sql='''
        select count(*) as total_count from tb_message_w m
 left join tb_constent_m c on m.IsRead =c.ItemID and c.typeID=015
 where m.ReceiverType=1 and m.Receiver=%s order by m.SendTime desc
        '''
        row=db.engine.execute(count_sql,(shop.shop_id)).fetchone()
        if row:
            result['total_count']=row['total_count']
        result['page']=page
        result['page_size']=page_size
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')

@shopcenter_controller.route('/m1/private/shopcenter/update_msg_2_is_read',methods=['POST'])    
@check_token
def update_msg_2_is_read(token_type,shop):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        sql='''
        UPDATE tb_message_w SET IsRead =1 WHERE MessageID =%s
        '''
        db.engine.execute(sql,(data['msg_id']))
        db.session.commit()
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        
@shopcenter_controller.route('/m1/private/shopcenter/get_goods_type_root',methods=['POST','GET'])    
@check_token        
def get_goods_type_root(token_type,shop):
    result={'code':1,'msg':'ok'}
    try:
        sql='''
        SELECT
            tgs.ShopID,
            tgs.GoodsTypeID,
            tgm.GoodsTypeName,
            tgs.ParentID,
            tgs.SortNo
            FROM
                tb_goodstype_s tgs,
                tb_goodstype_m tgm
            WHERE
                tgs.ShopID = %s
            AND tgs.GoodsTypeID = tgm.GoodsTypeID
            AND tgs.ParentID IS NULL
            ORDER BY tgs.SortNo desc
        '''   
        result_set=db.engine.execute(sql,(shop.shop_id))
        arr=[]
        for row in result_set:
            temp={}
            temp['shop_id']=int(row['ShopID'])
            temp['goods_type_id']=int(row['GoodsTypeID'])
            temp['goods_type_name']=row['GoodsTypeName']
            temp['parent_id']=row['ParentID']
            temp['sort_no']=row['SortNo']
            arr.append(temp)
        result['shop_goods_type_root']=arr        
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/get_shop_goods_type_child',methods=['POST'])    
@check_token  
def get_shop_goods_type_child(token_type,shop):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        parent_id=data['parent_id']
        sql='''SELECT
    tgs.ShopID,
    tgs.GoodsTypeID,
    tgm.GoodsTypeName,
    tgs.ParentID,
    tgs.SortNo
    FROM
        tb_goodstype_s tgs, tb_goodstype_m tgm
    WHERE
        tgs.ShopID = %s
        AND tgs.GoodsTypeID = tgm.GoodsTypeID
        AND tgs.ParentID = %s
    ORDER BY tgs.SortNo desc'''

        result_set=db.engine.execute(sql,(shop.shop_id,parent_id))
        arr=[]
        for row in result_set:
            temp={}
            temp['shop_id']=int(row['ShopID'])
            temp['goods_type_id']=int(row['GoodsTypeID'])
            temp['goods_type_name']=row['GoodsTypeName']
            temp['parent_id']=row['ParentID']
            temp['sort_no']=row['SortNo']
            arr.append(temp)  
        result['shop_goods_type_child']=arr        

    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
    
    
def add_goods_type(token_type,shop):
    result={'code':1,'msg':'ok'}
    
    try:
        pass
    except Exception,e:
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        