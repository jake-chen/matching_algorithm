import random

import classes
from classes import Project
from classes import FieldError
from classes import CompError
from classes import Student
import pandas as pd
import numpy as np
import ConfigParser

student_ids = []

class InputError(Exception):
	def __init__(self, value):
		self.val = value
	def __str__(self):
		return repr(self.val)

class FunctionError(Exception):
	def __init__(self, value):
		self.val = value
	def __str__(self):
		return repr(self.val)

# Functions for randomness
def random_index(lst_length):
	'''
		Generate a random index for a list of length lst_length.
		Handles the case that the list length is 1, which can be
		problematic if using random.randint.
		Fails on empty lists.

		Parameters:
		-----------
		lst_length: length of the list (int).

		Returns:
		--------
		r: a random index in the range [0, lst_length - 1] (int).

	'''
	if (lst_length == 0):
		raise FunctionError("List has length of 0.")
	elif (lst_length == 1):
		r = 0
	else:
		r = random.randint(0, lst_length - 1)
	return r

def random_project(projects, already_picked, reuse, verbose = False):
	'''
		Pick a random project from the list of projects. If reuse = False,
		then we will pick a project that is not in already_picked.

		Parameters:
		-----------
		projects: the list of projects to choose from (Project list).

		already_picked: the projects that have already been assigned students
		                (Project list).

		reuse: if False, then we would like to pick a project not
		       included in already_picked (boolean).

		verbose: print updates.

		Returns:
		--------
		project: a project.

	'''
	if (verbose):
		print "Length of projects is " + str(len(projects))
	rand_index = random_index(len(projects))
	if (verbose):
		statement =  "Length of project " + str(projects[rand_index].ID)
		statement += " is " + str(len(projects[rand_index].students))
		print statement
	if (not (reuse)):
		project_to_return = projects[rand_index]
		while (project_to_return in already_picked):
			rand_index = random_index(len(projects))
			project_to_return = projects[rand_index]
	return projects[rand_index]

def random_student(project):
	'''
		Picks a random student from a project.
		Fails on projects with no students.

		Parameters:
		-----------
		project: the project to pick a student from (Project).

		Returns:
		--------
		student: a student on this project (Student).

	'''
	rand_index = random_index(len(project.students))
	return project.students[rand_index]

def random_student_lst(student_lst, already_picked, reuse):
	'''
		Picks a random student from a list of students.
		Fails on an empty list.

		Parameters:
		-----------
		student_lst: a list of students (Student list).

		Returns:
		--------
		student: a student in the list (Student).

	'''
	rand_index = random_index(len(student_lst))
	if (not (reuse)):
		student_to_return = student_lst[rand_index]
		while (student_to_return in already_picked):
			rand_index = random_index(len(student_lst))
			student_to_return = student_lst[rand_index]
	
	return student_lst[rand_index]

def random_two_choice():
	'''	
		Picks either 0 or 1, randomly.

		Returns
		-------
		number: either 0 or 1 (int).
	'''
	non_int = random.random()
	if (non_int > 0.5):
		return 1
	else:
		return 0

def generate_all_projects():
	'''
		Creates a project for every ID in classes.valid_projects.
		Takes the values for number of MBAs per team and number of
		MEngs per team from config.txt.

		Returns:
		--------
		projects_lst: a list of projects, on a one-to-one correspondence
		with the IDs in classes.valid_projects. 

	'''

	configParser = ConfigParser.ConfigParser()
	configFilePath = r'config.txt'
	configParser.read(configFilePath)

	num_MBAs = configParser.getint('valid_values', 'num_MBAs')
	num_MEngs = configParser.getint('valid_values', 'num_MEngs')
	projects_lst = []
	for ID in classes.vals_valid_projects:
		p = Project(ID, num_MBAs, num_MEngs)
		projects_lst.append(p)
	return projects_lst

