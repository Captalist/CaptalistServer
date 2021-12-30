from cities import Cities
from gov_classes import Government, sqlite3
import weakref
import gc

class ArmyUnitsTransactions(object):
  def __init__(self, value: int):
    self.value = value

  def __add__(self, other):
    if type(other) == ArmyUnitsTransactions:
      return ArmyUnitsTransactions(self.value + other.value)
    return ArmyUnitsTransactions(self.value + other)
  
  def __sub__(self, other):
    if type(other) == ArmyUnitsTransactions:
      if self.value - other.value >= 0:
        return ArmyUnitsTransactions(self.value - other.value)
      else:
        return ArmyUnitsTransactions(0)
    else:
      if self.value - other >= 0:
        return ArmyUnitsTransactions(self.value - other)
      return ArmyUnitsTransactions(0)

  def __truediv__(self, other):
    if type(other) == ArmyUnitsTransactions:
      ans = self.value / other.value
      if ans >= 1 and type(ans) == int:
        return ArmyUnitsTransactions(ans)
      elif ans >= 1 and type(ans) == float:
        return ArmyUnitsTransactions(round(ans))
      elif 0 < ans < 1 and type(ans) == float:
        return ArmyUnitsTransactions(round(ans))
      elif ans == 0:
        return ArmyUnitsTransactions(0)
      return ArmyUnitsTransactions(0)

    else:
      ans = self.value / other
      if ans >= 1 and type(ans) == int:
        return ArmyUnitsTransactions(ans)
      elif ans >= 1 and type(ans) == float:
        return ArmyUnitsTransactions(round(ans))
      elif 0 < ans < 1 and type(ans) == float:
        return ArmyUnitsTransactions(round(ans))
      return ArmyUnitsTransactions(0)

  def __mod__(self, other):
    if type(other) == ArmyUnitsTransactions:
      return ArmyUnitsTransactions(self.value % other.value)
    return ArmyUnitsTransactions(self.value & other)

  def __lt__(self, other):
    if type(other) == ArmyUnitsTransactions:
      return self.value  < other.value
    return self.value < other

  def __le__(self, other):
    if type(other) == ArmyUnitsTransactions:
      return self.value <= other.value
    return self.value < other

  def __eq__(self, other):
    if type(other) == ArmyUnitsTransactions:
      return self.value == other.value
    return self.value == other

  def __ne__(self, other):
    if type(other) == ArmyUnitsTransactions:
      return self.value != other.value
    return self.value != other

  def __ge__(self, other):
    if type(other) == ArmyUnitsTransactions:
      return self.value >= other.value
    return self.value >= other

  def __gt__(self,other):
    if type(other) ==  ArmyUnitsTransactions:
      return self.value > other.value
    return self.value >= other

  def __pow__(self, other):
    if type(other) == ArmyUnitsTransactions:
      return ArmyUnitsTransactions(self.value ** other.value)
    return ArmyUnitsTransactions(self.value ** other)

  def __call__(self):
    return self.value

  def __repr__(self):
    return "{}".format(self.value)

  def __str__(self):
    return "{}".format(self.value)

class ArmyUnits:

  def __init__(self, ids, protector, attacker, owner, amount, health=200, damage=50, protect_which=None):
    self.ids = ids # Integer
    self.protector = protector # True or False value
    self.attacker = attacker # True or False value

    if protect_which != None:
      self.protect_which = Cities.active_cities[protect_which] 
    else:
      self.protect_which=protect_which

    self.owner = owner

    self.health =  health
    self.damage =  damage
    self.amount =  ArmyUnitsTransactions(amount)

  def __del__(self):
    self.save() # This save function will be implemeneted by all classes

  def change_db(self, query):
    conn = sqlite3.connect("server.db")
    cursor =  conn.cursor()

    cursor.execute(query)
    conn.commit()
    conn.close()

  def save(self):
    """
      Saves Army Units data should be implemeneted by all class using ArmyUnits Class
    """
    pass

class Troops(ArmyUnits):

  creation_requirements = {
    'oil': 0,
    'iron': 10,
    'food': 50,
    'water': 100,
    'money': 50
  }

  maintance_requirements = {
    'oil': 0,
    'iron': 10,
    'food': 25,
    'water': 50,
    'money': 25
  }

  def __init__(self, ids, protector, attacker, owner, amount, protect_which=None):
    super().__init__(ids, protector, attacker, owner, amount, protect_which=protect_which)

  def add_troops(self, how_many):
    self.amount += how_many
    query = "update Army set troops={} where id={}".format(self.amount(), self.ids)
    self.change_db(query)

  def remove_troops(self, how_many):
    self.amount -= how_many
    query = "update Army set troops={} where id={}".format(self.amount(), self.ids)
    self.change_db(query)
    

