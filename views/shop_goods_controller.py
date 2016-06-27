# -*- coding: utf-8 -*-
from flask import json,Response,Blueprint,request,current_app
from sqlalchemy import desc
from database.models import db,Photo
from utils import row_map_converter
shop_goods_controller=Blueprint('shop_goods_controller',__name__)
#取得店铺的商品关联图片信息（商品ID）
@shop_goods_controller.route('/m1/public/get_shop_goods_photos',methods=['POST'])
def get_shop_goods_photos():
    
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        photos=Photo.query.filter_by(link_id=data['goods_id'],is_checked='1').order_by(desc(Photo.is_visable),desc(Photo.sort_no)).all()
        arr=[]
        for photo in photos:
            arr.append(photo.get_map())
        result['photos']=arr
    except Exception ,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type="application/json")
        

@shop_goods_controller.route('/m1/public/get_shop_goods_detail',methods=['POST'])
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
        sql3='''
        select GoodsSpec,GoodsLocality,GoodsBrand from tb_goodsinfo_s where GoodsID=%s
        '''
        temp_row=db.engine.execute(sql3,data['goods_id']).fetchone()
        if temp_row:
            
            arr.insert(0,{'goods_id':data['goods_id'],'add_attr_name':'商品规格','add_attr_content':temp_row['GoodsSpec'],'goods_type_id':'0','add_attr_id':'0'})
            arr.insert(1,{'goods_id':data['goods_id'],'add_attr_name':'商品产地','add_attr_content':temp_row['GoodsLocality'],'goods_type_id':'0','add_attr_id':'0'})
            arr.insert(2,{'goods_id':data['goods_id'],'add_attr_name':'商品品牌','add_attr_content':temp_row['GoodsBrand'],'goods_type_id':'0','add_attr_id':'0'})
        result['goods_detail']=arr
    except Exception,e:
        current_app.logger.exception(e)
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
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type="application/json")

@shop_goods_controller.route('/m1/public/get_shop_goods_for_discount',methods=['POST'])
def get_shop_goods_for_discount():
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        sql='''SELECT
            tgs.GoodsID,
            tgs.ShopID,
            tgs.GoodsName,
            tgs.SetPrice,
            tgs.SetNum,
            IFNULL(tp.ThumbnailPath,'./Content/images/web/nowprinting2.jpg') AS ThumbnailPath,
            IFNULL(o.SaleQuantity,0) AS TotalSale,
            tgs.SalePrice,
            round(tgs.SalePrice * tgs.Discount, 2) AS DisPrice
            FROM
                tb_goodsinfo_s tgs
                
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
                   ) o ON tgs.GoodsID = o.GoodsID                
                
            LEFT JOIN tb_photo tp ON 
                    tgs.GoodsID = tp.LinkID
                    AND tp.IsVisable = '1'
                    AND tp.IsChecked = '1'
            WHERE
                tgs.ShopID = %s
                AND tgs.`Status` = %s
                AND tgs.Discount != %s
          
            
        
        '''
        
        order_by=data.get('order_by',None)
        
        if order_by=='saleasc':
            sql+='  order by TotalSale asc'
        elif order_by=='saledesc':
            sql+=' order by TotalSale desc'
        elif order_by=='priceasc':
            sql+=' order by SalePrice asc'
        elif order_by=='pricedesc':
            sql+=' order by SalePrice desc'   
        else:
            sql+=' order by SalePrice,TotalSale desc'        
        sql+= ' LIMIT 16'
        result_set=db.engine.execute(sql,(data['shop_id'],'0','1'))
        arr=[]
        for row in result_set:
            temp={}
            temp['goods_id']=row['GoodsID']
            temp['shop_id']=row['ShopID']
            temp['goods_name']=row['GoodsName']
            temp['thumbnail_path']=row['ThumbnailPath']
            temp['sale_price']=str(row['SalePrice'])
            temp['dis_price']=str(row['DisPrice'])
            arr.append(temp)
        result['discount_goods']=arr
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
@shop_goods_controller.route('/m1/public/get_goods_by_id',methods=['POST'])
def get_goods_by_id():
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        sql='''
            SELECT g.GoodsID,g.GoodsName,g.SalePrice,g.SetPrice,g.SetNum,
            round(g.SalePrice * g.Discount, 2) AS DisPrice,
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
            WHERE
            g.GoodsID = %s
            and g.Status = 0   '''     
    
        row=db.engine.execute(sql,(data['goods_id'])).fetchone()
        if row:
            result['goods_info']=row_map_converter(row)
            p_sql='''select quantity as remains from tb_purchase_s where GoodsID=%s order by BatchNo Desc'''
            _row=db.engine.execute(p_sql,(data['goods_id'])).fetchone()
            
            if _row:
                result['goods_info']['remains']=int(_row['remains'])
            else :
                result['goods_info']['remains']=0
            
    except Exception, e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