def get_student_from_ID(ID, students):
	'''
		Given a student ID and a list of students, returns the
		Student object associated with the given ID.

		Parameters:
		-----------
		ID: ID for the student to search for (int).
		students: list of students (Student list).

		Returns:
		--------
		student: object whose ID is ID (Student).
	'''
	matching_ID_lst = filter(lambda x: x.ID == ID, students)
	# No matching IDs
	if (len(matching_ID_lst) == 0):
		error = "ID " + str(ID) + " does not match to a valid project."
		raise FieldError(error)
	# Multiple matching IDs
	elif (len(matching_ID_lst) > 1):
		error = "There is more than one matching project. Problem!"
		raise FieldError(error)
	# Otherwise, there is one element in the list and it matches our desired ID.
	else:
		return matching_ID_lst[0]


def get_project_from_ID(ID, projects):
	'''
		Given a project ID and a list of projects, returns the
		Project object associated with the given ID.

		Parameters:
		-----------
		ID: ID for the project to search for (int).
		projects: list of projects (Project list).

		Returns:
		--------
		project: object whose ID is ID (Project).
	'''
	matching_ID_lst = filter(lambda x: x.ID == ID, projects)
	# No matching IDs
	if (len(matching_ID_lst) == 0):
		error = "ID " + str(ID) + " does not match to a valid project."
		raise FieldError(error)
	# Multiple matching IDs
	elif (len(matching_ID_lst) > 1):
		error = "There is more than one matching project. Problem!"
		raise FieldError(error)
	# Otherwise, there is one element in the list and it matches our desired ID.
	else:
		return matching_ID_lst[0]

# Filter out projects with insufficient rankings to get matched.
# Returns a list of projects which passed the test.
def create_feasible_projects(students, projects, verbose = False):
	'''
		Filters our the projects with insufficient rankings to get matched.

	'''
	insufficient_IDs = []
	for p in projects:
		matched = filter(lambda s: p.ID in s.project_rankings, students)
		if (verbose):
			print "For project " + str(p.ID) + ":"
			print [s.ID for s in matched]
		MBAs_ranked = [s for s in matched if s.degree_pursuing == "MBA" 
		  or s.degree_pursuing == 0]
		MEngs_ranked = [s for s in matched if s.degree_pursuing == "MEng" 
		  or s.degree_pursuing == 1]
		if (verbose):
			print "MBAs" + str([s.ID for s in MBAs_ranked])
			print "MEngs" + str([s.ID for s in MEngs_ranked])
			print "p.num_MBAs is " + str(p.num_MBAs)
			print "p.num_MEngs is " + str(p.num_MEngs)
			print str(len(MBAs_ranked)) + " MBAs ranked this project."
			print str(len(MEngs_ranked)) + " MEngs ranked this project."
			print str(len(MBAs_ranked)) + " < " + str(p.num_MBAs) + ":",
			print str(len(MEngs_ranked)) + " < " + str(p.num_MEngs) + ":",
			comparison = "The comparison that we are checking: "
			var_one = len(MBAs_ranked) < p.num_MBAs
			var_two = len(MEngs_ranked) < p.num_MEngs
			var = var_one or var_two
			comparison += str(var)
			print comparison
	 
	 	if ((len(MBAs_ranked) < p.num_MBAs) or (len(MEngs_ranked) < p.num_MEngs)):
	 		if (verbose):
	 			string = "Not enough MBAs or MEngs ranked project "
	 			string += str(p.ID)
	 			string += " for it to be included."
	 			print string
	 		insufficient_IDs.append(p.ID)

	projects = filter(lambda p: not(p.ID in insufficient_IDs), projects)
	return projects

def get_num_ranked(p, students):
	'''
		Get the number of students who ranked this project in their top 10.
	'''
	matched = filter(lambda s: p.ID in s.project_rankings, students)
	return len(matched)

def sort_projects_by_demand(students, projects, tup = False):
	'''
		Sort projects by highest demand to lowest demand.
	'''
	def liking (p):
		return get_num_ranked(p, students)
	projects.sort(key = liking, reverse = True)
	if (tup):
		lst_of_tuples = []
		likings = [liking(p) for p in projects]
		unique_likings = set(likings)
		for num_votes in unique_likings:
			count = likings.count(num_votes)
			lst_of_tuples.append((num_votes, count))
		return lst_of_tuples

	else:
		return projects

def are_unique(l1, l2):
	''' 
		Checks if two given lists are unique.

		Parameters
		----------
		l1, l2: two arbitrary lists.

		Returns
		-------
		are_unique: a boolean value indicating if these lists are unique.

	'''
	return (set(l1).intersection(set(l2)) == set([]))

