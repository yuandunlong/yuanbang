# -*- coding: utf-8 -*-
from flask import Blueprint,request,Response,json
from database.models import Constent,db,ShopInfo
from utils import row_map_converter
public_controller=Blueprint("public_controller",__name__)

def get_shop_by_id():
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        sql='''
         SELECT s.ShopName,s.ShopPhoto,s.ShopID,s.Email,s.ShopPhone,s.LinkMan,s.Mobile,
                s.ShopAddress,s.SEOTitle,s.SEOKeyWord,s.SEOContent,
            '''
        if xzb and yzb:
            sql=sql+'ROUND(SQRT(POW(%s - s.mktxzb, 2) + POW(%s- s.mktyzb, 2))/1000,2) AS Distance,'
        else:
            sql=sql+"'' AS Distance,"
        sql=sql+'''
                            IFNULL(v.VisitCount,0) AS VisitCount,
                            IFNULL(o.Quantity,0) AS SaleCount
                            FROM
                                    tb_shopinfo_s s
                                    LEFT JOIN (SELECT ShopID,sum(VisitCount) AS VisitCount FROM  tb_visitcount_s GROUP BY ShopID) v ON s.ShopID = v.ShopID
                                    LEFT JOIN (SELECT ShopID,COUNT(OrderNo) AS Quantity FROM tb_order_s GROUP BY ShopID) o ON s.ShopID = o.ShopID
                            WHERE
                                    s.IsChecked = '2' and s.ShopID=%s                     
        ''' 
        row=db.engine.execute(sql,(data['shop_id'])).fetchone()
        if row:
            result['shop_info']=row_map_converter(row)
        
    except Exception,e:
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        
def get_goods_by_id():
    
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        sql='''
        '''
        row=db.engine.execute(sql,(data['goods_id'])).fetchone()
        if row:
            result['goods']=row_map_converter(row)
        
    except Exception,e:
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        
#获取商铺类别
@public_controller.route('/m1/public/get_shop_types',methods=['GET'])
def get_shop_types():
    
    constents=Constent.query.filter_by(type_id='001').all()
    result={'code':1,'msg':''}
    
    try:
        shop_types=[]
        for constent in constents:
            shop_types.append({"item_id":constent.item_id,"item_name":constent.item_name})
        result['shop_types']=shop_types
    except Exception,e:
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type="application/json")
#按照页码获取商铺类别下的商铺
#@public_controller.route('/m1/public/get_shop_lists_by_page',methods=['POST'])
def get_shop_lists_by_page_bak():
    result={'code':1,'msg':''}
    try:
        query=request.get_json()
        page=query.get('page',1)
        page_size=query.get('count',20)
        shop_type=query.get('shop_type')
        order_by=query.get('order_by')
        if page<1:
            page=1
        if page_size<1:
            page_size=20
        #result_set=ShopInfo.query.outerjoin(Constent,ShopInfo.is_top==Constent.item_id).filter(Constent.type_id=='002').outerjoin(Constent,ShopInfo.status==Constent.item_id).filter(Constent.type_id=='003').all()
        shops=[] 
        sql='''
        select * from tb_shopinfo_s
        
        '''
        
        shop_infos=ShopInfo.query.filter_by(shop_type=shop_type,is_checked='2',status='0').offset(page-1).limit(page_size).all()
        for shop in shop_infos:
            shops.append(shop.get_map())

        result['shops']=shops
        result['page']=page
        result['count']=page_size
    except Exception ,e:
        result['msg']=e.message
        result['code']=0
    return Response(json.dumps(result),content_type="application/json")

