from flask import Flask,url_for,Response,json
from flask import jsonify
from views.token_controller import token_controller
from views.buyer_controller import buyer_controller
from views.public_controller import public_controller
from views.area_controller import area_controller
from views.order_controller import order_controller
from views.mobile_banner_controller import mobile_banner_controller
from views.shopcart_controller import shopcart_controller
from views.buyer_address_controller import buyer_address_controller
from views.shop_goods_type_controller import shop_goods_type_controller
from views.shop_goods_controller import shop_goods_controller
from views.comment_controller import comment_controller
from views.attention_controller import attention_controller
from database.models import db
app=Flask(__name__)
db.init_app(app)
app.config.from_pyfile('app.cfg')
app.register_blueprint(token_controller)
app.register_blueprint(buyer_controller)
app.register_blueprint(public_controller)
app.register_blueprint(area_controller)
app.register_blueprint(order_controller)
app.register_blueprint(mobile_banner_controller)
app.register_blueprint(shopcart_controller)
app.register_blueprint(buyer_address_controller)
app.register_blueprint(shop_goods_type_controller)
app.register_blueprint(shop_goods_controller)
app.register_blueprint(comment_controller)
app.register_blueprint(attention_controller)
def has_no_empty_params(rule):
	defaults = rule.defaults if rule.defaults is not None else ()
	arguments = rule.arguments if rule.arguments is not None else ()
	return len(defaults) >= len(arguments)


@app.route("/site-map")
def site_map():
	links = []
	for rule in app.url_map.iter_rules():
		# Filter out rules we can't navigate to in a browser
		# and rules that require parameters
		if "GET" in rule.methods and has_no_empty_params(rule):
			url = url_for(rule.endpoint)
			links.append((url, rule.endpoint))
	result=''
	for link in links:
		result=(result+link[0]+'&nbsp : &nbsp'+link[1]+'<br>')
	
	return Response(result)
		
@app.route('/')
def hello_world():
	return jsonify({'hello':'world'})

if __name__ == '__main__':
	reload(sys) 
	sys.setdefaultencoding( "utf-8" ) 	
	from os import environ
	##db.create_all(bind='__all__', app=app)
	app.debug=False
	app.run(host='0.0.0.0',port=environ.get("PORT", 5000), processes=1)
	#app.run('0.0.0.0:5050')

