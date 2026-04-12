from db.uow import unit_of_work

async def get_uow():
    async with unit_of_work() as uow:
        yield uow