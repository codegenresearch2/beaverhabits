from dataclasses import dataclass, field\\nimport datetime\\nfrom typing import List, Optional\\n\\nfrom beaverhabits.storage.storage import CheckedRecord, Habit, HabitList\\nfrom beaverhabits.utils import generate_short_hash\\n\\nDAY_MASK = "%Y-%m-%d"\\nMONTH_MASK = "%Y/%m"\\n\\n@dataclass(init=False)\\nclass DictStorage:\\n    data: dict = field(default_factory=dict, metadata={"exclude": True})\\n\\n@dataclass\\nclass DictRecord(CheckedRecord, DictStorage):\\n    def __init__(self, data: dict):\\n        self.data = data\\n\\n    @property\\n    def day(self) -> datetime.date:\\n        date = datetime.datetime.strptime(self.data["day"], DAY_MASK)\\n        return date.date()\\n\\n    @property\\n    def done(self) -> bool:\\n        return self.data["done"]\\n\\n    @done.setter\\n    def done(self, value: bool) -> None:\\n        self.data["done"] = value\\n\\n@dataclass\\nclass DictHabit(Habit[DictRecord], DictStorage):\\n    def __init__(self, data: dict):\\n        self.data = data\\n\\n    @property\\n    def id(self) -> str:\\n        if "id" not in self.data:\\n            self.data["id"] = generate_short_hash(self.name)\\n        return self.data["id"]\\n\\n    @id.setter\\n    def id(self, value: str) -> None:\\n        self.data["id"] = value\\n\\n    @property\\n    def name(self) -> str:\\n        return self.data["name"]\\n\\n    @name.setter\\n    def name(self, value: str) -> None:\\n        self.data["name"] = value\\n\\n    @property\\n    def star(self) -> bool:\\n        return self.data.get("star", False)\\n\\n    @star.setter\\n    def star(self, value: int) -> None:\\n        self.data["star"] = value\\n\\n    @property\\n    def records(self) -> list[DictRecord]:\\n        return [DictRecord(d) for d in self.data["records"]]\\n\\n    async def tick(self, day: datetime.date, done: bool) -> None:\\n        record = next((r for r in self.records if r.day == day), None)\\n        if record:\\n            record.done = done\\n        else:\\n            self.data["records"].append({"day": day.strftime(DAY_MASK), "done": done\\n            }) \\n\\n    async def merge(self, other: "DictHabit") -> "DictHabit":\\n        self_ticks = {r.day for r in self.records if r.done}\\n        other_ticks = {r.day for r in other.records if r.done}\\n        result = sorted(list(self_ticks | other_ticks))\\n\\n        d = {\"name\": self.name, \"records\": [\"day\": day.strftime(DAY_MASK), \"done\": True] for day in result\\n        } \\n        return DictHabit(d)\\n\\n    def __eq__(self, other: object) -> bool:\\n        return isinstance(other, DictHabit) and self.id == other.id\\n\\n    def __hash__(self) -> int:\\n        return hash(self.id)\\n\\n    def __str__(self) -> str:\\n        return f"{self.name}<{self.id}>"\\n    __repr__ = __str__\\n\\n@dataclass\\nclass DictHabitList(HabitList[DictHabit], DictStorage):\\n    def __init__(self, data: dict):\\n        self.data = data\\n\\n    @property\\n    def habits(self) -> list[DictHabit]:\\n        habits = [DictHabit(d) for d in self.data["habits"]]\\n\\n        if self.order:\\n            habits.sort(key=lambda x: (self.order.index(str(x.id)) if str(x.id) in self.order else float("inf")))\\n\\n        return habits\\n\\n    @property\\n    def order(self) -> List[str]:\\n        return self.data.get("order", [])\\n\\n    @order.setter\\n    def order(self, value: List[str]) -> None:\\n        self.data["order"] = value\\n\\n    async def get_habit_by(self, habit_id: str) -> Optional[DictHabit]:\\n        for habit in self.habits:\\n            if habit.id == habit_id:\\n                return habit\\n\\n    async def add(self, name: str) -> None:\\n        d = {\"name\": name, \"records\": [], \"id\": generate_short_hash(name)\"} \\n        self.data["habits"].append(d)\\n\\n    async def remove(self, item: DictHabit) -> None:\\n        self.data["habits"].remove(item.data)\\n\\n    async def merge(self, other: "DictHabitList") -> "DictHabitList":\\n        result = set(self.habits).symmetric_difference(set(other.habits))\\n\\n        for self_habit in self.habits:\\n            for other_habit in other.habits:\\n                if self_habit == other_habit:\\n                    new_habit = await self_habit.merge(other_habit)\\n                    result.add(new_habit)\\n\\n        return DictHabitList({\"habits\": [h.data for h in result]})