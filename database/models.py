# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from flask import json
import datetime,time
db=SQLAlchemy()

class User(db.Model):
	__tablename__='user'
	id=db.Column('id',db.Integer,primary_key=True)
	name=db.Column('name',db.String(100))

	def __init__(self,name):
		self.name=name
class MobileBanner(db.Model):
	__tablename__='mobile_banner'
	id=db.Column('id',db.Integer,primary_key=True)
	name=db.Column('name',db.String(64))
	picture_url=db.Column('picture_url',db.String(256))
	target=db.Column('target',db.String(256))
	display_order=db.Column('display_order',db.Integer)
	banner_type=db.Column('banner_type',db.Integer) #1 店铺 2商品   3webview链接
	description=db.Column('description',db.String(512))
	def get_map(self):
		result={'id':self.id,'name':self.name,'picture_url':self.picture_url,'target':self.target,'banner_type':self.banner_type,'display_order':self.display_order,'description':self.description}
		return result
class PromoteGoodsForHomePage(db.Model):
	__tablename__='discount_goods'
	id=db.Column('id',db.Integer,primary_key=True)
	goods_id=db.Column('goods_id',db.Integer)
	type=db.Column('type',db.Integer) #1  折扣 #2 人气
class Token(db.Model):
	__tablename__='token'
	def __init__(self,user_id,token_type,auth_code,client_id,access_token):
		self.user_id=user_id
		self.token_type=token_type
		self.auth_code=auth_code
		self.client_id=client_id
		self.access_token=access_token
		self.created_time=datetime.datetime.now()
		self.updated_time=datetime.datetime.now()
	id=db.Column('id',db.Integer,primary_key=True)
	user_id=db.Column('user_id',db.Integer)
	token_type=db.Column('token_type',db.Integer)
	auth_code=db.Column('auth_code',db.String(128))
	client_id=db.Column('client_id',db.String(128))
	access_token=db.Column('access_token',db.String(128))
	created_time=db.Column('created_time',db.DateTime)
	updated_time=db.Column('updated_time',db.DateTime)
	expire=db.Column('expire',db.DateTime)
	
class Area(db.Model):
	__tablename__='tb_area_m'
	area_id=db.Column('AreaID',db.Integer,primary_key=True)
	area_name=db.Column('AreaName',db.String(20))
	xzb=db.Column('xzb',db.DECIMAL)
	yzb=db.Column('yzb',db.DECIMAL)
	sort=db.Column('Sort',db.String(20))
	
	def get_map(self):
		s=self
		result={'area_id':s.area_id,'area_name':s.area_name,'xzb':str(s.xzb),'yzb':str(s.yzb),'sort':s.sort}
		return result
class Constent(db.Model):
	__tablename__='tb_constent_m'
	type_id=db.Column('TypeId',db.String(3),primary_key=True)
	type_name=db.Column('TypeName',db.String(20))
	item_id=db.Column('ItemId',db.String(3),primary_key=True)
	item_name=db.Column('ItemName',db.String(20))
	
	def get_map(self):
		s=self
		result={'type_id':s.type_id,'type_name':s.type_name,'item_id':s.item_id,'item_name':s.item_name}		
		return result
	def get_json(self):
		s=self
		result={'type_id':s.type_id,'type_name':s.type_name,'item_id':s.item_id,'item_name':s.item_name}
		return json.dumps(result)
	
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
	
	def get_map(self):
		s=self
		result={'buyer_id':s.buyer_id,'qquid':s.qquid,'account':s.account,'nick_name':s.nick_name,'real_name':s.real_name,
	                'sex':s.sex,'email':s.email,'status':s.status,'create_time':s.create_time,'create_ip':s.create_ip,
	                'last_login_ip':s.last_login_ip,'last_login_time':s.last_login_time,'login_times':s.login_times,
	                'is_visable':s.is_visable,'is_validate':s.is_validate
	                }
		return result
		
	def get_json(self):
		s=self
		result={'buyer_id':s.buyer_id,'qquid':s.qquid,'account':s.account,'nick_name':s.nick_name,'real_name':s.real_name,
		     'sex':s.sex,'email':s.email,'status':s.status,'create_time':s.create_time,'create_ip':s.create_ip,
		     'last_login_ip':s.last_login_ip,'last_login_time':s.last_login_time,'login_times':s.login_times,
		     'is_visable':s.is_visable,'is_validate':s.is_validate
		     }
		return json.dumps(self.get_json)
	
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
	is_default=db.Column('IsDefault',db.String(1))
	def get_map(self):
		result={'address_id':self.address_id,'buyer_id':int(self.buyer_id),'address':self.address,'consignee':self.consignee,
		     'phone':self.phone,'province':self.province,'detail_address':self.detail_address,'xzb':str(self.xzb),
		     'yzb':str(self.yzb),'is_default':self.is_default}
		return result
	
	
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
		return json.dumps(get_map())
	def get_map(self):
		s=self
		result={'shop_id':s.shop_id,'qquid':s.qquid,'account':s.account,'shop_type':s.shop_type,'shop_name':s.shop_name,
			'email':s.email,'introduce':s.introduce,'business_lisence':s.business_lisence,'shop_photo':s.shop_photo,
			'other_lisence':s.other_lisence,'shop_phone':s.shop_phone,'link_man':s.link_man,'mobile':s.mobile,
			'weixin':s.weixin,'weixin_photo':s.weixin_photo,'shop_address':s.shop_address,'xzb':str(s.xzb),'yzb':str(s.yzb),
			'is_checked':s.is_checked,'sort_no':s.sort_no,'is_recommend':s.is_recommend,'is_top':s.is_top,'default_freight':str(s.default_freight),
			'seo_title':s.seo_title,'seo_key_word':s.seo_key_word,'seo_content':s.seo_content,'status':s.status,
			'regist_date':s.regist_date,'regist_ip':s.regist_ip,'last_login_time':s.last_login_time,'login_times':s.login_times,
			'is_validate':s.is_validate
		
			}		
		return result
