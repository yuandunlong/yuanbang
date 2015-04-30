# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request
from flask import json,jsonify,Response
from database.models import Comment,db
from views.utils import row_map_converter
comment_controller=Blueprint('comment_controller',__name__)
@comment_controller.route('/m1/public/get_shop_goods_comment',methods=['POST'])
def get_shop_goods_comment():
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        page=data.get('page',1)
        page_size=data.get('page_size',20)
       
        comment_sql=''' 
        select c.*,IFNULL(IF(b.NickName = '',NULL,b.NickName),b.Account) AS BuyerName from tb_comment c 
           left join tb_buyer b on c.BuyerID =b.BuyerID  where GoodsID=%s order by c.CommitTime DESC limit %s,%s;
        '''
        result_set=db.engine.execute(comment_sql,(data['shop_id'],data['goods_id'],page-1,page_size))
        arr=[]
        for row in result_set:
            temp=row_map_converter(row)
            arr.append(temp)
            
        result['comments']=arr
        
        sql='''
        select avg(Level) as avg_level from tb_comment where GoodsID=%s;
        '''
        row=db.engine.execute(sql,(data['goods_id'])).fetchone()
        if row:
            if row['avg_level']:
                result['avg_level']=int(row['avg_level'])
        total_sql='''
        select count(*) as total from tb_comment  where ShopID=%s and GoodsID=%s
        '''
        totalrow=db.engine.execute(total_sql,(data['shop_id'],data['goods_id'])).fetchone()
        if totalrow:
            result['total']=totalrow['total']
        result['page']=page
        result['page_size']=page_size
    except Exception,e:
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        
@comment_controller.route('/m1/public/get_shop_goods_comment',methods=['POST'])
def get_shop_avg_level_comment():
    result={'code':1,'msg':'ok'}
    try:
        sql='''
            select avg(Level) as avg_level from tb_comment where ShopID=%s ;'''    
        if row:
            if row['avg_level']:
                result['avg_level']=int(row['avg_level'])        
    except Exception,e:
        result['code']=1
        result['msg']='ok'
    return Response(json.dumps(result),content_type='application/json')
        
    