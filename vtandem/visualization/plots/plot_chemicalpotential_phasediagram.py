
__author__ = 'Michael_Lidia_Jiaxing_Elif'
__name__ = 'VTAnDeM_Visualization-Toolkit-for-Analyzing-Defects-in-Materials'


###############################################################################################################################
###############################################################################################################################
##################################################### Introduction ############################################################
###############################################################################################################################
###############################################################################################################################

# 	This script stores the phase stability diagram of a single quaternary compound as an object within VTAnDeM.
#
# 	The stability of any compound is dictated by thermodynamic principles. All materials are made of atoms, and multicomponent
#		systems in particular (e.g. systems of two or more types of atoms, like GaAs) can exhibit distinct phases/materials
#		depending on how the atoms are arranged. Therefore, for a given set of atoms, there is a myriad of possible materials 
#		that can be formed by e.g. different synthesis methods. Fundamentally, the material with the lowest formation energy in some
#		environmental condition (e.g. GaAs in a 'Ga-rich' environment) is most and will likely form in a lab. Accordingly, if
#		we are studying some quaternary system, there may be other compounds that "compete" with the main compound to become the
#		most stable. For example, if we are interested in studying the quaternary compound Cu2HgGeTe4, in regions that are Cu-rich
#		or Hg-poor (or any combination of the sorts), another compound such as CuTe may be more stable than Cu2HgGeTe4. It is 
#		therefore crucial for material/device processing purposes that we know the exact environmental conditions necessary to create a 
#		stable version of the quaternary compound of interest. The stability of compounds can fortunately be studied using Density 
#		Functional Theory (DFT) calculations.



###############################################################################################################################
###############################################################################################################################
################################################### Import Libraries ##########################################################
###############################################################################################################################
###############################################################################################################################

import numpy as np
import itertools
import copy
import periodictable
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from vtandem.visualization.utils.chemicalpotential_phasediagram import Calculate_PhaseDiagram_Projected2D

from vtandem.visualization.utils.compound_name import Compound_Name_Formal


