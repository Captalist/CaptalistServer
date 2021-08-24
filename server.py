from gov_classes import *
from cities import Cities
from alliance import Alliance
from army import Army
import requests 

class Server:
    servers = {}

    def __init__(self, id, owner_id, name, code):
        self.id = id
        self.owner_id = owner_id
        self.name = name
        self.code = code
        self.Users = {}
        self.countries = {} # Returns in dict format
        self.city = {}
        Server.servers[id] = self
        print(self)

    def __repr__(self):
        string = """Server: id={}, owner_id={}, name={}, code={}
        """.format(self.id, self.owner_id, self.name, self.code)
        return string

    def get_user_cities(self, user):
        for gov in self.countries.values():
            if type(gov.owner) == int and gov.owner == user:
                cities = {}
                for city in self.city.values():
                    if city.gov_id == gov.ids:
                        data = city()
                        cities[city.id] = data
                return cities
            elif type(gov.owner) == User and gov.owner.ids == user:
                cities = {}
                for city in self.city.values():
                    if city.gov_id == gov.ids:
                        data = city()
                        cities[city.id] = data
                return cities
        
        return "User does not exist"

    @staticmethod
    def get_server_user_cities(server, user):
        try:
            servers = Server.servers[server]
        except KeyError:
            return {'return': 'Server does not exist'}

        returns = servers.get_user_cities(user)
        if type(returns) == str:
            return {'return': returns}

        for key in returns:
            returns[key] = returns[key]()
        return {'return': 'Success', 'data': returns}

    def get_country_data(self, user_id):
        for country in self.countries.values():
            if type(country.owner) == int and country.owner == user_id:
                return country.return_data()
            elif type(country.owner) == User and country.owner.ids == user_id:
                return country.return_data()

        return "User not found"

    @staticmethod
    def get_count_data(server_id, user_id):
        try:
            server = Server.servers[server_id]
        except KeyError:
            return {'return': 'Server not found'}

        returns = server.get_country_data(user_id)
        if type(returns) == str:
            return {'return': returns}

        data = {'return': 'Success'}
        return {**data, **returns}

    def create_new_city(self, user_id, city_name):
      query = 'select id from Countries where server={} and owner={}'.format(self.id, user_id)
      conn = sqlite3.connect('server.db')
      cursor = conn.cursor()
      cursor.execute(query)
      
      c_id = cursor.fetchone()

      if c_id == None:
        return "Country does not exist"

      query = """
      insert into cities (name, level, max_pop, tax, pop, gov_id, oil, iron, water, food) values ('{}', 0, 100, 0.25, 100, {}, 0, 0, 0, 0)
      """.format(city_name, c_id[0])
      try:
        cursor.execute(query)
        conn.commit()
        query = "select * from cities where name='{}' and gov_id={}".format(city_name, c_id[0])
        cursor.execute(query)
        new_da = cursor.fetchone()
        new_city = Cities(*new_da)
        self.city[new_city.id] = new_city

        conn.close()
        return ["Created", self.countries[c_id[0]].name]
      except Exception as e:
        word = 'Query for creating new city:' +'\n'+ query
        return word

    @staticmethod
    def form_new_city(server, user_id, city_name):
      try:
        servers = Server.servers[server]
        returns =  servers.create_new_city(user_id, city_name)
        if type(returns) == list:
          return {'returns': returns[0], 'country':returns[1]}
        return {'returns': servers.create_new_city(user_id, city_name)}
      except KeyError:
        return {'returns': 'Server does not exist'}
      

    def create_country(self, country_name, country_flag, user_id):
        query = "select id from Countries where name='{}'".format(country_name)
        conn = sqlite3.connect('server.db')
        cursor = conn.cursor()
        cursor.execute(query)

        if cursor.fetchone() != None:
            return "Name Taken"

        if country_flag.startswith('https://flag-designer.appspot.com/'):
            flag = requests.get(country_flag)
            if flag:
                try:
                    query = """insert into Countries (name, flag, pop, money, 
                    owner, oil, iron, food, water, server)  
                    values ('{}', '{}',{}, {}, {}, {},{}, {}, {}, {})""".format(
                        country_name, flag.text, user_id, 100, 100, 100, 100,
                        100, 100, self.id
                    )
                    cursor.execute(query)
                    conn.commit()

                    query = "select id from Countries where name='{}' and flag='{}' and server={}".format(
                        country_name, flag.text, self.id
                    )
                    cursor.execute(query)
                    ids =  cursor.fetchone()

                    query = """insert into cities (name, level, max_pop, tax, pop, gov_id, oil, iron, water, food) 
                    values ('{}', 0, 100, 0.25, 100, {}, 0, 0, 0, 0)""".format(
                        country_name+' city', ids[0]
                    )
                    cursor.execute(query) 
                    conn.commit()
                    conn.close()
                    if ids != None:
                        return {"Server_id": ids}
                    return 'Errror'
                except Exception as e:
                    print(e)
                    return "Error"
            return "Problem Getting Flag From URL"
        return "Invalid URL"

    @staticmethod
    def create_new_country(server_id, country_name, country_flag, user_id):
        try:
            ret = Server.servers[server_id]
        except KeyError:
            return {'return': 'Server Does Not Exist'}

        rets = ret.create_country(country_name, country_flag, user_id)
        return {'return': rets}

    @staticmethod
    def user_sign_out(user_id):
      query = "select id,server from countries where owner={}".format(user_id)
      conn = sqlite3.connect('server.db')
      cursor = conn.cursor()

      cursor.execute(query)

      count_d = cursor.fetchall()

      server_and_Count = []

      for country in count_d:
        query = "select id from Alliance where creator={} or acceptor={}".format(country[0], country[0])
        cursor.execute(query)
        alliance_d = cursor.fetchall()

        for alliance in alliance_d:
          try:
            Alliance.all_active_allies[alliance[0]].delete()
          except KeyError:
            continue

        query = "select id from cities where gov_id={}".format(country[0])
        cursor.execute(query)
        cities_d = cursor.fetchall()

        for city in cities_d:
          try:
            Server.servers[country[1]].city.pop(city[0])
            Cities.active_cities[city[0]].close()
          except KeyError:
            continue

        # Change army name later
        query = "select id from Army where owner={}".format(country[0])
        cursor.execute(query)

        army_d = cursor.fetchall()

        for army in army_d:
          try:
            Army.active_armies[army[0]].close()
          except KeyError:
            continue

        try:
          Server.servers[country[1]].countries.pop(country[0])
          Server.servers[country[1]].Users.pop(user_id)
          server_and_Count.append({
            'room': str(country[1]),
            'Country_Name': Government.active_gov[country[0]].name
          })
          Government.active_gov[country[0]].close()
        except KeyError:
          continue

      User.active_user[user_id].delete()
      return server_and_Count

    @staticmethod
    def run():
        query = "select * from servers"
        conn = sqlite3.connect('server.db')
        cursor = conn.cursor()
        cursor.execute(query)
        servers =  cursor.fetchall()
        for server in servers:
            Server(*server)

        print("All Server Activated")

    @staticmethod
    def server_data(user_id):
        query = "select server from countries where owner={}".format(user_id)
        conn = sqlite3.connect('server.db')
        cursor = conn.cursor()
        cursor.execute(query)

        server_dat = cursor.fetchall()
        server_data = {'You_Own':[], 'SomeOne_Else_Own':[]}

        if server_dat != None:
            for servers in server_dat:
                server = Server.servers[servers[0]]

                if server.owner_id == user_id:
                    server_data['You_Own'].append({'Name': server.name, 'Code': server.code, 'Count': len(server.Users), 'server_id': server.id})
                else:
                    query = "select name from user where id={}".format(server.owner_id)
                    cursor.execute(query)
                    name = cursor.fetchone()[0]
                    server_data['SomeOne_Else_Own'].append({'Name': server.name, 'Code': server.code, 'Count': len(server.Users), 'Owner': name, 'server_id': server.id})

        conn.close()
        return server_data

    def get_user_countries(self, user_id):
        count = {}
        conn = sqlite3.connect('server.db')
        cursor = conn.cursor()
        query = "select * from countries where server={} and owner={}".format(self.id, user_id)

        cursor.execute(query)
        countries = cursor.fetchall()
        conn.close()

        if countries == None:
            return None

        for countries in countries:
            count[countries[0]] = Government(*countries[:-1])
            self.countries[countries[0]] = count[countries[0]]

        return count

    def get_user_cities(self, gov_id):
        count = {}
        conn = sqlite3.connect('server.db')
        cursor=  conn.cursor()
        query = "select * from cities where gov_id={}".format(gov_id)
        cursor.execute(query)
        cities = cursor.fetchall()
        conn.close()

        if cities == None:
            return None

        for city in cities:
            count[city[0]] = Cities(*city)
            self.city[city[0]] = count[city[0]]

        return count
    
    def get_user_alliances(self, gov_id):
      count = {}
      conn = sqlite3.connect('server.db')
      cursor = conn.cursor()
      query = "select * from Alliance where creator={} or acceptor={}".format(gov_id, gov_id)
      cursor.execute(query)
      allies = cursor.fetchall()
      conn.close()
      if allies == None:
        return None

      for ally in allies:
        if not Alliance.is_it_active(ally[0]):
          print("In ALliance creation", ally)
          Alliance(*ally)

        count[ally[0]] = ally

      return count  

    def get_user_armies(self, gov_id):
      count = {}
      conn = sqlite3.connect('server.db')
      cursor = conn.cursor()

      # Change army name later
      query = "select * from Army where owner={}".format(gov_id)
      cursor.execute(query)

      armies =  cursor.fetchall()

      conn.close()

      if armies == None:
        return None

      for army in armies:
        Army(*army)

    @staticmethod
    def create_new_server(user_id, name, code):
        conn = sqlite3.connect('server.db')
        cursor = conn.cursor()
        query = "select id from servers where name='{}'".format(name)
        cursor.execute(query)

        if cursor.fetchone() != None:
            return {'return':"Server Already Exists"}

        query = "insert into servers (owner, name, code) values ('{}', '{}', '{}')".format(
            user_id, name, code
        )

        cursor.execute(query)
        conn.commit()

        query = "select id from servers where name='{}' and code='{}' and owner='{}'".format(
            name, code, user_id
        )

        cursor.execute(query)
        server_id = cursor.fetchone()

        if server_id == None:
            return {'return':"Problem Creating Server"}

        Server(server_id[0], user_id, name, code)

        conn.close()

        return {'return':"Server Created", 'server_id': server_id}


    @staticmethod
    def leave_server(id, user_id):
        Server.servers[id].Users.pop(user_id)

        for key, val in Server.servers[id].get_user_countries(user_id).items():
            val.close()
            Server.servers[id].countries.pop(key)
            re = Server.servers[id].get_user_resources(key)
            for re_i in re:
                for i_k, i_val in re[re_i]:
                    i_val.self_destruct()
                    Server.servers[id].resources[re_i].pop(i_k)

    @staticmethod
    def join_server(id, user_id):
        try:
          Server.servers[id].Users[user_id] = User.active_user[user_id]
        except KeyError:
          return "User not Logged In"
            
        """Activating Countries AND Resources"""
        user_countries = Server.servers[id].get_user_countries(user_id)
        
        if user_countries == None:
            return None 

        U_C = {}

        for key, val in user_countries.items():
          U_C[key] = val.return_data()
          Server.servers[id].get_user_cities(key)
          Server.servers[id].get_user_alliances(key)
          Server.servers[id].get_user_armies(key)
        
        return U_C

    def add_new_ally(self, ally_name, country_id):
      query = "select id from Countries where name='{}'".format(ally_name)

      conn = sqlite3.connect('server.db')
      cursor = conn.cursor()
      cursor.execute(query)

      ally_id = cursor.fetchone()

      if ally_id == None:
        return "Country does not exist"

      query = "select id from alliance_request where creator={} and acceptor={}".format(country_id, ally_id[0])
      print(query)
      cursor.execute(query)

      ans = cursor.fetchone()

      if ans != None:
        return "Request has already been sent"

      query = "select id from alliance_request where creator={} and acceptor={}".format(ally_id[0], country_id)

      cursor.execute(query)

      ans = cursor.fetchone()

      if ans != None:
        return "Request has already been sent"

      conn.close()

      Government.create_alliance_request(country_id, ally_id[0])

      return "Request sent"

    def getAllianceRequest(self, country_id):
      query = "select * from alliance_request where acceptor={}".format(country_id)
      conn = sqlite3.connect('server.db')
      cursor = conn.cursor()
      cursor.execute(query)

      all_request =  cursor.fetchall()
      all_requests = {}

      for request in all_request:
        query = "select name from Countries where id={}".format(request[1])
        cursor.execute(query)

        name = cursor.fetchone()[0]
        statement = "{} wants to form an alliance".format(name)
        data =  [*request]
        print(data)
        all_requests[request[0]] = {'data':data, 'name': name, 'statement': statement}

      return all_requests

    def acceptAllianceRequest(self, acceptor, creator):
      try:
        all_acceptor = Government.active_gov[acceptor]
        all_creator =  Government.active_gov[creator]
        query = "delete from alliance_request where acceptor={} and creator={}".format(acceptor, creator)

        conn = sqlite3.connect('server.db')
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        conn.close()

        row_id = Government.create_alliance(creator, acceptor)
      except KeyError:
        query = "delete from alliance_request where acceptor={} and creator={}".format(acceptor, creator)

        conn = sqlite3.connect('server.db')
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        conn.close()

        row_id = Government.create_alliance(creator, acceptor)
        return "One of the government is not on. Alliance will be activated when they come on"

      Alliance(row_id, creator, acceptor, 0, 0, 0, 0)

      return "Success"

    def denyAllianceRequest(self, acceptor, creator):
      query = "delete from alliance_request where acceptor={} and creator={}".format(acceptor, creator)

      conn = sqlite3.connect('server.db')
      cursor = conn.cursor()
      cursor.execute(query)
      conn.commit()
      conn.close()

      return "Success"
