# -*- coding: utf-8 -*-
from flask import Blueprint,current_app
from flask import request
from flask import json, jsonify, Response
from database.models import Comment, db,OrderDetail
from views.utils import row_map_converter,check_token
from datetime import datetime
comment_controller = Blueprint('comment_controller', __name__)

@comment_controller.route('/m1/public/get_shop_goods_comment', methods=['POST'])
def get_shop_goods_comment():
    result = {'code': 1, 'msg': 'ok'}
    try:
        data = request.get_json()
        page = data.get('page', 1)
        page_size = data.get('page_size', 20)

        comment_sql = '''
        select c.*,IFNULL(IF(b.NickName = '',NULL,b.NickName),b.Account) AS BuyerName from tb_comment c 
           left join tb_buyer b on c.BuyerID =b.BuyerID  where GoodsID=%s order by c.CommitTime DESC limit %s,%s;
        '''
        result_set = db.engine.execute(comment_sql, (data['goods_id'], (page - 1)*page_size, page_size))
        arr = []
        for row in result_set:
            temp = row_map_converter(row)
            arr.append(temp)

        result['comments'] = arr

        sql = '''
        select avg(Level) as avg_level from tb_comment where GoodsID=%s;
        '''
        row = db.engine.execute(sql, (data['goods_id'])).fetchone()
        if row:
            if row['avg_level']:
                result['avg_level'] = int(row['avg_level'])
        total_sql = '''
        select count(*) as total from tb_comment  where  GoodsID=%s
        '''
        totalrow = db.engine.execute(total_sql, (data['goods_id'])).fetchone()
        if totalrow:
            result['total'] = totalrow['total']
        result['page'] = page
        result['page_size'] = page_size
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = e.message
    return Response(json.dumps(result), content_type='application/json')


@comment_controller.route('/m1/public/get_shop_avg_level_comment', methods=['POST'])
def get_shop_avg_level_comment():
    result = {'code': 1, 'msg': 'ok'}
    avg_levle = 5
    try:
        data = request.get_json()
        sql = '''
            select avg(Level) as avg_level from tb_comment where ShopID=%s ;'''
        row = db.engine.execute(sql, (data['shop_id'])).fetchone()
        if row:
            if row['avg_level']:
                avg_levle = int(row['avg_level'])
        result['avg_level'] = avg_levle
    except Exception, e:
        current_app.logger.exception(e)
        result['code'] = 0
        result['msg'] = 'ok'
    return Response(json.dumps(result), content_type='application/json')

@comment_controller.route('/m1/private/submit_comment',methods=['POST'])      
@check_token
def submit_comment(token_type,user_info):
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        order_no=data['order_no']
        order_details=OrderDetail.query.filter_by(order_no=order_no)
        
        for order_detail in order_details:
            comment=Comment()
            comment.goods_id=order_detail.goods_id
            comment.shop_id=data['shop_id']
            comment.buyer_id=user_info.buyer_id
            comment.level=data['level']
            comment.content=data['content']
            comment.del_flag='0'
            comment.order_no=order_no
            comment.comment_type='1'
            comment.commit_time=datetime.now()
            comment.is_read='0'
            db.session.add(comment)
            db.session.commit()
    except Exception,e:
        current_app.logger.exception(e)
        result['code']=0
        result['msg']='ok'
    return Response(json.dumps(result),content_type="application/json")
        