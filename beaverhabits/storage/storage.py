class Habit:
    def __init__(self, id, name, star, records):
        self.id = id
        self.name = name
        self.star = star
        self.records = records

    @property
    def star(self):
        return self._star

    @star.setter
    def star(self, value):
        if not isinstance(value, int):
            raise ValueError("Star value must be an integer.")
        self._star = value

    def __str__(self):
        return f"{self.name} (ID: {self.id}, Star: {self.star})"

    __repr__ = __str__


class HabitList:
    def __init__(self):
        self.habits = []
        self.order = []

    def add(self, habit):
        self.habits.append(habit)
        if habit.id not in self.order:
            self.order.append(habit.id)

    def remove(self, habit_id):
        self.habits = [habit for habit in self.habits if habit.id != habit_id]
        self.order.remove(habit_id)

    def get_habit_by_id(self, habit_id):
        for habit in self.habits:
            if habit.id == habit_id:
                return habit
        return None

    def __str__(self):
        habit_strs = [str(habit) for habit in self.habits]
        return "\n".join(habit_strs)

    __repr__ = __str__


The provided code snippet has been revised to address the syntax error mentioned in the feedback. The comment that was causing the syntax error has been removed from within the class definitions. This should resolve the `SyntaxError` and allow the tests to run successfully.