import datetime

import flask_restful
from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy

from contracts import addresses_list
from db_config import PG_USER, PG_PASS, HOST, PG_NAME, PG_PORT, DB_API_PORT

print(f"db on {HOST}:{PG_PORT}")
app = Flask(__name__)
api = flask_restful.Api(app, catch_all_404s=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{PG_USER}:{PG_PASS}@{HOST}:{PG_PORT}/{PG_NAME}"
db = SQLAlchemy(app)


class Address_contracts(db.Model):
    __tablename__ = "address_contracts"
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    address_contract = db.Column(db.String(), primary_key=True)

    def __init__(self, address_contract):
        self.address_contract = address_contract

    def __repr__(self):
        return f"address_contract {self.address_contract} was added"




db.create_all()
for item in addresses_list:
    addresses = Address_contracts(address_contract=item)
    db.session.add(addresses)

# db.session.add(Address_contracts(address_contract="a3c3077f9c5c9e522534f529559dd14d07830ed4"))
db.session.commit()


class Users(db.Model):
    __tablename__ = 'users'
    chat_id = db.Column(db.Integer(), primary_key=True, nullable=False)
    bcs_address = db.Column(db.String(), nullable=False, unique=True)
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    balance = db.Column(db.BIGINT(), primary_key=True, default=0, nullable=False)
    created = db.Column(db.DateTime(), default=datetime.datetime.now())

    # value_counter = db.relationship("Users_check", back_populates="users", lazy="dynamic")

    def __init__(self, bcs_address, chat_id, balance):
        self.chat_id = chat_id
        self.bcs_address = bcs_address
        self.balance = balance

    def __repr__(self):
        return f"<user {self.bcs_address}, {self.chat_id}, {self.balance}>"


class Transactions(db.Model):
    __tablename__ = "transactions"
    transaction_id = db.Column(db.String(), primary_key=True, nullable=False, unique=True)
    sender = db.Column(db.String(), nullable=False)
    receiver = db.Column(db.String())
    chat_id = db.Column(db.Integer())

    def __init__(self, transaction_id, sender, receiver, chat_id):
        self.transaction_id = transaction_id
        self.sender = sender
        self.receiver = receiver

        self.chat_id = chat_id

    def __repr__(self):
        return f"<in check {self.transaction_id}, {self.sender}"


class AppCheck(db.Model):
    __tablename__ = "app_check"
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    check_hash = db.Column(db.String())
    chat_id = db.Column(db.Integer())
    sender = db.Column(db.String(), nullable=False)
    receiver = db.Column(db.String(), nullable=False)
    value = db.Column(db.Integer(), nullable=False)
    flag = db.Column(db.BOOLEAN(), default=False)

    def __init__(self, check_hash, chat_id, sender, receiver, value, flag):
        self.check_hash = check_hash
        self.chat_id = chat_id
        self.sender = sender
        self.receiver = receiver
        self.value = value
        self.flag = flag

    def __repr__(self):
        return f"<hash for user {self.receiver} from user {self.sender}>"


class AnonCheck(db.Model):
    __tablename__ = "anon_check"
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    check_hash = db.Column(db.String())
    chat_id = db.Column(db.Integer(), primary_key=True)
    sender = db.Column(db.String(), nullable=False)
    value = db.Column(db.Integer(), nullable=False)
    flag = db.Column(db.BOOLEAN(), default=False)

    def __init__(self, check_hash, chat_id, sender, value, flag):
        self.check_hash = check_hash
        self.chat_id = chat_id
        self.sender = sender
        self.value = value
        self.flag = flag

    def __repr__(self):
        return f"<hash {self.check_hash} for anon user {self.chat_id}>"


class Used_private_checks(db.Model):
    __tablename__ = "used_private_checks"
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    chat_id = db.Column(db.Integer(), primary_key=True)
    used_hashes = db.Column(db.String())

    def __init__(self, chat_id, used_hashes):
        self.chat_id = chat_id
        self.used_hashes = used_hashes

    def __repr__(self):
        return f"hash {self.used_hashes} has been used by {self.chat_id}"


class Used_person_checks(db.Model):
    __tablename__ = "used_person_checks"
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    chat_id = db.Column(db.Integer(), primary_key=True)
    used_hashes = db.Column(db.String())

    def __init__(self, chat_id, used_hashes):
        self.chat_id = chat_id
        self.used_hashes = used_hashes

    def __repr__(self):
        return f"hash {self.used_hashes} has been used by {self.chat_id}"


@app.route("/user/address/", methods=["GET"])
def get_address_contract():
    users = Address_contracts.query.all()

    results = [{
        "address_contract": user.address_contract
    } for user in users]
    return {"address": results}


@app.route("/user/used/person/<chat_id>", methods=["GET"])
def get_person_hash(chat_id):
    users = Used_person_checks.query.filter_by(chat_id=chat_id).all()

    results = [{
        "used_hash": user.used_hashes,
    } for user in users]

    return {"count": len(results), "added_hash": results}


@app.route('/user/add/person/<chat_id>', methods=["POST"])
def put_person_hash(chat_id):
    data = request.get_json()
    new_hash = Used_person_checks(chat_id=chat_id, used_hashes=data['used_hashes'])
    db.session.add(new_hash)
    db.session.commit()
    return {"message": f"hash by {new_hash.chat_id}, {new_hash.used_hashes} has been added successfully."}


@app.route("/user/used/hash/<chat_id>", methods=["GET"])
def get_used_hash(chat_id):
    users = Used_private_checks.query.filter_by(chat_id=chat_id).all()

    results = [{
        "used_hash": user.used_hashes,
    } for user in users]

    return {"count": len(results), "added_hash": results}


@app.route('/user/add/hash/<chat_id>', methods=["POST"])
def put_used_hash(chat_id):
    data = request.get_json()
    new_hash = Used_private_checks(chat_id=chat_id, used_hashes=data['used_hashes'])
    db.session.add(new_hash)
    db.session.commit()
    return {"message": f"hash by {new_hash.chat_id}, {new_hash.used_hashes} has been added successfully."}


@app.route("/users", methods=["GET"])
def get_users():
    users = Users.query.all()
    results = [
        {
            "bcs_address": user.bcs_address,
            "chat_id": user.chat_id,
            "balance": user.balance
        } for user in users]

    return {"count": len(results), "users": results}


@app.route('/user/<chat_id>', methods=['POST', 'GET', 'PUT', 'DELETE'])
def handle_users(chat_id):
    if request.method == "POST":
        data = request.get_json()
        new_user = Users(bcs_address=data['bcs_address'], chat_id=chat_id, balance=data['balance'])
        db.session.add(new_user)
        db.session.commit()
        return {"message": f"user {new_user.id}, {new_user.bcs_address} has been created successfully."}

    user = Users.query.filter_by(chat_id=chat_id).first()

    if request.method == 'GET':
        response = {
            # "chat_id": user.chat_id,
            "bcs_address": user.bcs_address,
            "id": user.id,
            "balance": user.balance
        }
        return {"message": "success", "users": response}

    elif request.method == 'PUT':
        data = request.get_json()
        user.bcs_address = data['bcs_address']
        user.balance = data['balance']
        db.session.add(user)
        db.session.commit()
        return {"message": f"user {user.id} successfully updated"}

    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return {"message": f"user {user.id} successfully deleted."}


@app.route("/user/balance/<chat_id>", methods=["GET"])
def get_balance(chat_id):
    users = Users.query.filter_by(chat_id=chat_id).first()
    response = {
        "bcs_address": users.bcs_address,
        "balance": users.balance,
    }
    return {"message": "success", "balance": response}


@app.route("/user/formhash/<chat_id>", methods=["POST"])
def form_user_hash(chat_id):
    data = request.get_json()
    print(data)
    dfg = AppCheck(check_hash=data["check_hash"], flag=data["flag"], chat_id=chat_id, sender=data["sender"],
                   receiver=data["receiver"], value=data["value"])
    db.session.add(dfg)
    db.session.commit()
    return {"message": f"user create hash."}


@app.route("/user/hash/<chat_id>", methods=["GET"])
def get_hash(chat_id):
    users = AppCheck.query.filter_by(chat_id=chat_id).order_by(AppCheck.id.desc()).first()

    response = {
        "check_hash": users.check_hash,
        "sender": users.sender,
        "receiver": users.receiver,
        "value": users.value,
        "flag": users.flag,
    }
    return {"message": "success", "hash": response}


@app.route("/user/get/phash/<chat_id>", methods=["GET"])
def get_all_hash(chat_id):
    users = AppCheck.query.filter_by(chat_id=chat_id).order_by(AppCheck.id.desc()).all()

    results = [{
        "check_hash": user.check_hash,
        "sender": user.sender,
        "receiver": user.receiver,
        "value": user.value,
        "flag": user.flag,
    } for user in users]
    return {"count": len(results), "hash": results}


@app.route("/user/updatehash/<chat_id>", methods=["PUT"])
def update_hash(chat_id):
    users = AppCheck.query.filter_by(chat_id=chat_id).first()

    data = request.get_json()
    users.flag = data['flag']
    db.session.add(users)
    db.session.commit()
    return {"message": f"user hash {users.check_hash} has been updated"}


@app.route("/user/transaction/<chat_id>", methods=["POST", "GET", "PUT", "DELETE"])
def transactions(chat_id):
    if request.method == "POST":
        data = request.get_json()
        print(data)
        new_transaction = Transactions(transaction_id=data["transaction_id"],
                                       sender=data["sender"], receiver=data["receiver"],
                                       chat_id=chat_id)
        db.session.add(new_transaction)
        db.session.commit()
        return {
            "message": f"transaction {new_transaction.transaction_id}, {new_transaction.sender}, {new_transaction.receiver} has been created successfully."}

    users = Transactions.query.filter_by(chat_id=chat_id)

    if request.method == "GET":
        response = {
            "transaction_id": users.transaction_id,
            "sender": users.sender,
            "receiver": users.receiver,
        }
        return {"message": "success", "balance": response}

    elif request.method == 'PUT':
        data = request.get_json()
        users.transaction_id = data['transaction_id']
        users.cash_value = data['cash_value']
        db.session.add(users)
        db.session.commit()
        return {"message": f"transaction {users.transaction_id} successfully updated"}

    elif request.method == "DELETE":
        db.session.delete(users)
        db.session.commit()
        return {"message": f"transaction {users.transaction_id} successfully deleted."}


@app.route("/address/<address>", methods=["GET"])
def get_by_address(address):
    user = Users.query.filter_by(bcs_address=address).first()
    return {"ok": user is not None}


@app.route("/user/form/anonhash/<chat_id>", methods=["POST"])
def form_anon_hash(chat_id):
    data = request.get_json()
    dfg = AnonCheck(check_hash=data["check_hash"], flag=data["flag"], chat_id=chat_id, sender=data["sender"],
                    value=data["value"])
    db.session.add(dfg)
    db.session.commit()
    return {"message": f"user create hash."}


@app.route("/user/get/anonhash/<chat_id>", methods=["GET"])
def get_anon_hash(chat_id):
    users = AnonCheck.query.filter_by(chat_id=chat_id).order_by(AnonCheck.id.desc()).first()

    response = {
        "check_hash": users.check_hash,
        "sender": users.sender,
        "value": users.value,
        "flag": users.flag,
    }
    return {"message": "success", "hash": response}


@app.route("/user/get/hash/flag/<chat_id>", methods=["GET"])
def get_hash_and_flag(chat_id):
    users = AnonCheck.query.filter_by(chat_id=chat_id).order_by(AnonCheck.id.desc()).all()

    results = [{
        "check_hash": user.check_hash,
        "flag": user.flag,
    } for user in users]
    return {"hash_flag": results}


@app.route("/user/get/hashlist/<chat_id>", methods=["GET"])
def send_hash_list(chat_id):
    users = AnonCheck.query.filter_by(chat_id=chat_id).order_by(AnonCheck.id.desc()).all()

    results = [{
        "check_hash": user.check_hash,
        "sender": user.sender,
        "value": user.value,
        "flag": user.flag,
    } for user in users]
    return {"message": "success", "hash": results}


@app.route("/user/update/anonhash/<chat_id>", methods=["PUT"])
def update_anon_hash(chat_id):
    users = AnonCheck.query.filter_by(chat_id=chat_id)

    data = request.get_json()
    users.flag = data['flag']
    db.session.add(users)
    db.session.commit()
    return {"message": f"user hash {users.check_hash} has been updated"}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=DB_API_PORT)
