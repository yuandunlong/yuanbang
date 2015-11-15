# -*- coding: utf-8 -*-
from flask import Blueprint,request,Response,json,current_app
from database.models import Constent,db,ShopInfo,BuyerAddress,Activity
from utils import row_map_converter,result_set_converter,jw_2_mkt
public_controller=Blueprint("public_controller",__name__)

@public_controller.route('/m1/public/get_shop_by_id',methods=['POST'])
def get_shop_by_id():
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        mktxzb=data.get('mktxzb',None)
        mktyzb=data.get('mktyzb',None)
        sql='''
         SELECT s.ShopName,s.ShopPhoto,s.ShopID,s.Email,s.ShopPhone,s.LinkMan,s.Mobile,
                s.ShopAddress,s.SEOTitle,s.SEOKeyWord,s.SEOContent,s.mktxzb,s.mktyzb,s.xzb,s.yzb,
            '''
        if mktxzb and mktyzb:
            sql=sql+'ROUND(SQRT(POW(%s - s.mktxzb, 2) + POW(%s- s.mktyzb, 2))/1000,2) AS Distance,'
        else:
            sql=sql+" '' AS Distance,"
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
        
        if mktxzb and mktyzb:
            row=db.engine.execute(sql,(mktxzb,mktyzb,data['shop_id'])).fetchone()
        else:   
            row=db.engine.execute(sql,(data['shop_id'])).fetchone()
        if row:
            result['shop_info']=row_map_converter(row)
            activities=Activity.query.filter_by(shop_id=data['shop_id'])
            result['shop_info']['activities']=result_set_converter(activities)
        
    except Exception,e:
        current_app.logger.exception(e)
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
        current_app.logger.exception(e)
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
        current_app.logger.exception(e)
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
        current_app.logger.exception(e)
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
        mktxzb=query.get('mktxzb')
        mktyzb=query.get('mktyzb')
        
        sql='''
        SELECT s.ShopName,s.ShopPhoto,s.ShopID,s.Email,s.ShopPhone,s.LinkMan,s.Mobile,
        s.ShopAddress,s.SEOTitle,s.SEOKeyWord,s.SEOContent,s.mktxzb,s.mktyzb,s.xzb,s.yzb,
        '''
        if mktxzb and mktxzb:
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
                                    s.IsChecked = '2' and s.Status='0'
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
        if mktxzb and mktyzb:
            result_set=db.engine.execute(sql,(mktxzb,mktyzb,'%'+shop_type+'%',(page-1)*page_size,page_size))
        else:
            result_set=db.engine.execute(sql,('%'+shop_type+'%',(page-1)*page_size,page_size))
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
        current_app.logger.exception(e)
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
            shop_infos=ShopInfo.query.filter_by(shop_type=shop_type,is_checked='2',status='0').filter(ShopInfo.shop_name.like('%'+key_words+'%')).offset((page-1)*page_size).limit(page_size).all()
        else:
            shop_infos=ShopInfo.query.filter_by(is_checked='2',status='0').filter(ShopInfo.shop_name.like('%'+key_words+'%')).offset((page-1)*page_size).limit(page_size).all()
        for shop in shop_infos:
            shops.append(shop.get_map())
    
        result['shops']=shops
        result['page']=page
        result['count']=page_size   
    except Exception,e:
        current_app.logger.exception(e)
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
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
@public_controller.route('/m1/public/get_home_page_shop_goods',methods=['POST'])
def get_home_page_shop_goods():
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        buyer_id=data.get('buyer_id')
        page_size=int(data.get('page_size',10))
        page=int(data.get('page',1))
        shop_goods_num=int(data.get('shop_goods_num',10))
        mktxzb=None
        mktyzb=None
        if data.get('mktxzb') and data.get('mktyzb'):
            mktxzb=data['mktxzb']
            mktyzb=data['mktyzb']
        elif buyer_id:
            buyer_address=BuyerAddress.query.filter_by(buyer_id=buyer_id,is_default='1').first()
            if buyer_address:
                mktxzb=buyer_address.mktxzb
                mktyzb=buyer_address.mktyzb
        if mktxzb and mktyzb:
            sql='''
            
              select shop.*,ROUND(SQRT(POW(%s - shop.mktxzb, 2) + POW(%s- shop.mktyzb, 2))/1000,2) AS Distance from tb_shopinfo_s shop where ShopID <>1 order by Distance limit %s,%s
            '''
            shops=db.engine.execute(sql,(mktxzb,mktyzb,(page-1)*page_size,page_size))
        else:
            sql='''
            select shop.* from tb_shopinfo_s shop where ShopID<>1 order by ShopID asc limit %s,%s
    
            '''
            shops=db.engine.execute(sql,((page-1)*page_size,page_size))
        shop_arr=[]
        for shop in shops:
            shop_temp=row_map_converter(shop)
            
            temp_sql='''
        SELECT g.GoodsID,g.GoodsName,g.SalePrice,g.Discount,g.SetPrice,g.SetNum,
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
        
        where ShopID=%s and g.Status=0
        order by Discount  asc limit %s
            
            '''
            goods=db.engine.execute(temp_sql,(shop_temp['shop_id'],shop_goods_num))
            goods_arr=[]
            for good in goods:
                good_temp=row_map_converter(good)
                goods_arr.append(good_temp)
            shop_temp['most_discount_goods']=goods_arr
            
            shop_arr.append(shop_temp)
        result['shopinfos']=shop_arr
            
        result['page_size']=page_size
        result['page']=page
    except Exception,e:
        current_app.logger.exception(e)
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
                order by Discount  asc limit 10
            '''        
        result_set=db.engine.execute(sql)
        arr=[]
        for row in result_set:
            temp=row_map_converter(row)
            arr.append(temp)
        result['goods_infos']=arr        
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')

@public_controller.route('/m1/public/search_goods_by_page',methods=['POST'])       
def search_goods_by_page():
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        page=data.get('page',1)
        page_size=data.get('page_size',20)
        order_by=data.get('order_by')
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
        result_set=db.engine.execute(sql,('%'+data['key_words']+'%',(page-1)*page_size,page_size))
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
        row=db.engine.execute(count_sql,('%'+data['key_words']+'%')).fetchone()
        if row:
            result['total_count']=row['total_count']
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
@public_controller.route('/m1/public/search_goods_by_bar_code',methods=['POST'])       
def search_goods_by_bar_code():
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
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

    and BarCode = %s 
        '''
        row=db.engine.execute(sql,(data['bar_code'])).fetchone()
        if row:
            data['key_words']=row['GoodsName']
            result=search_goods_by_page_ex_(data)
            result['keyword']=row['GoodsName']
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')

