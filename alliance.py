import sqlite3
from gov_classes import Government
from trade_classies import Trade

class Alliance:
  all_active_allies = {}
  trades = []
  server_running = True

  def __init__(self, id, creator, acceptor, army_trade, communication, trade, transport):
    self.id = id
    try:
      self.creator = Government.active_gov[creator]
      self.acceptor = Government.active_gov[acceptor]
      if army_trade == 1:
        self.army_trade = True
      else:
        self.army_trade = False

      if communication == 1:
        self.communication = True
      else:
        self.communication = False

      if trade == 1:
        self.trade = True
      else:
        self.trade = False

      if transport == 1:
        self.transport = True
      else:
        self.transport = False

      Alliance.all_active_allies[self.id] = self
      print(self)
    except KeyError:
      self.delete()

  def delete(self):
    try:
      Alliance.all_active_allies.pop(self.id)
    except KeyError:
      pass
    del self

  def __repr__(self):
    string = "New Alliance created between {} and {}".format(self.acceptor.name,self.creator.name)
    return string

  def change_db(self, query):
    conn = sqlite3.connect('server.db')
    cursor =  conn.cursor()
    cursor.execute(query)
    conn.commit()
    conn.close()

  @staticmethod
  def changing_db(query):
    conn = sqlite3.connect('server.db')
    cursor =  conn.cursor()
    cursor.execute(query)
    conn.commit()
    conn.close()

  def cancel_trade_agreement(self, which: str):
    trades = {'army_trade': self.army_trade, 'communication': self.communication, 'trade': self.trade, 'transport': self.transport}

    if trades[which] == True:
      query = "update Alliance set {}={} where id={}".format(
        which, 0, self.id
      )
      self.change_db(query)
      self.__dict__[which] = 0
      return "Trade Agreement has been canceled"
    else:
      return "Trade Agreement has not been created"

  def return_data_and_trade_deals(self, country_id):
    return {  **{
      'Army Trade': self.army_trade,
      'Transport': self.transport,
      'Communication': self.communication,
      'Trade': self.trade,     
      }, 
      **self.return_data(country_id)
    }

  def start_trade_agreement(self, which: str):
    trades = {'army_trade': self.army_trade, 'communication': self.communication, 'trade': self.trade, 'transport': self.transport}
    
    if trades[which] == False:
      query = "update Alliance set {}={} where id={}".format(
        which, 1, self.id
      )
      self.change_db(query)
      self.__dict__[which] = 1
      return "Trade Agreement has been created"
    else:
      return "Trade Agreement has already being created"

  def self_destruct(self):
    query = "delete from Alliance where id={}".format(self.id)
    self.change_db(query)
    Alliance.all_active_allies.pop(self.id)
    del self

  def close_alliance(self):
    Alliance.all_active_allies.pop(self.id)
    del self

  def return_data(self, country_id):
    if self.creator.ids != country_id:
      return {'flag': self.creator.flag, 'name': self.creator.name}
    return {'flag': self.acceptor.flag, 'name': self.acceptor.name}

  def create_trade(self, to, from_who, item, amount, cost, times):
    to = Government.active_gov[to]
    from_who = Government.active_gov[from_who]
    index = len(Alliance.trades)

    Alliance.trades.append(Trade(to, from_who, item, amount, cost, times, index))

    return "Trade Created Successfully"

  @staticmethod
  def run_trade():
    while Alliance.server_running:
      index = 0
      for trade in Alliance.trades:
        statement = trade.carry_out_trade(trade.item)
        if statement == 'Trade Ended':
          Alliance.trade.pop(index)
          del trade

        elif statement == 'Government offline':
          Alliance.trade.pop(index)
          del trade

        index += 1

  @staticmethod
  def is_it_active(ids):
    try:
      ally = Alliance.all_active_allies[ids]
      return True
    except KeyError:
      return False

  @staticmethod
  def alliance_data(country_id):
    query = "select id from Alliance where acceptor={} or creator={}".format(country_id, country_id)
    conn = sqlite3.connect('server.db')
    cursor=conn.cursor()

    cursor.execute(query)

    alliances = cursor.fetchall()

    allies_Data = {}

    for allies in alliances:
      try:
        allies_Data[allies[0]] = Alliance.all_active_allies[allies[0]].return_data(country_id)
      except Exception as e:
        print(e)
    
    return allies_Data

  @staticmethod
  def insert_into_db(query):
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    conn.close()

  @staticmethod
  def trade_request_already_exist(type_trade, creator_id, acceptor_id, alliance_id):
    real_name = {'army_trade': 'army_trade',
    'transport_trade': 'transport', 
    'com_trade': 'communication', 
    'trade': 'trade'}

    query = "select {} from Alliance where id={}".format(real_name[type_trade], alliance_id)
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()
    cursor.execute(query)

    exist_already = cursor.fetchone()[0]

    if exist_already == 1:
      return True
    
    real_tb = {'army_trade': 'army_trade_request',
    'transport_trade': 'transport_request', 
    'com_trade': 'communication_trade_requests', 
    'trade': 'trade_request'}

    query = "select id from {} where creator={} and alliance={}".format(
      real_tb[type_trade], creator_id, alliance_id
    )
    cursor.execute(query)

    exist_already = cursor.fetchone()

    if exist_already != None:
      return True

    query = "select id from {} where creator={} and alliance={}".format(
      real_tb[type_trade], acceptor_id, alliance_id
    )
    cursor.execute(query)

    exist_already = cursor.fetchone()

    if exist_already != None:
      return True

    return False

  @staticmethod
  def create_army_trade_request(alliance_id, creator_id, acceptor_id):
    query = "insert into army_trade_request (creator, acceptor, alliance) values ({}, {}, {})".format(creator_id, acceptor_id, alliance_id)

    Alliance.insert_into_db(query)

  @staticmethod
  def create_communication_trade_requests(alliance_id, creator_id, acceptor_id):
    query = "insert into communication_trade_requests (creator, acceptor, alliance) values ({}, {}, {})".format(creator_id, acceptor_id, alliance_id)

    Alliance.insert_into_db(query)

  @staticmethod
  def create_trade_request(alliance_id, creator_id, acceptor_id):
    query = "insert into trade_request (creator, acceptor, alliance) values ({}, {}, {})".format(creator_id, acceptor_id, alliance_id)

    Alliance.insert_into_db(query)

  @staticmethod
  def create_transport_request(alliance_id, creator_id, acceptor_id):
    query = "insert into transport_request (creator, acceptor, alliance) values ({}, {}, {})".format(creator_id, acceptor_id, alliance_id)

    Alliance.insert_into_db(query)

  @staticmethod
  def create_trade_deal(alliance_id, trade_type, acceptor_name):
    query = 'select id from Countries where name="{}"'.format(acceptor_name)
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()
    cursor.execute(query)

    acceptor_id = cursor.fetchone()

    if acceptor_id == None:
      return "Country does not exist"

    query = "select creator, acceptor from Alliance where id={}".format(alliance_id)

    cursor.execute(query)

    all_d = cursor.fetchone()

    conn.close()

    if all_d == None:
      return "Alliance no longer exist"

    if all_d[0] == acceptor_id[0]:
      creator_id =  all_d[1]
    else:
      creator_id = all_d[0]

    impor_func = {'army_trade': Alliance.create_army_trade_request,
    'transport_trade': Alliance.create_transport_request, 
    'com_trade': Alliance.create_communication_trade_requests, 
    'trade': Alliance.create_trade_request}
    
    if Alliance.trade_request_already_exist(trade_type, creator_id, acceptor_id[0], alliance_id) == False:

      impor_func[trade_type](alliance_id, creator_id, acceptor_id[0])

      return "Trade Request has been sent"
    else:
      return "Trade request already sent"

  @staticmethod
  def getAllianceTradeRequests(country_id):
    trade_list = {'army_trade_request': 'Army Trade',
    'transport_request': 'Transport Trade', 
    'communication_trade_requests': 'Communication Trade', 
    'trade_request': 'Trade'}

    all_different_trade_request = {'Army Trade': [], 'Transport Trade': [], 
    'Communication Trade': [], 'Trade': []}

    for keys in trade_list:
      query = "select * from {} where acceptor={}".format(keys, country_id)
      conn = sqlite3.connect('server.db')
      cursor = conn.cursor()
      cursor.execute(query)

      data = cursor.fetchone()

      if data != None:
        query = "select name from Countries where id={}".format(data[1])
        cursor.execute(query)

        name = cursor.fetchone()[0]

        all_different_trade_request[trade_list[keys]].append({
          'data': data,
          'statement': Alliance.generate_trade_request_statement(keys, name)
        })

    return all_different_trade_request


  @staticmethod
  def generate_trade_request_statement(trade_type, name):
    statement = "Unknown trade type"
    
    if trade_type == 'army_trade_request':
      statement = f'{name} is requesting to create a Army Trade which will cost you 300 Capital to create and 600 Capital to manage. Are you sure you want to accept?'
    elif trade_type == 'transport_request':
      statement = f'{name} is requesting to create a Transport Trade which will cost you 1000 Capital to create and 2000 Capital to manage. Are you sure you want to accept?'
    elif trade_type == 'communication_trade_requests':
      statement = f'{name} is requesting to create a Communication Trade which will cost you 2500 Capital to create and 5000 Capital to manage. Are you sure you want to accept?'
    elif trade_type == 'trade_request':
      statement = f'{name} is requesting to create a Trade which will cost you 5000 Capital and 7000 Capital to manage. Are you sure you want to accept?'

    return statement
    
  @staticmethod
  def deny_alliance_trade_deal(**kwargs):
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()

    trade_list= {'Army Trade': 'army_trade_request', 
    "Transport Trade": 'transport_request',
    'Communication Trade': 'communication_trade_requests',
    'Trade':'trade_request'
    }

    trade_type = trade_list[kwargs['trade_type']]
    query = "select id from {} where id={}".format(trade_type, kwargs['id'])
    cursor.execute(query)

    exist = cursor.fetchone()

    if exist == None:
      return "Trade Request No longer exist"

    query = "delete from {} where id={}".format(trade_type, kwargs['id'])
    cursor.execute(query)
    conn.commit()
    conn.close()

    return "Trade Request No longer exist"


  @staticmethod
  def accept_alliance_trade_deal(**kwargs):
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()

    trade_list= {'Army Trade': 'army_trade_request', 
    "Transport Trade": 'transport_request',
    'Communication Trade': 'communication_trade_requests',
    'Trade':'trade_request'
    }

    trade_type = trade_list[kwargs['trade_type']]
    query = "select id from {} where id={}".format(trade_type, kwargs['id'])
    cursor.execute(query)

    exist = cursor.fetchone()

    if exist == None:
      return "Trade Request No longer exist"

    query = "delete from {} where id={}".format(trade_type, kwargs['id'])
    cursor.execute(query)
    conn.commit()

    trades = {
      'Army Trade': 'army_trade',
      "Transport Trade": 'transport',
      'Communication Trade': 'communication',
      'Trade': 'trade'
    }

    try:
      
      ally = Alliance.all_active_allies[kwargs['alliance']]
      return ally.start_trade_agreement(trades[kwargs['trade_type']])

    except KeyError:
      query = "update Alliance set {}={} where id={}".format(
        trades[kwargs['trade_type']], 1, kwargs['alliance']
      )

      Alliance.changing_db(query)
      return "Trade Agreement has been created"

  @staticmethod
  def end_trade_deal(alliance_id, trade_type):
    trades = {
      'army_trade':'army_trade',
      'transport_trade':'transport',
      'com_trade': 'communication',
      'trade': 'trade'
    }

    try:
      ally = Alliance.all_active_allies[alliance_id]
      return ally.cancel_trade_agreement(trades[trade_type])
    except KeyError:
      query = "update Alliance set {}={} where id={}".format(
        trades[trades[trade_type]], 0, alliance_id
      )

      Alliance.changing_db(query)
      return "Trade Agreement has been canceled"

  @staticmethod
  def get_list_ally_rooms(country):
    query = "select id from Alliance where creator={} or acceptor={}".format(country, country)

    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()

    cursor.execute(query)

    rooms = []

    rooms_id = cursor.fetchall()

    for room in rooms_id:
      rooms.append("AllianceRoom" + str(room[0]))

    conn.close()

    return rooms

  @staticmethod
  def get_alliance_end_statement(ally_id, trade_type, country):
    who = None
    cencelor = None

    # We first try the easy way of retrieving names, using the alliance reference
    try:
      alliance =  Alliance.all_active_allies[ally_id]
      if alliance.creator.ids == country:
        cencelor = alliance.creator.name
        who = alliance.acceptor.name
      else:
        cencelor = alliance.acceptor.name
        who = alliance.creator.name

    except KeyError:
      # If alliance is not online or "activated" we then go the hard way by making a query to the database asking for the needed data

      query = "select creator, acceptor from Alliance where id={}".format(ally_id)
      conn = sqlite3.connect('server.db')
      cursor = conn.cursor()

      cursor.execute(query)

      names = cursor.fetchone()

      if names[0] == country:
        query = "select name from Countries where id={}".format(names[0])

        cursor.execute(query)

        cencelor =  cursor.fetchone()[0]

        query = "select name from Countries where id={}".format(names[1])

        cursor.execute(query)

        who =  cursor.fetchone()[0]

      else:
        query = "select name from Countries where id={}".format(names[1])

        cursor.execute(query)

        cencelor =  cursor.fetchone()[0]

        query = "select name from Countries where id={}".format(names[0])

        cursor.execute(query)

        who =  cursor.fetchone()[0]

      conn.close()

    trades = {
      'army_trade':'Army Trade',
      'transport_trade':'Transport Trade',
      'com_trade': 'Communication Trade',
      'trade': 'Trade'
    }

    statement = "{} has canceled {} with {}".format(cencelor, trades[trade_type], who)

    return statement

