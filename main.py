from typing import List, Optional
from pydantic import BaseModel
import xml.etree.ElementTree as ET


class Time(BaseModel):
    days: str
    start: int
    length: int
    weeks: str
    penalty: int


class Room(BaseModel):
    id: str
    penalty: int


class Class(BaseModel):
    id: str
    limit: Optional[int]
    parent: Optional[str]
    room: bool = True
    rooms: List[Room]
    times: List[Time]


class Subpart(BaseModel):
    id: str
    classes: List[Class]


class Config(BaseModel):
    id: str
    subparts: List[Subpart]


class Course(BaseModel):
    id: str
    configs: Optional[List[Config]]


class Student(BaseModel):
    id: str
    courses: Optional[List[Course]]


class Distribution(BaseModel):
    type: str
    required: bool
    class_ids: List[str]


class OptimizationWeights(BaseModel):
    time: int
    room: int
    distibution: int
    student: int


class Problem(BaseModel):
    name: str  # unique name of the problem
    numberOfDays: int  # Number of days to use in optimization
    slotsPerDay: int  # One slot is 5 min
    numberOfWeeks: int  # Number of weeks in this problem (nrWeeks * nrDays * slotsPerDay = full optimization time)
    optimization_weights: OptimizationWeights
    courses: List[Course]
    distributions: List[Distribution]
    students: Optional[List[Student]]


class SolutionClass(BaseModel):
    id: str
    days: str
    start: str
    weeks: str
    room: str
    students: Optional[List[Student]]


class Solution(BaseModel):
    name: str
    rutime: float
    cores: int = 1
    technique: str
    author: str
    institution: str
    country: str
    classes: List[SolutionClass]


def parse_xml(file_path: str) -> Problem:
    tree = ET.parse(file_path)
    root = tree.getroot()

    optimization_elem = root.find("optimization")
    optimization_weights = OptimizationWeights(
        time=int(optimization_elem.get("time")),
        room=int(optimization_elem.get("room")),
        distibution=int(optimization_elem.get("distribution")),
        student=int(optimization_elem.get("student")),
    )

    courses = []
    for course_elem in root.findall("courses/course"):
        configs = []
        for config_elem in course_elem.findall("config"):
            subparts = []
            for subpart_elem in config_elem.findall("subpart"):
                classes = []
                for class_elem in subpart_elem.findall("class"):
                    # Parse rooms
                    rooms = [
                        Room(id=room.get("id"), penalty=int(room.get("penalty", 0)))
                        for room in class_elem.findall("room")
                    ]

                    # Parse times
                    times = [
                        Time(
                            days=time.get("days"),
                            start=int(time.get("start")),
                            length=int(time.get("length")),
                            weeks=time.get("weeks"),
                            penalty=int(time.get("penalty", 0)),
                        )
                        for time in class_elem.findall("time")
                    ]

                    # Create class
                    class_obj = Class(
                        id=class_elem.get("id"),
                        limit=int(class_elem.get("limit"))
                        if class_elem.get("limit")
                        else None,
                        parent=class_elem.get("parent"),
                        room=class_elem.get("room", "true").lower() != "false",
                        rooms=rooms,
                        times=times,
                    )
                    classes.append(class_obj)

                subpart = Subpart(id=subpart_elem.get("id"), classes=classes)
                subparts.append(subpart)

            config = Config(id=config_elem.get("id"), subparts=subparts)
            configs.append(config)

        course = Course(id=course_elem.get("id"), configs=configs)
        courses.append(course)

    # Parse distributions
    distributions = []
    for dist_elem in root.findall("distributions/distribution"):
        class_ids = [class_elem.get("id") for class_elem in dist_elem.findall("class")]
        distribution = Distribution(
            type=dist_elem.get("type"),
            required=dist_elem.get("required", "false").lower() == "true",
            class_ids=class_ids,
        )
        distributions.append(distribution)

    students = []
    for student_elem in root.findall("students/student"):
        courses = []
        for course in student_elem.findall("course"):
            courses.append(Course(course.get("id"), None))
        students.append(Student(student_elem.get("id"), courses))

    return Problem(
        name=root.get("name"),
        numberOfDays=root.get("nrDays"),
        slotsPerDay=root.get("slotsPerDay"),
        numberOfWeeks=root.get("nrWeeks"),
        optimization_weights=optimization_weights,
        courses=courses,
        distributions=distributions,
        students=students,
    )


def main():
    # Example usage
    problem = parse_xml("data/bet-sum18.xml")
    # You can now work with the structured data
    print(f"Number of courses: {len(problem.courses)}")
    print(f"Number of distributions: {len(problem.distributions)}")


if __name__ == "__main__":
    main()
