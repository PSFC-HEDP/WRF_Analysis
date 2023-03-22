import numpy as np
import re

# a few densities and masses for the shell
# see the __init__ docstring for more information
__material_composition__ = {'CH': {'C': 1.000, 'H': 1.352, 'O': .012},
                            'CH2': {'C': 1, 'H': 2},
                            'HDC': {'C': 1},
                            'SiO2': {'Si': 1, 'O': 2}}

__material_rho__ = {'CH': 1.084,
                    'CH2': 1.084,
                    'HDC': 3.5,
                    'SiO2': 2.56,
                    'Be': 1.85}

__element_A__ = {'H': 1,
                 'Be': 9,
                 'C': 12,
                 'O': 16,
                 'Si': 28.1,
                 'Ge': 72.6,
                 'W': 183.8}

__element_Z__ = {'H': 1,
                 'Be': 4,
                 'C': 6,
                 'O': 8,
                 'Si': 14,
                 'Ge': 32,
                 'W': 74}


class Material:
    def __init__(self, specifier):
        """ figure out the stopping-power-relevant material properties given
            a specification string.  the string should be hyphen-separated
            values, where each value is an optional number (the molecular
            percentage) followed by an abbreviated material name.  accepted
            material names are:
                CH = standard plastic
                CH2 = plastic with a higher hydrogen content
                HDC = diamond
                SiO2 = standard glass
                any standard chemical element symbol
            the words "and" and "with" may be inserted freely and will be
            ignored.  so for example, "CH-with-2Ge" means "plastic with a 2%
            Germanium dopage"
        """
        total_f = 0
        elements = []
        abundance = []
        for code in reversed(specifier.split('-')):
            the_last_one = specifier.startswith(code)

            if code in ['with', 'and']:
                if the_last_one:
                    raise ValueError(f"a material specification cannot start with {code}")
                continue

            # first, just get the number and symbol out of each part
            parsing = re.fullmatch(r'([0-9.]*)([A-Z].*)', code)
            if parsing is None:
                raise KeyError(f"Could not parse '{code}' in '{specifier}'")
            compound = parsing.group(2)
            if parsing.group(1):
                molecule_f = float(parsing.group(1))/100 # remember that these are percentages
                total_f += molecule_f
            else:
                if not the_last_one:
                    raise ValueError("a mass fraction must be specified for all components after the first.")
                else:
                    molecule_f = 1 - total_f

            # then, break each part up into its constituent elements
            if compound in __material_composition__:
                for element in __material_composition__[compound]:
                    elements.append(element)
                    atom_abundance = molecule_f * __material_composition__[compound][element]
                    abundance.append(atom_abundance)
            elif compound in __element_Z__:
                elements.append(compound)
                abundance.append(molecule_f)
            else:
                raise KeyError(f"I did not recognize the material '{compound}'")

            # take the density of the first component
            if the_last_one:
                self.rho = __material_rho__[compound]

        # lookup A and Z from the elemental symbols
        total_abundance = np.sum(abundance)
        self.f = [n/total_abundance for n in abundance]
        self.A = [__element_A__[e] for e in elements]
        self.Z = [__element_Z__[e] for e in elements]

        # compute average A and Z
        self.AvgA = np.average(self.A, weights=self.f)
        self.AvgZ = np.average(self.Z, weights=self.f)
