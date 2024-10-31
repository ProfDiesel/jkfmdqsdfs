#!/usr/bin/env python3
from datetime import date, timedelta, datetime
from uuid import uuid4
from dataclasses import dataclass

from nicegui import ui

@dataclass(frozen=True)
class Message:
    text: str
    stamp: datetime
    avatar: str = ''

@dataclass
class Thread:
    messages: list[Message]
    nb_thread: int
    labels: list[int]

@dataclass(frozen=True)
class Room:
    name: str
    threads: dict[date, Thread]

    def __hash__(self) -> int:
        return hash(self.name)


ROOMS = [
    Room("room 0", {
        date(2024, 10, 5): Thread(messages=[
                Message('pipo', datetime(2024, 10, 5, 9)),
                Message('lolo', datetime(2024, 10, 5, 10)),
                Message('tre', datetime(2024, 10, 5, 11))
            ], nb_thread=3, labels=[0, 0, 0]),
        date(2024, 10, 10): Thread(messages=[
                Message('gabu', datetime(2024, 10, 10, 11)),
                Message('zomeu', datetime(2024, 10, 10, 11)),
            ], nb_thread=3, labels=[0, 0]),
        date(2024, 10, 13): Thread(messages=[
                Message('tre', datetime(2024, 10, 13, 11))
            ], nb_thread=3, labels=[0]),
    }),
    Room("room 1", {
        date(2024, 9, 5): Thread(messages=[
                Message('youhoy', datetime(2024, 9, 5, 11))
            ], nb_thread=3, labels=[0]),
    }),
]


@ui.refreshable
def chat_messages(thread: Thread) -> None:
    for n, message in enumerate(thread.messages):
        def move():
            thread.labels[n] = (thread.labels[n] + 1) % thread.nb_thread
            chat_messages.refresh()
        with ui.chat_message(text=message.text, stamp=message.stamp.isoformat(), avatar=message.avatar):
            ui.button(icon='alt_route', on_click=move)


@ui.refreshable
def fancy_date_selector(dates: list[date]):
    date_index, select_date_index = ui.state(len(dates) - 1)
    dates_as_str = [date.isoformat() for date in dates]
    with ui.input(label='date', value=dates_as_str[date_index], autocomplete=dates_as_str, validation={'invalid date': lambda value: value in dates_as_str}) as date_input:
        with ui.menu().props('no-parent-event') as menu:
            with ui.date(on_change=lambda event: select_date_index(dates_as_str.index(event.value))) \
                .props(f''':options="date => ['{"', '".join(date.isoformat() for date in dates)}'].indexOf(new Date(date).toISOString().substring(0, 10)) != -1"''') \
                .bind_value(date_input):
                with ui.row().classes('justify-end'):
                    ui.button('Close', on_click=menu.close).props('flat')
        with date_input.add_slot('append'):
            if date_index == 0:
                ui.icon('block')
            else:
                ui.icon('chevron_left').on('click', lambda: select_date_index(date_index - 1)).classes('cursor-pointer')
            ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
            if date_index == len(dates) - 1:
                ui.icon('block')
            else:
                ui.icon('chevron_right').on('click', lambda: select_date_index(date_index + 1)).classes('cursor-pointer')
    return date_input

@ui.refreshable
async def label_editor(rooms: list[Room]) -> None:
    room, select_room = ui.state(rooms[0])
    all_dates: list[date] = sorted(room.threads.keys())
    current_date: date = all_dates[0]

    ui.select({room: room.name for room in rooms}, with_input=True, on_change=lambda event: select_room(event.value))
    date_select = fancy_date_selector(all_dates)
    date_select.bind_value_to(locals(), 'current_date', forward=date.fromisoformat)

    with ui.column():
        chat_messages(room.threads[current_date])

@ui.page('/')
async def main() -> None:
    await label_editor(ROOMS)


if __name__ in {'__main__', '__mp_main__'}:
    ui.run(show=False)

