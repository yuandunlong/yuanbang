# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import request
from flask import json
import datetime
import random
import string
from database.models import User,db
token_controller=Blueprint("token_controller",__name__)
@token_controller.route('/m1/authorize',methods=['GET', 'POST'])
def authorize():
	result={'code':0,'msg':''}
	try:
		json_data=request.form.get('request')
		if json_data:
			post_json=json.loads(json_data)
			client_id=post_json['client_id']
			auth_code = map(lambda i: chr(random.randint(65,90)),range(32))
			result['auth_code']=string.join(auth_code,'')
			result['code']=1
	except Exception, e:
		result['msg']=e.message
		raise e

	return json.dumps(result,ensure_ascii=False)

def access_token():
	result={'code':0,'msg':''}
	try:
		json_data=request.form['request']
		post_json=json.loads(json_data)
		account=post_json['account']
		auth_code=post_json['auth_code']
		client_id=post_json['client_id']
		pass_code=post_json['pass_code']
		account_type=post_json['account_type']
		#1普通用户
		if account_type==1:
			pass
		#2 商家
		elif account_type==2:
			pass

	except KeyError,key_error:
		result['msg']='not enpha params'
	except Exception, e:
		result['msg']=e.message 
	return json.dumps(result,ensure_ascii=False)
		