import sqlite3
from gov_classes import Government
from trade_classies import Trade

class Alliance:
  all_active_allies = {}
  trades = []
  server_running = True

  def __init__(self, id, creator, acceptor, army_trade, communication, trade, transport):
    self.id = id
    self.creator = Government.active_gov[creator]
    self.acceptor = Government.active_gov[acceptor]

    if army_trade == 1:
      self.army_trade = True
    else:
      self.army_trade == False

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

  def change_db(self, query):
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
    else:
      return "Trade Agreement has not been created"

  def start_trade_agreement(self, which: str):
    trades = {'army_trade': self.army_trade, 'communication': self.communication, 'trade': self.trade, 'transport': self.transport}
    
    if trades[which] == False:
      query = "update Alliance set {}={} where id={}".format(
        which, 1, self.id
      )
      self.change_db(query)
      self.__dict__[which] = 1
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
    return {'flag': self.acceptor.flag, 'name': self.acceptor.flag}

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