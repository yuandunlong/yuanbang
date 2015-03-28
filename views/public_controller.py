# -*- coding: utf-8 -*-
from flask import Blueprint,request,Response,json
from database.models import Constent,db,ShopInfo
public_controller=Blueprint("public_controller",__name__)
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
@public_controller.route('/m1/public/get_shop_lists_by_page',methods=['POST'])
def get_shop_lists_by_page():
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
@public_controller.route('/m1/public/search_shops_by_page',methods=['POST'])
def search_shops_by_page():
    result={'code':1,'msg':''}
    try:
        query=request.get_json()
        page=query.get('page',1)
        page_size=query.get('count',10)
        shop_type=query.get('shop_type')
        key_words=query.get('key_words')
        print key_words,type(key_words)
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
        
        
    
    
    
