# -*- coding: utf-8 -*-
from flask import Blueprint,current_app
from flask import request
from flask import json,Response
from database.models import db

shop_goods_type_controller=Blueprint('shop_goods_type_controller',__name__)
@shop_goods_type_controller.route('/m1/public/get_shop_goods_type_parent',methods=['POST'])
def get_shop_goods_type_parent():
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        shop_id=data['shop_id']
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
        result_set=db.engine.execute(sql,(shop_id))
        arr=[]
        for row in result_set:
            temp={}
            temp['shop_id']=int(row['ShopID'])
            temp['goods_type_id']=int(row['GoodsTypeID'])
            temp['goods_type_name']=row['GoodsTypeName']
            temp['parent_id']=row['ParentID']
            temp['sort_no']=row['SortNo']
            arr.append(temp)
        result['shop_goods_type_parent']=arr
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type="application/json")

@shop_goods_type_controller.route('/m1/public/get_shop_goods_type_child',methods=['POST'])
def get_shop_goods_type_child():
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        shop_id=data['shop_id']
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
        
        result_set=db.engine.execute(sql,(shop_id,parent_id))
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
    return Response(json.dumps(result),content_type="application/json")
        
        
        
        
    