from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ChatType
from bot_app import markups, misc, db, config
from bot_app.misc import bot, dp, _, _l
import requests
import aiohttp


@dp.message_handler(commands='start', state='*', chat_type=ChatType.PRIVATE)
async def process_start(message: Message, state: FSMContext, locale):
    await state.finish()
    user_data = await db.users.get_user(message.from_user.id)
    if user_data is None:
        await db.users.create_user(message.from_user)
        await bot.send_message(message.from_user.id,
                               _('Welcome to the transaction notification bot.\n'
                                 'Please select a language.\n'
                                 '<b>It can be changed later in the settings.</b>'),
                               reply_markup=markups.base.language_menu())
        return
    await bot.send_message(message.from_user.id,
                           _('You are in the main menu.\n'),
                           reply_markup=markups.user.main.main_menu(locale))


@dp.message_handler(text=_l('👨 Change Language'))
async def get_language_menu(message: Message):
    await bot.send_message(message.from_user.id,
                           _('Welcome to the transaction notification bot.\n'
                             'Please select a language.\n'
                             '<b>It can be changed later in the settings.</b>'),
                           reply_markup=markups.base.language_menu())


@dp.callback_query_handler(text_startswith='set-lang_', state='*', chat_type=ChatType.PRIVATE)
async def change_user_language(call: CallbackQuery, state: FSMContext):
    chosen_locale = call.data.split('_')[-1]
    await state.finish()
    await misc.set_lang(call.from_user.id, chosen_locale)

    await call.answer(_('The language has been successfully changed to: {language}',
                        locale=chosen_locale).format(language=call.data.split('_')[-1]),
                      show_alert=True)
    await call.message.delete()

    await bot.send_message(call.from_user.id,
                           text=_('You are in the main menu', locale=chosen_locale),
                           reply_markup=markups.user.main.main_menu(chosen_locale))


@dp.message_handler(commands=['pay'])
async def pay_creation(message: Message, state: FSMContext):


    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer $HIG#IRHRF#gn3ljpgHEIROF42IGHPOWJF',
        'Content-Type': 'application/json',
    }

    json_data = {
        'amount': '100',
        'currency': 'UAH',
        'callback_url': f"{config.WEBHOOK_HOST}/{config.ROUTE_URL}/super_payment_system_callback",
    }

    print(json_data)

    async with aiohttp.ClientSession() as session:
        async with session.post('https://prud-super-payment-api.telegram-crm.work/payment', headers=headers,
                             json=json_data) as resp:
            print(resp.status)
            payment_data = await resp.json()

    order_id = await db.payments.create_new(payment_data['payment_id'], message.from_user.id)

    await bot.send_message(message.from_user.id, f'ссылка на оплату {order_id}\n\n{payment_data["payment_url"]}')
