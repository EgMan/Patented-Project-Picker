#!/usr/bin/python3

import re
import os
import sys
import csv
from munkres.munkres import Munkres, print_matrix, DISALLOWED

valid_data = True

def main():
    projects_loc, project_picks_loc, manager_picks_loc = gather_params()

    projects = ProjectDirectory(projects_loc)
    project_picks = AssociatePicksDirectory(project_picks_loc, projects)
    assigments = compute_assignments(project_picks)

"""
    matrix = [[DISALLOWED, 2, DISALLOWED, 3],
                    [3, 7, 8, 2],
                    [DISALLOWED, 3, 6, 1]]
    m = Munkres()
    indexes = m.compute(matrix)
    print_matrix(matrix, msg='Highest profits through this matrix:')
    total = 0
    for row, column in indexes:
        value = matrix[row][column]
        total += value
        print('(%d, %d) -> %d' % (row, column, value))
        print('total profit=%d' % total)
  """  

def gather_params():
    #TODO add param validation
    return sys.argv[1], sys.argv[2], None

def compute_assignments(project_picks):
    cprint("\nCasting hungarian magic", bcolors.BOLD)
    matrix = project_picks.cost_matrix
    m = Munkres()
    indexes = m.compute(matrix)
    print_matrix(matrix)
    total = 0
    for row, column in indexes:
        value = matrix[row][column]
        total += value
        print('(%d, %d) -> %d' % (row, column, value))
        print('total profit=%d' % total)


class ProjectDirectory:
    def __init__(self, projects_loc):
        self.projects_by_name, self.projects_by_idx, self.projects_by_vacancy_number = self.__load_projects(projects_loc)

    class Project:
        def __init__(self, index, name, vacancies, tech):
            self.index = index
            self.name = name
            self.vacancies = vacancies
            self.tech = tech

    def __load_projects(self, projects_loc):
        cprint("\nLoading Projects", bcolors.BOLD)
        projects_by_name = {}
        projects_by_idx = []
        projects_by_vacancy_number = []
        with open(projects_loc, 'r') as file:
            try:
                reader = csv.reader(file)
                for rowidx, row in enumerate(reader):
                    name = row[0]
                    vacancies = row[1]
                    tech = row[2]
                    if not name:
                        cprint("\tFixMe: no name specified for project {}".format(rowidx), bcolors.FAIL)
                        valid_data = False
                    if not vacancies:
                        cprint("\tWrn: no number of vacancies specified for project {}. Assuming 1 free spot.".format(rowidx), bcolors.WARNING)
                        vacancies = 1
                    if not vacancies.isdigit():
                        cprint("\tWrn: number of vacancies for project {} is not a number.  Assuming 1 free spot.".format(rowidx), bcolors.WARNING)
                        vacancies = 1
                    else:
                        vacancies = int(vacancies)
                    if all( not t for t in tech ):
                        cprint("\tWrn: Project {} has no tech specified".format(rowidx), bcolors.WARNING)
                    new_project = self.Project(rowidx, name, vacancies, tech)
                    projects_by_idx.append(new_project)
                    projects_by_name[new_project.name.lower()] = new_project
                    projects_by_vacancy_number.extend([new_project] * new_project.vacancies)
                    cprint("\tProject {}: name='{}' vacancies={} tech={}".format(rowidx, new_project.name, new_project.vacancies, new_project.tech), bcolors.OKBLUE)
            except csv.Error as e:
                sys.exit('file {}, line {}: {}'.format(projects_loc, reader.line_num, e))
        return projects_by_name, projects_by_idx, projects_by_vacancy_number


class AssociatePicksDirectory:
    def __init__(self, picks_loc, projects):
       self.picks_by_idx, self.cost_matrix = self.__load_picks(picks_loc, projects)

    class AssociatePicks:
        def __init__(self, index, name, associate_id, picks):
            self.index = index
            self.associate_name = name
            self.associate_id = associate_id
            self.picks = picks

    def __load_picks(self, picks_loc, projects):
        cprint("\nLoading Picks", bcolors.BOLD)

        picks_by_idx = []
        cost_matrix = []

        with open(picks_loc, 'r') as file:
            try:
                reader = csv.reader(file)
                for rowidx, row in enumerate(reader):
                    associate_name = row[0]
                    associate_id = row[1].upper()
                    picks = []
                    if not associate_name:
                        cprint("Wrn: Associate below is missing a name.", bcolors.WARNING)
                    if not associate_id:
                        cprint("\tFixMe: Associate below is missing an associate id.", bcolors.FAIL)
                        valid_data = False
                    for pick in row[2:]:
                        if not pick:
                            continue
                        if pick.isdigit():
                            pickidx = int(pick)
                            if pickidx < 0 or pickidx >= len(projects.projects_by_idx):
                                cprint("\tFixMe: Project index below {} is out of bounds".format(pickidx), bcolors.FAIL)
                                valid_data = False
                            else:
                                picks.append(projects.projects_by_idx[pickidx])
                        else:
                            if not pick.lower() in projects.projects_by_name:
                                cprint("\tFixMe: couldn't find project below '{}'"
                                    "in projects file.\n\tConsider fixing spelling "
                                    "(case insensitive) or using a project index in "
                                    "place of the name.".format(pick), bcolors.FAIL)
                                valid_data = False
                            else:
                                picks.append(projects.projects_by_name[pick.lower()])
                    if len(picks) == 0:
                        cprint("\tWrn: No picks have been chosen below", bcolors.WARNING)
                    new_picks = self.AssociatePicks(rowidx, associate_name, associate_id, picks)
                    picks_by_idx.append(new_picks)
                    cprint("\t({}) {}'s picks in order: {}".format(new_picks.associate_id, new_picks.associate_name, [ p.name for p in new_picks.picks]), bcolors.OKBLUE)

                    #Create the cost matrix row
                    if len(new_picks.picks) == 0:
                        cost_row = [0]*len(projects.projects_by_vacancy_number)
                    else:
                        cost_row = [DISALLOWED]*len(projects.projects_by_vacancy_number)
                    for projidx, project in enumerate(projects.projects_by_vacancy_number):
                        if project in new_picks.picks:
                            cost = new_picks.picks.index(project) + 1
                            cost_row[projidx] = cost
                    cost_matrix.append(cost_row)
            except csv.Error as e:
                sys.exit('file {}, line {}: {}'.format(projects_loc, reader.line_num, e))
        
        return picks_by_idx, cost_matrix
    

                

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
def cprint(message, color):
    print("{0}{1}{2}".format(color,message,bcolors.ENDC))

if __name__ == '__main__':
    main()
