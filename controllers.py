from sqlalchemy.exc import IntegrityError, InterfaceError
from courses import Course, CourseOffering, Section
from persons import Student, Instructor, Advisor
from database import Database
from logs import log

db_session = Database().get_session()
STUDENT_COURSE_LIMIT = 3


class CourseBuilder:
    """
    Class to build courses in a chained manner. Will only add components if the composite is present.
    For example, will only add section if the course offering is present.
    """
    def __init__(self, course_id=None, course_offering_id=None):
        self.course_id = course_id
        self.course_offering_id = course_offering_id

    def create_new_course(self, name, description, course_code, department, prereqs):
        try:
            new_course = Course(name=name, course_code=course_code, description=description, department=department)
            for prereq in prereqs:
                new_course.prereqs.append(prereq)
            db_session.add(new_course)
            db_session.flush()
            self.course_id = new_course.id
        except IntegrityError:
            db_session.rollback()
            log.error("Error due to attempted insertion of duplicate new course")
        finally:
            db_session.commit()
            return self

    def create_new_course_offering(self, year, quarter):
        if self.course_id:
            try:
                new_offering = CourseOffering(course_id=self.course_id, year=year, quarter=quarter)
                db_session.add(new_offering)
                db_session.flush()
                self.course_offering_id = new_offering.id
            except (IntegrityError, TypeError):
                db_session.rollback()
                log.error("Error due to attempted insertion of duplicate new course offering")
        db_session.commit()
        return self

    def create_new_section(self, location, instructor, section_type, time_):
        if self.course_offering_id:
            try:
                new_section = Section(course_offering_id=self.course_offering_id, type=section_type,
                                      location=location, time=time_)
                new_section.instructor = instructor
                db_session.add(new_section)
            except IntegrityError:
                db_session.rollback()
                log.error("Error due to attempted insertion of duplicate new course section")
        db_session.commit()
        return self


class CourseViewer:
    """ Class to help in viewing courses """
    def __init__(self):
        self.queried_courses = db_session.query(Course, CourseOffering, Section). \
            filter(CourseOffering.id == Section.course_offering_id). \
            filter(Course.id == CourseOffering.course_id)

    def view_courses(self, name=None, course_code=None, dept=None, quarter=None, instructor=None, section_type=None):
        if name:
            self.queried_courses = self.queried_courses.filter(Course.name.like('%' + name + '%'))
        if course_code:
            self.queried_courses = self.queried_courses.filter(Course.course_code == course_code)
        if dept:
            self.queried_courses = self.queried_courses.filter(Course.department == dept)
        if quarter:
            self.queried_courses = self.queried_courses.filter(CourseOffering.quarter == quarter)
        if instructor:
            self.queried_courses = self.queried_courses.filter(Section.instructor.contains(instructor))
        if section_type:
            self.queried_courses = self.queried_courses.filter(Section.type == section_type)
        return self.queried_courses.all()

    def view_roster(self, student):
        return self.queried_courses.filter(Section.enrolled_students.contains(student)).all()


def get_or_create(session, model, **kwargs):
    """
    Function to retrieve from db an object instance from the model table that matches kwargs
    or else create this instance in the db
    """
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance
