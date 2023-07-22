from bot_app.db.base import create_dict_con, create_con


async def create_new(uuid, from_user):
    con, cur = await create_con()
    await cur.execute('insert into payments (order_id, from_user) VALUES (%s, %s)',
                      (uuid, from_user))
    await con.commit()
    new_order_id = cur.lastrowid
    await con.ensure_closed()
    return new_order_id


async def get(uuid):
    con, cur = await create_dict_con()
    await cur.execute('select record_id, order_id, from_user from payments where order_id = %s ',(uuid, ))
    order_data = await cur.fetchone()
    await con.ensure_closed()
    return order_data
