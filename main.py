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
    rooms: List[Room] = []
    times: List[Time] = []

class Subpart(BaseModel):
    id: str
    classes: List[Class]

class Config(BaseModel):
    id: str
    subparts: List[Subpart]

class Course(BaseModel):
    id: str
    configs: List[Config]

class Distribution(BaseModel):
    type: str
    required: bool
    class_ids: List[str]

class Problem(BaseModel):
    courses: List[Course]
    distributions: List[Distribution]

def parse_xml(file_path: str) -> Problem:
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    courses = []
    for course_elem in root.findall('courses/course'):
        configs = []
        for config_elem in course_elem.findall('config'):
            subparts = []
            for subpart_elem in config_elem.findall('subpart'):
                classes = []
                for class_elem in subpart_elem.findall('class'):
                    # Parse rooms
                    rooms = [
                        Room(
                            id=room.get('id'),
                            penalty=int(room.get('penalty', 0))
                        )
                        for room in class_elem.findall('room')
                    ]
                    
                    # Parse times
                    times = [
                        Time(
                            days=time.get('days'),
                            start=int(time.get('start')),
                            length=int(time.get('length')),
                            weeks=time.get('weeks'),
                            penalty=int(time.get('penalty', 0))
                        )
                        for time in class_elem.findall('time')
                    ]
                    
                    # Create class
                    class_obj = Class(
                        id=class_elem.get('id'),
                        limit=int(class_elem.get('limit')) if class_elem.get('limit') else None,
                        parent=class_elem.get('parent'),
                        room=class_elem.get('room', 'true').lower() != 'false',
                        rooms=rooms,
                        times=times
                    )
                    classes.append(class_obj)
                
                subpart = Subpart(
                    id=subpart_elem.get('id'),
                    classes=classes
                )
                subparts.append(subpart)
            
            config = Config(
                id=config_elem.get('id'),
                subparts=subparts
            )
            configs.append(config)
        
        course = Course(
            id=course_elem.get('id'),
            configs=configs
        )
        courses.append(course)
    
    # Parse distributions
    distributions = []
    for dist_elem in root.findall('distributions/distribution'):
        class_ids = [class_elem.get('id') for class_elem in dist_elem.findall('class')]
        distribution = Distribution(
            type=dist_elem.get('type'),
            required=dist_elem.get('required', 'false').lower() == 'true',
            class_ids=class_ids
        )
        distributions.append(distribution)
    
    return Problem(courses=courses, distributions=distributions)

def main():
    # Example usage
    problem = parse_xml('data/pu-llr-spr07.xml')
    # You can now work with the structured data
    print(f"Number of courses: {len(problem.courses)}")
    print(f"Number of distributions: {len(problem.distributions)}")

if __name__ == "__main__":
    main()
