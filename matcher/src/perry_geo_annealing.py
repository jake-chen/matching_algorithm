import numpy as np
import util
from classes import CompError
from numpy import random
import pdb

def energy(state):
	'''
		Calculates the energy of a given state.
	'''
	projects = state[0]
	inv_cov_mat_tup = state[1]

	# Averages the costs on each project, and then averages across all projects.
	def avg_project_costs():
		project_costs = []
		for project in projects:
			costs = []
			for student in project.students:
				rank = student.get_ranking(project.ID)
				cost = student.get_cost_from_ranking(rank)
				costs.append(cost)
			avg_project_cost = np.mean(costs)
			project_costs.append(avg_project_cost)
		energy = np.mean(project_costs)
                print "AVERAGE PROJECT COSTS ARE " + str(energy)
		return energy

	def team_diversity_cost():
		diversities = []
                penalties = 0
		for project in projects:
			project_diversity = project.calculate_diversity(inv_cov_mat_tup)
			diversities.append(project_diversity)
                        numerics = []
                        for student in project.students:
                                numerics.append(student.get_numerical_student_properties())
                        programs = [x[0] for x in numerics]
                        b_abilities = [x[1] for x in numerics]
                        c_abilities = [x[2] for x in numerics]
                        w_exp = [x[3] for x in numerics]
                        #penalty for no MBAs
                        if 0 not in programs:
                                penalties += 1000
                        #penalty for no MEngs
                        if 1 not in programs:
                                penalties += 1000
                        #penalty for lack of coding experience (i.e. no one who rated their own coding ability as 3 or more)
                        if 3 not in c_abilities and 4 not in c_abilities:
                                penalties += 1000
                        #penalty for a lack of business ability
                        if 3 not in b_abilities and 4 not in b_abilities:
                                penalties += 1000
                        #penalty for lack of work experience
                        if 3 not in w_exp and 4 not in w_exp:
                                penalties += 1000
		avg_diversity = np.mean(diversities)
                print "TEAM DIVERSITY COST IS " + str(-avg_diversity)
                print "PENALTIES ARE " + str(penalties)
		return -(0.5 * avg_diversity) + penalties

	return 2*(avg_project_costs()) + team_diversity_cost()

def move(state, verbose = True, super_verbose = False):
	'''
		Makes a random change to a state.
		
		Picks two random teams, picks two random members, and performs
		a swap of these members across the teams.
		
		NOTE: there should be no teams of size 0 before calling the function.	
	'''
        project_exchange_probability = 0.01

	projects = state[0]
	inv_cov_mat_tup = state[1]
        feasibles = state[2]

        if random.random() < project_exchange_probability:
                project_to_swap = util.random_project(projects, [], True)
                feasible_IDs = [p.ID for p in feasibles]
                reasonable_project_IDs = list(set().union(*[set(s.project_rankings) for s in project_to_swap.students]))
                reasonable_projects = filter(lambda p:p.ID in reasonable_project_IDs, feasibles)
                def popularity(p):
                        return len(filter(lambda s:s.get_ranking(p.ID) < 100,project_to_swap.students))
                reasonable_projects.sort(key=popularity, reverse = True)
                most_likely_popular = reasonable_projects[:10]
                other = util.random_project(most_likely_popular, projects, False)
                tmp = project_to_swap.ID
                #pdb.set_trace()
                #print "swapping %s for %s" %(str(project_to_swap.ID), str(other.ID))
                #only remove/append if we're not swapping projects in the current list
                projects.remove(project_to_swap)
                projects.append(other)
                util.safe_project_swap(project_to_swap, other)
        else: 
                project_one = util.random_project(projects, [], True)
                project_two = util.random_project(projects, [], True)

                # Guarantee that the projects are not the same.
                # Continue to swap project two until it is diff from project one.
                while (project_one.ID == project_two.ID):
                        project_two = util.random_project(projects, [], True)
                        if (super_verbose):
                                print "Project one and project two are the same."

                if (super_verbose):
                        print "Found two different projects."

                        print "First team students are " + str([s.ID for s in project_one.students])
                        print "Second team students are " + str([s.ID for s in project_two.students])

                        print "CLEAR: made it to pick_team"

                # Team to pick first students from 
                pick_team = util.random_two_choice()

                if (pick_team == 0):
                        first_team = project_one
                        second_team = project_two
                else:
                        first_team = project_two
                        second_team = project_one

                # Pick a student from the first team, and this student will be swapped.

                student_one = util.random_student(first_team)
                student_two = util.random_student(second_team)

                # NOTE: this is problematic if teams aren't full.
                # 38
                # Guarantee that the students are of the same type.
                # while (not (student_one.degree_pursuing == student_two.degree_pursuing)):
                #	student_two = util.random_student(second_team)

                # Remove the students from their respective teams
                first_team.students.remove(student_one)
                if (not(student_two in second_team.students)):
                        if (super_verbose):
                                print "Second team students is " + str([s.ID for s in second_team.students])
                        error = "Student two ("
                        error += str(student_two.ID)
                        error += ") is not in second_team.students ("
                        error += str(second_team.ID)
                        error += ") "

                        raise CompError(error)
                second_team.students.remove(student_two)

                first_team.students.append(student_two)
                second_team.students.append(student_one)

	if (verbose):
		print "AFTER MOVE:"
		for p in projects:
		 	print str(p.ID) + ": " + str([s.ID for s in p.students])

	state_after_change = (projects, inv_cov_mat_tup, feasibles)

	print energy(state_after_change)

	return projects


