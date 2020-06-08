MyDiaryApp is a web app in which users can create and maintain multiple diaries. Users can add entries to each diary, creating a unique title and editing the text of the entry. Each entry is given a time stamp upon creation and can be sorted by recency (most recent first, or most recent last). Users can also create their own tags by which to categorize their entries in a given diary.

Code Style
For Python code, use pycodestyle. See https://pypi.org/project/pycodestyle/ for installation and other details. To install the linter plugin in Atom (IDE of choice), see https://atom.io/packages/linter-pycodestyle. After installation, open Atom and follow the prompts for installation of dependencies. Once all are complete, you should be able to navigate to the Packages tab in Atom's Settings page and find linter-pycodestyle there. When viewing python files, the number of errors and warnings will be marked in the bottom left menu bar of Atom.

For JavaScript/React code use Prettier. Either type in the command line apm install prettier-atom or in Atom, go to File->Settings->Install and search for and install prettier-atom. Restart Atom, and the installation will be complete. See https://atom.io/packages/prettier-atom for details.

Needed Versions:
IMPORTANT: Flask 1.1 https://palletsprojects.com/blog/flask-1-1-released/
We're also using Python 3.6

UI Prototype
A UI Prototype for this project an can be found on Figma at the url below.
https://www.figma.com/file/UlfzbnwB736Uien6Gj9IHU/MyDiaryApp?node-id=0%3A1

Use Case Diagram and Class Diagram:
https://github.com/lhmcgann/MyDiaryApp/wiki

Development Environment Setup

Instructions to Run Backend
1. clone the repository
2. cd into the backend directory
3. Activate the python virtual environment by running "source python_env/bin/activate"
4. Run flask using flask run
5. Send appropriate API requests following the API design doc in the docs folder of the repository

Instructions to Run FrontEnd
1. Run 'npm install'
2. Run 'npm start'


Travis CI Link:
https://travis-ci.org/github/lhmcgann/MyDiaryApp


