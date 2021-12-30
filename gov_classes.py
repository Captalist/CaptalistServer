from user_classes import *

class Government:
    active_gov = {}

    def __init__(self, ids, name, flag, pop, money, owner, oil, iron, food, water):
        # Identification 
        self.ids = ids
        self.name = name
        self.flag = flag
        self.pop = pop
        self.money = money
        try:
            self.owner = User.active_user[owner] 
        except KeyError:
            self.owner = owner

        # Resources
        self.oil = oil
        self.iron = iron
        self.food = food
        self.water = water

        Government.active_gov[self.ids] = self

    def have_enough(self, dicts, how_many):
      """
        Used to see there is enough resources
      """
      new_dicts= {'oil': self.oil, 'iron': self.iron, 'food': self.food, 'water': self.water}

      for d in dicts:
        if new_dicts[d] < dicts[d] * how_many:
          return False
      
      return True

    def __repr__(self):
        string = """
            ids={}, name={}, flag={}, pop={}, money={}
        """.format(self.ids, self.name, self.flag, self.pop, self.money)
        return string
        
    def return_data(self):
      return {
        'id': self.ids, 
        'name': self.name,
        'flag': self.flag,
        'population': self.pop,
        'money': self.money,
        'oil': self.oil,
        'iron': self.iron,
        'food': self.food,
        'water': self.water
      }

    def close(self):
      Government.active_gov.pop(self.ids, None)
      del self

    def s_q(self, query, all=False, many=False, how_many=5, one=False):
        """
            Runs a sql query
        """
        conn = sqlite3.connect('server.db')
        cursor = conn.cursor()
        cursor.execute(query)
        if all:
            returns= cursor.fetchall()
        elif many:
            returns= cursor.fetchmany(size=how_many)
        elif one:
            returns = cursor.fetchone()
        conn.close()
        return returns

    def change_q(self, query):
        """
            Updates a database using query
        """
        try:
            conn = sqlite3.connect('server.db')
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            conn.close()
        except Exception as e:
            print(e)

    def change_name(self, new_):
        query = """update Countries set name='{}' where id={}""".format(new_, self.ids)
        self.change_q(query)
        self.name= new_
    
    def change_flag(self, new_):
        query = """udpate Countries set flag='{}' where id={}""".format(new_, self.ids)
        self.change_q(query)
        self.flag = new_

    def change_owner(self, new_):
        query = """update Countries set owner={} where id={}""".format(new_, self.ids)
        self.change_q(query)
        self.owner = User.active_user[new_] or new_

    def change_oil(self, new_):
        query = """update Countries set oil={} where id={}""".format(new_, self.ids)
        self.change_q(query)
        self.oil = new_

    def add_oil(self, amount):
        new = self.oil + amount
        self.change_oil(new)

    def remove_oil(self, amount):
        new = self.oil - amount
        self.change_oil(new)

    def change_iron(self, new_):
        query = """update Countries set iron={} where id={}""".format(new_, self.ids)
        self.change_q(query)
        self.iron = new_

    def add_iron(self, amount):
        new = self.iron + amount
        self.change_iron(new)

    def remove_iron(self, amount):
        new = self.iron - amount
        self.change_iron(new)
    
    def change_food(self, new_):
        query = """update Countries set food={} where id={}""".format(new_, self.ids)
        self.change_q(query)
        self.food = new_

    def add_food(self, amount):
        new = self.food + amount
        self.change_food(new)

    def remove_food(self, amount):
        new = self.food - amount
        self.change_food(new)

    def change_water(self, new_):
        query = """update Countries set water={} where id={}""".format(new_, self.ids)
        self.change_q(query)
        self.water = new_

    def add_water(self, amount):
        new = self.water + amount
        self.change_water(new)
    
    def remove_water(self, amount):
        new = self.water + amount
        self.change_water(new)

    def change_pop(self, new_):
        query = """update Countries set pop={} where id={}""".format(new_, self.ids)
        self.change_q(query)
        self.pop = new_

    def add_pop(self, amount):
        new = self.pop + amount
        self.change_pop(new)

    def remove_amount(self, amount):
        new = self.pop + amount
        self.change_pop(new)

    def change_money(self, new_):
      """
        Changes amount of money a government have
      """
      query = """update Countries set money={} where id={}""".format(new_, self.ids)
      self.change_q(query)
      self.money = new_

    def add_money(self, amount):
        new = self.money + amount
        self.change_money(new)
    
    def remove_money(self, amount):
      """
        Changes amount of money a government have
      """
      new = self.money - amount
      self.change_money(new)

    @staticmethod
    def create_alliance_request(creator, acceptor):
      """
        Adds an alliance request to database
      """
      conn = sqlite3.connect('server.db')
      cursor = conn.cursor()
        
      query= "insert into alliance_request (creator, acceptor) values ({},{})".format(creator, acceptor)

      
      cursor.execute(query)  
      conn.commit()
      conn.close()

    @staticmethod
    def create_alliance(creator, acceptor):
      """
        Adds alliance to database and returns the newly add allaince id
      """
      query = "insert into Alliance (creator, acceptor, army_trade, communication, trade, transport) values ({}, {}, 0, 0, 0, 0)".format(creator, acceptor)

      conn = sqlite3.connect('server.db')
      cursor = conn.cursor()
      cursor.execute(query)

      conn.commit()

      lastrow = cursor.lastrowid

      conn.close()
      
      return lastrow
