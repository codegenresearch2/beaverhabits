from dataclasses import dataclass, field\\\nimport datetime\\\\\nfrom typing import List, Optional\\\\\nfrom enum import Enum\\\\\n\\\\\nfrom beaverhabits.storage.storage import CheckedRecord, Habit, HabitList\\\\\nfrom beaverhabits.utils import generate_short_hash\\\\\n\\\\\nDAY_MASK = "%Y-%m-%d"\\\\\nMONTH_MASK = "%Y/%m"\\\\\n\\\\\nclass HabitStatus(Enum):\\\\\n    ACTIVE = "normal"\\\\\n    ARCHIVED = "archive"\\\\\n    SOFT_DELETED = "soft_delete"\\\\\n\\\\\n@dataclass(init=False)\\\\\nclass DictStorage:\\\\\n    data: dict = field(default_factory=dict, metadata={"exclude": True})\\\\\n\\\\\n@dataclass\\\\\nclass DictRecord(CheckedRecord, DictStorage):\\\\\n    def __init__(self, data: dict):\\\\\n        self.data = data\\\\\n\\\\\n    @property\\\\\n    def day(self) -> datetime.date:\\\\\n        date = datetime.datetime.strptime(self.data["day"], DAY_MASK)\\\\\n        return date.date()\\\\\n\\\\\n    @property\\\\\n    def done(self) -> bool:\\\\\n        return self.data["done"]\\\\\n\\\\\n    @done.setter\\\\\n    def done(self, value: bool) -> None:\\\\\n        self.data["done"] = value\\\\\n\\\\\n@dataclass\\\\\nclass DictHabit(Habit[DictRecord], DictStorage):\\\\\n    def __init__(self, data: dict):\\\\\n        self.data = data\\\\\n\\\\\n    @property\\\\\n    def id(self) -> str:\\\\\n        if "id" not in self.data:\\\\\n            self.data["id"] = generate_short_hash(self.name)\\\\\n        return self.data["id"]\\\\\n\\\\\n    @id.setter\\\\\n    def id(self, value: str) -> None:\\\\\n        self.data["id"] = value\\\\\n\\\\\n    @property\\\\\n    def name(self) -> str:\\\\\n        return self.data["name"]\\\\\n\\\\\n    @name.setter\\\\\n    def name(self, value: str) -> None:\\\\\n        self.data["name"] = value\\\\\n\\\\\n    @property\\\\\n    def star(self) -> bool:\\\\\n        return self.data.get("star", False)\\\\\n\\\\\n    @star.setter\\\\\n    def star(self, value: int) -> None:\\\\\n        self.data["star"] = value\\\\\n\\\\\n    @property\\\\\n    def records(self) -> list[DictRecord]:\\\\\n        return [DictRecord(d) for d in self.data["records"]]\\\\\n\\\\\n    @property\\\\\n    def status(self) -> HabitStatus:\\\\\n        return HabitStatus(self.data.get("status", "ACTIVE"))\\\\\n\\\\\n    @status.setter\\\\\n    def status(self, value: HabitStatus) -> None:\\\\\n        self.data["status"] = value.value\\\\\n\\\\\n    async def tick(self, day: datetime.date, done: bool) -> None:\\\\\n        record = next((r for r in self.records if r.day == day), None)\\\\\n        if record:\\\\\n            record.done = done\\\\\n        else:\\\\\n            self.data["records"].append({"day": day.strftime(DAY_MASK), "done": done})\\\\\n\\\\\n    async def merge(self, other: "DictHabit") -> "DictHabit":\\\\\n        self_ticks = {r.day for r in self.records if r.done}\\\\\n        other_ticks = {r.day for r in other.records if r.done}\\\\\n        result = sorted(list(self_ticks | other_ticks))\\\\\n\\\\\n        d = {\\\"\"name": self.name,\\\""