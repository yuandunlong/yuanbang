# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request
from flask import json,jsonify,Response
from database.models import Comment
from views.utils import result_set_converter
comment_controller=Blueprint('comment_controller',__name__)
@comment_controller.route('/m1/public/get_shop_goods_comment',methods=['POST'])
def get_shop_goods_commnet():
    result={'code':1,'msg':'ok'}
    try:
        data=request.get_json()
        page=data.get('page',1)
        count=data.get('count',20)
        comments=Comment.query.filter_by(shop_id=data['shop_id'],goods_id=data['goods_id']).offset(page).limit(count).all()
        result['comments']=result_set_converter(comments)
    except Exception,e:
        result['code']=0
        result['msg']=e.message
    return Response(json.dumps(result),content_type='application/json')
        
    