from pydantic import BaseModel
from typing import List, Optional


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


class Travel(BaseModel):
    room: str
    value: int


class Room(BaseModel):
    id: str
    capacity: int
    travels: List[Travel]
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
    room: Optional[Room]
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
