import asyncio
from aiogram import types
from aiogram.types import KeyboardButton, InlineKeyboardButton, contact, reply_keyboard
from aiogram.types.message import ContentType, ParseMode, ReplyKeyboardRemove, ReplyKeyboardMarkup, InlineKeyboardMarkup
from django.db.models import expressions
from utils.db_api.db import cmd
from dispatcher import dp, bot
import json
import pprint
import os
import re
import urllib
import datetime
import humanize
import logging
import random
from aiogram.utils import executor

from aiogram.utils.markdown import text
from aiogram.dispatcher import Dispatcher
from data.config import ADMIN_GROUP, NOTIFICATION_TIME
import aioschedule

humanize.i18n.activate("ru_RU")
logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
# ================================================ #

languages = {
    'uz': {
        'BTN_OPENED_TICKETS': 'Ochiq',
        'BTN_CLOSED_TICKETS': 'Yopiq',

        'BTN_NEW_TICKET': 'Yangi ariza',
        'BTN_TICKETS_STATUS': 'Status',

        'BTN_FINISH': 'Tugatish',
        'BTN_CANCEL': 'Bekor qilish',
        'BTN_CLOSE': 'Yopish',
        'BTN_RETURN': 'Qaytish',
        'BTN_NEXT': 'Keyingi',

        'BTN_ACTIVATE_CHECK': 'Aktivatsiya tekshirish',

        'MSG_EVERYDAY_NOTIFICATION_SUMMARY': '<b>Arizalar soni (oylik):</b> {0}\n<b>Arizalar koʻrildi:</b> {1}\n<b>Kutish jarayonida:</b> {2}\n<b>Yopilgan:</b> {3}',
        'MSG_EVERYDAY_NOTIFICATION_TICKET_INWORK': '<b>Arizalar roʻyxati (ish jarayonda):</b>\n\n',
        'MSG_EVERYDAY_NOTIFICATION_TICKET_NEW': '<b>Yangi arizalar roʻyxati:</b>\n\n',
        'REG_USER': 'Siz roʻyxatdan oʻtish uchun ariza topshirdingiz. Administrator tomonidan faollashtirilgandan soʻng, tugmani bosing.',
        'REG_ACTIVATE_ADMIN': '{1} ({0}) foydalanuvchi avtorizatsiyani kutmoqda. Foydalanuvchi qaysi filialga ulanishi kerak?',
        'REG_USER_ACTIVATE_NOTIFICATION': 'Administrator soʻrovni maʻqulladi. Siz roʻyxatdan oʻtdiz. Tugmani bosing.',
        'REG_USER_CHECK': 'Sizning arizangiz hali tasdiqlanmagan. Keyinroq urinib koʻring.',
        'MAIN_MENU_DESCRIPTION': 'Service Desk administratorlari filial xodimlariga bankomatlar, terminallar, infokiosklar, embosserlar sozlash yoki boshqa muammolarni hal qilishda yordam beradi.\n\nBoʻsh sahifa:',
        'MENU_SELECT_OBJ': 'Bankomatni tanlang',
        'MENU_SELECT_TICKETS_STATUS': 'Koʻrmoqchi boʻlgan arizalarni holatini tanlang.',
        'MENU_CLOSED_TICKETS_DESCRIPTION': 'Yopiq arizalar (oxirgi uchtasi):\n\n',
        'MENU_OPENED_TICKETS_DESCRIPTION': 'Arizalar:\n\n',
        'MENU_OBJ_SELECTED': '#{0} raqamli ariza:\n#{1} bankomat muammolarini tanlang',
        'ADMIN_USER_OPENED_TICKET_EDITOR_NOTIFICATION': '#{0} arizani {1} oʻzgartirvotdi.',
        'ADMIN_USER_createTicket_NOTIFICATION': '#{0} arizani {1} yaratdi.',
        'MENU_CREATE_OBJ_DESCRIPTION': '#{0} raqamli ariza:\nQoʻshimcha maʻlumotlarni kiriting va <b>Tugatish</b> tugmasini bosing.',
        'MENU_FINISH_OBJ_DESCRIPTION': '#{0} raqamli ariza qabul qilindi.\nTez orada administrator siz bilan bogʻlanadi.',
        'ADMIN_USER_CLOSED_TICKET_EDITOR_NOTIFICATION': '#{0} arizani {1} oʻzgartirshni tugatdi.',
        'MSG_ADMIN_CHANGE_STATUS': 'Administrator {2} - #{0} arizaning holatini {1}-ga oʻzgartirdi.',
        'ADMIN_TICKET_INFORMATION': '#{0}\n\nСотрудник:\n {4}\n\nОператор:\n {3}\n{2}\n\n{5}\n{1}',
        'MSG_NEW': '{1}-dan yangi jovob.\nKoʻrish uchun Status -> Ochiq -> #{0} ga o‘ting',
    },
    'ru': {
        'BTN_OPENED_TICKETS': 'Открытые',
        'BTN_CLOSED_TICKETS': 'Закрытые',

        'BTN_NEW_TICKET': 'Новая заявка',
        'BTN_TICKETS_STATUS': 'Статус заявок',

        'BTN_FINISH': 'Закончить',
        'BTN_CANCEL': 'Отменить',
        'BTN_CLOSE': 'Закрыть',
        'BTN_RETURN': 'Вернуться',
        'BTN_NEXT': 'Далее',

        'BTN_ACTIVATE_CHECK': 'Проверка активации',

        'MSG_EVERYDAY_NOTIFICATION_SUMMARY': '<b>Количество заявок (за месяц):</b> {0}\n<b>Обработано:</b> {1}\n<b>В ожидании:</b> {2}\n<b>Закрыто:</b> {3}',
        'MSG_EVERYDAY_NOTIFICATION_TICKET_INWORK': '<b>Список заявок (в исполнении):</b>\n\n',
        'MSG_EVERYDAY_NOTIFICATION_TICKET_NEW': '<b>Список новых заявок:</b>\n\n',

        'REG_USER': 'Вы подали заявку на регистрацию. После активации администратором нажмите на кнопку.',
        'REG_ACTIVATE_ADMIN': '{1} ({0}) ожидает авторизации. К какому филиалу должен подключиться пользователь?',
        'REG_USER_ACTIVATE_NOTIFICATION': 'Администратор одобрил запрос. Вы зарегистрированы. Нажми на кнопку.',
        'REG_USER_CHECK': 'Ваша заявка еще не одобрена. Пожалуйста, попробуйте позже.',
        'MAIN_MENU_DESCRIPTION': 'Администраторы Service Desk помогают сотрудникам филиала настроить банкоматы, терминалы, киоски, эмбоссеры или решить другие проблемы.:',
        'MENU_SELECT_OBJ': 'Выберите банкомат',
        'MENU_SELECT_TICKETS_STATUS': 'Выберите статус заявки, которые вы хотите просмотреть.',
        'MENU_CLOSED_TICKETS_DESCRIPTION': 'Закрытые заявки (последние три):\n\n',
        'MENU_OPENED_TICKETS_DESCRIPTION': 'Заявки:\n\n',
        'MENU_OBJ_SELECTED': '#{0} заявка:\n #{1} выберите категории',
        'ADMIN_USER_OPENED_TICKET_EDITOR_NOTIFICATION': '{1} редактирует заявку #{0}.',
        'ADMIN_USER_createTicket_NOTIFICATION': ' {1} создал заявку #{0}.',
        'MENU_CREATE_OBJ_DESCRIPTION': 'Заявка #{0}:\nВведите дополнительную информацию и нажмите Готово.',
        'MENU_FINISH_OBJ_DESCRIPTION': 'Заявка #{0} получена.\nАдминистрация свяжется с Вами в ближайшее время.',
        'ADMIN_USER_CLOSED_TICKET_EDITOR_NOTIFICATION': '{1} завершил изменение заявки #{0}.',
        'MSG_ADMIN_CHANGE_STATUS': 'Администратор {2} изменил статус #{0} заявки на {1}.',
        'ADMIN_TICKET_INFORMATION': '#{0}\n\nИнициатор:\n{4}\n\nОператор:\n{3}\n{2}\n\n{5}\n{1}',
        'MSG_NEW': 'Новый ответ от {1}.\nЧтобы посмотреть перейдите Заявки -> Открытые -> #{0}',
    },
}

