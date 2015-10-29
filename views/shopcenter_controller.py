# -*- coding: utf-8 -*-
from flask import json,Response,Blueprint,request,json,current_app
from database.models import db,GoodsInfo,Photo,DeliveryMan
from datetime import datetime
from views.utils import check_token,row_map_converter,rows_array_converter
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
        result_set=db.engine.execute(sql,(shop.shop_id,(page-1)*page_size,page_size))
        arr=[]
        sql_detail='''
        
                select a.* ,b.GoodsName,
                c.PhotoID ,c.PhotoName,c.PhotoPath,c.ThumbnailPath,c.SortNo
                from tb_orderdetail_s a
                left join tb_goodsinfo_s b on b.GoodsID=a.GoodsID
                left join tb_photo c on c.LinkID=a.GoodsID and c.IsChecked=1 and c.IsVisable=1
                where OrderNo=%s
                '''        
        for row in result_set:
            temp=row_map_converter(row)
            order_detail_result_set=db.engine.execute(sql_detail,(temp['order_no']))
            order_detail_arr=[]
            for item in order_detail_result_set:
                order_detail_arr.append(row_map_converter(item))
                temp['goods']=order_detail_arr            
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
    
    
@shopcenter_controller.route("/m1/private/shopcenter/upload_goods_photo",methods=['POST'])
def upload_goods_photo(token_type,shop):
    result={'code':1,'msg':'ok'}
    try:
        if request.method == 'POST':
            file = request.files['file']
            extension = os.path.splitext(file.filename)[1]
            f_name = str(uuid.uuid4()) + extension
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
            
        
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        
    
        
@shopcenter_controller.route("/m1/private/shopcenter/add_goods_info",methods=['POST'])
@check_token
def add_goods_info(token_type,shop):
    result={'code':1,'msg':'ok'}
    
    try:
        data=request.get_json()
        bar_code=data['bar_code']
        goods_type_id=data['goods_type_id']
        goods_type_ids=data['goods_type_ids']
        goods_name=data['goods_name']
        sale_price=data['sale_price']
        photos=data['photos']
        goods_info=GoodsInfo()
        goods_info.bar_code=bar_code
        goods_info.goods_type_id=goods_type_id
        goods_info.goods_type_ids=goods_type_ids
        goods_info.goods_name=goods_name
        goods_info.sale_price=sale_price
        
        goods_info.goods_brand=data.get('goods_brand')
        goods_info.goods_locality=data.get('goods_locality')
        goods_info.goods_spec=data.get('goods_spec')
        goods_info.remark=data.get('remark')
        goods_info.set_num=data.get('set_num')
        goods_info.set_price=data.get('set_price')
        goods_info.can_edit='1'
        goods_info.discount=data.get('discount',1)
        goods_info.shop_id=shop.shop_id
        goods_info.warning_num=0
        goods_info.sort_no=0
        goods_info.status=0
        goods_info.create_time=datetime.now()
        db.session.add(goods_info)
        db.session.commit()
        
        #新增销售价格履历
        insert_saleprice_sql='''Insert Into TB_SALEPRICE_S (
        GoodsID,SalePrice,StartTime)
        values (%s,%s,%s) '''
        db.engine.execute(insert_saleprice_sql,(goods_info.goods_id,goods_info.sale_price,datetime.now()))
        db.session.commit()
        # 添加图片
        for p_item in photos:
            
            photo=Photo()
            photo.link_id=goods_info.goods_id
            photo.is_checked='1'
            photo.is_visable='1'
            photo.photo_path=p_item['photo_path']
            photo.thumbnail_path=p_item['thumbnail_path']
            db.session.add(photo)
            db.session.commit()
        #添加商铺类别，只存前两级类别表
        goods_type_id_arr=goods_info.goods_type_ids.split(',')
        goods_type_id_arr.reverse()
        level=0
        for type_id in goods_type_ids:
            temp_sql='''
            INSERT INTO tb_goodstype_s (
    ShopID,
    GoodsTypeID,
    ParentID
    ) SELECT
    %s,
    GoodsTypeID,
    ParentID
    FROM
        tb_goodstype_m
    WHERE
    GoodsTypeID =%s AND NOT EXISTS (select * from tb_goodstype_s where ShopID = %s AND GoodsTypeID = %s)
            '''
            if level<2:
                
                db.engine.execute(temp_sql,(goods_info.shop_id,type_id,goods_info.shop_id,type_id))
                db.session.commit()
            level+=1
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        
#@shopcenter_controller.route('')       
def update_goods_by_id():
    pass
