# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from flask import json
db=SQLAlchemy()

class User(db.Model):
	__tablename__='user'
	id=db.Column('id',db.Integer,primary_key=True)
	name=db.Column('name',db.String(100))

	def __init__(self,name):
		self.name=name

class Token(db.Model):
	__tablename__='token'
	id=db.Column('id',db.Integer,primary_key=True)
	user_id=db.Column('user_id',db.Integer)
	token_type=db.Column('type',db.Integer)
	auth_code=db.Column('auth_code',db.String(128))
	client_id=db.Column('client_id',db.String(128))
	access_token=db.Column('access_token',db.String(128))
	created_time=db.Column('created_time',db.DateTime)
	updated_time=db.Column('updated_time',db.DateTime)
	expire=db.Column('expire',db.DateTime)

class Buyer(db.Model):
	__tablename__='tb_buyer'
	buyer_id=db.Column('BuyerID',db.Integer ,primary_key=True)
	qquid=db.Column('QQUid',db.String(50))
	account=db.Column('Account',db.String(20))
	password=db.Column('Password',db.String(100))
	nick_name=db.Column('NickName',db.String(20))
	real_name=db.Column('RealName',db.String(20))
	sex=db.Column('Sex',db.String(1)) #0 男 1 女 2 保密
	email=db.Column('Email',db.String(100))
	status=db.Column('Status',db.String(1)) # 0:启动 1:禁用
	create_time=db.Column('CreateTime',db.DateTime)
	create_ip=db.Column('CreateIp',db.String(20))
	last_login_time=db.Column('LastLoginTime',db.DateTime)
	last_login_ip=db.Column('LastLoginIp',db.String(20))
	login_times=db.Column('LoginTimes',db.Integer)
	is_visable=db.Column('IsVisable',db.String(1)) # 0 否 1是
	is_validate=db.Column('IsValidate',db.String(1)) # 0否 1是
	def get_json(self):
		s=self
		result={'buyer_id':s.buyer_id,'qquid':s.qquid,'account':s.account,'nick_name':s.nick_name,'real_name':s.real_name,
		     'sex':s.sex,'email':s.email,'status':s.status,'create_time':s.create_time,'create_ip':s.create_ip,
		     'last_login_ip':s.last_login_ip,'last_login_time':s.last_login_time,'login_times':s.login_times,
		     'is_visable':s.is_visable,'is_validate':s.is_validate
		     }
		return json.dumps(result)
	
class BuyerAddress(db.Model):
	__tablename__='tb_buyeraddress'
	address_id=db.Column('AddressID',db.Integer,primary_key=True)
	buyer_id=db.Column('BuyerID',db.String(20)) 
	address=db.Column('Address',db.String(200))
	consignee=db.Column('Consignee',db.String(20))
	phone=db.Column('Phone',db.String(20))
	province=db.Column('Province',db.String(3))
	detail_address=db.Column('DetailAddress',db.String(200))
	xzb=db.Column('xzb',db.DECIMAL)
	yzb=db.Column('yzb',db.DECIMAL)
	
	def get_json(self):
		result={'address_id':self.address_id,'buyer_id':int(self.buyer_id),'address':self.address,'consignee':self.consignee,
		     'phone':self.phone,'province':self.province,'detail_address':self.detail_address,'xzb':str(self.xzb),
		     'yzb':str(self.yzb)
		     }
		return json.dumps(result)
	
	