class Tanks(ArmyUnits):

  creation_requirements = {
    'oil': 10,
    'iron': 20,
    'food': 25,
    'water': 10,
    'money': 100
  }
  
  maintance_requirements = {
    'oil': 40,
    'iron': 50,
    'food': 20,
    'water': 50,
    'money': 50
  }

  def __init__(self, ids, protector, attacker, owner, amount, protect_which=None, health=100, damage=100):
    super().__init__(ids, protector, attacker, owner, amount, health=health, damage=damage,protect_which=protect_which)

  def add_tanks(self, how_many):
    self.amount += how_many
    query = "update Army set tanks={} where id={}".format(self.amount(), self.ids)
    self.change_db(query)

  def remove_tanks(self, how_many):
    self.amount -= how_many
    query = "update Army set tanks={} where id={}".format(self.amount(), self.ids)
    self.change_db(query)

class Planes(ArmyUnits):

  creation_requirements = {
    'oil': 100,
    'iron': 80,
    'food': 20,
    'water': 30,
    'money': 200
  }
  
  maintance_requirements = {
    'oil': 50,
    'iron': 40,
    'food': 20,
    'water': 50,
    'money': 100
  }

  def __init__(self, ids, protector, attacker, owner, amount, protect_which=None, health=200, damage=200):
    super().__init__(ids, protector, attacker, owner, amount, health=health, damage=damage, protect_which=protect_which)

class Artilery(ArmyUnits):

  creation_requirements ={
    'oil': 120,
    'iron': 100,
    'food': 20,
    'water': 50,
    'money': 250
  }
  
  maintance_requirements = {
    'oil': 100,
    'iron': 90,
    'food': 20,
    'water': 10,
    'money': 125
  }

  def __init__(self, ids, protector, attacker, owner, amount, protect_which=None, health=20, damage=300):
    super().__init__(ids, protector, attacker, owner, amount, health=health, damage=damage, protect_which=protect_which)

