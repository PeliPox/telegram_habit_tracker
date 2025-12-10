from sqlalchemy.orm import Session
from db.base import SessionLocal
from db.models import User
from db.models import Habit
from db.models import HabitCompletion
from datetime import date
from sqlalchemy import func


def get_user(db: Session, tg_id: int):
    return db.query(User).filter(User.tg_id == tg_id).first()


def create_user(db: Session, tg_id: int, name: str):
    user = User(tg_id=tg_id, name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_habit(user_id: int, title: str, description: str = None, periodicity: int = 1):
    with SessionLocal() as session:
        user = session.query(User).filter_by(tg_id=user_id).first()
        habit = Habit(
            user_id=user.id,
            title=title,
            description=description,
            periodicity=periodicity
        )
        session.add(habit)
        session.commit()
        session.refresh(habit)
        return habit


def get_habits_by_user(db: Session, user_id: int):
    return db.query(Habit).filter(Habit.user_id == user_id).all()


def get_habit_by_id(db: Session, habit_id: int):
    return db.query(Habit).filter(Habit.id == habit_id).all()


def update_habit(db: Session, habit_id: int, **kwargs):
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        return None

    for key, value in kwargs.items():
        if hasattr(habit, key) and value is not None:
            setattr(habit, key, value)

    db.commit()
    db.refresh(habit)
    return habit


def delete_habit(db: Session, habit_id: int):
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if habit:
        db.delete(habit)
        db.commit()


def complete_habit(db: Session, habit_id: int):
    completion = HabitCompletion(habit_id=habit_id)
    db.add(completion)
    db.commit()
    db.refresh(completion)
    return completion


def not_complete_habit(db: Session, habit_id: int):
    completion = db.query(HabitCompletion).filter(HabitCompletion.id == habit_id).first()
    if completion:
        db.delete(completion)
        db.commit()


def is_habit_completed_today(db: Session, habit_id: int):
    record = (
        db.query(HabitCompletion)
        .filter(
            HabitCompletion.habit_id == habit_id,
            func.date(HabitCompletion.completed_at) == date.today()
        )
        .first()
    )
    return record is not None


def update_habit_title(db: Session, habit_id: int, title: str):
    habit = db.query(Habit).get(habit_id)
    habit.title = title
    db.commit()


def update_habit_description(db: Session, habit_id: int, description: str):
    habit = db.query(Habit).get(habit_id)
    habit.description = description
    db.commit()


def update_habit_periodicity(db: Session, habit_id: int, days: int):
    habit = db.query(Habit).get(habit_id)
    habit.periodicity = days
    db.commit()