#!/usr/bin/env python3
import asyncio
from datetime import date, datetime
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

    def thread(self, n: int) -> Thread:
        return sorted(self.threads.items())[n][1]


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

THREAD_COLORS = ['#ff9999', '#ffcc99', '#ffff99', '#99ff99', '#99ffcc', '#99ffcc', '#99ccff', '#9999ff', '#cc99ff', '#ff99ff']

@ui.refreshable
def chat_message(thread: Thread, n: int) -> None:
    message: Message = thread.messages[n]
    def move_to_next_thread(n=n):
        thread.labels[n] = (thread.labels[n] + 1) % thread.nb_thread
        chat_message.refresh()
    color = THREAD_COLORS[thread.labels[n]]
    with ui.item(on_click=move_to_next_thread):
        with ui.item_section() as s:
            s.style(f'background-color: {color}')
            ui.item_label(message.stamp.isoformat())
        with ui.item_section():
            ui.item_label(message.text)

    
@ui.refreshable
def label_editor(rooms: list[Room]) -> None:
    room, set_room = ui.state(rooms[0])
    date_index, set_date_index = ui.state(len(room.threads) - 1)

    if date_index >= len(room.threads):
        set_date_index(len(room.threads) - 1)
        return

    with ui.row():
        ui.select({room: room.name for room in rooms}, value=room, label="room", with_input=True, on_change=lambda event: set_room(event.value))

        dates_as_str = [date.isoformat() for date in sorted(room.threads.keys())]
        with ui.input(label='date', value=dates_as_str[date_index], autocomplete=dates_as_str, validation={'invalid date': lambda value: value in dates_as_str}) as date_input:
            with ui.menu().props('no-parent-event') as menu:
                with ui.date(on_change=lambda event: set_date_index(dates_as_str.index(event.value))) \
                    .props(f''':options="date => ['{"', '".join(dates_as_str)}'].indexOf(new Date(date).toISOString().substring(0, 10)) != -1"'''):
                    with ui.row().classes('justify-end'):
                        ui.button('Close', on_click=menu.close).props('flat')
            with date_input.add_slot('append'):
                if date_index == 0:
                    ui.icon('block')
                else:
                    ui.icon('chevron_left').on('click', lambda: set_date_index(date_index - 1)).classes('cursor-pointer')
                ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
                if date_index == len(dates_as_str) - 1:
                    ui.icon('block')
                else:
                    ui.icon('chevron_right').on('click', lambda: set_date_index(date_index + 1)).classes('cursor-pointer')

    with ui.column():
        with ui.list().props('bordered separator'):
            for n in range(len(room.thread(date_index).messages)):
                chat_message(room.thread(date_index), n)

async def save():
    await asyncio.sleep(3)
    print("saved")

@ui.page('/')
async def main() -> None:
    label_editor(ROOMS)
    ui.button(icon="save", on_click=save)

if __name__ in {'__main__', '__mp_main__'}:
    ui.colors(primary='#007348',
              secondary='#8bc8aa',
              accent='#99cc00',
              dark='#000000',
              dark_page='#121212',
              positive='#00a300',
              negative='#a30000',
              info='#00005c',
              warning='#a35200')
    ui.run(show=False)
