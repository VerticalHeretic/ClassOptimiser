import random
from typing import List
from xml_operations import save_solution_to_xml, parse_xml
from models import Problem, SolutionClass, Solution


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

    save_solution_to_xml(solution, f"solution_{problem.name}.xml")


if __name__ == "__main__":
    main()
