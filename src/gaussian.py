class Quantity:
	def __init__(self, value: float, error: float):
		""" a number with an attached uncertainty """
		self.value = value
		self.error = error

	def __str__(self):
		return f"{self.value} ± {self.error}"

	def __mul__(self, v: float):
		return Quantity(self.value*v, self.error*v)


class Peak:
	def __init__(self, yeeld: Quantity, mean: Quantity, sigma: Quantity):
		""" the three numbers needed to define a Gaussian, with uncertainties attached """
		self.yeeld = yeeld
		self.mean = mean
		self.sigma = sigma

	def __str__(self):
		return f"{self.mean.value:.2f} ± {self.sigma.value:.2f}"
