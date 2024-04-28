async def _main():
    endpoint = Endpoint()
    c = issue_detection_chain(partial(endpoint.llm, model_name='pipo'))

    #await ("pipo" > c)

    

    c = issue_detection_chain(partial(mock_llm(('YES', 'NO')), model_name='pipo'))
    await ("pipo" > c)

def main():
    asyncio.run(_main())

