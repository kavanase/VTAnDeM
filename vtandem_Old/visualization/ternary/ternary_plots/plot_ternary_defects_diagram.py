
__name__ = 'VTAnDeM_Visualization-Toolkit-for-Analyzing-Defects-in-Materials'
__author__ = 'Michael_Lidia_Jiaxing_Elif'

# Import defect formation energy diagram object
from vtandem.visualization.plots.plot_defects_diagram import Plot_DefectsDiagram

class Plot_Ternary_DefectsDiagram(Plot_DefectsDiagram):
	
	def __init__(self, main_compound = None, first_element = None, second_element = None, third_element = None):
		
		# Inherit all variables (plot object, etc.) from parent object (DefectFormationEnergy_Diagram)
		super().__init__()
		
		# Establish the first, second, third, and fourth species of the quaternary compound.
		# Note that this list is subject to change, depending on what the user chooses.
		self.main_compound  = main_compound
		self.first_element  = first_element
		self.second_element = second_element
		self.third_element  = third_element
		self.elements_list = [self.first_element, self.second_element, self.third_element]
		
		# Keep track of chemical potential values
		self.mu_elements = {self.first_element: {"mu0": 0.0, "deltamu": 0.0},
							self.second_element: {"mu0": 0.0, "deltamu": 0.0},
							self.third_element: {"mu0": 0.0, "deltamu": 0.0} }
		
		# Store all extracted DFT data
		self.first_element_mu0 = 0.0
		self.second_element_mu0 = 0.0
		self.third_element_mu0 = 0.0












