import enum


class StudentType(enum.Enum):
    """ Enum class to denote the status of students"""
    full_time = 1
    part_time = 2


class DegreeProgram(enum.Enum):
    """ Enum class that denotes a degree program"""
    mpcs = 1
    ba = 2
    mscapp = 3
    macss = 4
    mpcs_mba = 5


class Quarter(enum.Enum):
    """ Enum class that denotes a quarter"""
    fall = 1
    winter = 2
    spring = 3
    summer = 4


class Department(enum.Enum):
    """ Enum class that denotes a department"""
    mpcs = 1
    ppha = 2
    cmsc = 3
    busn = 4
    ttic = 5


class SectionType(enum.Enum):
    """ Enum class that denotes the type of section"""
    lecture = 1
    lab = 2
