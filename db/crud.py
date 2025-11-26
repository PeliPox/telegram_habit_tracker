from sqlalchemy.orm import Session
from db.models import User
from db.models import Habit


def get_user(db: Session, tg_id: int):
    return db.query(User).filter(User.tg_id == tg_id).first()


def create_user(db: Session, tg_id: int, name: str):
    user = User(tg_id=tg_id, name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_habit(db: Session, user_id: int, title: str, description: str = None, periodicity: str = "daily"):
    habit = Habit(
        user_id=user_id,
        title=title,
        description=description,
        periodicity=periodicity
    )
    db.add(habit)
    db.commit()
    db.refresh(habit)

    return habit


def get_habits_by_user(db: Session, user_id: int):
    return db.query(Habit).filter(Habit.user_id == user_id).all()


def update_habit():
    pass


def delete_habit(db: Session, habit_id: int):
    habit = db.query(Habit).filter(Habit.id == habit_id).all()
    if habit:
        db.delete(habit)
        db.commit()
        return True
    return False

def complete_habit():
    pass



