from cities import Cities
from gov_classes import Government, sqlite3
import weakref
import gc

class ArmyUnits:

  def __init__(self, ids, protector, attacker, owner, amount, health=200, damage=50,protect_which=None):
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
    self.amount =  amount

  def __del__(self):
    self.save() # This save function will be implemeneted by all classes

  def save(self):
    """
      Saves Army Units data should be implemeneted by all class using ArmyUnits Class
    """
    pass

class Troops(ArmyUnits):

  def __init__(self, ids, protector, attacker, owner, amount, protect_which=None):
    super().__init__(ids, protector, attacker, owner, amount, protect_which=protect_which)

class Tanks(ArmyUnits):

  def __init__(self, ids, protector, attacker, owner, amount, protect_which=None, health=100, damage=100):
    super().__init__(ids, protector, attacker, owner, amount, health=health, damage=damage, protect_which=protect_which)

class Planes(ArmyUnits):

  def __init__(self, ids, protector, attacker, owner, amount, protect_which=None, health=200, damage=200):
    super().__init__(ids, protector, attacker, owner, amount, health=health, damage=damage, protect_which=protect_which)

class Artilery(ArmyUnits):

  def __init__(self, ids, protector, attacker, owner, amount, protect_which=None, health=20, damage=300):
    super().__init__(ids, protector, attacker, owner, amount, health=health, damage=damage, protect_which=protect_which)

class Army:
  active_armies = {}
  def __init__(self, ids, name, troops, tanks, planes, artilery, protector, attacker, protect_which, owner):
    self.id = ids
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

    self.tanks = Tanks(self.ids, self.protector, self.attackers, self.owner, tanks, self.protect_which)

    self.airplanes = Planes(self.ids, self.protector, self.attacker, self.owner, planes, self.protect_which)

    self.artilery = Artilery(self.ids, self.protector, self.attacker, self.owner, artilery, self.protect_which)

    Army.active_armies[self.ids] = self

  def close(self):
    Army.active_armies.pop(self.ids)
    del self

  def troops_amount(self):
    """
      Gets amount of troops in army
    """
    return self.troops.amount

  def tank_amount(self):
    """
      Gets amount of tanks in army
    """
    return self.tanks.amount

  def planes_amount(self):
    """
      Gets amount of planes in army
    """
    return self.planes.amount

  def artilery_amount(self):
    """
      Gets amount of artilery in army
    """
    return self.artilery.amount
