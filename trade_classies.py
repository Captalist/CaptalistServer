class Trade:
  def __init__(self, to, from_who, item, amount, cost, times, index):
    self.to = to
    self.from_who = from_who
    self.item = item
    self.amount = amount
    self.cost = cost
    self.times = times
    self.index = index

  def oil(self):
    try:
      self.to.add_oil(self.amount)
      self.to.remove_money(self.cost)
      self.from_who.remove_oil(self.amount)
      self.from_who.add_money(self.cost)
      
      self.times -= 1

      if self.times <= 0:
        return "Trade Ended"
      
      return "You have {} years left".format(self.times)
    except NameError:
      return "Government offline"

  def iron(self):
    try:
      self.to.add_iron(self.amount)
      self.to.remove_money(self.cost)
      self.from_who.remove_oil(self.amount)
      self.from_who.add_money(self.cost)

      self.times -= 1

      if self.times <= 0:
        return "Trade Ended"

      return "You have {} years left".format(self.times)

    except NameError:
      return "Government offline"

  def food(self):
    try:
      self.to.add_food(self.amount)
      self.to.remove_money(self.cost)
      self.from_who.remove_food(self.amount)
      self.from_who.add_money(self.cost)

      self.times -= 1
      
      if self.times <= 0:
        return "Trade Ended"

      return "You have {} years left".format(self.times)

    except NameError:
      return "Governement offline"

  def water(self):
    try:
      self.to.add_water(self.amount)
      self.to.remove_money(self.cost)
      self.from_who.remove_water(self.amount)
      self.from_who.add_money(self.cost)

      self.times -= 1

      if self.times <= 0:
        return "Trade Ended"

      return "You have {} years left".format(self.times)
    except NameError:
      return "Government offline"

  def carry_out_trade(self, types):
    return Trade.__dict__[types](self)
