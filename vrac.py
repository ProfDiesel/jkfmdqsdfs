#!/usr/bin/env python3
from datetime import datetime
from uuid import uuid4
from dataclasses import dataclass, field 
from colorsys import hsv_to_rgb
from math import fmod, sqrt
from random import randrange

from nicegui import ui


@dataclass
class Message:
    user: str
    text: str
    timestamp: datetime = field(default_factory=lambda: datetime.now())

@dataclass
class Thread:
    messages: list[Message] = field(default_factory=list)

THREADS: list[Thread] = [Thread() for _ in range(3)]

def nth_color(n: int) -> str:
    r, g, b = hsv_to_rgb(fmod(n * 0.618033988749895, 1.0),
                    0.5,
                    sqrt(1.0 - fmod(n * 0.618033988749895, 0.5)))
    return f'#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}'


@ui.refreshable
def chat_messages(own_id: str) -> None:
    messages = sorted(((message, thread, n_thread) for n_thread, thread in enumerate(THREADS) for message in thread.messages), key=lambda x: x[0].timestamp)
    for message, thread, n_thread in messages:
        avatar = f'https://robohash.org/{message.user}?bgset=bg2'
        ui.chat_message(text=message.text, stamp=message.timestamp.strftime('%X'), avatar=avatar, sent=own_id == message.user).props(f'bg-color=thread-{n_thread}')
    ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')


@ui.page('/')
async def main():
    user_id = str(uuid4())
    avatar = f'https://robohash.org/{user_id}?bgset=bg2'

    def send() -> None:
        thread = THREADS[randrange(len(THREADS))]
        thread.messages.append(Message(user_id, text.value))
        text.value = ''
        chat_messages.refresh()

    ui.colors(**{f'thread-{n}': f'{nth_color(n)}' for n in range(10)})

    ui.add_css(r'a:link, a:visited {color: inherit !important; text-decoration: none; font-weight: 500}')
    with ui.footer().classes('bg-white'), ui.column().classes('w-full max-w-3xl mx-auto my-6'):
        with ui.row().classes('w-full no-wrap items-center'):
            with ui.avatar().on('click', lambda: ui.navigate.to(main)):
                ui.image(avatar)
            text = ui.input(placeholder='message').on('keydown.enter', send) \
                .props('rounded outlined input-class=mx-3').classes('flex-grow')

    await ui.context.client.connected()  # chat_messages(...) uses run_javascript which is only possible after connecting
    with ui.column().classes('w-full max-w-2xl mx-auto items-stretch'):
        chat_messages(user_id)


if __name__ in {'__main__', '__mp_main__'}:
    ui.run()







KPIs:
=====
https://huggingface.co/nuclia/REMi-v0

https://www.rungalileo.io/blog/mastering-rag-how-to-observe-your-rag-post-deployment:
Chunk Attribution 	Indicates the chunks used for generating the response, facilitating debugging and understanding of chunk characteristics.
Chunk Utilization 	Measures the utilization of retrieved information in generating responses, aiding in the optimization of retrieval strategies. Lower utilization may indicate excessively large chunk sizes.

https://docs.ragas.io/en/stable/concepts/metrics/index.html




import numpy.random
import umap
from math import fmod, sqrt
from colorsys import hsv_to_rgb
from random import randint

N = 20
C = 3

SEED = 42

colors = [
    hsv_to_rgb(fmod(n * 0.618033988749895, 1.0),
                    0.5,
                    sqrt(1.0 - fmod(n * 0.618033988749895, 0.5)))
    for n in range(C)
]

messages = [str(i) for i in range(N)]

dense = [numpy.random.rand(768)  for message in messages]
sparse = [numpy.random.rand(50) for message in messages]
mapped = umap.UMAP(n_jobs=1, random_state=SEED, n_components=3, metric='cosine').fit(dense)
clusters = [colors[int(randint(0, C - 1))] for message in messages]

--------

import plotly.express as px
fig = px.scatter_3d(mapped.embedding_, x=0, y=1, z=2, color=clusters, hover_data=[messages], size_max=1)

# tight layout
fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))
fig.show()

https://stackoverflow.com/questions/29432629/plot-correlation-matrix-using-pandas