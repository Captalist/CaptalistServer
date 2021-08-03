from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response 

from email.mime.text import MIMEText
import email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
import smtplib, ssl
import threading
from server import *
import random
from flask_socketio import SocketIO, emit, join_room, leave_room, send
app = Flask(__name__)

app.secret_key = 'ChidozieNnajiMySQLAdminDbhost2005@gmail.com#codewithcn.com'
socketio = SocketIO(app, logger=True, engineio_logger=True)
def send_email(subject, message, email, emailer, emailer_pass):
        port = 587  # For starttls
        smtp_server = "smtp.mail.me.com"
        sender_email = emailer
        receiver_email = email
        password = emailer_pass
        messages = MIMEMultipart()
        messages['From'] = sender_email
        messages['To'] = receiver_email
        messages['Subject'] = subject
        messages['Bcc'] = receiver_email
        messages.attach(MIMEText(message, 'plain'))
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, messages.as_string())

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')
    
@app.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    try:
        returns = User.login(data['name'], data['password'])
        if type(returns) == int:
            session['id'] = returns
            session['name'] = data['name']
            session['password'] = data['password']
            resp = make_response(jsonify({'return': 'Correctly Logged In', 'id': session['id'], 'name': session['name'],
            'password':session['password']}))
            for key in session:
                resp.headers.add('Set-Cookie', '{}={}; SameSite=Lax; Secure'.format(key, session[key]))
               
            return resp
        return jsonify({'return': returns})
    except KeyError:
        return jsonify({'return': 'Can not get key'})


@app.route('/sign_out', methods=['POST'])
def sign_out():
  data = request.get_json()
  sign_u_m = Server.user_sign_out(data['id'])
  for me in sign_u_m:
    message = "{} has left the server".format(me['Country_Name'])
    emit('Update',message, to=me['room'], namespace='/')
  return jsonify({'return': 'Done'})


@app.route('/server_data', methods=["POST"])
def server_data():
    data = request.get_json()
    server_data = Server.server_data(data['id'])
    return jsonify(server_data)


@app.route('/join/server', methods=['POST'])
def join_server():
    data = request.get_json()
    query = "select id from servers where name='{}' and code='{}'".format(
        data['name'], data['password']
    )
    conn = sqlite3.connect('server.db')
    cursor =  conn.cursor()
    cursor.execute(query)
    server_id = cursor.fetchone()
    conn.close()
    if server_id != None:
        count = Server.join_server(server_id[0], data['id'])
        if count != None:
            if count == "User not Logged In":
                return jsonify({'return':'Failed, Your are not logged in'})

            if len(count.keys()) == 0:
                return jsonify({'return': "You do not have a country in this server",'server_id':server_id[0]})  

            return jsonify({'return': 'Success', 'country_id':count, 'server_id':server_id[0]})
        return jsonify({'return': "You do not have a country in this server", 'server_id':server_id[0]})
    return jsonify({'return': 'Server does not exist'})


@app.route('/create/server', methods=['POST'])
def create_server():
    data = request.get_json()
    returns = Server.create_new_server(data['id'], data['name'], data['psw'])
    return jsonify(returns)
    
@app.route('/create/country', methods=['POST'])
def create_country():
    data = request.get_json()
    returns = Server.create_new_country(data['server_id'], data['country_name'], data['country_flag'], data['user_id'])
    return jsonify(returns)

@app.route('/get_country_data', methods=['POST'])
def country_data():
    data = request.get_json()
    returns = Server.get_count_data(data['server_id'], data['user_id'])
    return jsonify(returns)

@app.route('/get/city/data', methods=['POST'])
def get_city_data():
    data = request.get_json()
    returns = Server.get_server_user_cities(data['server_id'], data['user_id'])
    return jsonify(returns)
    
