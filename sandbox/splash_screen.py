from nicegui import ui

class Overlay(ui.dialog):
    def __init__(self, timeout: float, click_close: bool = True) -> None:
        super().__init__()
        self.open()
        if timeout is not None:
            ui.timer(timeout, callback=self.close, once=True)
        if click_close:
            self.on('click', handler=self.close)

@ui.page('/')
def index():
    ui.label('something obscured in the background')
    with Overlay(timeout=4):
        with ui.column().classes('items-center'):
            ui.label('').classes('text-white text-xl')
            ui.spinner(size='lg')

ui.run(show=False, favicon='🐀')


FORTUNES = [
    '"You are a competent cat belling adivsor ..."'
    'mice in the walls'
    'mice in the machine'
    'rat\'s nest'
]