from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.sqlite'
db = SQLAlchemy(app)


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cost = db.Column(db.Integer)
    name = db.Column(db.String(20))
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    client = db.relationship('Client', backref='orders')


def create_data():
    clients = [
        {'name': 'Client1'},
        {'name': 'Client2'},
        {'name': 'Client3'},
        {'name': 'Client4'}
    ]
    orders = [
        {'cost': 100, 'name': 'Order1', 'client_id': 1},
        {'cost': 200, 'name': 'Order2', 'client_id': 1},
        {'cost': 300, 'name': 'Order3', 'client_id': 2},
        {'cost': 400, 'name': 'Order4', 'client_id': 2},
        {'cost': 500, 'name': 'Order5', 'client_id': 2},
        {'cost': 600, 'name': 'Order6', 'client_id': 3},
        {'cost': 700, 'name': 'Order7', 'client_id': 4},
        {'cost': 800, 'name': 'Order8', 'client_id': 4},
        {'cost': 900, 'name': 'Order9', 'client_id': 4},
        {'cost': 1000, 'name': 'Order10', 'client_id': 4}
    ]
    
    for c in clients:
        client = Client(name=c['name'])
        db.session.add(client)
    db.session.commit()

    for o in orders:
        order = Order(cost=o['cost'], name=o['name'], client_id=o['client_id'])
        db.session.add(order)
    db.session.commit()


def get_orders_using_orm():
    clients = Client.query.all()
    order_dict = {}
    for client in clients:
        orders = client.orders
        order_dict[client.name] = [{'name': order.name, 'cost': order.cost} for order in orders]
    return order_dict


def get_orders_using_raw_sql():
    query = '''
    SELECT c.name AS client_name, o.name AS order_name, o.cost
    FROM client c
    INNER JOIN "order" o ON c.id = o.client_id;
    '''
    connection = db.engine.raw_connection()
    with connection.cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
        order_dict = {}
        for row in results:
            client_name, order_name, cost = row
            if client_name not in order_dict:
                order_dict[client_name] = []
            order_dict[client_name].append({'name': order_name, 'cost': cost})
    return order_dict


@app.route('/')
def get_orders():
    orders = get_orders_using_orm()
    return render_template('orders.html', orders=orders)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_data()
    app.run(debug=True)
