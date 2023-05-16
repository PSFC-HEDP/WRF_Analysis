"""
Based on Bosch-Hale reactivity fits for Maxwellian plasmas, publishd in
	H.-S. Bosch and G.M. Hale (1992), "Improved formulas for fusion cross-sections and thermal reactivities",
	*Nucl. Fusion 32*, 611. DOI: 10.1088/0029-5515/32/4/I07.
"""
from math import sqrt, exp


class Reactivity:
	def __init__(self, B_G: float, m_r: float, C: list[float]):
		self.B_G = B_G
		self.m_r = m_r
		self.C = C


REACTIONS = {
	"DD-n": Reactivity(31.3970, 937814, [5.43360e-12, 5.85778e-3, 7.68222e-3, 0., -2.96400e-6, 0., 0.]),
	"DD-p": Reactivity(31.3970, 937814, [5.65718e-12, 3.41267e-3, 1.99167e-3, 0., 1.05060e-5, 0., 0.]),
	"DT-n": Reactivity(34.3827, 1124656, [1.1302e-9, 1.51361e-2, 7.51886e-2, 4.60643e-3, 1.35e-2, -1.0675e-4, 1.366e-5]),
	"D3He-p": Reactivity(68.7508, 1124572, [5.51036e-10, 6.41918e-3, -2.02896e-3, -1.91080e-5, 1.35776e-4, 0., 0.]),
}


def get_reactivity(reaction: str, T_ion: float) -> float:
	fit = REACTIONS[reaction]
	numerator       = T_ion*(fit.C[1] + T_ion*(fit.C[3] + T_ion*fit.C[5]))
	denominator = 1 + T_ion*(fit.C[2] + T_ion*(fit.C[4] + T_ion*fit.C[6]))

	θ = T_ion/(1 - numerator/denominator)
	ξ = (fit.B_G**2/(4*θ))**(1/3)

	σv = fit.C[0]*θ*sqrt(ξ/(fit.m_r*T_ion**3))*exp(-3*ξ)

	return σv


def get_reactivity_ratio(reaction_A: str, reaction_B: str, T_ion: float) -> float:
	return get_reactivity(reaction_A, T_ion)/get_reactivity(reaction_B, T_ion)
