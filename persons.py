from sqlalchemy import Column, Integer, String, Table, Boolean, ForeignKey, create_engine, Time, Enum, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from database import Database
from enums import DegreeProgram, Department, StudentType
from courses import student_roster, instructor_roster

Base = Database().get_base()
db_session = Database().get_session()


class Student(Base):
    """
    Student class representing student in the model.
    Students aggregate enrolled courses
    """
    __tablename__ = 'student'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(20))
    last_name = Column(String(30))
    type = Column(Enum(StudentType))
    preferred_name = Column(String(30))
    degree_program = Column(Enum(DegreeProgram))
    department = Column(Enum(Department))
    academic_advisor_id = Column(Integer, ForeignKey('advisor.id'))
    academic_advisor = relationship("Advisor", back_populates="students_advised")
    restriction_hold = Column(Boolean, default=False)
    enrolled_courses = relationship("Section", secondary=student_roster, back_populates="enrolled_students")

    __table_args__ = (
        UniqueConstraint(first_name, last_name, preferred_name, department),
    )

    def __repr__(self):
        return f"id: {self.id}, first_name: {self.first_name}, last_name: {self.last_name}, type: {self.type}" \
               f"degree_program: {self.degree_program}"


class Instructor(Base):
    """
    Instructor class that represents an instructor in the model.
    Instructors aggregate courses that they personally teach.
    """
    __tablename__ = 'instructor'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(20))
    last_name = Column(String(30))
    preferred_name = Column(String(30))
    department = Column(Enum(Department))
    taught_courses = relationship("Section", secondary=instructor_roster, back_populates="instructor")

    __table_args__ = (
        UniqueConstraint(first_name, last_name, preferred_name, department),
    )

    def __repr__(self):
        return f"id: {self.id}, first_name: {self.first_name}, last_name: {self.last_name}, " \
               f"department: {self.department}"


class Advisor(Base):
    """
    Advisor class that represents academic advisors in the model.
    Advisors aggregate students that they advise.
    """
    __tablename__ = 'advisor'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(20))
    last_name = Column(String(30))
    preferred_name = Column(String(30))
    department = Column(Enum(Department))
    students_advised = relationship("Student", back_populates="academic_advisor")

    __table_args__ = (
        UniqueConstraint(first_name, last_name, preferred_name, department),
    )

    def __repr__(self):
        return f"id: {self.id}, first_name: {self.first_name}, last_name: {self.last_name}, " \
               f"department: {self.department}"



