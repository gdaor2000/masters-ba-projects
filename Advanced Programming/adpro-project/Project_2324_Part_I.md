# Welcome to project Icaras
---

## Scenario

Your company was asked to analyse Commercial Airfligh data for a sustainability study. Your group is the best team of Data Scientists in the company's roster and are given the challenge. By undertaking this task, your company expects to contribute to the green transition by having a more savvy taskforce. You decide to create some python tools for the challenge.

## Goal

For this project, we will be using data from [International Air Transport Association](https://www.iata.org/). The datasets can be found [here](https://gitlab.com/adpro1/adpro2024/-/raw/main/Files/flight_data.zip?inline=false).

Go over the datasets. You were not given a data dictionary, but the fields can be easily discovered with an online search, as this is heavily used data.

<div class="alert alert-danger">
    <b> THE MOST IMPORTANT TOOLS FOR A DATA SCIENTIST IS PATIENCE AND COMMUNICATION</b>
    <br>
    <b> Discuss the contents of the dataset with your colleagues. Understanding the data is a priority. </b>
</div>

Use whatever python tools you find apropriate.

## Structure of the project

You are going to build a **Showcase Notebook** that doubles as a presentation for your analysis.  
Keep all the .py files in separate directories. The only files in the main directory of the project should be the **Showcase Notebook** and the several configuration files (.yml, .gitignore, and others). Everything else should have their own directories.

### Day 1, Phase 1

- [ ] One of you will create a gitlab/github repository (it does not matter who). __THE NAME OF THE REPOSITORY MUST BE "Group_XX" where XX is the number of your group! If you are group 3, then XX must be 03. Always use two digits and an underscore!__
- [ ] Initialize the repo with a README.md file, a proper license, and a .gitignore for the programming language you will use. The README.md file __MUST__ have your emails in a way that it is possible to copy and paste it into an email.
- [ ] The one who created the repository will then give __Maintainer__ permissions to the rest of the group. Check under "Project Information" > "Members".
- [ ] Every element of the group clones the repository to their own laptops.

### Day 1, Phase 2

- [ ] The class you decide the create for the project has finally been named after a brief internal fight and is __PEP8 compliant, like the entire project__.

The class will have several methods, which you will __not__ develop in the master branch.  
Document everything!  
Make your calls compliant with __pydantic__ and __static type checking__ when appliable.

- [ ] During the _init_ method, your class must download the data file into a __downloads/__ directory in the root directory of the project (main project directory). If the data file already exists, the method will not download it again.
- [ ] The _init_ method must also read the datasets into a corresponding pandas dataframe which become attributes for your class. Remove superfluous columns.
- [ ] Develop a function to calculate the real __distances__ between airports in kilometers in its own .py file with the information in the datasets. Approximate the earth to a sphere (it is safe to disregard __altitude__). Develop a unit test to this function with three cases, where one must be between two airports in different continents. Implement a way to make the distances between airports part of the information contained in your future class instance.

## Day 1, Phase 3

- [ ] Develop a first method that takes a country as an input and plots a map with the locations of its airports (as well as a map for that country). If the country does not exist, return a useful error message. __DO NOT USE INTERACTIVE PROMPTS; IT SHOULD REALLY JUST BE AN ARGUMENT!__
- [ ] Develop a second method called __distance_analysis__. This should plot the distribution of flight distances for all flights.
- [ ] Develop a third method that receives an airport as an input and an optional argument called __internal__ with a value of __False__ by default. If __internal__ is __True__, then this method should plot only the flights leaving this airport with a destination in the same country. Otherwise, it plots all flights.
- [ ] Develop a fourth method that may receive a string with a country or a list of country strings but has __None__ by default. This method should plot the __N__ most used airplane models by number of routes. If the input argument is __None__ it should plot for all dataset. If it receives only a country or list of countries, it should plot just for that subset.
- [ ] Develop a fifth method that receives a country name as an input and an optional argument called __internal__ with a value of __False__ by default. If __internal__ is __True__, then this method should plot only the flights leaving the country with a destination in the same country. Otherwise, it plots all flights. This is analogous to the third method, but for country now.

### Day 1, Phase 4

- [ ] Make a "showcase notebook" where you import your __Class__ and showcase all the methods you developed. Tell a story about your analysis and findings in the showcase notebook. Use all methods with several complementary options. If you feel lost about what story to tell, don't hesitate to contact the professor.

<div class="alert alert-info">
    <b> REMEMBER: The first delivery is until March 4 23:59:59 and it is not graded. It is used as course correction. The delivery is the git repo link. </b>
</div>

<div class="alert alert-danger">
    <b> The notebook must RUN from start to finish. If one runs all cells again, the output must be the same.</b>
</div>

<div class="alert alert-info">
    <b> REMEMBER: IT IS OK TO PROTOTYPE CODE IN NOTEBOOKS, BUT THE FINAL CLASS MUST BE IN A SINGLE .py FILE! </b>
    <br>
    <b> The final delivery of the project is the "showcase" notebook from Phase 4. Don't place this notebook together with prototyping notebooks.</b>
    <br>
    <b> Prototyping notebooks must have their own separate directory.</b>
    <br>
    <b> We will only consider contents in your "master" repository.</b>
</div>

<div class="alert alert-warning">
    <b>When in doubt, ask.</b>
</div>
