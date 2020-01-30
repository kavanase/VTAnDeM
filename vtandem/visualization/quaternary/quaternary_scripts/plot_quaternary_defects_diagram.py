
__name__ = 'VTAnDeM_Visualization-Toolkit-for-Analyzing-Defects-in-Materials'
__author__ = 'Michael_Lidia_Jiaxing_Elif'


import numpy as np
import itertools
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from labellines import labelLine, labelLines

from vtandem.visualization.defect_formation_energy import Calculate_IntrinsicDefectFormationEnthalpies
from vtandem.visualization.defect_formation_energy import Calculate_ExtrinsicDefectFormationEnthalpies
from vtandem.visualization.defect_formation_energy import Find_MinimumDefectFormationEnthalpies


class Quaternary_Defects_Diagram(object):
	
	def __init__(self, parent = None, main_compound = None, first_element = None, second_element = None, third_element = None, fourth_element = None):
		
		# Font description for phase stability diagram plot
		self.font = {'family': 'sans-serif',
				'color':  'black',
				'weight': 'normal',
				'size': 14 }
		
		# Establish the first, second, third, and fourth species of the quaternary compound.
		# Note that this list is subject to change, depending on what the user chooses.
		self.main_compound  = main_compound
		self.first_element	= first_element
		self.second_element	= second_element
		self.third_element	= third_element
		self.fourth_element	= fourth_element
		self.elements_list   = [self.first_element, self.second_element, self.third_element, self.fourth_element]
		
		# Keep track of chemical potential values
		self.mu_elements = {self.first_element: {"mu0": 0.0, "deltamu": 0.0},
							self.second_element: {"mu0": 0.0, "deltamu": 0.0},
							self.third_element: {"mu0": 0.0, "deltamu": 0.0},
							self.fourth_element: {"mu0": 0.0, "deltamu": 0.0} }
		
		# Store all extracted DFT data
		self.quaternary_defects_data = None
		self.main_compound_total_energy = 0.0
		self.first_element_mu0 = 0.0
		self.second_element_mu0 = 0.0
		self.third_element_mu0 = 0.0
		self.fourth_element_mu0 = 0.0
		self.EVBM = 0.0
		self.ECBM = 0.0
		self.fermi_energy_array = None
		
		# Minimum and maximum y-value range
		self.ymin = -2.0
		self.ymax = 2.0
		
		# Store defect formation energy data
		self.intrinsic_defects_enthalpy_data = {}
		self.extrinsic_defects_enthalpy_data = {}
		
		# Store defect formation plots and their labels
		self.intrinsic_defect_plots = {}
		self.extrinsic_defect_plots = {}
		self.defect_labels = {}
		
		# Store user-selected dopant
		self.extrinsic_defect = "None"
		self.extrinsic_defect_mu0 = 0.0
		self.extrinsic_defect_deltamu = 0.0
		
		# Defects diagram
		self.quaternary_defects_diagram_plot_figure = plt.figure()
		self.quaternary_defects_diagram_plot_figure.subplots_adjust(left=0.225)
		self.quaternary_defects_diagram_plot_drawing = self.quaternary_defects_diagram_plot_figure.add_subplot(111)
		self.quaternary_defects_diagram_plot_canvas = FigureCanvas(self.quaternary_defects_diagram_plot_figure)
		
		# Equilibrium Fermi energy vertical line
		self.equilibrium_fermi_energy_plot = None
		self.equilibrium_fermi_energy_tick = self.quaternary_defects_diagram_plot_drawing.twiny()
	
	
	
	def Activate_DefectsDiagram_Plot_Axes(self):
		
		self.quaternary_defects_diagram_plot_drawing.set_xlim(0.0, self.ECBM-self.EVBM)
		self.quaternary_defects_diagram_plot_drawing.set_ylim(self.ymin, self.ymax)
		self.quaternary_defects_diagram_plot_drawing.set_xlabel("Fermi Energy (eV)", fontdict=self.font)
		self.quaternary_defects_diagram_plot_drawing.set_ylabel("$\Delta$H (eV)", fontdict=self.font, rotation=90)
		self.quaternary_defects_diagram_plot_drawing.set_xticks([0.0, self.ECBM-self.EVBM])
		self.quaternary_defects_diagram_plot_drawing.set_xticklabels(["VBM = 0.0", "CBM = "+str(round(self.ECBM-self.EVBM, 2))])
		self.quaternary_defects_diagram_plot_drawing.xaxis.tick_bottom()
		self.quaternary_defects_diagram_plot_drawing.yaxis.tick_left()
		self.quaternary_defects_diagram_plot_drawing.tick_params(axis='both', labelsize=9)
		self.quaternary_defects_diagram_plot_drawing.xaxis.set_label_position("bottom")
		self.quaternary_defects_diagram_plot_drawing.yaxis.set_label_position("left")
		self.quaternary_defects_diagram_plot_drawing.set_aspect("auto")
		self.quaternary_defects_diagram_plot_drawing.fill_between(self.fermi_energy_array - self.EVBM, 0, -100, facecolor='#614126', interpolate=True, alpha=.1)
		self.equilibrium_fermi_energy_tick.set_xlim(0.0, self.ECBM-self.EVBM)
		self.equilibrium_fermi_energy_tick.set_xticks([])
		self.equilibrium_fermi_energy_tick.tick_params(axis='both', labelsize=9)
	
	
	
	def Calculate_DefectFormations(self):
		
		intrinsic_defects_enthalpy_data = Calculate_IntrinsicDefectFormationEnthalpies(self.quaternary_defects_data, self.main_compound_total_energy, self.fermi_energy_array, self.mu_elements)
		self.intrinsic_defects_enthalpy_data = Find_MinimumDefectFormationEnthalpies(intrinsic_defects_enthalpy_data)
		
		if self.extrinsic_defect != "None":
			extrinsic_defects_enthalpy_data = Calculate_ExtrinsicDefectFormationEnthalpies(self.quaternary_defects_data, self.main_compound_total_energy, self.fermi_energy_array, self.mu_elements, self.extrinsic_defect, self.extrinsic_defect_mu0, self.extrinsic_defect_deltamu)
			self.extrinsic_defects_enthalpy_data = Find_MinimumDefectFormationEnthalpies(extrinsic_defects_enthalpy_data)
	
	
	
	def Initialize_Intrinsic_DefectsDiagram_Plot(self):
		
		# Plot defect formation energy of each intrinsic defect
		for intrinsic_defect in self.intrinsic_defects_enthalpy_data.keys():
			defect_label = r"$"+intrinsic_defect.split("_")[0]+"_{"+intrinsic_defect.split("_")[-1]+"}$"
			self.intrinsic_defect_plots[intrinsic_defect], = self.quaternary_defects_diagram_plot_drawing.plot(self.fermi_energy_array - self.EVBM, self.intrinsic_defects_enthalpy_data[intrinsic_defect], label = defect_label)
		
		# Create label for each defect
		labelLines(list(self.intrinsic_defect_plots.values()), align = False, xvals = np.linspace(0.0, self.ECBM-self.EVBM, len(self.intrinsic_defect_plots.keys())+2)[1:len(self.intrinsic_defect_plots.keys())+1], fontsize = 10, bbox = dict(facecolor = 'white', alpha = 0.8, edgecolor = 'white', pad = 0.5))
		
		# Draw defects diagram canvas
		self.quaternary_defects_diagram_plot_canvas.draw()
	
	
	
	def Update_Intrinsic_DefectsDiagram_Plot(self):
		
		# Update defect formation energy of each intrinsic defect
		for intrinsic_defect in self.intrinsic_defects_enthalpy_data.keys():
			self.intrinsic_defect_plots[intrinsic_defect].set_ydata(self.intrinsic_defects_enthalpy_data[intrinsic_defect])
		
		# Remove labels before redrawing them at new positions
		self.quaternary_defects_diagram_plot_drawing.texts.clear()
		labelLines(list(self.intrinsic_defect_plots.values()), align = False, xvals = np.linspace(0.0, self.ECBM-self.EVBM, len(self.intrinsic_defect_plots.keys())+2)[1:len(self.intrinsic_defect_plots.keys())+1], fontsize = 10, bbox = dict(facecolor = 'white', alpha = 0.8, edgecolor = 'white', pad = 0.5))
		
		# Draw defects diagram canvas
		self.quaternary_defects_diagram_plot_canvas.draw()
	
	
	
	def Initialize_Extrinsic_DefectsDiagram_Plot(self):
		
		# Plot defect formation energy of dopant
		defect_label = r"$"+self.extrinsic_defect.split("_")[0]+"_{"+self.extrinsic_defect.split("_")[-1]+"}$"
		self.extrinsic_defect_plots[self.extrinsic_defect], = self.quaternary_defects_diagram_plot_drawing.plot(self.fermi_energy_array - self.EVBM, self.extrinsic_defects_enthalpy_data[self.extrinsic_defect], label = defect_label)
		
		# Create label for each defect	
		labelLine(self.extrinsic_defect_plots[self.extrinsic_defect], x=(self.ECBM-self.EVBM)/2., align=False)
		
		# Draw defects diagram canvas
		self.quaternary_defects_diagram_plot_canvas.draw()
	
	
	
	def Update_Extrinsic_DefectsDiagram_Plot(self):
		
		# Update defect formation energy of dopant
		self.extrinsic_defect_plots[self.extrinsic_defect].set_ydata(self.extrinsic_defects_enthalpy_data[self.extrinsic_defect])
		
		# Remove labels before redrawing them at new positions
		labelLine(self.extrinsic_defect_plots[self.extrinsic_defect], x=(self.ECBM-self.EVBM)/2., align=False)
		
		# Draw defects diagram canvas
		self.quaternary_defects_diagram_plot_canvas.draw()
	
	
	
	def Plot_Equilibrium_Fermi_Energy(self, temperature, equilibrium_fermi_energy):
		
		# Plot equilibrium Fermi energy
		try:
			self.equilibrium_fermi_energy_plot.remove()
			self.equilibrium_fermi_energy_plot = self.quaternary_defects_diagram_plot_drawing.axvline(equilibrium_fermi_energy, zorder=1E9, ls='--', color='k')
		except:
			self.equilibrium_fermi_energy_plot = self.quaternary_defects_diagram_plot_drawing.axvline(equilibrium_fermi_energy, zorder=1E9, ls='--', color='k')
		
		# Place EF^eq text
		try:
			self.equilibrium_fermi_energy_tick.set_xticks([equilibrium_fermi_energy])
			self.equilibrium_fermi_energy_tick.set_xticklabels([r"$E_{f}^{eq}$"])
		except:
			self.equilibrium_fermi_energy_tick.set_xticks([])
			self.equilibrium_fermi_energy_tick.set_xticklabels([])
		
		
		# Draw defects diagram canvas
		self.quaternary_defects_diagram_plot_canvas.draw()




