@public_controller.route('/m1/public/search_goods_in_shop_by_page',methods=['POST'])       
def search_goods_in_shop_by_page():
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        mktxzb=data.get('mktxzb',None)
        mktyzb=data.get('mktyzb',None)
        page=data.get('page',1)
        page_size=data.get('page_size',10)
        order_by=data.get('order_by','')
        sql='''
        SELECT g.ShopID,g.GoodsID,g.GoodsName,g.SalePrice,round(g.SalePrice * g.Discount, 2) AS DisPrice,g.SetPrice,g.SetNum,
        p.ThumbnailPath,
        IFNULL(o.Quantity, 0) AS Quantity,
        s.ShopName,s.mktxzb,s.mktyzb,s.xzb,s.yzb,
        '''
        if  mktxzb and  mktyzb:
            sql+='ROUND(SQRT(POW(%s - s.mktxzb, 2) + POW(%s- s.mktyzb, 2))/1000,2) AS Distance '

        else:
            sql+=''' 0 as Distance '''


        sql+='''
        FROM TB_GOODSINFO_S g
        INNER JOIN tb_shopinfo_s s ON s.ShopID = g.ShopID
        AND s.IsChecked = '2'
        AND (
            s.ShopType IS NOT NULL
            OR s.ShopType <> ''
        )
        AND (s.xzb IS NOT NULL OR s.xzb <> '')
        AND (s.yzb IS NOT NULL OR s.yzb <> '')

        LEFT JOIN (
                SELECT
                sum(t.Quantity) AS Quantity,
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
                INNER JOIN TB_PHOTO p ON g.GoodsID = p.LinkID
                AND p.IsVisable = '1'
                AND p.IsChecked = '1'
                LEFT JOIN TB_GOODSTYPE_M m on m.GoodsTypeID = g.GoodsTypeID
                WHERE g.Status = 0
                AND	(g.GoodsName LIKE %s
                OR  g.GoodsLocality LIKE %s
                OR  g.GoodsBrand LIKE %s
                OR  g.GoodsSpec LIKE %s
                OR  m.GoodsTypeName LIKE %s
                OR  g.Remark LIKE %s) and g.ShopID=%s

        '''

        if order_by=='saleasc':
            sql+='ORDER BY IFNULL(o.Quantity,0) asc'
        elif order_by=='saledesc':
            sql+='ORDER BY IFNULL(o.Quantity,0) desc '
        elif order_by=='distancedesc':
            sql+='ORDER BY Distance desc '
        elif order_by=='distanceasc':
            sql+='ORDER BY Distance asc'
        elif order_by=='pricedesc':
            sql+='ORDER BY round(g.SalePrice * g.Discount, 2) desc '
        elif order_by=='priceasc':
            sql+='ORDER BY round(g.SalePrice * g.Discount, 2) asc'
        else:
            sql+='ORDER BY Distance asc'

        sql+=' limit %s,%s'

        search_words='%'+data['key_words']+'%'

        if  mktxzb and mktyzb:
            result_set=db.engine.execute(sql,( mktxzb,mktyzb,search_words,search_words,search_words,search_words,search_words,search_words,data['shop_id'],(page-1)*page_size,page_size))

        else:
            result_set=db.engine.execute(sql,(search_words,search_words,search_words,search_words,search_words,search_words,data['shop_id'],(page-1)*page_size,page_size))


        goods=[]   
        for row in result_set:
            temp=row_map_converter(row)
            goods.append(temp)
        result['goods']=goods
        result['page']=page
        result['page_size']=page_size
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')    
    