@app.route('/change/city/data', methods=['POST'])
def change_city_data():
    data = request.get_json()
    try:
        if data['action'] == 'change_name':
            Cities.active_cities[data['id']].change_name(data['name'])
            return jsonify({'return': 'Success'})
        elif data['action'] =='change_tax':
            Cities.active_cities[data['id']].change_tax(data['tax'])
            return jsonify({'return': 'Success'})
        elif data['action'] == 'change_level':
            gov_id = Cities.active_cities[data['id']].gov_id
            money =  Government.active_gov[gov_id].money
            state_ment = Cities.active_cities[data['id']].upgrade(money)
            if state_ment == "Not Enough":
                return jsonify({'return': "You do not have enough money to upgrade city"})
            else:
                Government.active_gov[gov_id].remove_money(state_ment)
                return jsonify({
                    'return': 'Success',
                    'Max Pop': Cities.active_cities[data['id']].max_pop,
                    'Level': Cities.active_cities[data['id']].level
                })
        elif data['action'] == 'add_oil':
            oil = Cities.active_cities[data['id']].oil
            Cities.active_cities[data['id']].change_oil(oil+1)
            return jsonify({
                'return': 'Success',
                'oil': Cities.active_cities[data['id']].oil
            })
        elif data['action'] == 'remove_oil':
            oil = Cities.active_cities[data['id']].oil
            Cities.active_cities[data['id']].change_oil(oil-1)
            return jsonify({
                'return': 'Success',
                'oil': Cities.active_cities[data['id']].oil
            })
        elif data['action'] == 'remove_food':
            food = Cities.active_cities[data['id']].food
            Cities.active_cities[data['id']].change_food(food-1)
            return jsonify({
                'return': 'Success',
                'food': Cities.active_cities[data['id']].food
            })
        elif data['action'] == 'add_food':
            food = Cities.active_cities[data['id']].food
            Cities.active_cities[data['id']].change_food(food+1)
            return jsonify({
                'return': 'Success',
                'food': Cities.active_cities[data['id']].food
            })
        elif data['action'] == 'add_iron':
            iron = Cities.active_cities[data['id']].iron
            Cities.active_cities[data['id']].change_iron(iron + 1)
            return jsonify({
                'return': 'Success',
                'iron': Cities.active_cities[data['id']].iron
            })
        elif data['action'] == 'remove_iron':
            iron = Cities.active_cities[data['id']].iron
            Cities.active_cities[data['id']].change_iron(iron - 1)
            return jsonify({
                'return': 'Success',
                'iron': Cities.active_cities[data['id']].iron
            })
        elif data['action'] == 'add_water':
            water = Cities.active_cities[data['id']].water
            Cities.active_cities[data['id']].change_water(water+1)
            return jsonify({
                'return': 'Success',
                'water': Cities.active_cities[data['id']].water
            })
        elif data['action'] == 'remove_water':
            water = Cities.active_cities[data['id']].water
            Cities.active_cities[data['id']].change_water(water-1)
            return jsonify({
                'return': 'Success',
                'water': Cities.active_cities[data['id']].water
            })
        else:
            return jsonify({'return': 'Invalid Actions'})
    except KeyError:
        return jsonify({'return': 'Invalid Parameters'})

@app.route('/create/new_city', methods=['POST'])
def create_new_city():
  data = request.get_json()
  try:
    statement = Server.form_new_city(data['server_id'], data['user_id'], data['name'])
    return jsonify(statement)
  except KeyError:
    return jsonify({'returns': 'Invalid Parameters'})

@app.route('/get/alliance/data', methods=['POST'])
def get_alliance_data():
  data = request.get_json()

  try:
    statement = Alliance.alliance_data(data['country_id'])
    return jsonify({'data': statement, 'returns': 'Success'})
  except Exception as e:
    print(e)
    return jsonify({'returns': 'Unsuccessful'})

@app.route('/add/ally', methods=['POST'])
def add_ally():
  data = request.get_json()

  return jsonify({'return':Server.servers[data['server_id']].add_new_ally(
    data['new_ally'], data['country_id']
  )})

@app.route('/accept/alliance', methods=['POST'])
def accept_alliance():
  data = request.get_json()
  return jsonify({
    'return': Server.servers[data['server_id']].acceptAllianceRequest(
      data['acceptor'], data['creator']
    )
  })

@app.route('/deny/alliance', methods=['POST'])
def deny_alliance():
  data = request.get_json()
  return jsonify({
    'return': Server.servers[data['server_id']].denyAllianceRequest(
      data['acceptor'], data['creator']
    )
  })

@app.route('/alliance/data_and_trade_deals', methods=['POST'])
def data_and_trade_deals():
  data = request.get_json()
  return jsonify({
    'return': Alliance.all_active_allies[int(data['alliance'])].return_data_and_trade_deals(data['country_id'])
  })

@socketio.on('Joined')
def on_join(data):
    print(data)
    username = data['country']
    room = data['room']
    join_room(str(room))
    emit('Update', username + ' has joined the server.', to=str(room), broadcast=True)

@socketio.on('change_name')
def change_name(data):
    old_name = Cities.active_cities[data['id']].name 
    emit("Update", old_name + ' city has now become ' + data['name'] +' city', to=str(data['room']), broadcast=True)

@socketio.on('new_city_created')
def new_city_created(data):
  String = "{} has created a new city called {}".format(data['country'], data['city'])
  emit("Update", String, to=str(data['room']), broadcast=True)

@socketio.on('AllianceRequest')
def AllianceRequest(data):
  print("DATA", data)
  returns = Server.servers[data['server']].getAllianceRequest(data['country'])
  emit("HereIsYourAllianceRequest", returns)

if __name__ == '__main__':
    User.server_running = True
    Alliance.server_running = True
    Server.run()
    threading.Thread(target=Alliance.run_trade, args=()).start()
    port = random.randint(2000, 9000)
    print("POrt", port)
    socketio.run(app, host='0.0.0.0',debug=True,port=port)
    User.server_running= False
    Alliance.server_running = False