import datetime\"nfrom dataclasses import dataclass, field, InitVar\"nfrom typing import List, Optional\"nfrom beaverhabits.utils import generate_short_hash\"nfrom beaverhabits.storage.storage import CheckedRecord, Habit, HabitList\"n\"nDAY_MASK = '%Y-%m-%d'\"nMONTH_MASK = '%Y/%m'\"n\"n@dataclass\"nclass DictStorage:\"n    data: dict = field(default_factory=dict, metadata={\"exclude\": True})\"n\"n@dataclass\"nclass DictRecord(CheckedRecord, DictStorage):\"n    day: datetime.date\"n    done: bool\"n\"n    def __str__(self):\"n        return f'{self.day} {'[x]' if self.done else '[ ]'}'\"n\"n    __repr__ = __str__\"n\"n@dataclass\"nclass DictHabit(Habit[DictRecord], DictStorage):\"n    id: str\"n    name: str\"n    star: bool = False\"n    records: List[DictRecord] = field(default_factory=list)\"n\"n    def __init__(self, data: dict):\"n        super().__init__(data)\"n\"n    def __str__(self):\"n        return self.name\"n\"n    __repr__ = __str__\"n\"n@dataclass\"nclass DictHabitList(HabitList[DictHabit], DictStorage):\"n    habits: List[DictHabit] = field(default_factory=list)\"n    order: List[str] = field(default_factory=list)\"n\"n    def __init__(self, data: dict):\"n        super().__init__(data)\"n\"n    def add(self, name: str) -> None:\"n        habit = DictHabit({'name': name, 'records': [], 'id': generate_short_hash(name)})\"n        self.habits.append(habit)\"n\"n    def remove(self, item: DictHabit) -> None:\"n        self.habits.remove(item)\"n\"n    def get_habit_by(self, habit_id: str) -> Optional[DictHabit]:\"n        for habit in self.habits:\"n            if habit.id == habit_id:\"n                return habit\"n\"n    def merge(self, other: 'DictHabitList') -> 'DictHabitList':\"n        result = set(self.habits).symmetric_difference(set(other.habits))\"n        for self_habit in self.habits:\"n            for other_habit in other.habits:\"n                if self_habit == other_habit:\"n                    new_habit = self_habit.merge(other_habit)\"n                    result.add(new_habit)\"n        return DictHabitList({'habits': list(result), 'order': self.order if hasattr(self, 'order') else []})\"n