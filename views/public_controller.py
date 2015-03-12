# -*- coding: utf-8 -*-
from flask import Blueprint,request,Response,json
from database.models import Constent,db,ShopInfo
public_controller=Blueprint("public_controller",__name__)
#获取商铺类别
@public_controller.route('/m1/public/get_shop_types',methods=['GET'])
def get_shop_types():
    
    constents=Constent.query.filter_by(type_id='001').all()
    result={'code':0,'msg':''}
    
    try:
        shop_types=[]
        for constent in constents:
            shop_types.append({"item_id":constent.item_id,"item_name":constent.item_name})
        result['shop_types']=shop_types
        result['code']=1
    except Exception,e:
        result['msg']=e.message
    return Response(json.dumps(result))
#按照页码获取商铺类别下的商铺
@public_controller.route('/m1/public/get_shop_lists_by_page',methods=['POST'])
def get_shop_lists_by_page():
    result={'code':0,'msg':''}
    try:
        query=request.get_json()
        page=query.get('page',1)
        page_size=query.get('count',10)
        shop_type=query.get('shop_type')
        if page<1:
            page=1
        if page_size<1:
            page_size=20
        #result_set=ShopInfo.query.outerjoin(Constent,ShopInfo.is_top==Constent.item_id).filter(Constent.type_id=='002').outerjoin(Constent,ShopInfo.status==Constent.item_id).filter(Constent.type_id=='003').all()
        shops=[]        
        shop_infos=ShopInfo.query.filter_by(shop_type=shop_type).offset(page).limit(page_size).all()
        for shop in shop_infos:
            shops.append(shop.get_map())

        result['shops']=shops
        result['page']=page
        result['page_size']=page_size
    except Exception ,e:
        result['msg']=e.message
        raise e
    return Response(json.dumps(result))

def search_shops_by_page():
    result={'code':0,'msg':''}
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
        
    except Exception,e:
        result['mgs']=e.message
        shops=[]             
        shop_infos=ShopInfo.query.filter_by(shop_type=shop_type).filter().offset(page).limit(page_size).all()
        for shop in shop_infos:
            shops.append(shop.get_map())
    
        result['shops']=shops
        result['page']=page
        result['page_size']=page_size             
    return Response(json.dumps(result))
        
        
    
    
    