@public_controller.route('/m1/public/search_goods_by_page_ex',methods=['POST'])
def search_goods_by_page_ex():
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        mktxzb=data.get('mktxzb',None)
        mktyzb=data.get('mktyzb',None)
        page=data.get('page',1)
        page_size=data.get('page_size',10)
        order_by=data.get('order_by','')
        sql='''
        SELECT g.ShopID,g.GoodsID,g.GoodsName,g.SetPrice,g.SetNum, g.SalePrice,round(g.SalePrice * g.Discount, 2) AS DisPrice,
        p.ThumbnailPath,
        IFNULL(o.Quantity, 0) AS Quantity,
        s.ShopName,s.ShopPhoto,s.mktxzb,s.mktyzb,s.xzb,s.yzb,
        '''
        if  mktxzb and  mktyzb:
            sql+='ROUND(SQRT(POW(%s - s.mktxzb, 2) + POW(%s- s.mktyzb, 2))/1000,2) AS Distance '
            
        else:
            sql+=''' 0 as Distance '''
            
            
        sql+='''
        FROM TB_GOODSINFO_S g
        INNER JOIN tb_shopinfo_s s ON s.ShopID = g.ShopID
        AND s.IsChecked = '2' and s.Status='0'
        AND (
            s.ShopType IS NOT NULL
            OR s.ShopType <> ''
        )
        AND (s.xzb IS NOT NULL OR s.xzb <> '')
        AND (s.yzb IS NOT NULL OR s.yzb <> '')
        
        LEFT JOIN (
                SELECT
                sum(t.Quantity) AS Quantity,
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
                INNER JOIN TB_PHOTO p ON g.GoodsID = p.LinkID
                AND p.IsVisable = '1'
                AND p.IsChecked = '1'
                LEFT JOIN TB_GOODSTYPE_M m on m.GoodsTypeID = g.GoodsTypeID
                WHERE g.Status = 0
                AND	(g.GoodsName LIKE %s
                OR  g.GoodsLocality LIKE %s
                OR  g.GoodsBrand LIKE %s
                OR  g.GoodsSpec LIKE %s
                OR  m.GoodsTypeName LIKE %s
                OR  g.Remark LIKE %s)
        
        '''
        
        if order_by=='saleasc':
            sql+='ORDER BY IFNULL(o.Quantity,0) asc'
        elif order_by=='saledesc':
            sql+='ORDER BY IFNULL(o.Quantity,0) desc '
        elif order_by=='distancedesc':
            sql+='ORDER BY Distance desc '
        elif order_by=='distanceasc':
            sql+='ORDER BY Distance asc'
        elif order_by=='pricedesc':
            sql+='ORDER BY round(g.SalePrice * g.Discount, 2) desc '
        elif order_by=='priceasc':
            sql+='ORDER BY round(g.SalePrice * g.Discount, 2) asc'
        else:
            sql+='ORDER BY Distance asc'
        
        sql+=' limit %s,%s'
        
        search_words='%'+data['key_words']+'%'
        
        if  mktxzb and mktyzb:
            result_set=db.engine.execute(sql,(mktxzb,mktyzb,search_words,search_words,search_words,search_words,search_words,search_words,(page-1)*page_size,page_size))
            
        else:
            result_set=db.engine.execute(sql,(search_words,search_words,search_words,search_words,search_words,search_words,(page-1)*page_size,page_size))
            
            
        goods=[]   
        for row in result_set:
            temp=row_map_converter(row)
            goods.append(temp)
        result['goods']=goods
        result['page']=page
        result['page_size']=page_size
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        
        