class Plot_ChemicalPotential_Quaternary_PhaseDiagramProjected2D(QWidget):
	
	def __init__(self, parent = None, main_compound = None, first_element = None, second_element = None, third_element = None, fourth_element = None):
		
		# All elements in the periodic table
		self.all_elements = []
		for element in periodictable.elements:
			self.all_elements.append(str(element))
		
		
		# Font description for phase stability diagram plot
		self.font = {'family': 'sans-serif',
				'color':  'black',
				'weight': 'normal',
				'size': 16 }
		
		# Establish the first, second, third, and fourth species of the quaternary compound.
		# Note that this list is subject to change, depending on what the user chooses.
		self.main_compound  = main_compound
		self.first_element	= first_element
		self.second_element	= second_element
		self.third_element	= third_element
		self.fourth_element	= fourth_element
		self.elements_list  = [self.first_element, self.second_element, self.third_element, self.fourth_element]	# List of elements that gets updated as user selects element order
		self.elements_list_original = [self.first_element, self.second_element, self.third_element, self.fourth_element]	# Unchanged list of elements for compound naming purposes (e.g. see Compound_Name_Formal)
		
		# Store all extracted DFT data
		self.compounds_info = {}
		
		# Necessary numerical variables
		self.main_compound_number_first_specie  = 0	# Number of each specie in the main quaternary compound
		self.main_compound_number_second_specie = 0
		self.main_compound_number_third_specie  = 0
		self.main_compound_number_fourth_specie = 0
		self.main_compound_enthalpy = 0.0			# Enthalpy of the main quaternary compound
		self.phasediagram_endpoints = 0.0			# Endpoints for quaternary phase diagram
		#self.mu4 = 0.0								# Track the fourth species mu value as the user changes it
		self.deltamu = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
		
		# Quaternary phase diagram object
		self.quaternary_phase_diagram_plot_figure = plt.figure()
		#self.quaternary_phase_diagram_plot_figure.subplots_adjust(left=0.001, right=0.85, bottom=0.001, top=0.85)
		self.quaternary_phase_diagram_plot_figure.subplots_adjust(left=0.0, bottom=0.0, right=0.8, top=0.8)
		self.quaternary_phase_diagram_plot_drawing = self.quaternary_phase_diagram_plot_figure.add_subplot(111)
		self.quaternary_phase_diagram_plot_canvas = FigureCanvas(self.quaternary_phase_diagram_plot_figure)
		
		#self.toolbar = NavigationToolbar(self.quaternary_phase_diagram_plot_canvas, self)
		
		# Necessary plot-related variables
		self.main_compound_plot = None				# Main compound plot (holds plot object)
		self.competing_compound_plots = {}			# Competing compound plots (holds plot objects)
		self.competing_compound_colorwheel = {}		# Legend
		self.PSR_vertices_plot = None				# Dots for intersections
		self.PSR_vertices = []						# Coordinates of each intersection
	
	
	def Update_PhaseDiagram_Object(self):
		
		# Number of elements in main compound
		self.main_compound_number_first_specie = self.compounds_info[self.main_compound][self.first_element]	# Number of first species in quaternary compound
		self.main_compound_number_second_specie = self.compounds_info[self.main_compound][self.second_element]	# Number of second species in quaternary compound
		self.main_compound_number_third_specie = self.compounds_info[self.main_compound][self.third_element]	# Number of third species in quaternary compound
		self.main_compound_number_fourth_specie = self.compounds_info[self.main_compound][self.fourth_element]	# Number of fourth species in quaternary compound
		
		# Enthalpy of quaternary compound
		self.main_compound_enthalpy = self.compounds_info[self.main_compound]["enthalpy"]	# Enthalpy of quaternary compound
		
		# Endpoints of phase diagram
		self.phasediagram_endpoints = min(self.main_compound_enthalpy/self.main_compound_number_first_specie, self.main_compound_enthalpy/self.main_compound_number_second_specie, self.main_compound_enthalpy/self.main_compound_number_third_specie, self.main_compound_enthalpy/self.main_compound_number_fourth_specie)
	
	
	def Update_PhaseDiagram_Plot_Axes(self):
		
		self.quaternary_phase_diagram_plot_drawing.set_xlim(self.phasediagram_endpoints, 0.0)
		self.quaternary_phase_diagram_plot_drawing.set_ylim(self.phasediagram_endpoints, 0.0)
		self.quaternary_phase_diagram_plot_drawing.set_xlabel("$\Delta\mu_{"+self.first_element+"}$ (eV)",fontdict=self.font)
		self.quaternary_phase_diagram_plot_drawing.set_ylabel("$\Delta\mu_{"+self.second_element+"}$ (eV)",fontdict=self.font,rotation=270,labelpad=20)
		self.quaternary_phase_diagram_plot_drawing.xaxis.tick_top()
		self.quaternary_phase_diagram_plot_drawing.yaxis.tick_right()
		#self.quaternary_phase_diagram_plot_drawing.tick_params(axis='both', labelsize=9)
		self.quaternary_phase_diagram_plot_drawing.xaxis.set_label_position("top")
		self.quaternary_phase_diagram_plot_drawing.yaxis.set_label_position("right")
		self.quaternary_phase_diagram_plot_drawing.spines['left'].set_visible(False)
		self.quaternary_phase_diagram_plot_drawing.spines['bottom'].set_visible(False)
		self.quaternary_phase_diagram_plot_drawing.set_aspect("equal")
	
	
	
	def Plot_PhaseDiagram(self):
		
		# Calculate phase diagram
		main_compound_deltamu_first_element, main_compound_stability_limit, \
			competing_compounds_deltamu_first_element_limit, competing_compounds_deltamu_second_element_limit, \
			main_compound_deltamu_first_element_cutoff, stability_minimum_cutoff, stability_maximum_cutoff \
			= Calculate_PhaseDiagram_Projected2D(self.main_compound, {1: self.first_element, 2: self.second_element, 3: self.third_element, 4: self.fourth_element}, self.compounds_info, self.deltamu)
		
		# Check if the phase diagram has already been plotted
		try:
			self.main_compound_plot.set_data(main_compound_deltamu_first_element, main_compound_stability_limit)
		except:
			self.main_compound_plot, = self.quaternary_phase_diagram_plot_drawing.plot(main_compound_deltamu_first_element, main_compound_stability_limit, color='k')
		
		for competing_compound in self.compounds_info.keys():
			
			# Skip if compound is either the main compound or one of the elements
			if (competing_compound in self.all_elements) or (competing_compound == self.main_compound):
				continue
			
			try:
				# See if plot exists so it just needs to be updated
				self.competing_compound_plots[competing_compound].set_data(competing_compounds_deltamu_first_element_limit[competing_compound], competing_compounds_deltamu_second_element_limit[competing_compound])
			except:
				# If the plot doesn't exist initially, then create it
				self.competing_compound_plots[competing_compound], = self.quaternary_phase_diagram_plot_drawing.plot(competing_compounds_deltamu_first_element_limit[competing_compound], competing_compounds_deltamu_second_element_limit[competing_compound], label=Compound_Name_Formal(competing_compound, self.compounds_info, type="latex"))
				self.competing_compound_colorwheel[competing_compound] = self.competing_compound_plots[competing_compound].get_color()
		
		try:
			self.phase_stability_region.remove()
			self.phase_stability_region = self.quaternary_phase_diagram_plot_drawing.fill_between(main_compound_deltamu_first_element_cutoff, stability_maximum_cutoff, stability_minimum_cutoff, facecolor='0.75')
		except:
			self.phase_stability_region = self.quaternary_phase_diagram_plot_drawing.fill_between(main_compound_deltamu_first_element_cutoff, stability_maximum_cutoff, stability_minimum_cutoff, facecolor='0.75')
		
		
		# Legend
		self.quaternary_phase_diagram_plot_drawing.legend(loc=3)
		
		
		
		# Find the vertices of the phase stability region
		if self.phase_stability_region.get_paths() != []:	# Check if phase stability region exists
			self.PSR_vertices = self.Find_PhaseStabilityRegion_Vertices(self.phase_stability_region.get_paths())
			if self.PSR_vertices == []:
				try:
					self.PSR_vertices_plot.remove()
				except:
					pass
			elif self.PSR_vertices != []:
				try:
					self.PSR_vertices_plot.remove()
					self.PSR_vertices_plot = self.quaternary_phase_diagram_plot_drawing.scatter(*zip(*self.PSR_vertices), s=20, c='black')
				except:
					self.PSR_vertices_plot = self.quaternary_phase_diagram_plot_drawing.scatter(*zip(*self.PSR_vertices), s=20, c='black')
					pass
		elif self.phase_stability_region.get_paths() == []:	# If phase stability region does not exist, then done
			self.PSR_vertices = []
			try:
				self.PSR_vertices_plot.remove()
			except:
				pass
		
		# Draw the phase diagram
		self.quaternary_phase_diagram_plot_canvas.draw()
	
	
	def Find_PhaseStabilityRegion_Vertices(self, plots):
		
		# This function finds the vertices bounding the phase stability region. It takes
		#	the points of the phase stability region as input.
		
		PSR_vertices = []					# Keep track of the vertices of the phase stability region
		PSR_bound_slope_previous = None		# Keep track of the slope of a side of the phase stability region
		PSR_bounding_point_previous = None	# Keep track of the phase stability region points
		tolerance = 1E-6
		# Record a point as a vertex if the slope drastically changes
		for PSR_bounds in plots[0].iter_segments():
			PSR_bounding_point = PSR_bounds[0]
			try:
				PSR_bound_slope = (PSR_bounding_point[1]-PSR_bounding_point_previous[1]) / (PSR_bounding_point[0]-PSR_bounding_point_previous[0])
			except:
				PSR_bounding_point_previous = PSR_bounding_point
				PSR_bound_slope_previous = 0.0
				continue
			if (PSR_bound_slope < PSR_bound_slope_previous - tolerance) or (PSR_bound_slope > PSR_bound_slope_previous + tolerance):
				PSR_vertices.append(PSR_bounding_point_previous)
				PSR_vertices.append(PSR_bounding_point)
			PSR_bound_slope_previous = PSR_bound_slope
			PSR_bounding_point_previous = PSR_bounding_point
		# Some vertices may be repeated, so get rid of those
		PSR_vertices_Omit = []
		for PSR_vertices_Index in range(len(PSR_vertices)-1):
			if (np.linalg.norm(PSR_vertices[PSR_vertices_Index]-PSR_vertices[PSR_vertices_Index+1]) < 0.01):
				PSR_vertices_Omit.append(PSR_vertices[PSR_vertices_Index])
		PSR_vertices_unrepeated = [x for x in PSR_vertices if (not any((x is y for y in PSR_vertices_Omit)))]
		return PSR_vertices_unrepeated



