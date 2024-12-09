import random
from typing import Any, List, Optional
from pydantic import BaseModel
import xml.etree.ElementTree as ET


class Time(BaseModel):
    days: str
    start: int
    length: int
    weeks: str
    penalty: int


class Unavailable(BaseModel):
    days: str
    start: int
    length: int
    weeks: str


class Room(BaseModel):
    id: str
    capacity: int
    unavailable: List[Unavailable]


class PossibleRoom(BaseModel):
    id: str
    penalty: int


class Class(BaseModel):
    id: str
    limit: Optional[int]
    parent: Optional[str]
    room: bool = True
    rooms: List[PossibleRoom]
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
    rooms: List[Room]
    courses: List[Course]
    distributions: List[Distribution]
    students: Optional[List[Student]]


class SolutionClass(BaseModel):
    id: str
    days: str
    start: int
    weeks: str
    room: Optional[str]
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


def parse_rooms_xml(root: ET.Element | Any) -> List[Room]:
    rooms = []
    for room_elem in root.findall("rooms/room"):
        unavailable = []
        for unavailable_elem in room_elem.findall("unavailable"):
            unavailable.append(
                Unavailable(
                    days=unavailable_elem.get("days"),
                    start=int(unavailable_elem.get("start")),
                    length=int(unavailable_elem.get("length")),
                    weeks=unavailable_elem.get("weeks"),
                )
            )
        rooms.append(
            Room(
                id=room_elem.get("id"),
                capacity=int(room_elem.get("capacity")),
                unavailable=unavailable,
            )
        )
    return rooms


def parse_courses_xml(root: ET.Element | Any) -> List[Course]:
    courses = []
    for course_elem in root.findall("courses/course"):
        configs = []
        for config_elem in course_elem.findall("config"):
            subparts = []
            for subpart_elem in config_elem.findall("subpart"):
                classes = []
                for class_elem in subpart_elem.findall("class"):
                    # Parse rooms
                    possible_rooms = [
                        PossibleRoom(
                            id=room.get("id"), penalty=int(room.get("penalty", 0))
                        )
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
                        rooms=possible_rooms,
                        times=times,
                    )
                    classes.append(class_obj)

                subpart = Subpart(id=subpart_elem.get("id"), classes=classes)
                subparts.append(subpart)

            config = Config(id=config_elem.get("id"), subparts=subparts)
            configs.append(config)

        course = Course(id=course_elem.get("id"), configs=configs)
        courses.append(course)
    return courses


def parse_distributions_xml(root: ET.Element | Any) -> List[Distribution]:
    distributions = []
    for dist_elem in root.findall("distributions/distribution"):
        class_ids = [class_elem.get("id") for class_elem in dist_elem.findall("class")]
        distribution = Distribution(
            type=dist_elem.get("type"),
            required=dist_elem.get("required", "false").lower() == "true",
            class_ids=class_ids,
        )
        distributions.append(distribution)
    return distributions


def parse_students_xml(root: ET.Element | Any) -> List[Student]:
    students = []
    for student_elem in root.findall("students/student"):
        courses = [
            Course(course.get("id"), None) for course in student_elem.findall("course")
        ]
        students.append(Student(student_elem.get("id"), courses))
    return students


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

    rooms = parse_rooms_xml(root)
    courses = parse_courses_xml(root)
    distributions = parse_distributions_xml(root)
    students = parse_students_xml(root)

    return Problem(
        name=root.get("name"),
        numberOfDays=root.get("nrDays"),
        slotsPerDay=root.get("slotsPerDay"),
        numberOfWeeks=root.get("nrWeeks"),
        optimization_weights=optimization_weights,
        rooms=rooms,
        courses=courses,
        distributions=distributions,
        students=students,
    )


def initial_solution(problem: Problem) -> List[SolutionClass]:
    solution_classes = []
    for course in problem.courses:
        for config in course.configs:
            for subpart in config.subparts:
                for class_ in subpart.classes:
                    time = random.choice(class_.times)
                    if class_.room:
                        room = random.choice(class_.rooms)
                    else:
                        room = None

                    solution_class = SolutionClass(
                        id=class_.id,
                        days=time.days,
                        start=time.start,
                        weeks=time.weeks,
                        room=room.id if room else None,
                        students=None,
                    )
                    solution_classes.append(solution_class)
    return solution_classes


def save_solution(solution: Solution, file_path: str):
    # Create an XML element for the solution
    solution_elem = ET.Element("solution")
    solution_elem.set("name", solution.name)
    solution_elem.set("rutime", str(solution.rutime))
    solution_elem.set("cores", str(solution.cores))
    solution_elem.set("technique", solution.technique)
    solution_elem.set("author", solution.author)
    solution_elem.set("institution", solution.institution)
    solution_elem.set("country", solution.country)

    # Add classes to the solution element
    for sol_class in solution.classes:
        class_elem = ET.SubElement(solution_elem, "class")
        class_elem.set("id", sol_class.id)
        class_elem.set("days", sol_class.days)
        class_elem.set("start", str(sol_class.start))
        class_elem.set("weeks", sol_class.weeks)
        if sol_class.room:
            class_elem.set("room", sol_class.room)

    # Write the XML to a file
    tree = ET.ElementTree(solution_elem)
    tree.write(file_path)


def main():
    # Example usage
    problem = parse_xml("data/bet-sum18.xml")
    # You can now work with the structured data
    print(f"Number of rooms: {len(problem.rooms)}")
    print(f"Number of courses: {len(problem.courses)}")
    print(f"Number of distributions: {len(problem.distributions)}")
    solution = initial_solution(problem)

    solution = Solution(
        name=problem.name,
        rutime=0,
        cores=1,
        technique="Simulated Annealing",
        author="Łukasz Stachnik",
        institution="University of Economics in Katowice",
        country="Poland",
        classes=solution,
    )

    save_solution(solution, f"solution_{problem.name}.xml")


if __name__ == "__main__":
    main()
