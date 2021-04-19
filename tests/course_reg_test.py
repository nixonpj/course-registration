import unittest
from courses import Course, CourseOffering, Section
from persons import Student, Instructor, Advisor
from controllers import CourseBuilder, CourseViewer, get_or_create
from database import Database
from enums import Quarter, Department, StudentType, DegreeProgram, SectionType
from sqlalchemy import create_engine
from course_registration import CourseRegChain


class TestCourseSection(unittest.TestCase):
    def setUp(self) -> None:
        Base = Database().get_base()
        engine = create_engine('mysql+mysqlconnector://root:root@localhost:3306/regie', echo=True)

        Base.metadata.create_all(bind=engine)
        self.db_session = Database().get_session()
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
        self.student3 = get_or_create(self.db_session, Student, first_name="Nita", last_name="C",
                                      type=StudentType.full_time, preferred_name="Nita",
                                      degree_program=DegreeProgram.mpcs, department=Department.mpcs,
                                      academic_advisor=self.advisor1, restriction_hold=True)
        self.instructor1 = get_or_create(self.db_session, Instructor, first_name="Mark", last_name="Shacklette",
                                         preferred_name="Mark", department=Department.mpcs)
        cb = CourseBuilder()
        cb.create_new_course("OOP", "All about objects", 51210, Department.mpcs, []). \
            create_new_course_offering(2020, Quarter.winter). \
            create_new_section("Ryerson 271", [self.instructor1], SectionType.lecture, "17:30"). \
            create_new_section("Ryerson 272", [self.instructor1], SectionType.lab, "13:30")
        self.db_session.add(self.student1)
        self.db_session.add(self.student2)
        self.db_session.add(self.student3)
        self.db_session.commit()

    def test_course_registration_success(self):
        # Client calling the chain
        student = self.db_session.query(Student).first()
        section = self.db_session.query(Section).first()
        crc = CourseRegChain()
        crc.chain1.handle_request(student, section)
        self.assertIn(section, student.enrolled_courses)

    def test_course_registration_failure(self):
        # Client calling the chain
        student = self.db_session.query(Student).filter(Student.restriction_hold == True).first()
        section = self.db_session.query(Section).first()
        crc = CourseRegChain()
        crc.chain1.handle_request(student, section)
        self.assertNotIn(section, student.enrolled_courses)


if __name__ == '__main__':
    unittest.main()
