from gov_classes import *
from cities import Cities
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

                    query = """insert into cities (name, level, max_pop, tax, pop, gov_id) 
                    values ('{}', 0, 100, 0.25, 100, {})""".format(
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
        """
            This will have to be a thread because it takes to long
            First Loops through online servers and gets all the server
            then loops through each server online users and checks for the user
            If the user is found it loops through server gov and see if 
            the gov belongs to the user and if it does. Loops through
            the server resources and see if resources belongs to gov 
            if it does it loops through resources belonging to gov and
            remove that resource from server
            then deletes all the gov belonging to user and then finnally 
            deletes the user
        """
        for server in Server.servers.values():
            for user, server_user in server.users.items():
                if server_user.id == user_id:
                    for key, server_gov in server.countries.items():
                        if server_gov.owner == user_id or server_user:
                            server.countries.pop(key)
                            for city in server.city.values():
                                if city.gov_id == server_gov.ids:
                                    city.close()
                            server_gov.close()
                    server.users.pop(user)
                    user_name = server_user.name
                    server_user.delete()
                    print("Signing Out:", user_name)

        # This is incase the user did not join any servers 
        # But was still online; 
        try:
            actual_user = User.active_user[user_id]
            user_name =  actual_user.name
            actual_user.delete()
            print("Signing Out:", user_name)
        except KeyError:
            pass

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
        
        return U_C
