
__author__ = 'Michael_Lidia_Jiaxing_Elif'
__name__ = 'VTAnDeM_Visualization-Toolkit-for-Analyzing-Defects-in-Materials'

import re

###############################################################################################
########################## Rewrite Compound Name Latex-Style ##################################
###############################################################################################

"""
def Compound_Name_Formal(compound_name, compounds_info, type: str):
	
	# Check if 'type' variable is either 'unicode' or 'latex'
	if (type != "unicode") and (type != "latex"):
		raise ValueError("'type' variable must be one of: 'unicode' or 'latex'")
	
	# Go into the compounds_info dictionary and obtains the chemistry and stoichiometry of the compound of choice
	compound_species_info = compounds_info[compound_name]
	
	compound_name_formal = ""
	for species in compound_species_info["elements_list"]:				# Loop through the list of possible species that can be contained in the compound
		if compound_species_info[species] == 0:
			continue								# Don't add the species to the name if the compound doesn't contain the species
		elif compound_species_info[species] == 1:
			compound_name_formal += species			# Add the species to the name of the compound
		elif compound_species_info[species] > 1:
			if type == "latex":
				compound_name_formal += species+"$_{"+str(int(compound_species_info[species]))+"}$"	# Add the species to the name of the compound
			elif type == "unicode":
				compound_name_formal += species+"<sub>"+str(int(compound_species_info[species]))+"</sub>"	# Add the species to the name of the compound
																											#	with a subscript for the stoichiometry
	
	return compound_name_formal
"""


def Compound_Name_Formal(compound_name, type: str):
	
	# Check if 'type' variable is either 'unicode' or 'latex'
	if (type != "unicode") and (type != "latex"):
		raise ValueError("'type' variable must be one of: 'unicode' or 'latex'")
	
	# Obtain the chemistry and stoichiometry of the compound
	compound_stoichiometry_list = re.findall(r'\d+|[A-Z][a-z]*', compound_name)

	# Create fancy compound name
	compound_name_formal = r""
	for i in compound_stoichiometry_list:
		if i.isnumeric():
			if i == "1":
				continue
			if type == "latex":
				compound_name_formal += "$_\mathrm{"+str(int(i))+"}$"
			elif type == "unicode":
				compound_name_formal += "<sub>"+str(int(i))+"</sub>"
		else:
			compound_name_formal += i

	return compound_name_formal







