# -*- coding: utf-8 -*-
from flask import json, Response, Blueprint, request, json, current_app
from database.models import db, GoodsInfo, Photo, DeliveryMan, ShopInfo, Order, Member, Activity, Purchase, GoodsType,DeliveryList
from datetime import datetime
import datetime as dt
import os
from views.utils import check_token, row_map_converter, rows_array_converter, result_set_converter

shopcenter_controller = Blueprint('shopcenter_controller', __name__)


@shopcenter_controller.route('/m1/private/shopcenter/get_shop_info', methods=['GET'])
@check_token
def get_shop_info(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        result['shop_info'] = shop.get_map()
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type="application/json")


@shopcenter_controller.route('/m1/private/shopcenter/get_goods_by_page', methods=['POST'])
@check_token
def get_goods_by_page(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        data = request.get_json()
        page = int(data.get('page', 1))
        page_size = int(data.get('page_size', 20))
        order_by = data.get('order_by', 'summarydesc')

        sql = '''
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

        if order_by == 'saleasc':
            sql += 'order by Quantity asc'
        if order_by == 'saledesc':
            sql += 'order by Quantity desc'
        if order_by == 'priceasc':
            sql += 'order by SalePrice asc'
        if order_by == 'pricedesc':
            sql += 'order by SalePrice desc'
        if order_by == 'summarydesc':
            sql += 'order by Saleprice,Quantity desc'
        if order_by == 'summaryasc':
            sql += 'order by Saleprice,Quantity asc'
        sql += ' limit %s,%s'
        result_set = db.engine.execute(sql, (shop.shop_id, (page - 1)*page_size, page_size))
        arr = []
        for row in result_set:
            temp = row_map_converter(row)
            arr.append(temp)
            result['goods'] = arr
        count_sql = '''
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
        row = db.engine.execute(count_sql, (shop.shop_id)).fetchone()
        total_count = 0
        if row:
            result['total_count'] = int(row['TotalCount'])
        result['page'] = page
        result['page_size'] = page_size
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/get_orders_by_page', methods=['POST'])
@check_token
def get_orders_by_page(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        data = request.get_json()
        page = int(data.get('page', 1))
        page_size = int(data.get('page_size', 20))
        sql = '''
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
                TOS.PayType,
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
        result_set = db.engine.execute(sql, (shop.shop_id, (page - 1) * page_size, page_size))
        arr = []
        sql_detail = '''
        
                select a.* ,b.GoodsName,
                c.PhotoID ,c.PhotoName,c.PhotoPath,c.ThumbnailPath,c.SortNo
                from tb_orderdetail_s a
                left join tb_goodsinfo_s b on b.GoodsID=a.GoodsID
                left join tb_photo c on c.LinkID=a.GoodsID and c.IsChecked=1 and c.IsVisable=1
                where OrderNo=%s
                '''
        for row in result_set:
            temp = row_map_converter(row)
            order_detail_result_set = db.engine.execute(sql_detail, (temp['order_no']))
            order_detail_arr = []
            for item in order_detail_result_set:
                order_detail_arr.append(row_map_converter(item))
                temp['goods'] = order_detail_arr
            arr.append(temp)
        result['orders'] = arr
        count_Sql = '''
        
        select count(*) as TotalCount  FROM
                tb_order_s TOS
        LEFT JOIN  tb_constent_m TCM ON TCM.TypeID = '009'
        AND TOS. STATUS = TCM.ItemID
        LEFT JOIN tb_constent_m PCM ON PCm.TypeID = '010'
        AND TOS.PayStatus = PCM.ItemID
        WHERE
                TOS.ShopID = %s  ORDER BY SubmitTime desc 
        '''
        row = db.engine.execute(count_Sql, (shop.shop_id)).fetchone()
        if row:
            result['total_count'] = row['TotalCount']
        result['page'] = page
        result['page_size'] = page_size
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/up_goods_by_id', methods=['POST'])
@check_token
def up_goods_by_id(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        data = request.get_json()
        sql = 'update tb_goodsinfo_s set Status=1 where GoodsID = %s'
        db.engine.execute(sql, (data['goods_id']))
        db.session.commit()
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message


@shopcenter_controller.route('/m1/private/shopcenter/down_goods_by_id', methods=['POST'])
@check_token
def down_goods_by_id(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        data = request.get_json()
        sql = 'update tb_goodsinfo_s set Status=0 where GoodsID = %s'
        db.engine.execute(sql, (data['goods_id']))
        db.session.commit()
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 1
        result['msg'] = e.message
    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/get_msgs_by_page', methods=['POST'])
@check_token
def get_msgs_by_page(token_type, shop):
    data = request.get_json()
    page = int(data.get('page', 1))
    page_size = int(data.get('page_size', 20))
    result = {'code': 1, 'msg': 'ok'}
    try:
        sql = ''' select
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
        result_set = db.engine.execute(sql, (shop.shop_id, page - 1, page_size))
        arr = []
        for row in result_set:
            temp = row_map_converter(row)
            arr.append(temp)
        result['msgs'] = arr
        count_sql = '''
        select count(*) as total_count from tb_message_w m
 left join tb_constent_m c on m.IsRead =c.ItemID and c.typeID=015
 where m.ReceiverType=1 and m.Receiver=%s order by m.SendTime desc
        '''
        row = db.engine.execute(count_sql, (shop.shop_id)).fetchone()
        if row:
            result['total_count'] = row['total_count']
        result['page'] = page
        result['page_size'] = page_size
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/update_msg_2_is_read', methods=['POST'])
@check_token
def update_msg_2_is_read(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        data = request.get_json()
        sql = '''
        UPDATE tb_message_w SET IsRead =1 WHERE MessageID =%s
        '''
        db.engine.execute(sql, (data['msg_id']))
        db.session.commit()
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/get_goods_type_root', methods=['POST', 'GET'])
@check_token
def get_goods_type_root(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        sql = '''
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
        result_set = db.engine.execute(sql, (shop.shop_id))
        arr = []
        for row in result_set:
            temp = {}
            temp['shop_id'] = int(row['ShopID'])
            temp['goods_type_id'] = int(row['GoodsTypeID'])
            temp['goods_type_name'] = row['GoodsTypeName']
            temp['parent_id'] = row['ParentID']
            temp['sort_no'] = row['SortNo']
            arr.append(temp)
        result['shop_goods_type_root'] = arr
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/get_shop_goods_type_child', methods=['POST'])
@check_token
def get_shop_goods_type_child(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        data = request.get_json()
        parent_id = data['parent_id']
        sql = '''SELECT
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

        result_set = db.engine.execute(sql, (shop.shop_id, parent_id))
        arr = []
        for row in result_set:
            temp = {}
            temp['shop_id'] = int(row['ShopID'])
            temp['goods_type_id'] = int(row['GoodsTypeID'])
            temp['goods_type_name'] = row['GoodsTypeName']
            temp['parent_id'] = row['ParentID']
            temp['sort_no'] = row['SortNo']
            arr.append(temp)
        result['shop_goods_type_child'] = arr

    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route("/m1/private/shopcenter/upload_goods_photo", methods=['POST'])
def upload_goods_photo(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        if request.method == 'POST':
            file = request.files['file']
            extension = os.path.splitext(file.filename)[1]
            f_name = str(uuid.uuid4()) + extension
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))


    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route("/m1/private/shopcenter/add_goods_info", methods=['POST'])
@check_token
def add_goods_info(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}

    try:
        data = request.get_json()
        bar_code = data['bar_code']
        goods_type_id = data['goods_type_id']
        goods_type_ids = data['goods_type_ids']
        goods_name = data['goods_name']
        sale_price = data['sale_price']
        warning_num = data.get('warning_num',0)
        sort_no = data.get('sort_no',0)
        quantity = data.get('quantity',None)
        photos = data.get('photos',None)
        goods_info=GoodsInfo.query.filter_by(bar_code=bar_code).first()
        edit_flag=True
        if not  goods_info:
            edit_flag=False
            goods_info = GoodsInfo()
        goods_info.bar_code = bar_code
        goods_info.goods_type_id = goods_type_id
        goods_info.goods_type_ids = goods_type_ids
        goods_info.goods_name = goods_name
        goods_info.sale_price = sale_price

        goods_info.goods_brand = data.get('goods_brand')
        goods_info.goods_locality = data.get('goods_locality')
        goods_info.goods_spec = data.get('goods_spec')
        goods_info.remark = data.get('remark')
        goods_info.set_num = data.get('set_num')
        goods_info.set_price = data.get('set_price')
        goods_info.can_edit = '1'
        goods_info.discount = data.get('discount', 1)
        goods_info.shop_id = shop.shop_id
        goods_info.warning_num = warning_num
        goods_info.sort_no = sort_no
        goods_info.status = 0
        goods_info.create_time = datetime.now()
        if edit_flag:
            db.session.commit()
        else:
            db.session.add(goods_info)
            db.session.commit()

        # 新增销售价格履历
        insert_saleprice_sql = '''Insert Into TB_SALEPRICE_S (
        GoodsID,SalePrice,StartTime)
        values (%s,%s,%s) '''
        db.engine.execute(insert_saleprice_sql, (goods_info.goods_id, goods_info.sale_price, datetime.now()))
        db.session.commit()
        # 添加图片
        if photos:
            for p_item in photos:
                photo = Photo()
                photo.link_id = goods_info.goods_id
                photo.is_checked = '1'
                photo.is_visable = '1'
                photo.photo_path = p_item['photo_path']
                photo.thumbnail_path = p_item['thumbnail_path']
                db.session.add(photo)
                db.session.commit()
        # 添加商铺类别，只存前两级类别表
        goods_type_id_arr = goods_info.goods_type_ids.split(',')
        goods_type_id_arr.reverse()
        level = 0
        for type_id in goods_type_ids:
            temp_sql = '''
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
            if level < 2:
                db.engine.execute(temp_sql, (goods_info.shop_id, type_id, goods_info.shop_id, type_id))
                db.session.commit()
            level += 1

        if quantity!=None:
            p = Purchase.query.filter_by(goods_id=data['goods_id']).order_by(Purchase.batch_no.desc()).first()
            if p:
                p.quantity = data['quantity']
                db.session.commit()
            else:
                purchase=Purchase()
                purchase.quantity=data['quantity']
                purchase.batch_no=1
                purchase.goods_id=data['goods_id']
                purchase.buy_price=0
                purchase.start_time=datetime.now()
                purchase.end_time=datetime.now()+dt.timedelta(days=365)
                db.session.add(purchase)
                db.session.commit()
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type='application/json')





@shopcenter_controller.route('/m1/private/shopcenter/delete_goods_by_id', methods=['POST'])
@check_token
def delete_goods_by_id(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        data = request.get_json()
        goods_id = data['goods_id']
        sql = 'delete from tb_goodsinfo_s where GoodsID=%s and ShopID=%s'
        db.engine.execute(sql, (goods_id, shop.shop_id))
        db.session.commit()
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/get_goods_info_by_bar_code', methods=['POST'])
@check_token
def get_goods_info_by_bar_code(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        data = request.get_json()
        bar_code = data['bar_code']
        sql = '''
                SELECT g.*,m.GoodsTypeName,
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

             LEFT JOIN tb_goodstype_m m ON g.GoodsTypeID = m.GoodsTypeID
            where BarCode = %s
                '''
        row = db.engine.execute(sql, (bar_code)).fetchone()
        if row:
            result['goods'] = row_map_converter(row)
        else:
            result['goods'] = None
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/get_delivery_member', methods=['POST'])
@check_token
def get_delivery_member(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        data = request.get_json()
        is_validate = data['is_validate']
        if is_validate == -1 or is_validate == "-1":

            sql = '''
        
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
        b.BuyerID,
        b.Phone,
        IFNULL(SUM(d.DeliveryMoney),0) AS DeliveryMoney,
        m.Remark,
        m.IsValidate,
        d.DeliveryStatus,

        b.Avatar
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

            rows = db.engine.execute(sql, (shop.shop_id))

        else:
            sql = '''
            
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
                    b.BuyerID,
                    IFNULL(SUM(d.DeliveryMoney),0) AS DeliveryMoney,
                    m.Remark,
                     m.IsValidate,
                    d.DeliveryStatus,
                    b.Avatar
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

            rows = db.engine.execute(sql, (shop.shop_id, is_validate))

        result['delivery_members'] = rows_array_converter(rows)
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message

    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/get_all_shop_member', methods=['GET'])
@check_token
def get_all_shop_member(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        sql = '''SELECT
    IFNULL(IF(b.NickName = '',NULL,b.NickName),b.Account) AS BuyerName,
    a.CreateTime,
    a.`Level`,
    a.Remark,
    a.ShopID,
    a.BuyerID,
    b.Phone,
    b.Avatar,
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
        rows = db.engine.execute(sql, (shop.shop_id))
        result['members'] = rows_array_converter(rows)
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/get_shop_member_and_is_not_delivery_man', methods=['GET'])
@check_token
def get_shop_member_and_is_not_delivery_man(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        sql = '''
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
    b.Phone,
    b.Avatar,
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
        rows = db.engine.execute(sql, (shop.shop_id, shop.shop_id))
        result['members'] = rows_array_converter(rows)
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message

    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/add_delivery_member', methods=['POST'])
@check_token
def add_delivery_member(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        data = request.get_json()
        delivery_man = DeliveryMan()
        delivery_man.shop_id = shop.shop_id
        delivery_man.buyer_id = data['buyer_id']
        delivery_man.is_validate = '1'
        delivery_man.is_active='1'
        delivery_man.remark = data.get('remark', '')
        db.session.add(delivery_man)
        db.session.commit()
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/update_delivery_member', methods=['POST'])
@check_token
def update_delivery_member(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        data = request.get_json()
        d = DeliveryMan.query.filter_by(shop_id=shop.shop_id, buyer_id=data['buyer_id']).first()
        if d:
            d.remark = data.get('remark', '')
            db.session.commit()
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/validate_delivery_member', methods=['POST'])
@check_token
def validate_delivery_member(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        data = request.get_json()
        remark = data.get('remark', '')

        dm = DeliveryMan.query.filter_by(shop_id=shop.shop_id, buyer_id=data['buyer_id']).first()
        if dm:
            dm.is_validate = '1'
            db.remark = remark
            db.session.commit()

    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/del_delivery_member', methods=['POST'])
@check_token
def del_delivery_member(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        data = request.get_json()
        sql = '''delete from tb_deliveryman where ShopID=%s and BuyerID=%s'''
        db.engine.execute(sql, (shop.shop_id, data['buyer_id']))
        db.session.commit()

    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/del_shop_member', methods=['POST'])
@check_token
def del_shop_member(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        data = request.get_json()
        sql = '''delete from tb_member where ShopID=%s and BuyerID=%s'''
        db.engine.execute(sql, (shop.shop_id, data['buyer_id']))
        db.session.commit()
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type='application/json')


# 店铺指定
@shopcenter_controller.route('/m1/private/shopcenter/add_delivery_list_info_by_ps', methods=['POST'])
@check_token
def add_delivery_list_info_by_ps(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        data = request.get_json()
        order_no = data['order_no']
        delivery_money = data['delivery_money']
        buyer_id = data['buyer_id']
        sql = '''insert into tb_deliverylist (OrderNo,ShopID,BuyerID,DeliveryMoney,DeliveryStatus,ReceiveTime)
    values (%s,%s,%s,%s,%s,%s)'''
        db.engine.execute(sql, (order_no, shop.shop_id, buyer_id, delivery_money, 1, datetime.now()))
        db.session.commit()
        # 更新订单状态为已发货
        order = Order.query.filter_by(order_no=order_no).first()
        if order:
            order.status = 1  # 已发货
            db.session.commit()
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type='application/json')


# 抢单配送
@shopcenter_controller.route('/m1/private/shopcenter/add_delivery_list_info_by_qd', methods=['POST'])
@check_token
def add_delivery_list_info_by_qd(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    data = request.get_json()
    try:
        order_no = data['order_no']
        delivery_money = data['delivery_money']
        sql = '''insert into tb_deliverylist (OrderNo,ShopID,DeliveryMoney,DeliveryStatus)
    values (%s,%s,%s,%s)'''
        db.engine.execute(sql, (order_no, shop.shop_id, delivery_money, 0))

    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message

    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/get_delivery_list_by_page', methods=['POST'])
@check_token
def get_delivery_list_by_page(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}

    data = request.get_json()

    try:
        page = data.get('page', 1)
        page_size = data.get('page_size', 20)
        buyer_id = data.get('buyer_id', None)
        order_no = data.get('order_no', None)
        sql = '''SELECT d.id,
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
        b.Avatar,
    (o.SaleMoney + o.Freight) AS orderMoney,
        o.Freight,
    o.PayStatus,
        d.DeliveryMoney,
        c.ItemName,
        o.PayType,
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
        values = []
        values.append(shop.shop_id)

        if buyer_id:
            sql += ' and d.BuyerID=%s'
            values.append(buyer_id)
        if order_no:
            sql += ' and d.OrderNo=%s'
            values.append(order_no)

        sql += ' ORDER BY d.ReceiveTime DESC limit %s , %s'
        values.append((page - 1) * page_size)
        values.append(page_size)

        rows = db.engine.execute(sql, tuple(values))
        result['delivery_list'] = rows_array_converter(rows)

    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message

    return Response(json.dumps(result), content_type='application/json')

@shopcenter_controller.route('/m1/private/shopcenter/update_delivery_list_status', methods=['POST'])
@check_token
def update_delivery_list_status(token_type, shop):

    result = {'code':1,'msg':'ok'}
    try:
        data=request.json
        id=data['deliverylist_id']
        delivery_status=data['delivery_status']
        re= DeliveryList.query.get(id)
        if re:
            re.delivery_status=delivery_status
            db.session.commit()
    except Exception as e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message

    return Response(json.dumps(result), content_type='application/json')






# --------------------------12.28新增------------------------

@shopcenter_controller.route('/m1/private/shopcenter/update_shop_info', methods=['POST'])
@check_token
def update_shop_info(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}

    data = request.get_json()
    current_app.logger.info(data)
    try:
        shop_info = ShopInfo.query.filter_by(shop_id=shop.shop_id).first()
        if shop_info:
            if data.get('shop_phone', None):
                shop_info.shop_phone = data['shop_phone']
            if data.get('link_man', None):
                shop_info.link_man = data['link_man']
            if data.get('with_draw_account', None):
                shop_info.with_draw_account = data['with_draw_account']
            if data.get('weixin', None):
                shop_info.weixin = data['weixin']
            if data.get('operating_status', None):
                shop_info.operating_status = str(data['operating_status'])
            db.session.commit()
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message

    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/save_shop_address', methods=['POST'])
@check_token
def save_shop_address(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    data = request.get_json()

    try:
        shop_info = ShopInfo.query.filter_by(shop_id=shop.shop_id).first()
        if shop_info:
            shop_info.shop_address = data['shop_address']
            shop_info.xzb = data['xzb']
            shop_info.yzb = data['yzb']
            shop_info.mktxzb = data['mktxzb']
            shop_info.mktyzb = data['mktyzb']
            db.session.commit()
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message

    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/get_supply_shop_list', methods=['GET'])
@check_token
def get_supply_shop_list(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        sql = '''SELECT S.ShopID,S.ShopPhoto,S.Account,S.ShopName,S.ShopType,S.Email,
						S.ShopPhone,S.LinkMan,S.Mobile,S.ShopAddress,S.RegistDate
				   FROM TB_SHOPINFO_S S
				   where S.`status`=0 and IsSupplyShop = 1
				order by IsTop desc,SortNo desc,Status'''
        rows = db.engine.execute(sql)
        result['shop_list'] = rows_array_converter(rows)
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message

    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/update_member', methods=['POST'])
@check_token
def update_member(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        data = request.json
        member = Member.query.filter_by(shop_id=shop.shop_id, buyer_id=data['buyer_id']).first()
        if member:
            if data.get('remark', None) != None:
                member.remark = data.get('remark', '')
            if data.get('level', None) != None:
                member.level = str(data.get('level'))
            db.session.commit()
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/get_goods_types_tree', methods=['GET'])
@check_token
def get_goods_types_tree(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        get_types(result, 0)
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message

    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/get_goods_type_parent', methods=['GET'])
@check_token
def get_goods_type_parent(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        sql = '''select * from tb_goodstype_m where ParentID is NULL ''';
        rows = db.engine.execute(sql)

        result['shop_goods_type_parent'] = rows_array_converter(rows)
        for item in result['shop_goods_type_parent']:
            item['parent_id'] = ''

    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/get_goods_type_child', methods=['POST'])
@check_token
def get_goods_type_child(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        sql = '''select * from tb_goodstype_m where ParentID = %s ''';
        rows = db.engine.execute(sql, (request.json['parent_id']))
        result['shop_goods_type_child'] = rows_array_converter(rows)
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/get_shop_activities_list', methods=['GET', 'POST'])
@check_token
def get_shop_activities_list(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        sql = '''SELECT
					ID,
					Title,
					Count,
					IsTop,
					SortNo,
					IsHot,
					Publisher,
					PublishTime,
					Updater,
					UpdateTime
				FROM
					tb_activities_w
				WHERE
					Type = 1
				AND ShopID = %s AND DelFlag = 0
				ORDER BY
					IsTop DESC,
					SortNo DESC  ''';
        rows = db.engine.execute(sql, (shop.shop_id))
        result['activities'] = rows_array_converter(rows)
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type='application/json')


def get_types(parent, parentId):
    if parentId and parentId > 0:
        sql = '''select * from tb_goodstype_m where ParentID=%s'''
        rows = db.engine.execute(sql, (parentId))
    else:
        sql = ''' select * from tb_goodstype_m where ParentID is NULL '''
        rows = db.engine.execute(sql)
    tmp = rows_array_converter(rows)
    if len(tmp) > 0:
        parent['sons'] = tmp
        for item in tmp:
            get_types(item, item['goodstype_id'])

    else:
        return


@shopcenter_controller.route('/m1/private/shopcenter/add_activities_info', methods=['GET', 'POST'])
@check_token
def add_activities_info(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        data = request.json
        activity = Activity()
        activity.shop_id = shop.shop_id
        activity.content = data.get('content', '')
        activity.title = data.get('title', '')
        activity.sort_no = data.get('sort_no', 1)
        activity.seo_key_word = data.get('seo_key_word', '')
        activity.seo_title = data.get('seo_title', '')
        activity.seo_content = data.get('seo_content', '')
        activity.is_hot = str(data.get('is_hot', '0'))
        activity.is_top = str(data.get('is_top', '0'))
        activity.publish_time = datetime.now()
        activity.publisher = shop.shop_name
        db.session.add(activity)
        db.session.commit()
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/update_activities_info', methods=['POST'])
@check_token
def update_activities_info(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        data = request.json
        activity = Activity.query.get(data['activity_id'])
        if activity:
            activity.content = data.get('content', '')
            activity.title = data.get('title', '')
            activity.sort_no = data.get('sort_no', 1)
            activity.seo_key_word = data.get('seo_key_word', '')
            activity.seo_title = data.get('seo_title', '')
            activity.seo_content = data.get('seo_content', '')
            activity.is_hot = str(data.get('is_hot', '0'))
            activity.is_top = str(data.get('is_top', '0'))
            activity.publish_time = datetime.now()
            activity.publisher = shop.shop_name
            db.session.commit()
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/del_activities', methods=['POST'])
@check_token
def del_activities(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        data = request.json
        Activity.query.filter_by(id=data['activity_id']).delete()
        db.session.commit()
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type='application/json')


##添加货源意向
@shopcenter_controller.route('/m1/private/shopcenter/shop_stock', methods=['POST'])
@check_token
def shop_stock(token_type, shop):
    result = {'code': 1, 'msg': 'ok'}
    try:
        data = request.json
        sql_e = ''' select * from  TB_PURCHASEINTENTION_S where ShopID=%s and GoodsID=%s '''
        row = db.engine.execute(sql_e, (shop.shop_id, data["goods_id"])).fetchone()
        if row:
            sql_u = '''UPDATE TB_PURCHASEINTENTION_S
					SET Quantity = %s, CreateTime = %s,Price = %s
					WHERE
						ShopID = %s
					AND GoodsID = %s
					AND IsHandled = 0'''
            db.engine.execute(sql_u, (data['quantity'], datetime.now(), data['price'], shop.shop_id, data['goods_id']))
            db.session.commit()
        else:

            sql = '''INSERT INTO
    				TB_PURCHASEINTENTION_S
    				(`ShopID`, `GoodsID`,Price, `Quantity`, `CreateTime`,IsHandled)
    			VALUES
    				(%s, %s, %s, %s, %s, '0')'''

            db.engine.execute(sql, (shop.shop_id, data['goods_id'], data['price'], data['quantity'], datetime.now()))
            db.session.commit()
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/update_goods_info', methods=['POST'])
@check_token
def update_goods_info(token_type, shop):
    result = {"code": 1, 'msg': 'ok'}
    try:
        data = request.json
        goods_info = GoodsInfo.query.filter_by(goods_id=data['goods_id']).first()
        sale_price = data.get('sale_price', None)
        waring_num = data.get('warning_num', None)
        goods_spec = data.get('goods_spec', None)
        goods_name = data.get('goods_name', None)
        discount = data.get('discount', None)
        goods_locality = data.get('goods_locality', None)
        goods_brand = data.get("goods_brand", None)
        set_num = data.get('set_num', None)
        set_price = data.get('set_price', None)
        goods_type_id = data.get('goods_type_id', None)
        goods_type_ids = data.get('goods_type_ids', None)
        sort_no = data.get('sort_no', None)
        photos = data.get('photos', None)

        quantity=data.get('quantity',None)

        if goods_info:
            if sale_price:
                goods_info.sale_price = sale_price
            if waring_num:
                goods_info.warning_num = waring_num
            if goods_spec:
                goods_info.goods_spec = goods_spec
            if goods_name:
                goods_info.goods_name = goods_name
            if discount:
                goods_info.discount = discount
            if goods_locality:
                goods_info.goods_locality = goods_locality
            if goods_brand:
                goods_info.goods_brand = goods_brand
            if set_num:
                goods_info.set_num = set_num
            if set_price:
                goods_info.set_price = set_price
            if goods_type_id:
                goods_info.goods_type_id = goods_type_id
            if goods_type_ids:
                goods_info.goods_type_ids = goods_type_ids
            if sort_no:
                goods_info.sort_no = sort_no
            if photos:
                for p_item in photos:
                    if not p_item.get('photo_id', None):
                        photo = Photo()
                        photo.link_id = goods_info.goods_id
                        photo.is_checked = '1'
                        photo.is_visable = '1'
                        photo.photo_path = p_item['photo_path']
                        photo.thumbnail_path = p_item['thumbnail_path']
                        db.session.add(photo)
                        db.session.commit()
                    else:
                        if p_item['photo_path']=='':
                            Photo.query.filter_by(photo_id=p_item['photo_id']).delete()
                        else:
                            photo = Photo.query.get(p_item['photo_id'])
                            if photo:
                                photo.link_id = goods_info.goods_id
                                photo.is_checked = '1'
                                photo.is_visable = '1'
                                photo.photo_path = p_item['photo_path']
                                photo.thumbnail_path = p_item['thumbnail_path']
                                db.session.commit()
            if quantity!=None:
                p = Purchase.query.filter_by(goods_id=data['goods_id']).order_by(Purchase.batch_no.desc()).first()
                if p:
                    p.quantity = data['quantity']
                    p.end_time=datetime.now()+dt.timedelta(days=3650)
                    db.session.commit()
                else:
                    purchase=Purchase()
                    purchase.quantity=data['quantity']
                    purchase.batch_no=1
                    purchase.goods_id=data['goods_id']
                    purchase.buy_price=0
                    purchase.start_time=datetime.now()
                    purchase.end_time=datetime.now()+dt.timedelta(days=3650)
                    db.session.add(purchase)
                    db.session.commit()
            db.session.commit()
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message

    return Response(json.dumps(result), content_type="application/json")


@shopcenter_controller.route('/m1/private/shopcenter/update_goods_quantity', methods=['POST'])
@check_token
def update_goods_quantity(token_type, shop):
    result = {"code": 1, 'msg': 'ok'}

    try:
        data = request.json

        p = Purchase.query.filter_by(goods_id=data['goods_id']).first()
        if p:
            p.quantity = data['quantity']
            db.session.commit()

    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message

    return Response(json.dumps(result), content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/get_goods_info_for_edit', methods=['POST'])
@check_token
def get_goods_info_for_edit(token_type, shop):
    result = {"code": 1, 'msg': 'ok'}

    try:
        data = request.json
        goods_id = data['goods_id']
        goods = GoodsInfo.query.filter_by(goods_id=goods_id).first()
        if goods:
            result['goods'] = goods.get_map()
            photos = Photo.query.filter_by(link_id=goods.goods_id, is_visable='1', is_checked=1).all()
            result['goods']['photos'] = result_set_converter(photos)
            goods_type_name = GoodsType.query.filter_by(goods_type_id=goods.goods_type_id).first()
            if goods_type_name:
                result['goods']['goods_type_name'] = goods_type_name.get_map()

            p=Purchase.query.filter_by(goods_id=goods_id).order_by(Purchase.batch_no.desc()).first()

            if p:
                result['goods']['quantity']=p.quantity
            else:
                result['goods']['quantity']=0

        else:
            result['goods'] = None


    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message

    return Response(json.dumps(result), content_type='application/json')

#获取货源意向
@shopcenter_controller.route('/m1/private/shopcenter/get_purchase_intention', methods=['POST','GET'])
@check_token
def get_purchase_intention(token_type,shop):
    result={"code":1,'msg':'ok'}
    try:
        sql='''SELECT
					a.id,
					c.barcode,
					a.ShopID,
					c.GoodsName,
					a.Price,
					a.Quantity,
					a.CreateTime,
					c.GoodsSpec,
					c.GoodsBrand,
					a.IsHandled,
					d.ItemName
				FROM
					tb_purchaseintention_s a
				LEFT JOIN tb_shopinfo_s b ON a.ShopID = b.ShopID
				LEFT JOIN tb_goodsinfo_s c ON a.GoodsID = c.GoodsID
				LEFT JOIN tb_constent_m d ON a.IsHandled = d.ItemID
				AND d.TypeID = 020
				WHERE
					a.ShopID = %s'''
        rows=db.engine.execute(sql,(shop.shop_id))

        result['goods']=rows_array_converter(rows)

    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message

    return Response(json.dumps(result),content_type='application/json')


@shopcenter_controller.route('/m1/private/shopcenter/complete_order',methods=['POST'])
@check_token
def complete_order(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        data=request.json
        order_no=data['order_no']
        sql='''update tb_order_s set Status=2 where OrderNo=%s'''
        db.engine.execute(sql,(order_no))
        db.session.commit()
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')

@shopcenter_controller.route('/m1/private/shopcenter/cancle_order',methods=['POST'])
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