def create_students_from_input(file):
	'''
		There is a check for how many columns are in the student data input file.
		If the data does not have all of the following information, this function
		will fail.
		Currently assumes:
			- 1 column for ID
			- 1 column for degree degree_pursuing
			- 1 column for cs_ug
			- 1 column for coding coding_ability
			- 1 column for work experience
			- classes.number_project_rankings columns for project rankings
			- 1 column for first name
			- 1 column for last name
	'''
	try:
		data = pd.read_csv(file)
		data_array = np.array(data)
		shape = data_array.shape
		num_rows = shape[0]

		students_lst = []

		# Extract rows and create students
		for i in range(0, num_rows):
			student = data_array[i,:]
			if (not(len(student) == classes.number_project_rankings + 7)):
				error = "Row " + str(i) + " in " + str(file) + " does not have"
				error += "the number of fields required by the config file."
				raise InputError(error)

			ID 	= student[0]
			if (ID in student_ids):
				raise CompError("Student IDs must be unique.")
			student_ids.append(ID)
			 
			degree_pursuing = student[1]
			cs_ug = student[2]
			coding_ability = student[3]
			num_yrs_work_exp = student[4]

			# Only take the desired number of project rankings that we want.
			rankings = student[5:(5 + classes.number_project_rankings)]
			first_name = student[5 + classes.number_project_rankings]
			last_name = student[5 + classes.number_project_rankings + 1]
			name = first_name + " " + last_name

			a = Student(name, ID, degree_pursuing, cs_ug, coding_ability, 
				num_yrs_work_exp, rankings)
			students_lst.append(a)

		return students_lst

	except(IOError):
		if (len(file) == 0):
			error = "Please enter a valid filename."
			raise InputError(error)
		else:
			error = "Error with reading the file for student data."
			raise InputError(error)


def input_checks(students, projects, num_MBAs, num_MEngs,
                 project_id_mappings, sorted = False):
	'''
		num_MBAs and num_MEngs are the numbers required per team
		(i.e. 2 and 2), not the total numbers.
	'''
	if (len(projects) == 0):
		raise FieldError ("There are no feasible projects.")

	elif (len(students) == 0):
		raise FieldError ("There are no students.")

	team_size = num_MBAs + num_MEngs

	MBAs = filter(lambda student: student.degree_pursuing == 0 or 
		student.degree_pursuing == "MBA", students)
	MEngs = filter(lambda student: student.degree_pursuing == 1 or 
		student.degree_pursuing == "MEng", students)

	# Make sure that there are no overlapping student IDs.
	MBA_IDs = [s.ID for s in MBAs]
	MEng_IDs = [s.ID for s in MEngs]

	if (not (are_unique(MBA_IDs, MEng_IDs))):
		raise FieldError('Student ID lists must not overlap.')

	# Make sure that team size is not zero.
	if (team_size == 0):
		raise FieldError('Team size cannot be 0.')

	if (len(MBAs) < len(MEngs)):
	 	smaller = MBAs
	 	num_req_per_team = num_MBAs
	else:
	 	smaller = MEngs
	 	num_req_per_team = num_MEngs
	
	num_teams = len(smaller)/num_req_per_team

	if (len(project_id_mappings) == 0):
		error = "Please enter a filename for the project_id_mappings"
		error += "field in config.txt."
		raise InputError(error)
	try:
		data = pd.read_csv(project_id_mappings)
	except(IOError):
		error = "Could not read file for project-ID mappings. Fix the file and enter"
		error += "its name in the field project_id_mappings in config.txt."
		raise InputError(error)

	# If team size is too big for input.
	if (num_teams == 0):
		raise FieldError ("Team size is too large for given input.")

	#If none of these errors are raised, then the input is fine.
	else:
		pass

def read_project_ids_and_names_from_input():

	configParser = ConfigParser.ConfigParser()
	configFilePath = r'config.txt'
	configParser.read(configFilePath)

	file = configParser.get('files', 'project_id_mappings')

	data = pd.read_csv(file)

	data_array = np.array(data)
	shape = data_array.shape
	num_rows = shape[0]

	dict_project_names = {}

	# Extract rows and create students
	for i in range(0, num_rows):
		project_tup = data_array[i,:]
		ID 	= project_tup[0]
		name = project_tup[1]
		company = project_tup[2]
		dict_project_names[ID] = str(company) + ": " + str(name)

	return dict_project_names