@shopcenter_controller.route('/m1/private/shopcenter/delete_goods_by_id',methods=['POST'])
@check_token
def delete_goods_by_id(token_type,shop):
    
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        goods_id=data['goods_id']
        sql='delete from tb_goodsinfo_s where GoodsID=%s and ShopID=%s'
        db.engine.execute(sql,(goods_id,shop.shop_id))
        db.session.commit()
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')

@shopcenter_controller.route('/m1/private/shopcenter/get_goods_info_by_bar_code',methods=['POST'])
@check_token
def get_goods_info_by_bar_code(token_type,shop):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        bar_code=data['bar_code']
        sql='''
                SELECT g.*,
            IFNULL(p.ThumbnailPath,'./Content/images/web/nowprinting2.jpg') AS ThumbnailPath,
            IFNULL(o.SaleQuantity,0) AS TotalSale
            FROM
            tb_goodsinfo_s g
            LEFT JOIN (
                SELECT
                sum(t.Quantity) AS SaleQuantity,
                t.GoodsID
                FROM
                tb_order_s d,
                tb_orderdetail_s t
                WHERE
                d.OrderNo = t.OrderNo
                AND d.`Status` <> '3'
                GROUP BY
                t.GoodsID
                ) o ON g.GoodsID = o.GoodsID
            INNER JOIN tb_photo p ON g.GoodsID = p.LinkID
            AND p.IsVisable = '1'
            AND p.IsChecked = '1'
        
            and BarCode = %s 
                '''
        row=db.engine.execute(sql,(data['bar_code'])).fetchone()   
        
        result['goods']=row_map_converter(row)
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        
    
@shopcenter_controller.route('/m1/private/shopcenter/get_delivery_member',methods=['POST'])
@check_token    
def get_delivery_member(token_type,shop):
    
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        is_validate=data['is_validate']
        if is_validate==-1:
        
            sql='''
        
    SELECT
        m.id,
        IFNULL(

            IF (
                b.NickName = '',
                NULL,
                b.NickName
                ),
            b.Account
            ) AS BuyerName,
        b.Phone,
        IFNULL(SUM(d.DeliveryMoney),0) AS DeliveryMoney,
        m.Remark
        FROM
            tb_deliveryman m
        INNER JOIN tb_buyer b ON m.BuyerID = b.BuyerID
        LEFT JOIN tb_deliverylist d ON m.BuyerID = d.BuyerID
        AND d.ShopID = m.ShopID
        WHERE
            m.ShopID = %s
        GROUP BY
            m.BuyerID
        '''
            
            rows=db.engine.execute(sql,(shop.shop_id))
            
        else:
            sql='''
            
                SELECT
                    m.id,
                    IFNULL(
            
                        IF (
                            b.NickName = '',
                            NULL,
                            b.NickName
                            ),
                        b.Account
                        ) AS BuyerName,
                    b.Phone,
                    IFNULL(SUM(d.DeliveryMoney),0) AS DeliveryMoney,
                    m.Remark
                    FROM
                        tb_deliveryman m
                    INNER JOIN tb_buyer b ON m.BuyerID = b.BuyerID
                    LEFT JOIN tb_deliverylist d ON m.BuyerID = d.BuyerID
                    AND d.ShopID = m.ShopID
                    WHERE
                        m.ShopID = %s
                    AND m.IsValidate = %s
                    GROUP BY
                        m.BuyerID
                    '''
            
            rows=db.engine.execute(sql,(shop.shop_id,is_validate))            
                
        result['delivery_members']=rows_array_converter(rows)
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
        
    return Response(json.dumps(result),content_type='application/json')
