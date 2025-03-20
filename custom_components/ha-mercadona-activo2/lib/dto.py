from pydantic import BaseModel
from typing import List, Optional

class DayType(BaseModel):
    ids: List[str]
    name: str
    primaryColour: Optional[str]
    secondaryColour: Optional[str]
    isWorkingDay: bool

class Task(BaseModel):
    processId: str
    colour: Optional[str]
    name: str
    description: str
    shortDescription: str
    abbreviation: str
    priority: str
    startHour: str
    endHour: str

class Schedule(BaseModel):
    start: str
    end: str
    total: str
    nightShift: bool
    nightShiftLabel: str

class Store(BaseModel):
    codeLabel: str
    name: str

class Detail(BaseModel):
    store: Store
    schedule: Schedule
    taskList: List[Task]

class Day(BaseModel):
    dayLabel: str
    date: str
    dayName: str
    dayType: DayType
    hasTasks: bool
    detail: List[Detail]

class Week(BaseModel):
    weekLabel: str
    weekNumber: str
    totalHours: str
    days: List[Day]

class Month(BaseModel):
    yearLabel: str
    monthLabel: str
    monthNumber: str
    weeks: List[Week]

class ScheduleResponse(BaseModel):
    startMonday: bool
    months: List[Month]
