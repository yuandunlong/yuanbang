# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request
from flask import json,Response
import datetime
import random
import string
import hashlib
from database.models import db,Buyer,ShopInfo,Token

token_controller=Blueprint("token_controller",__name__)
@token_controller.route('/m1/authorize',methods=['GET', 'POST'])
def authorize():
	result={'code':0,'msg':''}
	try:
		post_json=request.get_json()
		if post_json:
			client_id=post_json['client_id']
			auth_code = map(lambda i: chr(random.randint(65,90)),range(32))
			result['auth_code']=string.join(auth_code,'')
			result['code']=1
	except Exception, e:
		result['msg']=e.message

	return Response(json.dumps(result))
@token_controller.route('/m1/access_token',methods=['POST'])
def access_token():
	result={'code':0,'msg':''}
	try:
		
		post_json=request.get_json()
		account=post_json['account']
		auth_code=post_json['auth_code']
		client_id=post_json['client_id']
		pass_code=post_json['pass_code']
		account_type=post_json['account_type']
		md5=hashlib.md5()
		#1普通用户
		if account_type==1:
			buyer=Buyer.query.filter_by(account=account).first()
			if buyer==None:
				result['msg']='account dont exist'
			else:	
				md5.update(buyer.password+auth_code)
				check_code=md5.hexdigest()

				if pass_code==check_code:
					access_token=map(lambda i: chr(random.randint(65,90)),range(32))
					access_token=string.join(access_token,'')
					token=Token(buyer.buyer_id,account_type,auth_code,client_id,access_token)
					Token.query.delete()
					db.session.add(token)
					db.session.commit()
					result['access_token']=access_token
					result['code']=1
				else:
					result['msg']='account or password wrong'
					result['code']=0
		#2 商家
		elif account_type==2:
			shop_info=ShopInfo.query.filter_by(account=account).first()
			if shop_info==None:
				result['msg']='account dont exist'
			else:
				md5.update(shop_info.password+auth_code)
				check_code=md5.hexdigest()
				
				if pass_code==check_code:
					access_token=map(lambda i: chr(random.randint(65,90)),range(32))
					access_token=string.join(token,'')
					token=Token(shop_info.shop_id,account_type,auth_code,client_id,access_token)
					db.session.add(token)
					db.session.commit()					
					result['access_token']=access_token
					result['code']=1
				else:
					result['code']=0

	except KeyError,key_error:
		result['msg']='not enpha params'
	except Exception, e:
		result['msg']=e.message 
	return Response(json.dumps(result),mimetype='application/json')
@token_controller.route('/m1/refresh_token',methods=['POST'])
def refresh_token():
	result={'code':0,'msg':''}
	try:
		post_json=request.get_json()
		access_token=post_json['access_token']
		token=Token.query.filter_by(access_token=access_token).first()
		if token:
			access_token=map(lambda i: chr(random.randint(65,90)),range(32))
			access_token=string.join(access_token,'')
			token.access_token=access_token
			db.session.commit()
			result['access_token']=access_token
			result['code']=1
		else:
			result['msg']='invalid access_token '+post_json['access_token']
		
	except Exception ,e:
		result['msg']=e.message
		
	return Response(json.dumps(result))
		
		

	
	