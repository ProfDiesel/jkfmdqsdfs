#!/usr/bin/env python3
from dataclasses import dataclass
from nicegui import app, ui
import draganddrop as dnd

app.native.window_args['resizable'] = True
app.native.start_args['debug'] = False 
app.native.settings['ALLOW_DOWNLOADS'] = True

@dataclass
class ToDo:
    title: str


def handle_drop(todo: ToDo, location: str):
    ui.notify(f'"{todo.title}" is now in {location}')


ui.dark_mode().enable()
with ui.row():
    with dnd.column('Next', on_drop=handle_drop):
        dnd.card(ToDo('Simplify Layouting'))
        dnd.card(ToDo('Provide Deployment'))
    with dnd.column('Doing', on_drop=handle_drop):
        dnd.card(ToDo('Improve Documentation'))
    with dnd.column('Done', on_drop=handle_drop):
        dnd.card(ToDo('Invent NiceGUI'))
        dnd.card(ToDo('Test in own Projects'))
        dnd.card(ToDo('Publish as Open Source'))
        dnd.card(ToDo('Release Native-Mode'))

#ui.run(native=True)
ui.run(show=False, favicon='🐀')
