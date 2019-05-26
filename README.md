# Patented Project Picker
Script for optimally assigning associates with project preferences to projects with limited availability.   
Nothing about this script is patented.  I just like the alliteration.  
It's mainly just an IO wrapper for an implementation of the [Kuhn–Munkres (Hungarian) algorithm](https://en.wikipedia.org/wiki/Hungarian_algorithm).


## Prerequisites
Installation of [Python 3](https://www.python.org/downloads/) (v3.5.0 or greater) is required.

## Usage
This repo contains two (mostly) empty .csv files.  The only information they contain is column headers to guide in placement of information.  These two files are to be used as input for the script.  

### Projects.csv
| Project Name | Number of vacancies  | Technologies |
|--------------|----------------------|--------------|
| ...          | ...                  | ...          |
| ...          | ...                  | ...          |

*Project Name - Identifying information of a project.  Project Name will be referenced in Preferences.csv.*  
*Number of vacancies - Maximum amount of associates which can be assigned to a given project.*  
*Technologies - Comma delimited list of technologies utilized in project.*
   
### Preferences.csv
| Associate Name | Associate ID | Pick1 | Pick2 | Pick3 | Pick4 | Pick5 |
|----------------|--------------|-------|-------|-------|-------|-------|
| ...            | ...          | ...   | ...   | ...   | ...   | ...   |
| ...            | ...          | ...   | ...   | ...   | ...   | ...   |

*Associate Name - The associate's name*  
*Associate ID - The associate's ID.  Any form of ID is fine: AW055790, aw055790, and 055790 are all acceptable*  
*Pick(x) - In order, the projects that the associate would prefer to be placed on.  Projects must be spelled the same here as they are in Projects.csv.  Alternatively, a digit can be placed here (which will index into the projects listed in Projects.csv).*  
**Note: Although there are only 5 slots for project picks, the script accepts arbitrary amounts of project picks.  Generally, the more picks listed, the more likely everyone will be able to get close to their top pick.**  

Executing script like this will use default input files: Projects.csv, and Projects.csv
```
./project_assigner.py
```

Optionally, you can override the default input files like so
```
./project_assigner.py non_default_projects.csv non_default_preferences.csv
```

You can also specify your python interpreter if you have multiple (remember, it needs to be > v3.5.0)
```
python3 ./project_assigner.py
```
### The resulting output will be written both to the screen and to Assignments.csv
Note: The console output of the script uses ANSI escape sequences, so use a terminal which supports this or else things won't be nice and colorful.