@shop_goods_controller.route('/m1/public/get_shop_goods_by_type',methods=['POST'])
def get_shop_goods_by_type():
    result={'code':1,'msg':'ok'}
    
    try:
        data=request.get_json()
        sql='''
        SELECT g.GoodsID,g.GoodsName,g.SalePrice,g.SetPrice,g.SetNum,
    round(g.SalePrice * g.Discount, 2) AS DisPrice,
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
        LEFT JOIN tb_photo p ON g.GoodsID = p.LinkID
        AND p.IsVisable = '1'
        AND p.IsChecked = '1'
        WHERE
                g.ShopID = %s
        and g.Status = 0
        and (g.GoodsTypeIDs like %s or g.GoodsTypeIDs like %s)

        GROUP BY g.GoodsID 
        
        '''
        
        order_by=data.get('order_by',None)
        
        if order_by=='saleasc':
            sql+='  order by TotalSale asc'
        elif order_by=='saledesc':
            sql+=' order by TotalSale desc'
        elif order_by=='priceasc':
            sql+=' order by SalePrice asc'
        elif order_by=='pricedesc':
            sql+=' order by SalePrice desc'
        else:
            sql+=' order by SalePrice,TotalSale desc'        
        shop_id=str(data['shop_id'])
        if data.get('goods_type_id'):
            goods_type_id=str(data['goods_type_id'])
            result_set=db.engine.execute(sql,(shop_id,goods_type_id+'%','%'+goods_type_id+'%'))
        else:
            another_sql='''
            
            SELECT g.GoodsID,g.GoodsName,g.SalePrice,
        round(g.SalePrice * g.Discount, 2) AS DisPrice,
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
            WHERE
                g.ShopID = %s
            and g.Status = 0
            '''
            order_by=data.get('order_by','saledesc')
            
            if order_by=='saleasc':
                sql+='  order by TotalSale asc'
            elif order_by=='saledesc':
                sql+=' order by TotalSale desc'
            elif order_by=='priceasc':
                sql+=' order by SalePrice asc'
            elif order_by=='pricedesc':
                sql+=' order by SalePrice desc'   
                
            result_set=db.engine.execute(another_sql,(shop_id))
        arr=[]
        for row in result_set:
            temp=row_map_converter(row)
            arr.append(temp)
        result['goods']=arr
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')

@shop_goods_controller.route('/m1/public/get_latest_shop_goods',methods=['POST'])
def get_latest_shop_goods():
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        sql='''
        SELECT g.GoodsID,g.GoodsName,g.SalePrice,g.SetPrice,g.SetNum,
    round(g.SalePrice * g.Discount, 2) AS DisPrice,
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
        WHERE
            g.ShopID = %s
        and g.Status = 0  
        '''
        order_by=data.get('order_by',None)
        if order_by=='saleasc':
            sql+='  order by TotalSale asc'
        elif order_by=='saledesc':
            sql+=' order by TotalSale desc'
        elif order_by=='priceasc':
            sql+=' order by SalePrice asc'
        elif order_by=='pricedesc':
            sql+=' order by SalePrice desc' 
        else:
            sql+=' order by SalePrice,TotalSale desc'
        sql+=' limit %s'
        shop_id=str(data['shop_id'])
        count=data.get('count',4)
        result_set=db.engine.execute(sql,(shop_id,count))
        arr=[]
        for row in result_set:
            temp=row_map_converter(row)
            arr.append(temp)
        result['goods']=arr        
    
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')