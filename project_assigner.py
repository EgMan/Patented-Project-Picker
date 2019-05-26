#!/usr/bin/python3

import re
import os
import sys
import csv
from munkres.munkres import Munkres, print_matrix, DISALLOWED

valid_data = True

def main():
    projects_loc, project_picks_loc = gather_params()
    projects = ProjectDirectory(projects_loc)
    project_picks = AssociatePicksDirectory(project_picks_loc, projects)
    if valid_data:
        assignments = compute_assignments(project_picks)
        output_assignments(assignments, projects, project_picks)
    else:
        cprint("\nSome input data is malformed.  Please fix this before moving forward.\n"
                "Such issues will be prefaced with \"FixMe\" in the output above.", bcolors.FAIL)

def gather_params():
    if len(sys.argv) == 3:
        proj = sys.argv[1]
        pick = sys.argv[2]
    else:
        proj = "Projects.csv"
        pick = "Preferences.csv"
    cprint(f"\nUsing input files: \n\t{bcolors.OKBLUE}Projects = {proj}\n\tPicks = {pick}\n", bcolors.BOLD)
    return proj, pick

def compute_assignments(project_picks):
    cprint("\nCasting Hungarian magic\n", bcolors.BOLD)
    matrix = project_picks.cost_matrix
    m = Munkres()
    assignments = m.compute(matrix)
    print_matrix(matrix)
    return assignments

def output_assignments(assignments, projects, project_picks):
    cprint("\nOutputting assignments to file", bcolors.BOLD)
    assignments_out_console = []
    assignments_out_file = []

    for associateidx, vacancyidx in assignments:
        assignments_out_console.append([project_picks.picks_by_idx[associateidx].associate_name, "->", 
            projects.projects_by_vacancy_number[vacancyidx].name, 
            f"(pick #{project_picks.cost_matrix[associateidx][vacancyidx]})"])

        assignments_out_file.append([project_picks.picks_by_idx[associateidx].associate_name, 
            project_picks.picks_by_idx[associateidx].associate_id,
            projects.projects_by_vacancy_number[vacancyidx].name])

    #Print the assignments to console
    printcols(assignments_out_console, color=bcolors.OKGREEN)

    #Output the assignments to file
    out_file_name = "Assignments.csv"
    with open(out_file_name, 'w') as file:
        writer = csv.writer(file)
        writer.writerows(assignments_out_file)
    cprint(f"\nSuccesfully wrote assignments to: {out_file_name}", bcolors.OKGREEN)


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
        global valid_data
        cprint("\nLoading projects", bcolors.BOLD)
        projects_by_name = {}
        projects_by_idx = []
        projects_by_vacancy_number = []
        projs_out=[]
        errs=""
        wrns=""
        with open(projects_loc, 'r', encoding="utf-8-sig") as file:
            try:
                reader = csv.reader(file)
                for rowidx, row in enumerate(reader):
                    if rowidx == 0 and row[0] == "Project Name":
                        #skip first row with column names
                        continue
                    name = row[0]
                    vacancies = row[1]
                    tech = row[2]
                    if not name:
                        errs+=cstring(f"\tFixMe: (row {rowidx + 1}) No name specified for project.\n", bcolors.FAIL)
                        valid_data = False
                    else:
                        name.replace('\\ufeff', '')
                    if not vacancies:
                        wrns+=cstring(f"\tWrn: (row {rowidx + 1}) No number of vacancies specified for project. Assuming 1 free spot.\n", bcolors.WARNING)
                        vacancies = 1
                    if not vacancies.isdigit():
                        wrns+=cstring(f"\tWrn: (row {rowidx + 1}) Number of vacancies for project is not a number.  Assuming 1 free spot.\n", bcolors.WARNING)
                        vacancies = 1
                    else:
                       vacancies = int(vacancies)
                    if all( not t for t in tech ):
                        wrns+=cstring(f"\tWrn: (row {rowidx + 1}) Project has no tech specified.", bcolors.WARNING)
                    new_project = self.Project(rowidx, name, vacancies, tech)
                    projects_by_idx.append(new_project)
                    projects_by_name[new_project.name.lower()] = new_project
                    projects_by_vacancy_number.extend([new_project] * new_project.vacancies)
                    projs_out.append([new_project.name+":", f"vacancies={new_project.vacancies}", f"tech={new_project.tech}"])
            except csv.Error as e:
                sys.exit(f'file {projects_loc}, line {reader.line_num}: {e}')
            printcols(projs_out)
            print(wrns+errs)
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
        global valid_data
        cprint("\nLoading associate picks", bcolors.BOLD)

        picks_by_idx = []
        cost_matrix = []
        picks_out=[]
        errs=""
        wrns=""

        with open(picks_loc, 'r', encoding="utf-8-sig") as file:
            try:
                reader = csv.reader(file)
                for rowidx, row in enumerate(reader):
                    if rowidx == 0 and row[0] == "Associate Name":
                        #skip first row with column names
                        continue
                    associate_name = row[0]
                    associate_id = row[1].upper()
                    picks = []
                    if not associate_name:
                        wrns+=cstring(f"\tWrn: (row {rowidx + 1}) Associate is missing a name.\n", bcolors.WARNING)
                    if not associate_id:
                        wrns+=cstring(f"\tFixMe: (row {rowidx + 1}) Associate is missing an associate id.\n", bcolors.FAIL)
                        valid_data = False
                    for pick in row[2:]:
                        if not pick:
                            continue
                        if pick.isdigit():
                            pickidx = int(pick)
                            if pickidx < 0 or pickidx >= len(projects.projects_by_idx):
                                errs+=cstring(f"\tFixMe: (row {rowidx + 1}) Project index {pickidx} is out of bounds.\n", bcolors.FAIL)
                                valid_data = False
                            else:
                                picks.append(projects.projects_by_idx[pickidx])
                        else:
                            if not pick.lower() in projects.projects_by_name:
                                errs+=cstring(f"\tFixMe: (row {rowidx + 1}) couldn't find project '{pick}' "
                                    "in projects file.\n\tConsider fixing spelling "
                                    "(case insensitive) or using a project index in "
                                    "place of the name.\n", bcolors.FAIL)
                                valid_data = False
                            else:
                                picks.append(projects.projects_by_name[pick.lower()])
                    if len(picks) == 0:
                        wrns+=cstring(f"\tWrn: (row {rowidx + 1}) No picks have been chosen.\n", bcolors.WARNING)
                    new_picks = self.AssociatePicks(rowidx, associate_name, associate_id, picks)
                    picks_by_idx.append(new_picks)
                    picks_out.append([new_picks.associate_id, f"picks={str([ p.name for p in new_picks.picks ])}"])

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
                sys.exit('file {picks_loc}, line {reader.line_num}: {e}')
            printcols(picks_out)
            print(wrns+errs)        
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
def cstring(message, color):
    return f"{color}{message}{bcolors.ENDC}"
def cprint(message, color):
    print(cstring(message,color))
def printcols(data, color=bcolors.OKBLUE, padding=2):
    #col_width = [len(word) for word in data[:,idx]].max()
    if not data or len(data) == 0:
        return
    col_width = []
    for i, word in enumerate(data[0]):
        col_width.append(max([len(row[i]) for row in data]) + padding)
    for row in data:
            print("\t",color,"".join(word.ljust(col_width[idx]) for idx, word in enumerate(row)), bcolors.ENDC)

if __name__ == '__main__':
    main()