@shopcenter_controller.route('/m1/private/shopcenter/get_all_shop_member',methods=['GET'])
@check_token 
def get_all_shop_member(token_type,shop):
    
    result={'code':1,'msg':'ok'}
    try:
        sql='''SELECT
    IFNULL(IF(b.NickName = '',NULL,b.NickName),b.Account) AS BuyerName,
    a.CreateTime,
    a.`Level`,
    a.Remark,
    a.ShopID,
    a.BuyerID,
    IFNULL(c.SaleMoney,0) as SaleMoney
    FROM
        tb_member a
    LEFT JOIN tb_buyer b ON a.BuyerID = b.BuyerID
    LEFT JOIN (select ShopID,BuyerID,SUM(SaleMoney) AS SaleMoney 
        from tb_order_s 
        where `Status`<>'3' 
        GROUP BY ShopID,BuyerID) c
    ON c.ShopID = a.ShopID and c.BuyerID = a.BuyerID
    WHERE a.ShopID = %s'''
        rows=db.engine.execute(sql,(shop.shop_id))
        result['members']=rows_array_converter(rows)
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        
    


@shopcenter_controller.route('/m1/private/shopcenter/get_shop_member_and_is_not_delivery_man',methods=['GET'])
@check_token 
def get_shop_member_and_is_not_delivery_man(token_type,shop):
    result={'code':1,'msg':'ok'}
    try:
        sql='''
        SELECT
    IFNULL(

        IF (
            b.NickName = '',
            NULL,
            b.NickName
            ),
        b.Account
        ) AS BuyerName,
    a.CreateTime,
    m.ItemName as Level,
    a.Remark,
    a.ShopID,
    a.BuyerID,
    IFNULL(c.SaleMoney, 0) AS SaleMoney
    FROM
        tb_member a
    LEFT JOIN tb_buyer b ON a.BuyerID = b.BuyerID
    LEFT JOIN (
        SELECT
        ShopID,
        BuyerID,
        SUM(SaleMoney) AS SaleMoney
        FROM
        tb_order_s
        WHERE
        STATUS <> '3'
        GROUP BY
        ShopID,
        BuyerID
        ) c ON c.ShopID = a.ShopID
    AND c.BuyerID = a.BuyerID
    LEFT JOIN tb_constent_m m ON m.ItemID = a.`Level` AND m.TypeID='011'
    WHERE
        a.ShopID = %s
    AND NOT EXISTS (
        SELECT
        BuyerID
        FROM
        tb_deliveryman
        WHERE
        ShopID = %s
        AND BuyerID = a.BuyerID
    )
        '''
        rows=db.engine.execute(sql,(shop.shop_id,shop.shop_id))
        result['members']=rows_array_converter(rows)
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
        
    return Response(json.dumps(result),content_type='application/json')
        
    
@shopcenter_controller.route('/m1/private/shopcenter/add_delivery_member',methods=['POST'])
@check_token     
def add_delivery_member(token_type,shop):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        delivery_man=DeliveryMan()
        delivery_man.shop_id=shop.shop_id
        delivery_man.buyer_id=data['buyer_id']
        delivery_man.is_validate='1'
        db.session.add(delivery_man)
        db.session.commit()
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')

@shopcenter_controller.route('/m1/private/shopcenter/validate_delivery_member',methods=['POST'])
@check_token     
def validate_delivery_member(token_type,shop):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        dm=DeliveryMan.query.filter_by(shop_id=shop.shop_id,buyer_id=data['buyer_id']).first()
        if dm:
            dm.is_validate='1'
            db.session.commit()
        
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')        
        
        