def search_goods_by_page_ex_(data):
    result={'code':1,'msg':'ok'}
    try:
        
        mktxzb=data.get('mktxzb',None)
        mktyzb=data.get('mktyzb',None)
        page=data.get('page',1)
        page_size=data.get('page_size',10)
        order_by=data.get('order_by','')
        sql='''
        SELECT g.ShopID,g.GoodsID,g.GoodsName,g.SalePrice,round(g.SalePrice * g.Discount, 2) AS DisPrice,
        p.ThumbnailPath,
        IFNULL(o.Quantity, 0) AS Quantity,
        s.ShopName,s.ShopPhoto,s.mktxzb,s.mktyzb,s.xzb,s.yzb,
        '''
        if  mktxzb and  mktyzb:
            sql+='ROUND(SQRT(POW(%s - s.mktxzb, 2) + POW(%s- s.mktyzb, 2))/1000,2) AS Distance '

        else:
            sql+=''' 0 as Distance '''


        sql+='''
        FROM TB_GOODSINFO_S g
        INNER JOIN tb_shopinfo_s s ON s.ShopID = g.ShopID
        AND s.IsChecked = '2' and s.Status='0'
        AND (
            s.ShopType IS NOT NULL
            OR s.ShopType <> ''
        )
        AND (s.xzb IS NOT NULL OR s.xzb <> '')
        AND (s.yzb IS NOT NULL OR s.yzb <> '')

        LEFT JOIN (
                SELECT
                sum(t.Quantity) AS Quantity,
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
                INNER JOIN TB_PHOTO p ON g.GoodsID = p.LinkID
                AND p.IsVisable = '1'
                AND p.IsChecked = '1'
                LEFT JOIN TB_GOODSTYPE_M m on m.GoodsTypeID = g.GoodsTypeID
                WHERE g.Status = 0
                AND	(g.GoodsName LIKE %s
                OR  g.GoodsLocality LIKE %s
                OR  g.GoodsBrand LIKE %s
                OR  g.GoodsSpec LIKE %s
                OR  m.GoodsTypeName LIKE %s
                OR  g.Remark LIKE %s)

        '''

        if order_by=='saleasc':
            sql+='ORDER BY IFNULL(o.Quantity,0) asc'
        elif order_by=='saledesc':
            sql+='ORDER BY IFNULL(o.Quantity,0) desc '
        elif order_by=='distancedesc':
            sql+='ORDER BY Distance desc '
        elif order_by=='distanceasc':
            sql+='ORDER BY Distance asc'
        elif order_by=='pricedesc':
            sql+='ORDER BY round(g.SalePrice * g.Discount, 2) desc '
        elif order_by=='priceasc':
            sql+='ORDER BY round(g.SalePrice * g.Discount, 2) asc'
        else:
            sql+='ORDER BY Distance asc'

        sql+=' limit %s,%s'

        search_words='%'+data['key_words']+'%'

        if  mktxzb and mktyzb:
            result_set=db.engine.execute(sql,(mktxzb,mktyzb,search_words,search_words,search_words,search_words,search_words,search_words,(page-1)*page_size,page_size))

        else:
            result_set=db.engine.execute(sql,(search_words,search_words,search_words,search_words,search_words,search_words,(page-1)*page_size,page_size))


        goods=[]   
        for row in result_set:
            temp=row_map_converter(row)
            goods.append(temp)
        result['goods']=goods
        result['page']=page
        result['page_size']=page_size
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return result
        
@public_controller.route('/m1/public/get_activities_by_shop_id',methods=['POST'])        
def get_activities_by_shop_id():
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        activities=Activity.query.filter_by(shop_id=data['shop_id'])
        result['activities']=result_set_converter(activities)
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        
        
@public_controller.route('/m1/public/get_recommend_shop_for_home_page')      
def get_recommend_shop_for_home_page():
    
    result={'code':1,'msg':'ok'}
    
    try:
        sql='''
        select * from tb_shopinfo_s where ShopName like %s and  ShopID <>1
        '''
        result_set=db.engine.execute(sql,('%远邦%'))
        arr=[]
        for row in result_set:
            temp=row_map_converter(row)
            arr.append(temp)
        result['recommend_shops']=arr
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message        
    return Response(json.dumps(result),content_type='application/json')
        
        
    