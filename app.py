from flask import Flask
from flask import jsonify
from views.token_controller import token_controller
from views.buyer_controller import buyer_controller
from views.public_controller import public_controller
from views.area_controller import area_controller
from views.order_controller import order_controller
from views.mobile_banner_controller import mobile_banner_controller
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
@app.route('/')
def hello_world():
	return jsonify({'hello':'world'})

if __name__ == '__main__':
	from os import environ
	##db.create_all(bind='__all__', app=app)
	app.debug=False
	app.run(host='0.0.0.0',port=environ.get("PORT", 5000), processes=1)
	#app.run('0.0.0.0:5050')

