import sqlite3
from gov_classes import Government
from trade_classies import Trade

class Alliance:
  all_active_allies = {}
  trades = []

  def __init__(self, id, creator, acceptor, army_trade, communication, trade, transport):
    self.id = id
    self.creator = creator
    self.acceptor = acceptor

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

  def create_trade(self, to, from_who, item, amount, cost, times):
    to = Government.active_gov[to]
    from_who = Government.active_gov[from_who]
    index = len(Alliance.trades)

    Alliance.trades.append(Trade(to, from_who, item, amount, cost, times, index))

    return "Trade Created Successfully"

  def run_trade():
    while True:
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