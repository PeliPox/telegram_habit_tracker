from sqlalchemy.orm import Session
from db.base import SessionLocal
from db.models import User
from db.models import Habit
from db.models import HabitCompletion
from datetime import date, timedelta, time, datetime
from sqlalchemy import func


def get_user(db: Session, tg_id: int):
    return db.query(User).filter(User.tg_id == tg_id).first()


def create_user(db: Session, tg_id: int, name: str):
    user = User(tg_id=tg_id, name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_or_create_user(db: Session, tg_id: int):
    user = db.query(User).filter(User.tg_id == tg_id).first()
    if not user:
        user = User(tg_id=tg_id)
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


def get_habits_stats_for_user(db: Session, user_id: int):
    habits = db.query(Habit).filter(Habit.user_id == user_id).all()

    if not habits:
        return []

    stats = []

    start = datetime.combine(date.today(), time.min)
    end = datetime.combine(date.today(), time.max)

    for habit in habits:
        # Всего выполнений
        total = (
            db.query(func.count(HabitCompletion.id))
            .filter(HabitCompletion.habit_id == habit.id)
            .scalar()
        )
        # Выполнено сегодня
        today_done = (
            db.query(func.count(HabitCompletion.id))
            .filter(
                HabitCompletion.habit_id == habit.id,
                HabitCompletion.completed_at >= start,
                HabitCompletion.completed_at <= end
            )
            .scalar()
        )
        # Последнее выполнение
        last_completion = (
            db.query(func.max(HabitCompletion.completed_at))
            .filter(HabitCompletion.habit_id == habit.id)
            .scalar()
        )
        # Подсчёт запоя (streak)
        completions = (
            db.query(HabitCompletion.completed_at)
            .filter(HabitCompletion.habit_id == habit.id)
            .order_by(HabitCompletion.completed_at.desc())
            .all()
        )
        completion_dates = {c.completed_at.date() for c in completions}

        streak = 0
        current_date = date.today()
        while current_date in completion_dates:
            streak += 1
            current_date -= timedelta(days=1)

        # Максимальный Стрик
        max_streak = 0
        temp = 0
        prev = None

        for c in sorted(completion_dates):
            if prev and (c - prev == timedelta(days=1)):
                temp += 1
            else:
                temp = 1
            max_streak = max(max_streak, temp)
            prev = c

        stats.append({
            "habit": habit,
            "total": total,
            "today": today_done,
            "last": last_completion,
            "streak": streak,
            "max_streak": max_streak
        })

    return stats