#按照页码获取商铺类别下的商铺
@public_controller.route('/m1/public/get_shop_lists_by_page',methods=['POST'])
def get_shop_lists_by_page():
    result={'code':1,'msg':'ok'}
    try:
        query=request.get_json()
        page=query.get('page',1)
        page_size=query.get('count',20)
        shop_type=query.get('shop_type')
        order_by=query.get('order_by')
        xzb=query.get('xzb')
        yzb=query.get('yzb')
        
        sql='''
        SELECT s.ShopName,s.ShopPhoto,s.ShopID,s.Email,s.ShopPhone,s.LinkMan,s.Mobile,
        s.ShopAddress,s.SEOTitle,s.SEOKeyWord,s.SEOContent,
        '''
        if xzb and yzb:
            sql=sql+'ROUND(SQRT(POW(%s - s.mktxzb, 2) + POW(%s- s.mktyzb, 2))/1000,2) AS Distance,'
        else:
            sql=sql+"'' AS Distance,"
        sql=sql+'''
                            IFNULL(v.VisitCount,0) AS VisitCount,
                            IFNULL(o.Quantity,0) AS SaleCount
                            FROM
                                    tb_shopinfo_s s
                                    LEFT JOIN (SELECT ShopID,sum(VisitCount) AS VisitCount FROM  tb_visitcount_s GROUP BY ShopID) v ON s.ShopID = v.ShopID
                                    LEFT JOIN (SELECT ShopID,COUNT(OrderNo) AS Quantity FROM tb_order_s GROUP BY ShopID) o ON s.ShopID = o.ShopID
                            WHERE
                                    s.IsChecked = '2'
                            AND	(s.xzb is not null or s.xzb <> '')
                            AND (s.yzb is not null or s.yzb <> '')
                            AND s.ShopType LIKE %s 
    
        '''
        
        if "saleasc"==order_by:
            sql=sql+'order by SaleCount asc'
        elif "saledesc"==order_by:
            sql=sql+'order by SaleCount desc'
        elif 'visitasc'==order_by:
            sql=sql+'order by VisitCount asc'
        elif 'visitdesc'==order_by:
            sql=sql+'order by VisitCount desc'
        elif 'distanceasc'==order_by:
            sql=sql+'order by Distance asc'
        elif 'distancedesc'==order_by:
            sql=sql+'order by Distance desc'
        else:
            sql=sql+'order by SaleCount desc'
        
        sql=sql+' limit %s,%s'
        if xzb and yzb:
            result_set=db.engine.execute(sql,(xzb,yzb,'%'+shop_type+'%',page-1,page_size))
        else:
            result_set=db.engine.execute(sql,('%'+shop_type+'%',page-1,page_size))
        arr=[]
        for row in result_set:
            temp=row_map_converter(row)
            arr.append(temp)
        count_sql='''
        select count(*) as total from tb_shopinfo_s s
                                 LEFT JOIN (SELECT ShopID,sum(VisitCount) AS VisitCount FROM  tb_visitcount_s GROUP BY ShopID) v ON s.ShopID = v.ShopID
					LEFT JOIN (SELECT ShopID,COUNT(OrderNo) AS Quantity FROM tb_order_s GROUP BY ShopID) o ON s.ShopID = o.ShopID
				WHERE
					s.IsChecked = '2'
				AND	(s.xzb is not null or s.xzb <> '')
				AND (s.yzb is not null or s.yzb <> '')
				AND s.ShopType LIKE %s
        '''
        row=db.engine.execute(count_sql,('%'+shop_type+'%')).fetchone()
        if row:
            result['total_count']=row['total']
        
        result['shops']=arr
        result['page']=page
        result['count']=page_size
        result['order_by']=order_by
    except Exception ,e:
        result['msg']=e.message
        result['code']=0
    return  Response(json.dumps(result),content_type="application/json")
    
    
    
@public_controller.route('/m1/public/search_shops_by_page',methods=['POST'])
def search_shops_by_page():
    result={'code':1,'msg':''}
    try:
        query=request.get_json()
        page=query.get('page',1)
        page_size=query.get('count',10)
        shop_type=query.get('shop_type')
        key_words=query.get('key_words')
        if page<1:
            page=1
        if page_size<1:
            page_size=20
        shops=[]    
        if shop_type:
            shop_infos=ShopInfo.query.filter_by(shop_type=shop_type,is_checked='2',status='0').filter(ShopInfo.shop_name.like('%'+key_words+'%')).offset(page-1).limit(page_size).all()
        else:
            shop_infos=ShopInfo.query.filter_by(is_checked='2',status='0').filter(ShopInfo.shop_name.like('%'+key_words+'%')).offset(page-1).limit(page_size).all()
        for shop in shop_infos:
            shops.append(shop.get_map())
    
        result['shops']=shops
        result['page']=page
        result['count']=page_size   
    except Exception,e:
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type="application/json")
        
@public_controller.route('/m1/public/get_most_sale_goods',methods=['GET','POST'])      
def get_most_sale_goods():
    result={'code':1,'msg':'ok'}
    try:
        sql='''
       SELECT g.GoodsID,g.GoodsName,g.SalePrice,g.Discount,
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
            order by TotalSale  desc limit 10
        '''
        result_set=db.engine.execute(sql)
        arr=[]
        for row in result_set:
            temp=row_map_converter(row)
            arr.append(temp)
        result['goods_infos']=arr
    except Exception,e:
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
@public_controller.route('/m1/public/get_most_discount_goods',methods=['GET','POST'])            
def get_most_discount_goods():
    result={'code':1,'msg':'ok'}
    try:
        sql='''
           SELECT g.GoodsID,g.GoodsName,g.SalePrice,g.Discount,
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
                order by Discount  desc limit 10
            '''        
        result_set=db.engine.execute(sql)
        arr=[]
        for row in result_set:
            temp=row_map_converter(row)
            arr.append(temp)
        result['goods_infos']=arr        
    except Exception,e:
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
@public_controller.route('/m1/public/seach_goods_by_page',methods=['POST'])       
def seach_goods_by_page():
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        page=data.get('page',1)
        page_size=data.get('page_size',20)
        sql='''
               SELECT g.GoodsID,g.GoodsName,g.SalePrice,g.Discount,
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
                    
                    and GoodsName like %s limit %s,%s
                '''    
        result_set=db.engine.execute(sql,('%'+data['key_words']+'%',page-1,page_size))
        arr=[]
        for row in result_set:
            temp=row_map_converter(row)
            arr.append(temp)
        result['goods_infos']=arr
        result['page']=page
        result['page_size']=page_size
        
        count_sql='''
         SELECT count(*) as total_count
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
                    
                    and GoodsName like %s 
        '''
        row=db.engine.execute(count_sql,('%'+data['keyword']+'%')).fetchone()
        if row:
            result['total_count']=row['total_count']
    except Exception,e:
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        
    