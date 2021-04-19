import unittest
from courses import Course, CourseOffering, Section
from persons import Student, Instructor, Advisor
from controllers import CourseBuilder, CourseViewer, get_or_create
from database import Database
from enums import Quarter, Department, StudentType, DegreeProgram, SectionType
from sqlalchemy import create_engine


class TestCourseSection(unittest.TestCase):
    def setUp(self) -> None:
        Base = Database().get_base()
        engine = create_engine('mysql+mysqlconnector://root:root@localhost:3306/regie', echo=True)

        Base.metadata.create_all(bind=engine)
        self.db_session = Database().get_session()



    def test_advisor_addition(self):
        self.advisor1 = get_or_create(self.db_session, Advisor, first_name="Kate", last_name="B",
                                      preferred_name="Katie", department=Department.mpcs)
        self.assertEqual(self.advisor1.preferred_name, "Katie")

    def test_student_addition(self):
        self.advisor1 = get_or_create(self.db_session, Advisor, first_name="Kate", last_name="B",
                                      preferred_name="Katie", department=Department.mpcs)
        self.student1 = get_or_create(self.db_session, Student, first_name="John", last_name="Doe",
                                      type=StudentType.full_time, preferred_name="John",
                                      degree_program=DegreeProgram.mpcs, department=Department.mpcs,
                                      academic_advisor=self.advisor1)
        self.student2 = get_or_create(self.db_session, Student, first_name="Mark", last_name="Antony",
                                      type=StudentType.full_time, preferred_name="Mark",
                                      degree_program=DegreeProgram.mpcs, department=Department.mpcs,
                                      academic_advisor=self.advisor1)
        self.student3 = get_or_create(self.db_session, Student, first_name="Mary", last_name="George",
                                      type=StudentType.full_time, preferred_name="Mary",
                                      degree_program=DegreeProgram.mpcs, department=Department.mpcs,
                                      academic_advisor=self.advisor1)
        self.student4 = get_or_create(self.db_session, Student, first_name="Paula", last_name="Cardano",
                                      type=StudentType.full_time, preferred_name="Paula",
                                      degree_program=DegreeProgram.mpcs, department=Department.mpcs,
                                      academic_advisor=self.advisor1)
        self.assertEqual(self.student1.preferred_name, "John")
        self.assertEqual(self.student2.preferred_name, "Mark")
        self.assertEqual(self.student3.preferred_name, "Mary")
        self.assertEqual(self.student4.preferred_name, "Paula")

    def test_instructor_addition(self):
        self.instructor1 = get_or_create(self.db_session, Instructor, first_name="Mark", last_name="Shacklette",
                                         preferred_name="Mark", department=Department.mpcs)
        self.assertEqual(self.instructor1.preferred_name, "Mark")

    def test_course_addition(self):
        self.instructor1 = get_or_create(self.db_session, Instructor, first_name="Mark", last_name="Shacklette",
                                         preferred_name="John", department=Department.mpcs)
        cb = CourseBuilder()
        cb.create_new_course("OOP", "All about objects", 51210, Department.mpcs, []). \
            create_new_course_offering(2020, Quarter.winter). \
            create_new_section("Ryerson 271", [self.instructor1], SectionType.lecture, "17:30"). \
            create_new_section("Ryerson 272", [self.instructor1], SectionType.lab, "13:30")

        added_course = self.db_session.query(Course).filter(Course.course_code == 51210).one()
        self.assertIsNotNone(added_course)

    def test_offering_addition(self):
        added_offering = self.db_session.query(CourseOffering, Course).\
            filter(Course.id == CourseOffering.course_id).\
            filter(Course.name == "OOP").\
            filter(CourseOffering.year == 2020).one()
        self.assertIsNotNone(added_offering)

    def test_section_addition(self):
        added_section = self.db_session.query(Section, CourseOffering, Course).\
            filter(Course.name == "OOP").\
            filter(Section.course_offering_id==CourseOffering.id).\
            filter(Section.location=="Ryerson 271").first()
        self.assertIsNotNone(added_section)

    def test_prereq_addition(self):
        self.instructor1 = get_or_create(self.db_session, Instructor, first_name="Mark", last_name="Shacklette",
                                         preferred_name="John", department=Department.mpcs)
        oop_prereq = self.db_session.query(Course).filter(Course.course_code == '51210').one()
        CourseBuilder().create_new_course("Advanced OOP", "All about objects", 51211, Department.mpcs, [oop_prereq]). \
            create_new_course_offering(2021, Quarter.spring). \
            create_new_section("Ryerson 271", [self.instructor1], SectionType.lecture, "17:30"). \
            create_new_section("Ryerson 272", [self.instructor1], SectionType.lab, "13:30")
        cv = CourseViewer()
        self.assertIn(oop_prereq, cv.view_courses(name="OOP", course_code=51211, dept=Department.mpcs, quarter=Quarter.spring,
                                         section_type=SectionType.lecture)[0].Course.prereqs)

    def test_view_courses(self):
        cv = CourseViewer()
        self.assertEqual(cv.view_courses(name="OOP", course_code=51211, dept=Department.mpcs, quarter=Quarter.spring,
                                         section_type=SectionType.lecture)[0].Course.name, "Advanced OOP")

    def cleanUp(self):
        self.db_session.commit()


if __name__ == '__main__':
    unittest.main()