# ================================================ #

def geticket_statusTitle(id, local):
    if id > 4 or id < 0 or local != 'uz' or local != 'ru' or local != 'en':
        return 'unknown'
    else:
        return {
            0: {
                'ru': 'открыто',
                'uz': 'ochiq',
                'en': 'open'
            },
            1: {
                'ru': 'закрыто',
                'uz': 'yopiq',
                'en': 'close'
            },
            2: {
                'ru': 'отменено',
                'uz': 'bekor qilingan',
                'en': 'canceled'
            },
            3: {
                'ru': 'сервисное обслуживание',
                'uz': 'servis xizmat',
                'en': 'service'
            },
            4: {
                'ru': 'в работе',
                'uz': 'ish jarayonda',
                'en': 'in work'
            },
        }[id][local]

async def clearChat(chatId, userId):
    messages = await cmd.getUserMessages(chatId, userId)
    await cmd.deleteUserMessages(userId)
    if messages:
        for i in messages:
            try:
                m = await bot.delete_message(chat_id=i['chat'], message_id=i['message_id'])
                logging.debug('return: {0}'.format(m))
            except:
                logging.debug('Message #{1} was not found in chat #{0}. (userId #{2})'.format(chatId,i['message_id'],userId))
# ================================================ #

# async def summaryEveryDayNotification():
#     summary = await cmd.stats_summary()
#
#     await bot.send_message(
#         chat_id=ADMIN_GROUP,
#         text=languages['ru']['MSG_EVERYDAY_NOTIFICATION_SUMMARY'].format(
#             summary['month'],
#             summary['read'],
#             summary['news'],
#             summary['closed']
#             )
#         )
#
#     msg_inwork = languages['ru']['MSG_EVERYDAY_NOTIFICATION_TICKET_INWORK']
#     msg_new = languages['ru']['MSG_EVERYDAY_NOTIFICATION_TICKET_NEW']
#     for i in summary['list']:
#         ticket_status = geticket_statusTitle(i['status'], 'uz')
#
#         try:
#             if 'dataCreated' in i:
#                 opening_date = i['dataCreated']
#                 opening_date += datetime.timedelta(hours=5)
#                 opening_date = humanize.naturaldelta(opening_date)
#             else:
#                 opening_date = '-'
#
#             if 'dataClosed' in i:
#                 modification_date = i['dataClosed']
#                 modification_date += datetime.timedelta(hours=5)
#                 modification_date = humanize.naturaldelta(modification_date)
#             else:
#                 modification_date = '-'
#         except:
#             print('error')
#
#         if (i['status'] == 0):
#             msg_new += '№ <a href="http://10.231.202.31:8081/ticket/{0}">{0}</a> {1} ({2}) {3} {4}\n'.format(
#                 i['tid'], i['atm_name'], i['username'], opening_date, ticket_status)
#         elif (i['status'] == 0 or i['status'] == 3 or i['status'] == 4):
#             msg_inwork += '№ <a href="http://10.231.202.31:8081/ticket/{0}">{0}</a> {1} ({2}) {3} {4}\n'.format(
#                 i['tid'],
#                 i['atm_name'],
#                 i['username'],
#                 modification_date,
#                 ticket_status
#                 )
#             if i['operator']:
#                 msg_inwork += '{0}'.format(i['operator'])
#             if i['description']:
#                 msg_inwork += '<i>{0}</i> '.format(i['description'])
#             msg_inwork += '\n'
#
#     await bot.send_message(chat_id=ADMIN_GROUP, text=msg_inwork)
#     await bot.send_message(chat_id=ADMIN_GROUP, text=msg_new)
#
# async def scheduler():
#     aioschedule.every().day.at(NOTIFICATION_TIME).do(summaryEveryDayNotification)
#     while True:
#         await aioschedule.run_pending()
#         await asyncio.sleep(1)
# #
# async def on_startup(_):
#     asyncio.create_task(scheduler())

# ================================================ #

inlineButtonMenuCreate = InlineKeyboardButton(languages['ru']['BTN_NEW_TICKET'], callback_data='new_ticket')
inlineButtonMenuList = InlineKeyboardButton(languages['ru']['BTN_TICKETS_STATUS'], callback_data='status_list')
inlineButtonMenuListOpen = InlineKeyboardButton(languages['ru']['BTN_OPENED_TICKETS'], callback_data='btnOpened')
inlineButtonMenuListClose = InlineKeyboardButton(languages['ru']['BTN_CLOSED_TICKETS'], callback_data='btnClosed')
inlineButtonMenuListReturn = InlineKeyboardButton(languages['ru']['BTN_RETURN'], callback_data='btnBack')
inlineButtonFinish = InlineKeyboardButton(languages['ru']['BTN_FINISH'], callback_data='btnEnd')
inlineButtonCancel = InlineKeyboardButton(languages['ru']['BTN_CANCEL'], callback_data='btnCancel')
inlineButtonClose = InlineKeyboardButton(languages['ru']['BTN_CLOSE'], callback_data='btnClose')

