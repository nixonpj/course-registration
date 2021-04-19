import abc
from courses import Course, CourseOffering, Section
from persons import Student
from database import Database
from logs import log

db_session = Database().get_session()
STUDENT_COURSE_LIMIT = 3

"""
We use the chain of responsibility pattern to create a CourseRegistrationClass.
It checks for each of the possible barriers that could stop a student from registering."""

class CourseRegChain:
    """
    The Chain of Responsibility Client
    """

    def __init__(self):
        # Initializing the successors chain
        self.chain1 = StudentCourseLimitHandler()
        self.chain2 = SectionEnrolledLimitHandler()
        self.chain3 = PrereqsCheckHandler()
        self.chain4 = StudentRestrictionHandler()
        self.chain1.next_successor(self.chain2)
        self.chain2.next_successor(self.chain3)
        self.chain3.next_successor(self.chain4)


class CourseRegHandler(metaclass=abc.ABCMeta):
    """
    Define an interface for handling requests.
    Implement the successor link.
    """

    def __init__(self, successor=None):
        self._successor = successor

    def next_successor(self, next_handler):
        self._successor = next_handler

    @abc.abstractmethod
    def handle_request(self, student, course):
        pass


class StudentCourseLimitHandler(CourseRegHandler):
    """
    Handler that Checks if Student is enrolled in more than the course_limit before passing it on successor.
    """

    def handle_request(self, student, section):
        student_enrolled_in = db_session.query(Student.enrolled_courses).filter(Student.id == student.id).all()
        if len(student_enrolled_in) < STUDENT_COURSE_LIMIT:
            self._successor.handle_request(student, section)
        else:
            log.debug("course limit exceed. ask for permission")


class SectionEnrolledLimitHandler(CourseRegHandler):
    """
    Handler that checks if the section is full before forwardinf it to the successor.
    """

    def handle_request(self, student, section):
        section_enrolment = db_session.query(Section.enrolled_students).filter(Section.id == section.id).all()
        if len(section_enrolment) < section.size_limit:
            self._successor.handle_request(student, section)
        else:
            log.debug("course limit exceed. ask for permission")


class PrereqsCheckHandler(CourseRegHandler):
    """
    Handler that checks if the student has the necessary pre-reqs before it forwards it to the successor.
    """

    def handle_request(self, student, section):
        row = db_session.query(Section, CourseOffering, Course). \
            filter(Section.id == section.id).\
            filter(Section.course_offering_id == CourseOffering.id).\
            filter(CourseOffering.id == Course.id).one()
        for prereq in row.Course.prereqs:
            if prereq not in student.enrolled_courses:
                log.debug("Student doesnt have the prereq. Ask for Consent")
                return None
        self._successor.handle_request(student, section)


class StudentRestrictionHandler(CourseRegHandler):
    """ Handler that checks if student account has any restrictions on it before adding enrolling the student"""
    def handle_request(self, student, section):
        if student.restriction_hold:
            log.debug("Student has a restriction hold. Do something")
        else:
            student.enrolled_courses.append(section)
            db_session.commit()


class CourseRegModification:
    """ Student can drop or swap courses"""
    def __init__(self, student):
        self._student = student

    def drop_course(self, section):
        if section not in self._student.enrolled_courses:
            log.debug("Attempted to drop a course that student was not enrolled in.")
        else:
            self._student.enrolled_courses.remove(section)

    def swap_course(self, course_to_add, course_to_drop):
        self.drop_course(course_to_drop)
        crc = CourseRegChain()
        crc.chain1.handle_request(self._student, course_to_add)
        if course_to_add not in self._student.enrolled_courses:
            crc.chain1.handle_request(self._student, course_to_drop)

