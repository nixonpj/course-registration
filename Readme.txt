Course Registration System

Project Details:
Front-end: None
ORM: Sqlalchemy
Logger: Mongolog
Database: MySql

Setup
1. Clone repo on local machine.
2. Modify the engine parameters in the database.py file to point to your localhost.
3. Create a database called regie using Workbench.
3. Run the tests in the tests folder.

Completed
1. Created objects for each of the actors and entities in my project deliverable scope.
2. Persisted each of these in the MySql db.
3. Ability to create courses/offerings/sections.
4. Ability to look up courses by department, course number, time and instructor.
5. Ability to add a course to student's enrolled courses.

Incomplete/Missing
1. There is no user login and flow separation.
2. Not enough rigourous integrated testing.

Patterns Used
1. Builder to build a course/offering/section (controllers.py)
2. Decorator and Singleton for the database (database.py)
3. Chain of Responsibility and Template method (using ABCs) for implementing Course Registration(course_registration.py)
