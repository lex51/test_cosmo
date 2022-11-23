import asyncio
from chain_api import monitoring_chains_for_users


async def call_test():
    # loop = asyncio.get_running_loop().run_in_executor(None, monitoring_chains_for_user, 417592088 )
    # loop.create_task(test())
    loop = asyncio.get_running_loop()
    loop.create_task(monitoring_chains_for_users())


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

loop.create_task(call_test())
loop.run_forever()