# Главное меню
iMenu = InlineKeyboardMarkup(row_width=1)
iMenu.row(inlineButtonMenuList)
iMenu.row(inlineButtonMenuCreate)

# Список заявок
iMenuList = InlineKeyboardMarkup(row_width=1)
iMenuList.row(inlineButtonMenuListOpen)
iMenuList.row(inlineButtonMenuListClose)
iMenuList.row(inlineButtonMenuListReturn)

# Меню назад
iMenuBack = InlineKeyboardMarkup(row_width=1)
iMenuBack.row(inlineButtonMenuListReturn)

# Меню завершения тикета
iMenuTicketCreate = InlineKeyboardMarkup(row_width=1)
iMenuTicketCreate.row(inlineButtonFinish)

# Меню изменение тикета
iMenuTicketEdit = InlineKeyboardMarkup(row_width=2)
iMenuTicketEdit.row(inlineButtonFinish, inlineButtonClose, inlineButtonCancel)


# @dp.message_handler()
# async def echo(message: types.Message):
#     print('1')
#     await bot.send_message(chat_id=message.chat.id, text='123')
@dp.message_handler(commands=['start'])
async def registration(message: types.Message):
    #await bot.send_message(chat_id=message.from_user.id, text=message.from_user.as_json())
    userActivateStatus = await cmd.addUser(message.from_user.id, message.from_user.full_name, message.from_user.as_json())
    print('1')
    branchs = await cmd.getBranchList()
    print('2')
    inlineBranchs = InlineKeyboardMarkup(row_width=1)
    print('3')
    for i in branchs:
        branch_name = '({0}) {1}'.format(i['number'], i['name'])
        temp_str = 'branch_'+str(i['id'])+'_'+str(message.from_user.id)
        inlineBranchs.insert(InlineKeyboardButton(branch_name, callback_data=temp_str))

    print('4')
    if userActivateStatus:
        print('5')
        _msg = await bot.send_message(message.from_user.id, languages['ru']['REG_USER'])
        await cmd.addUserMessage(_msg.chat.id, _msg.chat.id, _msg.message_id)
        await bot.send_message(chat_id=ADMIN_GROUP, text=languages['ru']['REG_ACTIVATE_ADMIN'].format(message.from_user.id, message.from_user.full_name), reply_markup=inlineBranchs)
    if not userActivateStatus:
        print('6')
        _msg = await bot.send_message(message.from_user.id, languages['ru']['REG_USER'])
        await cmd.addUserMessage(_msg.chat.id, _msg.chat.id, _msg.message_id)
        #await bot.send_message(chat_id=ADMIN_GROUP, text=languages['ru']['REG_ACTIVATE_ADMIN'].format(message.from_user.id, message.from_user.full_name), reply_markup=inlineBranchs)
    await bot.delete_message(message.chat.id, message.message_id)
    #await bot.send_message(message.from_user.id, "99")
    print('7')


@dp.callback_query_handler(lambda c: c.data[0:7] == 'branch_')
async def callbackAdminSelectBranch(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    argv = callback_query.data.split('_')
    branchId = argv[1]
    userId = argv[2]

    userActivateStatus = await cmd.getUserStatus(userId)

    if not userActivateStatus:
        await cmd.setUserBranch(branchId, userId)

        await clearChat(userId, userId)

        _msg = await bot.send_message(userId, languages['uz']['REG_USER_ACTIVATE_NOTIFICATION'])
        await cmd.addUserMessage(_msg.chat.id, _msg.chat.id, _msg.message_id)

        await cmd.setUserStage(userId, 'menu')
        await bot.send_message(userId, languages['ru']['MAIN_MENU_DESCRIPTION'], reply_markup=iMenu)

    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)


@dp.callback_query_handler(lambda c: c.data == 'notif_ok')
async def process_callback_button11(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)