def print_final_solution(state, use_diversity, output_file):
		'''
			This prints the final solution in a pretty format.
			Writes the final teams to an Excel file (csv format).
		'''
		dict_project_names = read_project_ids_and_names_from_input()
		output = []
		print "Final Solution:"
 		(projects, inv_cov_mat_tup) = state
 		all_avg_ranks = []
		for p in projects:
			cur_project_output = ""
			if (not(use_diversity)):
				project_name = dict_project_names[p.ID]
				cur_project_output = cur_project_output + project_name
		 		print project_name + ": " + str([s.ID for s in p.students])
		 	print "------------------------------"
			ranks = []
			# NOTE: get ranking returns 100 if the student did not rank the project.
		 	for student in p.students:
				print student.name + " (" + str(student.degree_pursuing) + "):",
				rank = student.get_ranking(p.ID)
				if (not(use_diversity)):
		 			print "Rank:",
					print rank
				else:
					print "Attributes: "
					print str(student.get_numerical_student_properties())
				print
				ranks.append(rank)
				cur_project_output = cur_project_output + student.name + "\t"
			avg_project_rank = np.mean(ranks)
			all_avg_ranks.append(avg_project_rank)
			output.append(cur_project_output)
			if (use_diversity):
				print "Diversity: " + str(p.calculate_diversity(inv_cov_mat_tup))
			else:
				print "Average project rank: " + str(avg_project_rank)
			print
			print
		if (not(use_diversity)):
			print
			statement = "This solution had a " + str(np.mean(all_avg_ranks))
			statement +=" rank on average."
			print statement
		numpy_version_of_output = np.array(output)
		dataframe_output = pd.DataFrame(numpy_version_of_output, columns = [""])
		dataframe_output.to_csv(output_file, sep=',', index = False)
		print
		print
		print "Completed annealing and wrote results to " + output_file + "!"
		print


def list_unranked_students(state):
	'''
		Lists the students in state that were assigned to a project that they did
		not rank.
	'''
	dict_project_names = read_project_ids_and_names_from_input()
	unranked = False
	print
	print "The following students were assigned to projects that they did not rank:"
	print "-------------------------------------------------------------------------"
	(projects, inv_cov_mat_tup) = state
	for p in projects:
		for student in p.students:
			# Get the student's rank of this project.
			rank = student.get_ranking(p.ID)
			# The student didn't rank this
			if (rank > classes.number_project_rankings):
				print student.name + " (" + str(student.degree_pursuing) + "):"
				for i in range (0, len(student.project_rankings)):
					print "Rank " + str(i + 1) + ":",
					rank_i_project_id = student.project_rankings[i]
					print dict_project_names[rank_i_project_id]
				unranked = True
				print
	if (not(unranked)):
		print "There were no students assigned to projects that they did not rank."
	print

def list_low_interest_students(state):
	dict_project_names = read_project_ids_and_names_from_input()
	unranked = False
	print
	threshold = classes.number_project_rankings / 2
	statement =  "The following students were assigned to a project below rank "
	statement += str(threshold) + ":"
	print statement
	stars = "***************************************************"
	stars += "**********************************"
	print stars
	(projects, inv_cov_mat_tup) = state
	for p in projects:
		for student in p.students:
			# Get the student's rank of this project.
			rank = student.get_ranking(p.ID)
			# The student didn't rank this
			if (rank > threshold):
				print student.name + " (" + str(student.degree_pursuing) + "):"
				print "------------------------"
				statement = "Assigned to rank " + str(rank) + ": "
				statement += str(dict_project_names[p.ID]) + "."
				print statement
				print "This student's rankings are: "
				for i in range (0, len(student.project_rankings)):
					print "Rank " + str(i + 1) + ":",
					rank_i_project_id = student.project_rankings[i]
					print dict_project_names[rank_i_project_id]
				unranked = True
				print
	if (not(unranked)):
		print "There were no students assigned to a low threshold project."
	print