class ShopInfo(db.Model):
	__tablename__='tb_shopinfo_s'
	shop_id=db.Column('ShopID',db.Integer,primary_key=True)
	qquid=db.Column('QQUid',db.String(50))
	account=db.Column('account',db.String(20))
	password=db.Column('Password',db.String(100))
	shop_type=db.Column('ShopType',db.String(100))
	shop_name=db.Column('ShopName',db.String(100))
	email=db.Column('Email',db.String(100))
	introduce=db.Column('introduce',db.String(1000))
	business_lisence=db.Column('BusinessLisence',db.String(200))
	shop_photo=db.Column('ShopPhoto',db.String(200))
	other_lisence=db.Column('OtherLisence',db.String(200))
	shop_phone=db.Column('ShopPhone',db.String(20))
	link_man=db.Column('LinkMan',db.String(20))
	mobile=db.Column('Mobile',db.String(20))
	weixin=db.Column('Weixin',db.String(20))
	weixin_photo=db.Column('WeixinPhoto',db.String(200))
	shop_address=db.Column('ShopAddress',db.String(200))
	xzb=db.Column('xzb',db.DECIMAL)
	yzb=db.Column('yzb',db.DECIMAL)
	is_checked=db.Column('IsChecked',db.String(1)) #0 已注册 1 待审核 2已审核 3未通过
	sort_no=db.Column('SortNo',db.Integer)
	is_recommend=db.Column('IsRecommend',db.String(1)) #0 否 1是
	is_top=db.Column('IsTop',db.String(1))  #0 否 1是
	default_freight=db.Column('DefaultFreight',db.DECIMAL)
	seo_title=db.Column('SEOTitle',db.String(100))
	seo_key_word=db.Column('SEOKeyWord',db.String(100))
	seo_content=db.Column('SEOContent',db.String(2000))
	status=db.Column('Status',db.String(1))  #0启动 1禁用
	regist_date=db.Column('RegistDate',db.DateTime)
	regist_ip=db.Column('RegistIP',db.String(20))
	last_login_time=db.Column('LastLoginTime',db.DateTime)
	login_times=db.Column('LoginTimes',db.Integer)
	is_validate=db.Column('IsValidate',db.String(1)) #0否 1是
	
	def get_json(self):
		s=self
		result={'shop_id':s.shop_id,'qquid':s.qquid,'account':s.account,'shop_type':s.shop_type,'shop_name':s.shop_name,
		        'email':s.email,'introduce':s.introduce,'business_lisence':s.business_lisence,'shop_photo':s.shop_phone,
		        'other_lisence':s.other_lisence,'shop_phone':s.shop_phone,'link_man':s.link_man,'mobile':s.mobile,
		        'weixin':s.weixin,'weixin_photo':s.weixin_photo,'shop_address':s.shop_address,'xzb':str(s.xzb),'yzb':str(s.yzb),
		        'is_checked':s.is_checked,'sort_no':s.sort_no,'is_recommend':s.is_recommend,'is_top':s.is_top,'default_freight':s.default_freight,
		        'seo_title':s.seo_title,'seo_key_word':s.seo_key_word,'seo_content':s.seo_content,'status':s.status,
		        'regist_date':s.regist_date,'regist_ip':s.regist_ip,'last_login_time':s.last_login_time,'login_times':s.login_times,
		        'is_validate':s.is_validate
		        
		        }
		
		return json.dumps(result)
	

class GoodsType(db.Model):
	__tablename__='tb_goodstype_m'
	goods_type_id=db.Column('GoodsTypeID',db.Integer)
	goods_type_name=db.Column('GoodsTypeName',db.String(100))
	parent_id=db.Column('ParentID',db.String(20))
	
	def get_json(self):
		result={'good_type_id':self.goods_type_id,'goods_type_name':self.goods_type_name,
		        'parent_id':self.parent_id
		        }
		return json.dumps(result)
	

class ShopGoodsType(db.Model):
	__tablename__='tb_goodstype_s'
	shop_id=db.Column('ShopID',db.String(20),primary_key=True)
	goods_type_id=db.Column('GoodsTypeID',db.Integer)
	goods_type_name=db.Column('GoodsTypeName',db.String(100))
	parent_id=db.Column('ParentID',db.String(20))
	
class ShopCart(db.Model):
	__tablename__='tb_shoppingcart'
	buyer_id=db.Column('BuyerID',db.Integer,primary_key=True)
	goods_id=db.Column('GoodsID',db.Integer,primary_key=True)
	quntity=db.Column('Quntity',db.Integer)
	create_time=db.Column('CreateTime',db.DateTime)
	
	def get_json(self):
		s=self
		result={"buyer_id":s.buyer_id,"goods_id":s.goods_id,"quntity":s.quntity,'create_time':s.create_time}
		return json.dumps(result)
	
	
class Comment(db.Model):
	__tablename__='tb_comment'
	id=db.Column('ID',db.Integer,primary_key=True)
	buyer_id=db.Column('BuyerID',db.String(20))
	comment_type=db.Column('CommentType',db.String(3)) 
	order_no=db.Column('OrderNo',db.String(20))
	shop_id=db.Column('ShopID',db.String(20))
	goods_id=db.Column('GoodsID',db.String(20))
	level=db.Column('Level',db.Integer)
	content=db.Column('Content',db.String(1000))
	commit_time=db.Column('CommitTime',db.DateTime)
	reply_content=db.Column('ReplyContent',db.String(1000))
	reply_time=db.Column('ReplyTime',db.DateTime)
	del_flag=db.Column('del_flag',db.String(1)) #0 未删除 1已删除
	is_read=db.Column('IsRead',db.String(1))
	
	def get_json(self):
		s=self
		result={'id':s.id,'buyer_id':int(s.buyer_id),'comment_type':s.comment_type,'order_no':s.order_no,'shop_id':int(s.shop_id),
		        'goods_id':int(s.goods_id),'level':s.level,'content':s.content,'commit_time':s.commit_time,'reply_content':s.reply_content,
		        'reply_time':s.reply_time,'del_flag':s.del_flag,'is_read':s.is_read

		        }
		
		return json.dumps(result)

class Attention(db.Model):
	__tablename__='tb_attention'
	id=db.Column('ID',db.Integer,primary_key=True)
	buyer_id=db.Column('BuyerID',db.String(20))
	attention_type=db.Column('AttentionType',db.String(3)) # 0商铺  1 商品
	attention_id=db.Column('AttentionID',db.String(20)) # 商铺id或者 商铺id
	attention_time=db.Column('AttentionTime',db.DateTime)
	