@dp.callback_query_handler(lambda c: c.data == 'new_ticket')
async def process_callback_button2(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    userId = callback_query.from_user.id
    chatId = callback_query.message.chat.id
    messageId = callback_query.message.message_id
    await clearChat(chatId, userId)

    level = await cmd.getUserStage(userId)

    if level == 'menu' or level == '':
        await cmd.setUserStage(userId, 'select_obj')

        objs = await cmd.getObjects(userId)
        #await bot.send_message(chatId, '{0}'.format(objs))

        inlineObjects = InlineKeyboardMarkup(row_width=1)

        for i in objs:
            objName = i['atm_name']+' - ' + \
                i['model_company']+' '+i['model_name']
            inlineObjects.insert(InlineKeyboardButton(
                objName, callback_data='ticket_object_'+str(i['atm_id'])))
        inlineObjects.insert(inlineButtonMenuListReturn)
        #await bot.send_message(chatId, '{0}'.format(inlineObjects))

        await bot.edit_message_text(message_id=messageId, text=languages['ru']['MENU_SELECT_OBJ'], chat_id=chatId, reply_markup=inlineObjects)


@dp.callback_query_handler(lambda c: c.data == 'status_list')
async def process_callback_button3(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    userId = callback_query.from_user.id
    chatId = callback_query.message.chat.id
    messageId = callback_query.message.message_id

    await clearChat(chatId, userId)

    level = await cmd.getUserStage(userId)
    if level == 'menu' or level == '':
        await cmd.setUserStage(userId, 'select_status')
        await bot.edit_message_text(message_id=messageId, text=languages['ru']['MENU_SELECT_TICKETS_STATUS'], chat_id=chatId, reply_markup=iMenuList)


@dp.callback_query_handler(lambda c: c.data == 'btnBack')
async def process_callback_button4(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    userId = callback_query.from_user.id
    chatId = callback_query.message.chat.id
    messageId = callback_query.message.message_id

    await clearChat(chatId, userId)

    level = await cmd.getUserStage(userId)
    if level == 'menu' or level == '' or level == 'select_obj' or level == 'select_status' or level == 'status_closed' or level == 'status_opened':
        await cmd.setUserStage(userId, 'menu')
        await bot.edit_message_text(message_id=messageId, text=languages['ru']['MAIN_MENU_DESCRIPTION'], chat_id=chatId, reply_markup=iMenu)


@dp.callback_query_handler(lambda c: c.data == 'btnClosed')
async def process_callback_button5(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    messages = await cmd.getUserMessages(callback_query.message.chat.id, callback_query.from_user.id)
    await cmd.deleteUserMessages(callback_query.from_user.id)

    if messages:
        for i in messages:
            try:
                await bot.delete_message(chat_id=i['chat'], message_id=i['message_id'])
            except:
                print('error delete')
    st = await cmd.getUserStage(callback_query.from_user.id)
    arr = await cmd.get_status(callback_query.from_user.id, 1)
    tmp = '📝 <code>#{0}</code> ⏳ <i>{3}</i>\n🏧 {1}\n🛠 <code>{2}</code>'
    desc = '💬 <b>{0}:</b> {1}\n'
    if st == '' or st == 'select_status':
        await cmd.setUserStage(callback_query.from_user.id, 'status_closed')

        inline_closed = InlineKeyboardMarkup(row_width=1)
        message_all = '<code>Yopiq arizalar (oxirgi uchtasi)</code>\n\n'

        for i in arr:
            atm_name_with_geo_link = '<a href="https://maps.yandex.ru/?text={0}+{1}">{2}</a>'.format(
                i['lat'], i['long'], i['atm_name'])

            try:
                if 'created' in i:
                    opening_date = i['created']
                    opening_date += datetime.timedelta(hours=5)
                    opening_date = humanize.naturaldelta(opening_date)
                else:
                    opening_date = '-'

                if 'closed' in i:
                    modification_date = i['closed']-i['created']
                    modification_date = humanize.naturaldelta(modification_date)
                else:
                    modification_date = '-'
            except:
                print('error')

#
            #llol = 'j'
            message_all += tmp.format(i['ticket_id'],
                                      atm_name_with_geo_link,
                                      (i['details'] if i['details'] else 'нет'),
                                      modification_date)+'\n'
            message_all += desc.format(
                i['operator'] if i['operator'] else 'Admin',
                i['description'] if i['description'] else ' ')+'\n\n'
        inline_closed.insert(inlineButtonMenuListReturn)

        await bot.edit_message_text(message_id=callback_query.message.message_id, text=message_all, chat_id=callback_query.message.chat.id, reply_markup=inline_closed, disable_web_page_preview=True)


@dp.callback_query_handler(lambda c: c.data == 'btnOpened')
async def process_callback_button6(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    messages = await cmd.getUserMessages(callback_query.message.chat.id, callback_query.from_user.id)
    await cmd.deleteUserMessages(callback_query.from_user.id)

    if messages:
        for i in messages:
            try:
                await bot.delete_message(chat_id=i['chat'], message_id=i['message_id'])
            except:
                print('error delete')
    st = await cmd.getUserStage(callback_query.from_user.id)
    arr = await cmd.get_status(callback_query.from_user.id, 0)
    tmp = '📝 <code>#{0}</code> ⏱ <i>{2}</i>\n⏳ <i>{5}</i> <b>{1}</b>\n🏧 {3} \n🛠 <code>{4}</code>'
    desc = '💬 <b>{0}</b> {1}\n'
    if st == '' or st == 'select_status':
        await cmd.setUserStage(callback_query.from_user.id, 'status_opened')
#⏳
        inline_closed = InlineKeyboardMarkup(row_width=1)
        message_all = '<code>Arizalar:</code>\n\n'
        for i in arr:
            ticket_status = 'ochiq' if i['ticket_status'] == 0 else ('servis xizmat' if i['ticket_status'] == 3 else (
                'ish jarayonda' if i['ticket_status'] == 4 else 'noma\'lum'))

            inline_closed.insert(InlineKeyboardButton(
                '✍️ #'+str(i['ticket_id'])+' / '+ticket_status, callback_data='bcrta_{0}'.format(str(i['ticket_id']))))
            atm_name_with_geo_link = '<a href="https://maps.yandex.ru/?text={0}+{1}">{3} {2}</a>'.format(
                i['lat'], i['long'], i['atm_name'], str(i['atm_id']).zfill(5))
            try:
                if 'created' in i:
                    opening_date = i['created']
                    opening_date += datetime.timedelta(hours=5)
                    opening_date = humanize.naturaldelta(opening_date)
                else:
                    opening_date = '-'

                if 'closed' in i:
                    modification_date = i['closed']
                    modification_date += datetime.timedelta(hours=5)
                    modification_date = humanize.naturaldelta(modification_date)
                else:
                    modification_date = '-'
            except:
                print('error')

            message_all += tmp.format(
                i['ticket_id'],
                ticket_status,
                opening_date,
                atm_name_with_geo_link,
                (i['details'] if i['details'] else 'нет'),
                modification_date,
            )+'\n'
            if i['operator'] and i['description']:
                message_all += desc.format(
                    i['operator'],
                    i['description'])+'\n\n'
            else:
                message_all += '\n\n'
        inline_closed.insert(inlineButtonMenuListReturn)

        await bot.edit_message_text(message_id=callback_query.message.message_id, text=message_all, chat_id=callback_query.message.chat.id, reply_markup=inline_closed, disable_web_page_preview=True)


@dp.callback_query_handler(lambda c: c.data[0:14] == 'ticket_object_')
async def process_callback_button8(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    chatId = callback_query.message.chat.id
    userId = callback_query.from_user.id
    await clearChat(chatId, userId)

    st = await cmd.getUserStage(callback_query.from_user.id)
    if st == 'select_obj':
        stage = await cmd.setUserStage(callback_query.from_user.id, 'edit_ticket')
        user = await cmd.getUser(callback_query.from_user.id)
        p = await cmd.getProblems()
        arr = callback_query.data.split('_')
        ticket_id = await cmd.addTicket(arr[2], user['id'])
        b = await cmd.getEditTicket(ticket_id, 1)
#123
#TODO добавить проблему
        await cmd.setTicketProblem(ticket_id, 1)
        # hh = await cmd.existTicketProblem(s)
        messages = await cmd.getUserMessages(callback_query.message.chat.id, callback_query.from_user.id)
        await cmd.deleteUserMessages(callback_query.from_user.id)

        if messages:
            for i in messages:
                try:
                    await bot.delete_message(chat_id=i['chat'], message_id=i['message_id'])
                except:
                    print('error delete')

        await cmd.setEditTicket(ticket_id, 0)

        if st == 'status_opened':
            await bot.send_message(ADMIN_GROUP, '🛠 {1} редактирует заявку <code>#{0}</code>'.format(ticket_id,
                                                                                                    callback_query.from_user.first_name))
        else:
            await bot.send_message(ADMIN_GROUP, '🆕 {1} создал заявку <code>#{0}</code>'.format(ticket_id,
                                                                                               callback_query.from_user.first_name))

        await bot.edit_message_text(message_id=callback_query.message.message_id,
                                    text='<code>#{0} raqamli ariza:</code>\nQo\'shimcha ma\'lumotlarni kiriting va <b>❎ TUGATISH</b> tugmasini bosing.'.format(
                                        ticket_id), chat_id=callback_query.message.chat.id,
                                    reply_markup=iMenuTicketCreate)

        history = await cmd.getTicketMessages(ticket_id)
        for i in history:
            # try:
            ms_info = json.loads(i['json'], strict=False)
            fname = ms_info['from']['first_name']
            if 'last_name' in ms_info['from'] and ms_info['from']['last_name']:
                fname += ' ' + ms_info['from']['last_name']
            caption_msg = '<code>' + ms_info['from']['first_name'] + '</code>'
            if 'caption' in ms_info:
                caption_msg += '\n' + json.loads(i['caption'])
            if 'text' in ms_info:
                m = await bot.send_message(callback_query.from_user.id,
                                           '<code>' + fname + '</code>:\n' + json.loads(i['text']))
            elif 'document' in ms_info:
                m = await bot.send_document(chat_id=callback_query.from_user.id,
                                            document=ms_info['document']['file_id'], caption=caption_msg)
            elif 'voice' in ms_info:
                m = await bot.send_voice(chat_id=callback_query.from_user.id, voice=ms_info['voice']['file_id'],
                                         caption=caption_msg)
            elif 'video_note' in ms_info:
                m = await bot.send_video_note(callback_query.from_user.id, ms_info['video_note']['file_id'])
            elif 'video' in ms_info:
                m = await bot.send_video(chat_id=callback_query.from_user.id, video=ms_info['video']['file_id'],
                                         caption=caption_msg)
            elif 'photo' in ms_info:
                m = await bot.send_photo(chat_id=callback_query.from_user.id, photo=ms_info['photo'][-1]['file_id'],
                                         caption=caption_msg)
            elif 'sticker' in ms_info:
                m = await bot.send_sticker(chat_id=callback_query.from_user.id,
                                           sticker=ms_info['sticker']['file_id'])
            elif 'contact' in ms_info:
                m = await bot.send_contact(chat_id=callback_query.from_user.id,
                                           phone_number=ms_info['contact']['phone_number'], first_name=fname)
            elif 'location' in ms_info:
                m = await bot.send_location(chat_id=callback_query.from_user.id,
                                            latitude=ms_info['location']['latitude'],
                                            longitude=ms_info['location']['longitude'])
            if m:
                await cmd.addUserMessage(callback_query.message.chat.id, callback_query.from_user.id, m.message_id)

        ############3
        # inline_problems = InlineKeyboardMarkup(row_width=1)
        # for i in p:
        #     inline_problems.insert(InlineKeyboardButton(
        #         i['title'], callback_data='crta_{0}_{1}'.format(s, i['id'])))
        # inline_problems.insert(InlineKeyboardButton(
        #     '➡️ Далее / Keyingi', callback_data='bcrta_{0}'.format(s)))

        # await bot.edit_message_text(message_id=callback_query.message.message_id, text='<b>#{0} raqamli ariza:\n</b>#{1} ATM (bankomat) muammolarini tanlang'.format(s, arr[2]), chat_id=callback_query.message.chat.id, reply_markup=inline_problems)

#
# @dp.callback_query_handler(lambda c: c.data[0:5] == 'crta_')
# async def process_callback_button9(callback_query: types.CallbackQuery):
#     await bot.answer_callback_query(callback_query.id)
#
#     messages = await cmd.getUserMessages(callback_query.message.chat.id, callback_query.from_user.id)
#     await cmd.deleteUserMessages(callback_query.from_user.id)
#
#     if messages:
#         for i in messages:
#             try:
#                 await bot.delete_message(chat_id=i['chat'], message_id=i['message_id'])
#             except:
#                 print('error delete')
#     st = await cmd.getUserStage(callback_query.from_user.id)
#     if st == 'select_problem' or st == 'select_problem_m':
#         await callback_query.answer()
#         stage = await cmd.setUserStage(callback_query.from_user.id, 'select_problem_m')
#         user = await cmd.getUser(callback_query.from_user.id)
#
#         arr = callback_query.data.split('_')
#
#         p = await cmd.getProblems()
#
#         inline_problems = InlineKeyboardMarkup(row_width=1)
#
#         result = re.findall(r'[0-9]+', callback_query.message.text)
#
#         check = await cmd.getTicketProblem(arr[1], arr[2])
#         if check:
#             b = await cmd.deleteTicketProblem(arr[1], arr[2])
#         else:
#             b = await cmd.setTicketProblem(arr[1], arr[2])
#
#         for i in p:
#             ch = await cmd.getTicketProblem(arr[1], i['id'])
#             if ch:
#                 inline_problems.insert(InlineKeyboardButton(
#                     '✅ '+i['title'], callback_data='crta_{0}_{1}'.format(arr[1], i['id'])))
#             else:
#                 inline_problems.insert(InlineKeyboardButton(
#                     i['title'], callback_data='crta_{0}_{1}'.format(arr[1], i['id'])))
#         inline_problems.insert(InlineKeyboardButton(
#             '➡️ Далее / Keyingi', callback_data='bcrta_{0}'.format(arr[1])))
#
#         await bot.edit_message_text(message_id=callback_query.message.message_id, text='<code>#{0} raqamli ariza:</code>\n#{1} ATM (bankomat) muammolarini tanlang'.format(result[0], result[1]), chat_id=callback_query.message.chat.id, reply_markup=inline_problems)

#
# @dp.callback_query_handler(lambda c: c.data[0:6] == 'bcrta_')
# async def process_callback_button10(callback_query: types.CallbackQuery):
#     await bot.answer_callback_query(callback_query.id)
#     arr = callback_query.data.split('_')
#     hh = await cmd.existTicketProblem(arr[1])
#     messages = await cmd.getUserMessages(callback_query.message.chat.id, callback_query.from_user.id)
#     await cmd.deleteUserMessages(callback_query.from_user.id)
#
#     if messages:
#         for i in messages:
#             try:
#                 await bot.delete_message(chat_id=i['chat'], message_id=i['message_id'])
#             except:
#                 print('error delete')
#     st = await cmd.getUserStage(callback_query.from_user.id)
#     if hh and (st == 'select_problem' or st == 'select_problem_m' or st == 'status_opened'):
#         stage = await cmd.setUserStage(callback_query.from_user.id, 'edit_ticket')
#         user = await cmd.getUser(callback_query.from_user.id)
#
#         await cmd.setEditTicket(arr[1], 0)
#
#         if st == 'status_opened':
#             await bot.send_message(ADMIN_GROUP, '🛠 {1} редактирует заявку <code>#{0}</code>'.format(arr[1], callback_query.from_user.first_name))
#         else:
#             await bot.send_message(ADMIN_GROUP, '🆕 {1} создал заявку <code>#{0}</code>'.format(arr[1], callback_query.from_user.first_name))
#
#         await bot.edit_message_text(message_id=callback_query.message.message_id, text='<code>#{0} raqamli ariza:</code>\nQo\'shimcha ma\'lumotlarni kiriting va <b>❎ TUGATISH</b> tugmasini bosing.'.format(arr[1]), chat_id=callback_query.message.chat.id, reply_markup=iMenuTicketCreate)
#
#         history = await cmd.getTicketMessages(arr[1])
#         for i in history:
#             #try:
#             ms_info = json.loads(i['json'], strict=False)
#             fname = ms_info['from']['first_name']
#             if 'last_name' in ms_info['from'] and ms_info['from']['last_name']:
#                 fname += ' '+ms_info['from']['last_name']
#             caption_msg = '<code>'+ms_info['from']['first_name']+'</code>'
#             if 'caption' in ms_info:
#                 caption_msg += '\n'+json.loads(i['caption'])
#             if 'text' in ms_info:
#                 m = await bot.send_message(callback_query.from_user.id, '<code>'+fname+'</code>:\n'+json.loads(i['text']))
#             elif 'document' in ms_info:
#                 m = await bot.send_document(chat_id=callback_query.from_user.id, document=ms_info['document']['file_id'], caption=caption_msg)
#             elif 'voice' in ms_info:
#                 m = await bot.send_voice(chat_id=callback_query.from_user.id, voice=ms_info['voice']['file_id'], caption=caption_msg)
#             elif 'video_note' in ms_info:
#                 m = await bot.send_video_note(callback_query.from_user.id, ms_info['video_note']['file_id'])
#             elif 'video' in ms_info:
#                 m = await bot.send_video(chat_id=callback_query.from_user.id, video=ms_info['video']['file_id'], caption=caption_msg)
#             elif 'photo' in ms_info:
#                 m = await bot.send_photo(chat_id=callback_query.from_user.id, photo=ms_info['photo'][-1]['file_id'], caption=caption_msg)
#             elif 'sticker' in ms_info:
#                 m = await bot.send_sticker(chat_id=callback_query.from_user.id, sticker=ms_info['sticker']['file_id'])
#             elif 'contact' in ms_info:
#                 m = await bot.send_contact(chat_id=callback_query.from_user.id, phone_number=ms_info['contact']['phone_number'], first_name=fname)
#             elif 'location' in ms_info:
#                 m = await bot.send_location(chat_id=callback_query.from_user.id, latitude=ms_info['location']['latitude'], longitude=ms_info['location']['longitude'])
#             if m:
#                 await cmd.addUserMessage(callback_query.message.chat.id, callback_query.from_user.id, m.message_id)
#

@dp.callback_query_handler(lambda c: c.data == 'btnEnd')
async def process_callback_button12(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    messages = await cmd.getUserMessages(callback_query.message.chat.id, callback_query.from_user.id)
    await cmd.deleteUserMessages(callback_query.from_user.id)

    if messages:
        for i in messages:
            try:
                await bot.delete_message(chat_id=i['chat'], message_id=i['message_id'])
            except:
                print('error delete')
    st = await cmd.getUserStage(callback_query.from_user.id)
    result = re.findall(r'[0-9]+', callback_query.message.text)
    if len(result) > 0:
        await bot.edit_message_text(message_id=callback_query.message.message_id, text='<b>✅ #{0} raqamli ariza qabul qilindi.</b>\nTez orada administrator siz bilan bog\'lanadi.'.format(result[0]), chat_id=callback_query.message.chat.id, reply_markup=iMenu)
    else:
        await bot.edit_message_text(message_id=callback_query.message.message_id, text='Bo\'sh sahifa', chat_id=callback_query.message.chat.id, reply_markup=iMenu)
    if st == 'edit_ticket':
        user = await cmd.getUser(callback_query.from_user.id)
        b = await cmd.setEditTicket(result[0], 1)
        msgs = await cmd.getTicketMessages(result[0])
        messages = await cmd.getUserMessages(callback_query.message.chat.id, callback_query.from_user.id)
        await cmd.deleteUserMessages(callback_query.from_user.id)

        if messages:
            for i in messages:
                try:
                    await bot.delete_message(chat_id=i['chat'], message_id=i['message_id'])
                except:
                    print('error delete')

        await bot.send_message(ADMIN_GROUP, '❗ {1} завершил редактирование заявки <code>#{0}</code>'.format(result[0], callback_query.from_user.first_name))

    await cmd.setUserStage(callback_query.from_user.id, 'menu')


@dp.message_handler(commands=['menu'])
async def process_command_2(message: types.Message):

    messages = await cmd.getUserMessages(message.chat.id, message.from_user.id)
    await cmd.deleteUserMessages(message.from_user.id)

    if messages:
        for i in messages:
            try:
                await bot.delete_message(chat_id=i['chat'], message_id=i['message_id'])
            except:
                break
                print('error delete')

    st = await cmd.getUserStage(message.from_user.id)
    auth = await cmd.getUserStatus(message.from_user.id)
    if auth and st == '':
        await cmd.setUserStage(message.from_user.id, 'menu')
        await bot.send_message(message.from_user.id, 'Service Desk administratorlari filial xodimlariga bankomatlar, terminallar, infokiosklar, embosserlar sozlash yoki boshqa muammolarni hal qilishda yordam beradi.\n\nBo\'sh sahifa:', reply_markup=iMenu)
    try:
        await bot.delete_message(message.chat.id, message.message_id)
    except:
        print('error del')


@dp.callback_query_handler(lambda c: c.data[0:9] == 'opticket_')
async def process_callback_button13(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    arr = callback_query.data.split('_')
    await cmd.setStatusTicket(arr[1], arr[2])
    t_uid = await cmd.getTicketUID(arr[1])
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    ticket_status = 'ochiq' if int(arr[2]) == 0 else ('servis xizmat' if int(arr[2]) == 3 else (
        'ish jarayonda' if int(arr[2]) == 4 else ('yopiq' if int(arr[2]) == 1 else 'noma\'lum')))
    notif_inline = InlineKeyboardMarkup(row_width=1)
    notif_inline.insert(InlineKeyboardButton('🆗', callback_data='notif_ok'))
    m = await bot.send_message(t_uid, '🔔 Administrator <b>{2}</b> - <code>#{0}</code> arizaning holatini <i>{1}</i>-ga o\'zgartirdi.'.format(arr[1], ticket_status, callback_query.from_user.full_name), reply_markup=notif_inline)
    await cmd.addUserMessage(m.chat.id, m.chat.id, m.message_id)


@dp.callback_query_handler(lambda c: c.data == 'tcancel')
async def ticket_info_cancel(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)


@dp.message_handler(commands=['t'])
async def start_command(message: types.Message):
    arguments = message.get_args()

    if arguments != '' and arguments.isnumeric():
        tmp = await cmd.getTicket(arguments)
        try:
            ticket_status = 'открыто' if tmp['ticket_status'] == 0 else ('сервисное обслуживание' if tmp['ticket_status'] == 3 else (
                'в работе' if tmp['ticket_status'] == 4 else ('закрыто' if tmp['ticket_status'] == 1 else 'неизвестно')))
            if tmp['description'] or tmp['description'] == '':
                tmp['description'] = 'нет комментария'

            btns = InlineKeyboardMarkup(row_width=2)
            btns.row(InlineKeyboardButton('Закрыть', callback_data='opticket_{0}_1'.format(arguments)),
                     InlineKeyboardButton('Открыть', callback_data='opticket_{0}_0'.format(arguments)))
            btns.row(InlineKeyboardButton('Сервис', callback_data='opticket_{0}_3'.format(arguments)),
                     InlineKeyboardButton('В работе', callback_data='opticket_{0}_4'.format(arguments)))
            btns.row(InlineKeyboardButton('Отмена', callback_data='opticket_{0}_2'.format(arguments)),
                     InlineKeyboardButton('Выйти', callback_data='tcancel'))

            if not tmp['operator']:
                await cmd.setTicketOperator(arguments, message.from_user.full_name)

            await bot.send_message(message.chat.id, '<code>#{0}</code>\n\n🙍‍♂️ <b>Сотрудник:</b>\n {4}\n\n👨‍✈️ <b>Оператор:</b>\n {3}\n💬 {2}\n\n🏧 <b>{5}</b>\n<code>{1}</code>'.format(arguments, (tmp['details'] if tmp['details'] else 'нет'), tmp['description'], tmp['operator'], tmp['username'], tmp['atm_name']), reply_markup=btns)
        except Exception as e:
            if hasattr(e, 'message'):
                await bot.send_message(message.chat.id, '{0}'.format(e.message))
            else:
                await bot.send_message(message.chat.id, '{0}'.format(e))
    await bot.delete_message(message.chat.id, message.message_id)


@dp.message_handler(content_types=ContentType.ANY)
async def echo(message: types.Message):
    js_obj = message.to_python()
    txt = ''
    cap = ''
    if 'text' in js_obj:
        txt = json.dumps(message.html_text)
        js_obj.update({'text': ' '})
    if 'caption' in js_obj:
        cap = json.dumps(message.caption)
        js_obj.update({'caption': ' '})

    if message.chat.id == ADMIN_GROUP:
        if message.reply_to_message and message.reply_to_message.from_user.id == 5997574241:
            if message.reply_to_message:
                if message.reply_to_message.text:
                    ticket_num = re.findall(
                        r'[0-9]{0,3}', message.reply_to_message.text)
                    while '' in ticket_num:
                        ticket_num.remove('')
                else:
                    ticket_num = re.findall(
                        r'[0-9]{0,3}', message.reply_to_message.caption)
                if ticket_num:
                    t_uid = await cmd.getTicketUID(ticket_num[0])
                    st = await cmd.getUserStage(t_uid)
                    #❕
                    caption_msg = '<code>'+message.from_user.full_name+'</code>'
                    if message.caption:
                        caption_msg += '\n'+message.caption
                    if message.text:
                        await cmd.addTicketMessage(json.dumps(js_obj, sort_keys=True), ticket_num[0], 'text', '', False, True, False, cap, txt)
                        if st == 'edit_ticket':
                            m = await bot.send_message(t_uid, '<code>'+message.from_user.full_name+'</code>:\n'+message.text)
                    elif message.document:
                        file_id = message.document.file_id
                        file = await bot.get_file(file_id)
                        file_path = file.file_path
                        await bot.download_file(file_path, "/root/interlayer/media/telegram/"+file_path)
                        await cmd.addTicketMessage(json.dumps(js_obj, sort_keys=True), ticket_num[0], 'document', 'telegram/'+file_path, True, True, False, cap, txt)
                        if st == 'edit_ticket':
                            m = await bot.send_document(chat_id=t_uid, document=message.document.file_id, caption=caption_msg)
                    elif message.voice:
                        file_id = message.voice.file_id
                        file = await bot.get_file(file_id)
                        file_path = file.file_path
                        await bot.download_file(file_path, "/root/interlayer/media/telegram/"+file_path)
                        await cmd.addTicketMessage(json.dumps(js_obj, sort_keys=True), ticket_num[0], 'voice', 'telegram/'+file_path, True, True, False, cap, txt)
                        if st == 'edit_ticket':
                            m = await bot.send_voice(chat_id=t_uid, voice=message.voice.file_id, caption=caption_msg)
                    elif message.video_note:
                        file_id = message.video_note.file_id
                        file = await bot.get_file(file_id)
                        file_path = file.file_path
                        await bot.download_file(file_path, "/root/interlayer/media/telegram/"+file_path)
                        await cmd.addTicketMessage(json.dumps(js_obj, sort_keys=True), ticket_num[0], 'video_note', 'telegram/'+file_path, True, True, False, cap, txt)
                        if st == 'edit_ticket':
                            m = await bot.send_video_note(t_uid, message.video_note.file_id)
                    elif message.video:
                        file_id = message.video.file_id
                        file = await bot.get_file(file_id)
                        file_path = file.file_path
                        await bot.download_file(file_path, "/root/interlayer/media/telegram/"+file_path)
                        await cmd.addTicketMessage(json.dumps(js_obj, sort_keys=True), ticket_num[0], 'video', 'telegram/'+file_path, True, True, False, cap, txt)
                        if st == 'edit_ticket':
                            m = await bot.send_video(chat_id=t_uid, video=message.video.file_id, caption=caption_msg)
                    elif message.photo:
                        file_id = message.photo[-1].file_id
                        file = await bot.get_file(file_id)
                        file_path = file.file_path
                        await bot.download_file(file_path, "/root/interlayer/media/telegram/"+file_path)
                        await cmd.addTicketMessage(json.dumps(js_obj, sort_keys=True), ticket_num[0], 'photo', 'telegram/'+file_path, True, True, False, cap, txt)
                        if st == 'edit_ticket':
                            m = await bot.send_photo(chat_id=t_uid, photo=message.photo[-1].file_id, caption=caption_msg)
                    elif message.sticker:
                        file_id = message.sticker.file_id
                        file = await bot.get_file(file_id)
                        file_path = file.file_path
                        await bot.download_file(file_path, "/root/interlayer/media/telegram/"+file_path)
                        await cmd.addTicketMessage(json.dumps(js_obj, sort_keys=True), ticket_num[0], 'sticker', 'telegram/'+file_path, True, True, False, cap, txt)
                        if st == 'edit_ticket':
                            m = await bot.send_sticker(chat_id=t_uid, sticker=message.sticker.file_id)
                    elif message.contact:
                        await cmd.addTicketMessage(json.dumps(js_obj, sort_keys=True), ticket_num[0], 'contact', '', False, True, False, cap, txt)
                        if st == 'edit_ticket':
                            m = await bot.send_contact(chat_id=t_uid, phone_number=message.contact.phone_number, first_name=message.contact.first_name)
                    elif message.location:
                        await cmd.addTicketMessage(json.dumps(js_obj, sort_keys=True), ticket_num[0], 'location', '', False, True, False, cap, txt)
                        if st == 'edit_ticket':
                            m = await bot.send_location(chat_id=t_uid, latitude=message.location.latitude, longitude=message.location.longitude)
                    if st == 'edit_ticket' and m:
                        await cmd.addUserMessage(m.chat.id, m.chat.id, m.message_id)


                    if st != 'edit_ticket':
                        notif_inline = InlineKeyboardMarkup(row_width=1)
                        notif_inline.insert(InlineKeyboardButton(
                            '🆗', callback_data='notif_ok'))
                        m = await bot.send_message(t_uid, '📩 <b>{1}</b>-dan yangi jovob.\nKo\'rish uchun <code>Status -> Ochiq -> #{0}</code> ga o‘ting'.format(ticket_num[0], message.from_user.full_name), reply_markup=notif_inline)
                        await cmd.addUserMessage(m.chat.id, m.chat.id, m.message_id)
    else:
        st = await cmd.getUserStage(message.from_user.id)
        auth = await cmd.getUserStatus(message.from_user.id)
        if auth and st == 'edit_ticket':
            s = await cmd.getEditTicket(message.from_user.id, 0)

            caption_msg = '<code>#'+str(s['id'])+'</code>'
            if message.caption:
                caption_msg += '\n'+message.caption

            if message.document:
                file_id = message.document.file_id
                await bot.send_document(chat_id=ADMIN_GROUP, document=file_id, caption=caption_msg)
                file = await bot.get_file(file_id)
                file_path = file.file_path
                await bot.download_file(file_path, "/root/interlayer/media/telegram/"+file_path)

                await cmd.addTicketMessage(json.dumps(js_obj, sort_keys=True), s['id'], 'document', 'telegram/'+file_path, True, False, False, cap, txt)
            elif message.voice:
                file_id = message.voice.file_id
                await bot.send_voice(chat_id=ADMIN_GROUP, voice=file_id, caption=caption_msg)
                file = await bot.get_file(file_id)
                file_path = file.file_path
                await bot.download_file(file_path, "/root/interlayer/media/telegram/"+file_path)
                await cmd.addTicketMessage(json.dumps(js_obj, sort_keys=True), s['id'], 'voice', 'telegram/'+file_path, True, False, False, cap, txt)
            elif message.video_note:
                file_id = message.video_note.file_id
                await bot.send_message(chat_id=ADMIN_GROUP, text='<code>#'+str(s['id'])+'</code>'+'\n[видеосообщение]')
                await bot.send_video_note(ADMIN_GROUP, file_id)
                file = await bot.get_file(file_id)
                file_path = file.file_path
                await bot.download_file(file_path, "/root/interlayer/media/telegram/"+file_path)
                await cmd.addTicketMessage(json.dumps(js_obj, sort_keys=True), s['id'], 'video_note', 'telegram/'+file_path, True, False, False, cap, txt)
            elif message.video:
                file_id = message.video.file_id
                await bot.send_video(chat_id=ADMIN_GROUP, video=file_id, caption=caption_msg)
                file = await bot.get_file(file_id)
                file_path = file.file_path
                await bot.download_file(file_path, "/root/interlayer/media/telegram/"+file_path)
                await cmd.addTicketMessage(json.dumps(js_obj, sort_keys=True), s['id'], 'video', 'telegram/'+file_path, True, False, False, cap, txt)
            elif message.photo:
                file_id = message.photo[-1].file_id
                await bot.send_photo(chat_id=ADMIN_GROUP, photo=file_id, caption=caption_msg)
                file = await bot.get_file(file_id)
                file_path = file.file_path
                await bot.download_file(file_path, "/root/interlayer/media/telegram/"+file_path)
                await cmd.addTicketMessage(json.dumps(js_obj, sort_keys=True), s['id'], 'photo', 'telegram/'+file_path, True, False, False, cap, txt)
            elif message.sticker:
                await bot.send_message(chat_id=ADMIN_GROUP, text='<code>#'+str(s['id'])+'</code>'+'\n[стикер]')
                await bot.send_sticker(chat_id=ADMIN_GROUP, sticker=message.sticker.file_id)
                await cmd.addTicketMessage(json.dumps(js_obj, sort_keys=True), s['id'], 'sticker', '', False, False, False, cap, txt)
            elif message.contact:
                await bot.send_message(chat_id=ADMIN_GROUP, text='<code>#'+str(s['id'])+'</code>'+'\n[контакт]')
                await bot.send_contact(chat_id=ADMIN_GROUP, phone_number=message.contact.phone_number, first_name=message.contact.first_name)
                await cmd.addTicketMessage(json.dumps(js_obj, sort_keys=True), s['id'], 'contact', '', False, False, False, cap, txt)
            elif message.location:
                await bot.send_message(chat_id=ADMIN_GROUP, text='<code>#'+str(s['id'])+'</code>'+'\n[локация]')
                await bot.send_location(chat_id=ADMIN_GROUP, latitude=message.location.latitude, longitude=message.location.longitude)
                await cmd.addTicketMessage(json.dumps(js_obj, sort_keys=True), s['id'], 'location', '', False, False, False, cap, txt)
            elif message.text:
                await bot.send_message(chat_id=ADMIN_GROUP, text='<code>#'+str(s['id'])+'</code>'+'\n'+message.text)
                await cmd.addTicketMessage(json.dumps(js_obj, sort_keys=True), s['id'], 'text', '', False, False, False, cap, txt)
            else:
                await bot.send_message(chat_id=ADMIN_GROUP, text='<code>#'+str(s['id'])+'</code>'+'\n[неизвестно]')
                await cmd.addTicketMessage(json.dumps(js_obj, sort_keys=True), s['id'], 'unknown', '', False, False, False, cap, txt)

            await cmd.addUserMessage(message.chat.id, message.from_user.id, message.message_id)
        if st == 'select_problem_m' or st == 'select_problem' or st == 'select_obj' or st == 'menu':
            await bot.delete_message(message.chat.id, message.message_id)
