import datetime\\nfrom dataclasses import dataclass, field\\\\\\\nfrom typing import List, Optional\\\\\\nfrom beaverhabits.storage.storage import CheckedRecord, Habit, HabitList\\\\\\nfrom beaverhabits.utils import generate_short_hash\\\\\\nDAY_MASK = "%Y-%m-%d"\\\\\\nMONTH_MASK = "%Y/%m"\\\\\\n@dataclass\\\\\\nclass DictStorage:\\\\\\n    data: dict = field(default_factory=dict, metadata={"exclude": True})\\\\\\n@dataclass\\\\\\nclass DictRecord(CheckedRecord, DictStorage):\\\\\\n    """\\\\\\n    Represents a record of a habit check on a specific day.\\\\\\n\\\\\\n    Attributes:\\\\\\n    day (datetime.date): The date when the habit was checked.\\\\\\n    done (bool): Whether the habit was completed on the specified day.\\\\\\n    """\\\\\\\n    @property\\\\\\n    def day(self) -> datetime.date:\\\\\\n        date = datetime.datetime.strptime(self.data["day"], DAY_MASK)\\\\\\n        return date.date()\\\\\\n\\\\\\n    @property\\\\\\n    def done(self) -> bool:\\\\\\n        return self.data["done"]\\\\\\n\\\\\\n    @done.setter\\\\\\n    def done(self, value: bool) -> None:\\\\\\n        self.data["done"] = value\\\\\\n@dataclass\\\\\\nclass DictHabit(Habit[DictRecord], DictStorage):\\\\\\n    """\\\\\\n    Represents a habit with a name and a list of records.\\\\\\n\\\\\\n    Attributes:\\\\\\n    name (str): The name of the habit.\\\\\\n    records (List[DictRecord]): A list of records for the habit.\\\\\\n    id (str): A unique identifier for the habit.\\\\\\n    star (bool): Indicates if the habit is starred.\\\\\\n    """\\\\\\\n    @property\\\\\\n    def id(self) -> str:\\\\\\n        if "id" not in self.data:\\\\\\n            self.data["id"] = generate_short_hash(self.name)\\\\\\n        return self.data["id"]\\\\\\n\\\\\\n    @id.setter\\\\\\n    def id(self, value: str) -> None:\\\\\\n        self.data["id"] = value\\\\\\n\\\\\\n    @property\\\\\\n    def name(self) -> str:\\\\\\n        return self.data["name"]\\\\\\n\\\\\\n    @name.setter\\\\\\n    def name(self, value: str) -> None:\\\\\\n        self.data["name"] = value\\\\\\n\\\\\\n    @property\\\\\\n    def star(self) -> bool:\\\\\\n        return self.data.get("star", False)\\\\\\n\\\\\\n    @star.setter\\\\\\n    def star(self, value: int) -> None:\\\\\\n        self.data["star"] = value\\\\\\n\\\\\\n    @property\\\\\\n    def records(self) -> List[DictRecord]:\\\\\\n        return [DictRecord(d) for d in self.data["records"]]\\\\\\n\\\\\\n    async def tick(self, day: datetime.date, done: bool) -> None:\\\\\\n        record = next((r for r in self.records if r.day == day), None)\\\\\\n        if record:\\\\\\n            record.done = done\\\\\\n        else:\\\\\\n            data = {"day": day.strftime(DAY_MASK), "done": done}\\\\\\n            self.data["records"].append(data)\\\\\\n@dataclass\\\\\\nclass DictHabitList(HabitList[DictHabit], DictStorage):\\\\\\n    """\\\\\\n    Represents a list of habits.\\\\\\n\\\\\\n    Attributes:\\\\\\n    habits (List[DictHabit]): A list of habits.\\\\\\n    """\\\\\\\n    @property\\\\\\n    def habits(self) -> List[DictHabit]:\\\\\\n        habits = [DictHabit(d) for d in self.data["habits"]]\\\\\\n        habits.sort(key=lambda x: x.star, reverse=True)\\\\\\n        return habits\\\\\\n\\\\\\n    async def get_habit_by(self, habit_id: str) -> Optional[DictHabit]:\\\\\\n        for habit in self.habits:\\\\\\n            if habit.id == habit_id:\\\\\\n                return habit\\\\\\n\\\\\\n    async def add(self, name: str) -> None:\\\\\\n        d = {"name": name, "records": [], "id": generate_short_hash(name)}\\\\\\n        self.data["habits"].append(d)\\\\\\n\\\\\\n    async def remove(self, item: DictHabit) -> None:\\\\\\n        self.data["habits"].remove(item.data)\\\\\\n\\\\\\n    async def merge(self, other: 'DictHabitList') -> 'DictHabitList':\\\\\\n        for habit in other.habits:\\\\\\n            if not self.get_habit_by(habit.id):\\\\\\n                self.add(habit.name)\\\\\\n        return self\\\\\\n