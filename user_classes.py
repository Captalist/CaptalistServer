import sqlite3

class User:
    # This will be used by other classes to tell whether or a not server running
    server_running=False
    # This is use to easily collect the currently active users.
    # Rather using sqlite quieres continuesly
    active_user={}
    def __init__(self, ids, name, password, email):
        # This is used for identification purposes
        self.ids=ids
        self.name=name
        self.password=password
        self.email=email

        print("New user online. name:", self.name)
        User.active_user[self.ids]= self

    def return_idetifications(self):
        return {'ids': self.ids, 'name': self.name, 'password': self.password, 
        'email':self.email}
    
    # To view user data
    def get_data(self):
        return self.return_idetifications()

    # Saves all user data
    def save(self):
        self.change_name(self.name)
        self.change_password(self.password)
        self.change_email(self.email)

    # This function does not actually remove the user from the database. Just from active_users
    def delete(self):
        self.save()
        User.active_user.pop(self.ids)
        users = self.name
        del self
        print(users, "is offline")


    def change_name(self, name):
        conn = sqlite3.connect('server.db')
        cursor= conn.cursor()
        query = """update user set name='{}' where name='{}'""".format(name, self.name)
        try:
            cursor.execute(query)
            conn.commit()
            conn.close()
            self.name=name 
            return "Success"
        except Exception as e:
            print(e)
            return "Issue"

    def change_password(self, password):
        conn = sqlite3.connect('server.db')
        cursor= conn.cursor()
        query = """update user set password='{}' where name='{}'""".format(password, self.name)
        try:
            cursor.execute(query)
            conn.commit()
            conn.close()
            self.password=password 
            return "Success"
        except Exception as e:
            print(e)
            return "Issue"

    def change_email(self, email):
        conn = sqlite3.connect('server.db')
        cursor= conn.cursor()
        query = """update user set email='{}' where name='{}'""".format(email, self.name)
        try:
            cursor.execute(query)
            conn.commit()
            conn.close()
            self.email=email
            return "Success"
        except Exception as e:
            print(e)
            return "Issue"

    def __repr__(self):
        string = """ids={}, name={}, password={}, email={}""".format(
            self.ids, self.name, self.password, self.email
        )
        return string

    def login(name, password):
        conn = sqlite3.connect('server.db')
        cursor = conn.cursor()
        try:
            query = """select * from user where name='{}' and password='{}'""".format(name, password)
            print(query)
            cursor.execute(query)
            users = cursor.fetchone()
            if users == None:
                raise ValueError
            if users[0] not in User.active_user:
                User(ids=users[0], name=users[1], password=users[2], email=users[3])
            print(User.active_user[users[0]])
            conn.close()
            return users[0]
        except Exception as e:
            print(e)
            conn.close()
            return "Name or Password incorrect"

    def signup(name, password, email):
        conn = sqlite3.connect('server.db')
        cursor= conn.cursor()
        query="""select id from user where name ='{}'""".format(name)
        # We need this to return an error to make sure the name is not already
        # taken
        try:
            cursor.execute(query)
            ids = cursor.fetchone()
            if ids != None:
                return "Name is taken"
            raise ValueError('Name is not taken')
        except Exception as e:
            # Name is not taking
            print(e)
            try:
                query = """insert into user (name, password, email) 
                values ('{}','{}','{}')""".format(name, password, email)
                cursor.execute(query)
                conn.commit()
                conn.close()
                print('logining')
                ids= User.login(name, password)
                return ids
            except Exception as e:
                print(e)
                return "Issue"
    
    @staticmethod
    def does_it_exist(cls):
        try:
            test = User.active_user[cls.ids]
            return True
        except KeyError:
            return False
