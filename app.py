from flask import Flask
from flask import jsonify
from views.token_controller import token_controller
from views.buyer_controller import buyer_controller
from database.models import db
app=Flask(__name__)
db.init_app(app)
app.config.from_pyfile('app.cfg')
app.register_blueprint(token_controller)
app.register_blueprint(buyer_controller)
@app.route('/')
def hello_world():
	return jsonify({'hello':'world'})

if __name__ == '__main__':
	##db.create_all(bind='__all__', app=app)
	app.run()