class Army:
  active_armies = {}

  def __init__(self, ids, name, troops, tanks, planes, artilery, protector, attacker, protect_which, owner):
    self.ids = ids
    self.name = name
    
    if protector == 1:
      self.protector = True
      self.attacker = False
    else:
      self.attacker = True
      self.protector = False

    self.protect_which = protect_which

    self.owner =  Government.active_gov[owner]

    self.troops = Troops(self.ids, self.protector, self.attacker, self.owner, troops, self.protect_which)

    self.tanks = Tanks(self.ids, self.protector, self.attacker, self.owner, tanks, self.protect_which)

    self.airplanes = Planes(self.ids, self.protector, self.attacker, self.owner, planes, self.protect_which)

    self.artilery = Artilery(self.ids, self.protector, self.attacker, self.owner, artilery, self.protect_which)

    Army.active_armies[self.ids] = self
    print("New Army Created Name:", self.name)

  def close(self):
    Army.active_armies.pop(self.ids)
    del self

  def troops_amount(self):
    """
      Gets amount of troops in army
    """
    return self.troops.amount()

  def tank_amount(self):
    """
      Gets amount of tanks in army
    """
    return self.tanks.amount()

  def planes_amount(self):
    """
      Gets amount of planes in army
    """
    return self.airplanes.amount()

  def artilery_amount(self):
    """
      Gets amount of artilery in army
    """
    return self.artilery.amount()

  def change_protector(self, to):
    if to == False:
      conn = sqlite3.connect('server.db')
      cursor =  conn.cursor()

      query = "update Army set protector=0 where id={}".format(self.ids)
      cursor.execute(query)
      conn.commit()
      conn.close()
      self.protector = False
      self.protect_which = None
    else:
      query = "update Army set protect_which={} where id={}".format(to, self.ids)
      conn = sqlite3.connect('server.db')
      cursor = conn.cursor()

      cursor.execute(query)
      conn.commit()
      conn.close()
      self.protect_which = to
  
  def change_attacker(self, to):
    if to==False:
      conn = sqlite3.connect('server.db')
      cursor = conn.cursor()

      query = "update Army set attacker=0 where id={}".format(self.ids)
      cursor.execute(query)
      conn.commit()
      conn.close()
    else:
      conn = sqlite3.connect('server.db')
      cursor = conn.cursor()
      query = "update Army set attacker=1 where id={}".format(self.ids)
      cursor.execute(query)
      conn.commit()
      conn.close()

  def protectors(self):
    if self.protector == True:
      try:
        return Cities.active_cities[self.protect_which].name
      except KeyError:
        query = "select name from cities where id={}".format(self.protect_which)
        conn = sqlite3.connect('server.db')
        cursor = conn.cursor()
        cursor.execute(query)

        exist = cursor.fetchone()
        if exist != None:
          return exist[0]
        
        self.change_protector(False)
    return "No"
  
  def attackers(self):
    if self.attacker == True:
      return "Yes"
    return "No"

  def return_data(self):
    return {
      'Name': self.name,
      'Attacking': self.attackers(),
      'Protecting': self.protectors(),
      'Troops': self.troops_amount(),
      'Tanks': self.tank_amount(),
      'Airplanes': self.planes_amount(),
      'Airtilery': self.artilery_amount()
    }
    
  @staticmethod
  def get_country_data(country_id):
    """
      Queries database for armies belonging to a country, then putting that list in a dict before returning it
    """
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()

    query = "select id, name from Army where owner={}".format(country_id)
    cursor.execute(query)

    army_data =  cursor.fetchall()

    ordered_data = {}

    for army in army_data:
      ordered_data[army[0]] = {'id': army[0], 'name': army[1]}
    
    conn.close()
    return ordered_data

  @staticmethod
  def create_army(country_id, name_of_army):
    """
      Creates a new Army and inserts it in database, before creating a army class instance
    """
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()

    query = "select id from Army where name='{}' and owner={}".format(name_of_army, country_id)
    cursor.execute(query)

    result = cursor.fetchone()

    if result != None:
      return "Name already in use, choose a different name"

    query = "INSERT INTO Army (name, troops, tanks, planes, artilery, protector, attacker, protect_which, owner) VALUES ('{}', 0, 0, 0, 0, 0, 1, NULL, {})".format(name_of_army, country_id)

    cursor.execute(query)
    conn.commit()

    query = "select * from Army where id={}".format(cursor.lastrowid)
    cursor.execute(query)

    new_army_det =  cursor.fetchone()

    conn.close()

    if new_army_det != None:
      Army(*new_army_det)
      return "Army Succefully Created"

    return "Problem Creating Army"


  @staticmethod 
  def add_troops(army_id, how_many_troops):
    """
      Adds troops to selected army
    """
    try:
      unit = Army.active_armies[army_id]
      # Checks if user/government has enough resources to recruit troops
      if unit.owner.have_enough(unit.troops.creation_requirements, how_many_troops):
        # Checks if user/government has enough money to recruit troops
        if unit.owner.money >= (unit.troops.creation_requirements['money'] * how_many_troops):
          # Adds troops and removes money from user/government
          unit.troops.add_troops(how_many_troops) 
          unit.owner.remove_money(unit.troops.creation_requirements['money'] * how_many_troops)
          # If no issue it returns success
          return "Successfully recruted troops"
        # If not enough money it lets the user know
        return "Not enough money to recrute troops"
      else:
        # If not enough resources it lets the user know
        return "Not enough resources to recrute troops"
    except KeyError:
      # KeyError means the army does not exist or had a error during __init__
      return "Army does not exist"

  @staticmethod
  def add_tanks(army_id, how_many_tanks):
    """
      Adds tanks to selected army
    """
    try:
      unit = Army.active_armies[army_id]
      # Checks if government/user has enough resource to build tanks
      if unit.owner.have_enough(unit.tanks.creation_requirements, how_many_tanks):
        # Checks if government/user has enough money to build tanks
        if unit.owner.money >= (unit.tanks.creation_requirements['money'] * how_many_tanks):
          # Adds tanks and remove money from government/user
          unit.tanks.add_tanks(how_many_tanks)
          unit.owner.remove_money(unit.tanks.creation_requirements['money'] * how_many_tanks)
          # returns success once completed
          return "Successfully built tanks"
        # if not enough money it lets the user know
        return "Not enough money to build tanks"
      else:
        # if not enough resources it lets the user know
        return "Not enough resources to recrute troops"
    except KeyError:
      # keyerror means army has not been created or the class had a problem during init
      return "Army does not exist"

  @staticmethod
  def subtract_troops(army_id, how_many_troops):
    """
      Removes troops from selected army
    """
    try:
      unit = Army.active_armies[army_id]
      unit.troops.remove_troops(how_many_troops)
      return "Successfully removed troops"
    except KeyError:
      return "Army does not exist"

  @staticmethod
  def subtract_tanks(army_id, how_many_troops):
    """
      Removes tanks from selected army
    """
    try:
      unit = Army.active_armies[army_id]
      unit.tanks.remove_tanks(how_many_troops)
    except KeyError:
      return "Army does not exist"

  @staticmethod
  def get_army_details(army_id):
    arms =  Army.active_armies.get(army_id, None)
    if arms != None:
      return arms.return_data()
    return "Army Not Created"