from sqlalchemy.orm import Session
from db.base import SessionLocal
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


def complete_habit():
    pass



