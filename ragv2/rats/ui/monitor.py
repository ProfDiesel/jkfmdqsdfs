from nicegui import ui
import asyncio
import pandas as pd
import numpy.random
from umap import UMAP
import plotly.express as px
from functools import lru_cache
from typing import Any, cast
from collections.abc import Collection
from ..core.model import Embedding, Chunk, ChunkKpis


@lru_cache
def load_embeddings() -> Collection[Chunk]:
    return [Chunk(text=str(n), embedding=cast(Embedding, numpy.random.rand(768))) for n in range(100)]

@ui.page('/embeddings/plot')
async def embeddings_plot(chunks: Collection[Chunk], umap_random_state: Any = 42):
    spinner = ui.spinner('dots', size='xl', color='red').classes('absolute-center')
    async def compute():
        points = [chunk.embedding for chunk in chunks]
        mapped = UMAP(n_jobs=1, random_state=umap_random_state, n_components=3, metric='cosine').fit(points)
        spinner.set_visibility(False)
        fig = px.scatter_3d(mapped.embedding_, x=0, y=1, z=2, size_max=1)
        fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))
        ui.plotly(fig).classes('w-full h-40')
    asyncio.create_task(compute())

@ui.page('/embeddings/kpis')
def embeddings_kpis():
    # distribution histogram of length of the chunks (in tokens)
    pass
    

@ui.page('/rag/kpis')
def rag_kpis():
    #kpis = get_chunks_kips()
    kpis = pd.DataFrame(data={'col1': [1, 2], 'col2': [3, 4]})
    grid = ui.aggrid.from_pandas(df).classes('max-h-40')
    grid.on('cellClicked', lambda event: ui.notify(f'Cell value: {event.args["value"]}'))

    def update():
        grid.options['rowData'][0]['age'] += 1
        grid.update()
    ui.button('Update', on_click=update)
    #ui.button('Select all', on_click=lambda: grid.run_grid_method('selectAll'))
    #ui.button('Show parent', on_click=lambda: grid.run_column_method('setColumnVisible', 'parent', True))

@ui.page('/embeddings/detail/{docid}')
def embeddings_details(docid: str):
    '''
    Chunk visualization à-la Chunkviz
    '''
    ui.markdown('''
''')

ui.link('rag kpis', rag_kpis)

ui.run()
