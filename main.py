import random
from typing import List
from xml_operations import save_solution_to_xml, parse_xml
from models import Problem, SolutionClass, Solution, Student


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

                    students = []

                    print(
                        f"Will try to find students for class {class_.id} in course {course.id} in {len(problem.students)} students"
                    )
                    for student in problem.students:
                        for student_course in student.courses:
                            if student_course.id == course.id:
                                students.append(Student(id=student.id, courses=None))
                    print(f"Found {len(students)} students")

                    room = next(
                        (room for room in problem.rooms if room.id == room.id), None
                    )

                    solution_class = SolutionClass(
                        id=class_.id,
                        days=time.days,
                        start=time.start,
                        weeks=time.weeks,
                        room=room,
                        students=students if len(students) > 0 else None,
                    )
                    solution_classes.append(solution_class)
    return solution_classes


def score_solution(solution: Solution) -> float:
    hard_constraints_failed_or_not = {
        "room_capacity": 0,
        "class_overlap": 0,
        "class_room_overlap": 0,
    }

    ## Hard Constraints

    classes_over_capacity_count = len(
        [
            class_
            for class_ in solution.classes
            if class_.room is not None
            and class_.students is not None
            and class_.room.capacity > len(class_.students)
        ]
    )

    hard_constraints_failed_or_not["room_capacity"] = classes_over_capacity_count

    # TODO: Find and add weights for hard constraints
    # TODO: Classes cannot overlap in time
    # TODO: Classes cannot be in the same room at the same time

    ## Soft Constraints
    # TODO: Find and add weights for soft constraints
    # TODO: Prefer assigning rooms closer to their capacity
    # TODO: Minimize the gaps between classes
    # TODO: Minimize the travel time between classes

    hard_constraints_failed_count = sum(hard_constraints_failed_or_not.values())

    return hard_constraints_failed_count


def main():
    # Example usage
    problem = parse_xml("data/pu-cs-fal07.xml")
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
        author="Lukasz Stachnik",
        institution="University of Economics in Katowice",
        country="Poland",
        classes=solution,
    )

    score = score_solution(solution)

    print(f"Score: {score}")

    save_solution_to_xml(solution, f"solution_{problem.name}.xml")


if __name__ == "__main__":
    main()