@shopcenter_controller.route('/m1/private/shopcenter/del_delivery_member',methods=['POST'])
@check_token     
def del_delivery_member(token_type,shop):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        sql='''delete from tb_deliveryman where ShopID=%s and BuyerID=%s'''
        db.engine.execute(sql,(shop.shop_id,data['buyer_id']))
        db.session.commit()
        
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')        
        
@shopcenter_controller.route('/m1/private/shopcenter/del_shop_member',methods=['POST'])
@check_token      
def del_shop_member(token_type,shop):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        sql='''delete from tb_member where ShopID=%s and BuyerID=%s'''
        db.engine.execute(sql,(shop.shop_id,data['buyer_id']))
        db.session.commit()
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
    
    
#店铺指定
@shopcenter_controller.route('/m1/private/shopcenter/add_delivery_list_info_by_ps',methods=['POSt'])
@check_token
def add_delivery_list_info_by_ps(token_type,shop):
    result={'code':1,'msg':'ok'}
    try:
        order_no=data['order_no']
        delivery_money=data['delivery_money']
        buyer_id=data['buyer_id']
        sql='''insert into tb_deliverylist (OrderNo,ShopID,BuyerID,DeliveryMoney,DeliveryStatus,ReceiveTime)
    values (%s,%s,%s,%s )'''
        db.engine.execute(sql,(order_no,shop.shop_id,buyer_id,delivery_money,1,datetime.now()))
        db.session.commit()
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')


    
#抢单配送
@shopcenter_controller.route('/m1/private/shopcenter/add_delivery_list_info_by_qd',methods=['POST'])
@check_token
def add_delivery_list_info_by_qd(token_type,shop):
    
    result={'code':1,'msg':'ok'}
    data=request.get_json()
    try:
        order_no=data['order_no']
        delivery_money=data['delivery_money']        
        sql='''insert into tb_deliverylist (OrderNo,ShopID,DeliveryMoney,DeliveryStatus)
    values (%s,%s,%s,%s)'''
        db.engine.execute(sql,(order_no,shop.shop_id,delivery_money,0))
        
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
        
    return Response(json.dumps(result),content_type='application/json')
        
    
@shopcenter_controller.route('/m1/private/shopcenter/get_delivery_list_by_page',methods=['POST'])   
@check_token
def get_delivery_list_by_page(token_type,shop):
    result={'code':1,'msg':'ok'}
    
    data=request.get_json()
    
    try:
        page=data.get('page',1)
        page_size=data.get('page_size',20)
        buyer_id=data.get('buyer_id',None)
        order_no=data.get('order_no',None)
        sql='''
        SELECT
    d.id,
        d.SubmitTime,
        d.OrderNo,
        IFNULL(

            IF (
                b.NickName = '',
                NULL,
                b.NickName
                ),
            b.Account
            ) AS BuyerName,
        b.Phone,
    (o.SaleMoney + o.Freight) AS orderMoney,
        o.Freight,
    o.PayStatus,
        d.DeliveryMoney,
        c.ItemName,
    d.DeliveryStatus,
    CONCAT('+',(o.SaleMoney + o.Freight)-d.DeliveryMoney) as giveMoney
    FROM
        tb_deliverylist d
    LEFT JOIN tb_buyer b ON b.BuyerID = d.BuyerID
    LEFT JOIN tb_constent_m c ON c.ItemID = d.DeliveryStatus
    INNER JOIN tb_order_s o ON o.OrderNo = d.OrderNo
        AND c.TypeID = '021'
        WHERE
            d.ShopID = %s'''
        values=[]
        values.append(shop.shop_id)
        
        if buyer_id:
            sql+=' and d.BuyerID=%s'
            values.append(buyer_id)
        if order_no:
            sql+=' and d.OrderNo=%s'
            values.append(order_no)
            
        sql+=' ORDER BY d.ReceiveTime DESC limit %s , %s'
        values.append(page_size)
        values.append((page-1)*page_size)
        
        rows=db.engine.execute(sql,tuple(values))
        result['delivery_list']=rows_array_converter(rows)
        
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    
    return Response(json.dumps(result),content_type='application/json')
        
    