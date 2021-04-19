from sqlalchemy import Column, Integer, String, Table, Boolean, ForeignKey, create_engine, Time, Enum
from sqlalchemy.orm import relationship, backref
from database import Database
from enums import Quarter, Department, SectionType


Base = Database().get_base()
db_session = Database().get_session()

# A self-referential association table to link courses to other courses that are their prereqs
prereqs = Table(
    'prereqs', Base.metadata,
    Column('course_id', Integer, ForeignKey('course.id'), primary_key=True),
    Column('prereq_id', Integer, ForeignKey('course.id'), primary_key=True)
)

# A association table to link students to the courses that they are enrolled in
student_roster = Table(
    'student_roster', Base.metadata,
    Column('student_id', Integer, ForeignKey('student.id'), primary_key=True),
    Column('section_id', Integer, ForeignKey('section.id'), primary_key=True)
)

# A association table to link instructors to the courses that they are teaching
instructor_roster = Table(
    'instructor_roster', Base.metadata,
    Column('instructor_id', Integer, ForeignKey('instructor.id'), primary_key=True),
    Column('section_id', Integer, ForeignKey('section.id'), primary_key=True)
)

class Section(Base):
    """
    The section class that creates a section which can persisted in the db.
    A course offering can have multiple sections. Sections can be of type lab or lecture.
    Sections aggregate students who are enrolled in it and instructors who teach it.
    """
    __tablename__ = 'section'
    id = Column(Integer, primary_key=True)
    course_offering_id = Column(Integer, ForeignKey('course_offering.id'))
    location = Column(String(50))
    instructor = relationship("Instructor", secondary=instructor_roster, back_populates ="taught_courses")
    type = Column(Enum(SectionType))
    time = Column(Time)
    size_limit = Column(Integer, default=30)
    enrolled_students = relationship("Student", secondary=student_roster, back_populates ="enrolled_courses")

    def __repr__(self):
        return f"id: {self.id}, course_offering_id: {self.course_offering_id}, location: {self.location}, " \
               f"time: {self.time}, type: {self.type}, instructor: {self.instructor}"


class CourseOffering(Base):
    """
    The class that creates a course-offering which can be persisted in the db.
    A course can have multiple course offerings for different years and quarters.
    A course offering can be composed of multiple sections.
    """
    __tablename__ = 'course_offering'
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('course.id'))
    year = Column(Integer())
    quarter = Column(Enum(Quarter))
    sections = relationship("Section", backref="offerings")

    def __repr__(self):
        return f"id: {self.id}, course_id: {self.course_id}, year: {self.year}, quarter: {self.quarter}"


class Course(Base):
    """
    The class that creates a course which can be persisted in the db.
    A course can be composed of multiple course-offerings. A course can also have prereqs.
    """
    __tablename__ = "course"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    course_code = Column(String(50), unique=True)
    department = Column(Enum(Department))
    description = Column(String(30))
    course_offerings = relationship("CourseOffering", backref="course")
    prereqs = relationship("Course", secondary=prereqs,
                           primaryjoin=id == prereqs.c.course_id,
                           secondaryjoin=id == prereqs.c.prereq_id)

    def __repr__(self):
        return f"id: {self.id}, name: {self.name}, course_code: {self.course_code}, description: {self.description}"