class GoodsType(db.Model):
	__tablename__='tb_goodstype_m'
	goods_type_id=db.Column('GoodsTypeID',db.Integer,primary_key=True)
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
	quantity=db.Column('Quantity',db.Integer)
	create_time=db.Column('CreateTime',db.DateTime)
	is_selected=db.Column('IsSelected',db.String(1))  #0未选中 1选中
	
	def get_map(self):
		s=self
		result={"buyer_id":s.buyer_id,"goods_id":s.goods_id,"quntity":s.quntity,'create_time':s.create_time}
		return result
	
class Order(db.Model):
	__tablename__='tb_order_s'
	order_no=db.Column('OrderNo',db.String(20),primary_key=True)
	shop_id=db.Column('ShopID',db.Integer)
	buyer_id=db.Column('BuyerID',db.Integer)
	sale_money=db.Column('SaleMoney',db.DECIMAL)
	submit_time=db.Column('SubmitTime',db.DateTime)
	send_time=db.Column('SendTime',db.DateTime)
	confirm_time=db.Column('ConfirmTime',db.DateTime)
	freight=db.Column('Freight',db.DECIMAL)
	address_id=db.Column('AddressID',db.Integer)
	send_address=db.Column('SendAddress',db.String(200))
	receiver=db.Column('Receiver',db.String(20))
	phone=db.Column('Phone',db.String(20))
	remark=db.Column('Remark',db.String(200))
	status=db.Column('Status',db.String(1)) # 0：已提交；1：已发货；2：交易成功；3：交易取消
	pay_status=db.Column('PayStatus',db.String(1)) # 0:未支付,1:已支付
	update_time=db.Column('UpdateTime',db.DateTime)
	
	def get_map(self):
		s=self
		result={"order_no":s.order_no,'shop_id':s.shop_id,'sale_money':str(s.sale_money),'submit_time':s.submit_time,'send_time':s.send_time,
		        'confirm_time':s.confirm_time,'freight':str(s.freight),'address_id':s.address_id,'send_address':s.send_address,
		        'receiver':s.receiver,'phone':s.phone,'remark':s.remark,'status':s.status,'pay_status':s.pay_status,'update_time':s.update_time
		        }
		return result
class OrderDetail(db.Model):
	__tablename__='tb_orderdetail_s'
	order_no=db.Column('OrderNo',db.String(20),primary_key=True)
	goods_id=db.Column('GoodsID',db.Integer,primary_key=True)
	batch_no=db.Column('BatchNo',db.Integer,primary_key=True)
	sale_price=db.Column('SalePrice',db.DECIMAL)
	quantity=db.Column('Quantity',db.Integer)
	discount_price=db.Column('DiscountPrice',db.DECIMAL)
	
	def get_map(self):
		s=self
		result={'order_no':s.order_no,'goods_id':s.goods_id,'batch_no':s.batch_no,'sale_price':str(s.sale_price),'quantity':s.quantity}
		return result
	
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
	del_flag=db.Column('DelFlag',db.String(1)) #0 未删除 1已删除
	is_read=db.Column('IsRead',db.String(1))
	
	def get_map(self):
		s=self
		result={'id':s.id,'buyer_id':int(s.buyer_id),'comment_type':s.comment_type,'order_no':s.order_no,'shop_id':int(s.shop_id),
		        'goods_id':int(s.goods_id),'level':s.level,'content':s.content,'commit_time':s.commit_time,'reply_content':s.reply_content,
		        'reply_time':s.reply_time,'del_flag':s.del_flag,'is_read':s.is_read

		        }
		
		return result

class Attention(db.Model):
	__tablename__='tb_attention'
	id=db.Column('ID',db.Integer,primary_key=True)
	buyer_id=db.Column('BuyerID',db.String(20))
	attention_type=db.Column('AttentionType',db.String(3)) # 0商铺  1 商品
	attention_id=db.Column('AttentionID',db.String(20)) # 商铺id或者 商铺id
	attention_time=db.Column('AttentionTime',db.DateTime)

class Message(db.Model):
	__tablename__='tb_message_w'
	message_id=db.Column('MessageID',db.Integer,primary_key=True)
	sender_type=db.Column('SenderType',db.String(3))
	sender=db.Column('Sender',db.Integer)
	sender_name=db.Column('SenderName',db.String(20))
	receiver=db.Column('Receiver',db.Integer)
	receiver_name=db.Column('ReceiverName',db.String(20))
	send_title=db.Column('SendTitle',db.String(100))
	send_content=db.Column('SendContent',db.String(1000))
	reply_time=db.Column('ReplyTime',db.DateTime)
	is_read=db.Column('IsRead',db.String(1))
	receiver_type=db.Column('ReceiverType',db.String(3))
	send_time=db.Column('SendTime',db.DateTime)
	def get_map(self):
		s=self
		result={'message_id':s.message_id,'sender_type':s.sender_type,'sender':s.sender,'sender_name':s.sender_name,
		        'receiver':s.receiver,'receiver_name':s.receiver_name,'send_title':s.send_title,'send_content':s.send_content,
		        'reply_time':s.reply_time,'is_read':s.is_read,'receiver_type':s.receiver_type,'send_time':s.send_time
		        }
		return result


class Photo(db.Model):
	__tablename__='tb_photo'
	photo_id=db.Column('PhotoID',db.Integer,primary_key=True)
	photo_type=db.Column('PhotoType',db.String(3))
	link_id=db.Column('LinkID',db.Integer)
	photo_name=db.Column('PhotoName',db.String(100))
	photo_path=db.Column('PhotoPath',db.String(200))
	thumbnail_path=db.Column('ThumbnailPath',db.String(200))
	sort_no=db.Column('SortNo',db.Integer)
	is_visable=db.Column('IsVisable',db.String(1))
	is_checked=db.Column('IsChecked',db.String(1))
	create_time=db.Column('CreateTime',db.DateTime)
	verify_time=db.Column('VerifyTime',db.DateTime)
	
	
	def get_map(self):
		s=self
		result={'photo_id':s.photo_id,'photo_type':s.photo_type,'link_id':s.link_id,'photo_name':s.photo_name,
		        'photo_path':s.photo_path,'thumbnail_path':s.thumbnail_path,'sort_no':s.sort_no,'is_visable':s.is_visable,
		        'is_checked':s.is_checked,'create_time':s.create_time,'verify_time':s.verify_time
		        }
		return result
	

class Purchase(db.Model):
	__tablename__='tb_purchase_s'
	goods_id=db.Column('GoodsID',db.Integer,primary_key=True)
	batch_no=db.Column('BatchNo',db.Integer,primary_key=True)
	buy_price=db.Column('BuyPrice',db.DECIMAL)
	quantity=db.Column('Quantity',db.Integer)
	start_time=db.Column('StartTime',db.DateTime)
	end_time=db.Column('EndTime',db.DateTime)
	
	def get_map(self):
		result={'goods_id':self.goods_id,'batch_no':self.batch_no,'buy_price':str(self.buy_price),'quantity':self.quantity,'start_time':self.start_time,'end_time':self.end_time
		        }
		return result
	

class Activity(db.Model):
	__tablename__='tb_activities_w'
	id=db.Column('ID',db.Integer,primary_key=True)
	type=db.Column('Type',db.String(3))
	shop_id=db.Column('ShopID',db.Integer)
	title=db.Column('Title',db.String(100))
	content=db.Column('Content',db.Text)
	count=db.Column('Count',db.Integer)
	sort_no=db.Column('SortNo',db.Integer)
	is_top=db.Column('IsTop',db.String(1))
	is_hot=db.Column('IsHot',db.String(1))
	publisher=db.Column('Publisher',db.String(20))
	publish_time=db.Column('PublishTime',db.DateTime)
	updater=db.Column('Updater',db.String(20))
	update_time=db.Column('UpdateTime',db.DateTime)
	seo_title=db.Column('SEOTitle',db.String(100))
	seo_key_word=db.Column('SEOKeyWord',db.String(100))
	seo_content=db.Column('SEOContent',db.String(100))
	del_flag=db.Column('DelFlag',db.String(1))
	call_index=db.Column('CallIndex',db.String(10))
	
	def get_map(self):
		s=self
		result={'id':s.id,'type':s.type,'shop_id':s.shop_id,'title':s.title,'content':s.content,'count':s.count,'sort_no':s.sort_no,'is_top':s.is_top,'is_hot':s.is_hot,'publisher':s.publisher,'publish_time':s.publish_time,'updater':s.updater,'update_time':s.update_time,'seo_title':s.seo_title,'seo_content':s.seo_content,'del_flag':s.del_flag,'call_index':s.call_index }
		return result