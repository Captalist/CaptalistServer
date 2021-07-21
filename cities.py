import sqlite3

class Cities:
    active_cities = {}
    def __init__(self, id, name, level, max_pop, tax, pop, gov_id, oil, iron, water, food):
        self.id = id
        self.name = name
        self.level = level
        self.max_pop = max_pop 
        self.tax = tax
        self.pop = pop
        self.gov_id = gov_id
        self.iron = iron
        self.oil = oil
        self.water = water
        self.food = food
        Cities.active_cities[self.id] = self

    def change_max_pop(self, new_max_pop):
        query = "update cities set max_pop={} where id={}".format(
            new_max_pop, self.id
        )

        if self.change_db_data(query) == 'Ok':
            self.max_pop = new_max_pop
        else:
            return "Error line 27"

    def change_tax(self, new_tax):
        query = "update cities set tax={} where id={}".format(
            new_tax, self.id
        )
        
        if self.change_db_data(query) == 'Ok':
            self.tax = new_tax
        else:
            return "Error line 37"

    def change_db_data(self, query):
        conn = sqlite3.connect('server.db')
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        conn.close()

        return "Ok"

    def change_name(self, new_name):
        query = "update cities set name='{}' where id={}".format(
            new_name, self.id
        )

        if self.change_db_data(query) == 'Ok':
            self.name = new_name
        else:
            return "Error line 56"

    def change_level(self, new_level):
        query = "update cities set level={} where id={}".format(
            new_level, self.id
        )

        if self.change_db_data(query) == 'Ok':
            self.level = new_level
        else:
            return "Error line 67"

    def change_pop(self, new_pop):
        query = "update cities set pop={} where id={}".format(
            new_pop, self.id
        )

        if self.change_db_data(query) == 'Ok':
            self.pop = new_pop
        else:
            return "Error line 77"

    def change_gov_id(self, new_gov_id):
        query = "update cities set gov_id={} where id={}".format(
            new_gov_id, self.id
        )

        if self.change_db_data(query) == 'Ok':
            self.gov_id = new_gov_id
        else:
            return "Error line 86"

    def upgrade(self, money):
        money_needed = 1000
        level = self.level+1
        new_amount = money_needed +1 
        new_amount = new_amount ** level
        if money >= new_amount:
            self.change_max_pop(self.max_pop + 500)
            self.change_level(self.level + 1)
            return new_amount

        return "Not Enough"

    def get_tax(self):
        money = self.pop * 300

        new_amount = money * self.tax

        return new_amount + self.level

    def add_new_pop(self):
        rouns = 300

        new_rouns =  rouns * self.tax

        new_rouns = new_rouns + self.level

        pos_pop = self.max_pop - self.pop

        if pos_pop >= new_rouns:
            self.change_pop(self.pop + new_rouns)
            return self.pop + new_rouns

        self.change_pop(self.max_pop)
        return self.max_pop

    def __repr__(self):
        string = "id={}, name={}, level={}, max_pop={}, tax={}, pop={}, gov_id={}".format(self.id, self.name, self.level,
        self.max_pop, self.tax, self.pop, self.gov_id)
        return string

    def get_city_data(self):
        return {
            'id': self.id,
            'Name': self.name,
            'Level': self.level,
            'Max Population': self.max_pop,
            'Tax': self.tax,
            'Population': self.pop,
            'gov_id': self.gov_id,
            'iron': self.iron,
            'oil': self.oil,
            'water': self.water,
            'food': self.food
        } 
        
    def __call__(self):
        return {
            'id': self.id,
            'Name': self.name,
            'Level': self.level,
            'Max Population': self.max_pop,
            'Tax': self.tax,
            'Population': self.pop,
            'gov_id': self.gov_id,
            'iron': self.iron,
            'oil': self.oil,
            'water': self.water,
            'food': self.food
        } 

    def close(self):
        Cities.active_cities.pop(self.id)
        del self

    def change_iron(self, new_iron):
        query = "update cities set iron={} where id={}".format(
            new_iron, self.id
        )

        if self.change_db_data(query) == 'Ok':
            self.iron = new_iron
        else:
            return "Error line 170"

    def change_oil(self, new_oil):
        query = "update cities set oil={} where id={}".format(
            new_oil, self.id
        )

        if self.change_db_data(query) == 'Ok':
            self.oil = new_oil
        else:
            return "Error on line 180"

    def change_water(self, new_water):
        query = "update cities set water={} where id={}".format(
            new_water, self.id
        )

        if self.change_db_data(query) == 'Ok':
            self.water = new_water
        else:
            return "Error on line 190"

    def change_food(self, new_food):
        query = "update cities set food={} where id={}".format(
            new_food, self.id
        )

        if self.change_db_data(query) == 'Ok':
            self.food = new_food
        else:
            return "Error on line 200"