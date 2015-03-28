# -*- coding: utf-8 -*-
from flask import json,Response,Blueprint,request
from sqlalchemy import desc
from database.models import db,Photo

shop_goods_controller=Blueprint('shop_goods_controller',__name__)
#取得店铺的商品关联图片信息（商品ID）
@shop_goods_controller.route('/m1/public/get_shop_goods_photos',methods=['POST'])
def get_shop_goods_photos():
    
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        photos=Photo.query.filter_by(link_id=data['goods_id'],is_cheked='1').order_by(desc(Photo.is_visable),desc(Photo.sort_no)).all()
        arr=[]
        for photo in photos:
            arr.append(photo.get_map())
        result['photos']=arr
    except Exception ,e:
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type="application/json")
        

@shop_goods_controller.route('/m1/public/get_shop_goods_detail')
#取得店铺的商品详情信息（商品ID）
def get_shop_goods_detail():
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        sql='''SELECT
        TAS.GoodsID,
        TAS.GoodsTypeID,
        TAS.AddAttrID,
        TGM.AddAttrName,
        TAS.AddAttrContent
        FROM 
            TB_ADDATTRCONTENT_S TAS,
            TB_GOODSADDATTR_M TGM
        WHERE
        TAS.GoodsID = %s
        AND TAS.GoodsTypeID = TGM.GoodsTypeID
        AND TAS.AddAttrID = TGM.AddAttrID
        AND TAS.AddAttrContent <> ''
    
        '''
        result_set=db.engine.execute(sql,data['goods_id'])
        arr=[]
        for row in result_set:
            temp={}
            temp['goods_id']=row['GoodsID']
            temp['goods_type_id']=row['GoodsTypeID']
            temp['add_attr_id']=row['AddAttrID']
            temp['add_attr_name']=row['AddAttrName']
            temp['add_attr_content']=row['AddAttrContent']
            arr.append(temp)
        result['goods_detail']=arr
    except Exception,e:
        result['code']=0
        result['msg']=e.message
        
    return Response(json.dumps(result),content_type="application/json")
       
#取得商铺商品交易成功个数
@shop_goods_controller.route('/m1/public/get_shop_goods_count')
def get_shop_goods_count():
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        sql='''
        SELECT
        IFNULL(SUM(s.Quantity), 0) AS Quantity
        FROM
            tb_order_s o
        LEFT JOIN tb_orderdetail_s s ON o.OrderNo = s.OrderNo
        WHERE
            s.GoodsID = %s 
        AND o.ShopID = %s
        AND (o.Status = 1 OR o.Status = 2)
        '''
        row=db.engine.execute(sql,(data['goods_id'],data['shop_id'])).fetchone()
        if row:
            result['quantity']=row['Quantity']
        result['shop_id']=data['shop_id']
        result['goods_id']=data['goods_id']
    except Exception,e:
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type="application/json")

@shop_goods_controller.route('/m1/public/get_shop_goods_for_discount')
def get_shop_goods_for_discount():
    result={'code':1,'msh':'ok'}
    try:
        data=request.get_json()
        sql='''SELECT
            tgs.GoodsID,
            tgs.ShopID,
            tgs.GoodsName,
            IFNULL(tp.ThumbnailPath,'./Content/images/web/nowprinting2.jpg') AS ThumbnailPath,
            tgs.SalePrice,
            round(tgs.SalePrice * tgs.Discount, 2) AS DisPrice
            FROM
                tb_goodsinfo_s tgs
                LEFT JOIN tb_photo tp ON 
                    tgs.GoodsID = tp.LinkID
                    AND tp.IsVisable = '1'
                    AND tp.IsChecked = '1'
            WHERE
                tgs.ShopID = %s
                AND tgs.`Status` = %s
                AND tgs.Discount != %s
            ORDER BY tgs.Discount ASC
            LIMIT 16
        
        '''
        result_set=db.engine.execute(sql,(data['shop_id'],'0','1'))
        arr=[]
        for row in result_set:
            temp={}
            temp['goods_id']=row['GoodsID']
            temp['shop_id']=row['ShopID']
            temp['goods_name']=row['GoodsName']
            temp['thumbnail_path']=row['ThumbnailPath']
            temp['sale_price']=row['SalePrice']
            temp['dis_price']=row['DisPrice']
            arr.append(temp)
        result['discount_goods']=arr
    except Exception,e:
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
    