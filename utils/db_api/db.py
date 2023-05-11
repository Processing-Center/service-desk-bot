from aiomysql import Pool, DictCursor

from utils.db_api.sql import db_pool
import json
import io

class DBCommands:
    pool: Pool = db_pool
# 885533024
    TG_USER_ACTIVATE = "UPDATE app_telegramuser SET mfo_id = {0}, status = 1 WHERE uid = {1}"
    MFO_LIST = "select * from app_mfostruct"

    GET_ATMS = "SELECT app_atm.id as atm_id, app_atm.name as atm_name,app_telegramuser.uid as uid,app_telegramuser.name as tg_name,app_atmmodel.name as model_name,app_atmmodel.company as model_company FROM app_atm INNER JOIN app_telegramuser ON app_telegramuser.mfo_id=app_atm.mfo_id INNER JOIN app_atmmodel ON app_atmmodel.id=app_atm.atmModelId_id WHERE uid={0}"
    CREATE_TICKET = "INSERT INTO app_ticket(status, atm_id, dataClosed, dataCreated, user_id, edited) VALUES (0, {0}, UTC_TIMESTAMP(), UTC_TIMESTAMP(), {1}, 0)"
    SET_TICKET_BROKEN = "INSERT INTO app_ticket_broken(ticket_id, brokencategory_id) VALUES ({0}, {1})"
    REMOVE_TICKET_BROKEN = "DELETE FROM app_ticket_broken WHERE ticket_id = {0} AND brokencategory_id={1}"
    EXIST_TICKET_BROKEN = "SELECT * FROM app_ticket_broken WHERE ticket_id = {0} AND brokencategory_id={1}"
    EXIST_BROKEN = "SELECT * FROM app_ticket_broken WHERE ticket_id = {0}"

    GET_PROBLEMS = "select * from app_brokencategory"

    CAN_CREATE_TICKET = "SELECT count(*) AS COUNT\
                        FROM app_ticket\
                        INNER JOIN app_telegramuser ON app_telegramuser.mfo_id=app_ticket.user_id\
                        WHERE app_ticket.edited=0\
                            AND app_telegramuser.uid={0}"
    GET_EDIT_TICKET = "SELECT app_ticket.id, app_ticket.STATUS, app_ticket.atm_id, app_ticket.user_id,	app_ticket.edited, app_telegramuser.uid FROM app_ticket INNER JOIN app_telegramuser ON app_telegramuser.id = app_ticket.user_id WHERE app_ticket.edited = {1} and app_telegramuser.uid = {0} ORDER BY app_ticket.id DESC"
    SET_EDIT_TICKET = "UPDATE app_ticket SET edited = {1} WHERE id = {0}"
    SET_STATUS_TICKET = "UPDATE app_ticket SET status = {1} WHERE id = {0}"

    ADD_MSG = "INSERT INTO app_telegrammsg ( json, t_id, category, download, operator, show, text ) VALUES ( '{0}', {1}, '{2}', 0, 0, 0, '{3}' )"
    ADD_MSG_FILE = "INSERT INTO app_telegrammsg ( json, t_id, category, dt, path, download, operator, app_telegrammsg.show, caption, text) VALUES ( '{0}', {1}, '{2}', NOW(), '{3}', {4}, {5}, {6}, %s, %s )"

    GET_USER = "select * from app_telegramuser where uid={0}"
    EXIST_USER_IN_DB = "select * from app_telegramuser where uid={0}"

    GET_USER_STAGE = "SELECT * FROM app_telegramuser WHERE uid = {0}"
    SET_USER_STAGE = "UPDATE app_telegramuser SET stage = '{1}' WHERE uid={0}"

    REGISTRATION = "INSERT INTO app_telegramuser(uid,name,stage,status,json_info,language) VALUES({0}, '{1}','',0,'{2}',0)"

    GET_STATUS = "\
                    SELECT\
                        app_ticket.id AS ticket_id,\
                        GROUP_CONCAT( app_brokencategory.title SEPARATOR '; ' ) AS details,\
                        app_ticket.STATUS AS ticket_status,\
                        app_ticket.dataCreated AS created,\
                        app_ticket.dataClosed AS closed,\
                        app_ticket.description,\
                        app_ticket.operator,\
                        app_ticket.edited,\
                        app_telegramuser.uid AS user_id,\
                        app_telegramuser.NAME AS username,\
                        app_atm.NAME AS atm_name,\
                        app_atm.id AS atm_id,\
                        app_atm.serialNumber AS serial_number,\
                        app_atm.terminalId AS terminal_id,\
                        app_atm.lat,\
                        app_atm.long,\
                        app_atmmodel.image,\
                        app_atmmodel.NAME AS atm_model_name,\
                        app_atmmodel.company \
                    FROM\
                        app_ticket\
                        JOIN app_telegramuser ON app_telegramuser.id = app_ticket.user_id\
                        JOIN app_atm ON app_atm.id = app_ticket.atm_id\
                        JOIN app_atmmodel ON app_atm.atmModelId_id = app_atmmodel.id\
                        JOIN app_ticket_broken ON app_ticket.id = app_ticket_broken.ticket_id\
                        JOIN app_brokencategory ON app_brokencategory.id = app_ticket_broken.brokencategory_id \
                    WHERE\
                        app_telegramuser.uid = {0} \
                        AND app_ticket.STATUS IN ( {1} ) \
                    GROUP BY\
                        app_ticket.id \
                    ORDER BY\
                        app_ticket.id DESC\
                    LIMIT 3"
    GET_TICKET_OF_ID = "SELECT\
                                app_ticket.id AS ticket_id,\
                                GROUP_CONCAT( app_brokencategory.title SEPARATOR '; ' ) AS details,\
                                app_ticket.STATUS AS ticket_status,\
                                app_ticket.description,\
                                app_ticket.operator,\
                                app_ticket.edited,\
                                app_telegramuser.uid AS user_id,\
                                app_telegramuser.NAME AS username,\
                                app_atm.NAME AS atm_name,\
                                app_atm.id AS atm_id,\
                                app_atm.serialNumber AS serial_number,\
                                app_atm.terminalId AS terminal_id,\
                                app_atm.lat,\
                                app_atm.LONG,\
                                app_atmmodel.image,\
                                app_atmmodel.NAME AS atm_model_name,\
                                app_atmmodel.company \
                                FROM\
                                    app_ticket\
                                    JOIN app_telegramuser ON app_telegramuser.id = app_ticket.user_id\
                                    JOIN app_atm ON app_atm.id = app_ticket.atm_id\
                                    JOIN app_atmmodel ON app_atm.atmModelId_id = app_atmmodel.id\
                                    JOIN app_ticket_broken ON app_ticket.id = app_ticket_broken.ticket_id\
                                    JOIN app_brokencategory ON app_brokencategory.id = app_ticket_broken.brokencategory_id \
                                WHERE\
                                    app_ticket.id = {0} limit 1"

    GET_TICKET_MSG = "select * from app_telegrammsg where t_id = {0}"
    HISTORY_TICKET_CHAT = "\
                            SELECT \
                                json,t_id,app_ticket.operator as opername,uid,name,text,caption \
                            FROM \
                                app_telegrammsg \
                                INNER JOIN app_ticket ON app_ticket.id = app_telegrammsg.t_id \
                                INNER JOIN app_telegramuser ON app_ticket.user_id = app_telegramuser.id \
                            WHERE app_telegrammsg.t_id = {0}"

    HISTORY_MSG_FIX = "INSERT INTO app_chathistory(chat, user, message_id) VALUES ({0}, {1}, {2})"
    HISTORY_OF_USER = "SELECT * FROM app_chathistory where chat = {0} and user = {1}"
    HISTORY_CLEAR = "DELETE FROM app_chathistory WHERE chat = {0} and user = {0}"
    GET_USER_OF_TICKET = "SELECT\
                    app_ticket.id AS tid,\
                    app_telegramuser.uid AS uid \
                FROM\
                    app_ticket\
                    INNER JOIN app_telegramuser ON app_ticket.user_id = app_telegramuser.id \
                WHERE\
                    app_ticket.id = {0}"

    SET_TICKET_ADMIN = "UPDATE app_ticket SET operator = '{1}' WHERE id = {0}"

    LIST_NEW_TICKETS_NOTIF = 'select app_ticket.id as tid, app_ticket.status, app_ticket.dataClosed, app_ticket.dataCreated, app_ticket.description, app_ticket.operator, app_telegramuser.uid, app_telegramuser.name as username, app_atm.id as atm_id, app_atm.name as atm_name, app_atm.service_id from app_ticket inner join app_atm on app_atm.id = app_ticket.atm_id inner join app_telegramuser on app_telegramuser.id = app_ticket.user_id where app_ticket.status = 0'
    LIST_NOT_CLOSED_NOTIF = 'select app_ticket.id as tid, app_ticket.status, app_ticket.dataClosed, app_ticket.dataCreated, app_ticket.description, app_ticket.operator, app_telegramuser.uid, app_telegramuser.name as username, app_atm.id as atm_id, app_atm.name as atm_name, app_atm.service_id from app_ticket inner join app_atm on app_atm.id = app_ticket.atm_id inner join app_telegramuser on app_telegramuser.id = app_ticket.user_id where app_ticket.status in (0,3,4)'
    NOTIF_MONTH = 'SELECT COUNT(*) FROM app_ticket WHERE MONTH(app_ticket.dataCreated) = MONTH(NOW())'
    NOTIF_READ = 'SELECT COUNT(*) FROM app_ticket WHERE app_ticket.status not in (1,0,2,5)'
    NOTIF_NOT_OPEN = 'SELECT COUNT(*) FROM app_ticket WHERE app_ticket.status = 0'
    NOTIF_CLOSED = 'SELECT COUNT(*) FROM app_ticket WHERE app_ticket.status = 1'
    LIST_TICKETS_NOTIF = 'select app_ticket.id as tid, app_ticket.status, app_ticket.dataClosed, app_ticket.dataCreated, app_ticket.description, app_ticket.operator, app_telegramuser.uid, app_telegramuser.name as username, app_atm.id as atm_id, app_atm.name as atm_name, app_atm.service_id from app_ticket inner join app_atm on app_atm.id = app_ticket.atm_id inner join app_telegramuser on app_telegramuser.id = app_ticket.user_id'

    async def getTicketMessages(self, tid):
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute(self.GET_TICKET_MSG.format(tid))
                return await cur.fetchall()

    async def getBranchList(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute(self.MFO_LIST)
                return await cur.fetchall()

    async def setUserBranch(self, branch_id, user_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute(self.TG_USER_ACTIVATE.format(branch_id, user_id))
                return await cur.fetchall()

    async def getObjects(self, uid):
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute(self.GET_ATMS.format(uid))
                return await cur.fetchall()

    async def getProblems(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute(self.GET_PROBLEMS)
                return await cur.fetchall()

    async def addTicket(self, atmid, uid):
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute(self.CREATE_TICKET.format(atmid, uid))
                await cur.fetchone()
                return cur.lastrowid

    async def setTicketProblem(self, tid, pid):
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute(self.SET_TICKET_BROKEN.format(tid, pid))
                await cur.fetchone()
                return cur.lastrowid

    async def setTicketOperator(self, tid, name):
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute(self.SET_TICKET_ADMIN.format(tid, name))
                return await cur.fetchone()

    async def getStatsSummary(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                dt = {}

                await cur.execute(self.NOTIF_MONTH)
                t = await cur.fetchone()
                dt['month'] = t['COUNT(*)']

                await cur.execute(self.NOTIF_READ)
                t = await cur.fetchone()
                dt['read'] = t['COUNT(*)']

                await cur.execute(self.NOTIF_NOT_OPEN)
                t = await cur.fetchone()
                dt['news'] = t['COUNT(*)']

                await cur.execute(self.NOTIF_CLOSED)
                t = await cur.fetchone()
                dt['closed'] = t['COUNT(*)']
                # (number_of_rows,)= await cur.fetchone()

                # await cur.execute(self.LIST_NEW_TICKETS_NOTIF)
                # dt['list_new'] = await cur.fetchall()
                # await cur.execute(self.LIST_NOT_CLOSED_NOTIF)
                # dt['list'] = await cur.fetchall()
                await cur.execute(self.LIST_TICKETS_NOTIF)
                dt['list'] = await cur.fetchall()

                return {'list': dt['list'], 'month': dt['month'], 'read': dt['read'], 'news': dt['news'], 'closed': dt['closed']}
                # return cur.rowcount

    async def getTicketProblem(self, tid, pid):
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute(self.EXIST_TICKET_BROKEN.format(tid, pid))
                await cur.fetchall()
                # (number_of_rows,)= await cur.fetchone()
                return True if cur.rowcount > 0 else False
                # return cur.rowcount

    async def existTicketProblem(self, tid):
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute(self.EXIST_BROKEN.format(tid))
                await cur.fetchall()
                # (number_of_rows,)= await cur.fetchone()
                return True if cur.rowcount > 0 else False
                # return cur.rowcount

    async def deleteTicketProblem(self, tid, pid):
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute(self.REMOVE_TICKET_BROKEN.format(tid, pid))
                return await cur.fetchone()

    async def getUser(self, uid):
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute(self.GET_USER.format(uid))
                return await cur.fetchone()

    async def getTicketUID(self, tid):
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute(self.GET_USER_OF_TICKET.format(tid))
                tmp = await cur.fetchone()
                return tmp['uid']

    async def getEditTicket(self, uid, edited):
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute(self.GET_EDIT_TICKET.format(uid, edited))
                return await cur.fetchone()

    async def getUserStage(self, uid):
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute(self.GET_USER_STAGE.format(uid))
                tmp = await cur.fetchone()
                return tmp['stage']

    async def addUser(self, uid, name, json):
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute(self.GET_USER.format(uid))
                await cur.fetchall()
                if cur.rowcount > 0:
                    return False
                else:
                    await cur.execute(self.REGISTRATION.format(uid, name, json, 0))
                    await cur.fetchone()
                    return True

    async def getUserStatus(self, uid):
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute(self.GET_USER.format(uid))
                a = await cur.fetchone()
                return False if a['status'] == 0 else True

    async def setUserStage(self, uid, stage):
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute(self.SET_USER_STAGE.format(uid, stage))
                return await cur.fetchone()

    async def setEditTicket(self, tid, status):
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute(self.SET_EDIT_TICKET.format(tid, status))
                return await cur.fetchone()

    async def setStatusTicket(self, tid, status):
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute(self.SET_STATUS_TICKET.format(tid, status))
                return await cur.fetchone()

    async def checkCreateTicket(self, uid):
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute(self.CAN_CREATE_TICKET.format(uid))
                b = await cur.fetchone()
                # (number_of_rows,)= await cur.fetchone()
                return False if b['count'] > 0 else True
                # return await cur.fetchone()

#"INSERT INTO app_telegrammsg ( json, t_id, category, dt, path, download, operator, app_telegrammsg.show) VALUES ( '{0}', {1}, '{2}', NOW(), '{3}', {4}, {5}, {6} )"
    async def addTicketMessage(self, text, tid, category, path, download, operator, show, caption, text_msg):
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                # text_msg.replace('\'','\\\'')
                # await cur.mycursor.execute("INSERT INTO app_telegrammsg ( json, t_id, category, dt, path, download, operator, app_telegrammsg.show, caption, text) VALUES ( '{0}', {1}, '{2}', NOW(), '{3}', {4}, {5}, {6}, '{7}', binary(%s) );", (line,))
                field = self.ADD_MSG_FILE.format(
                    text, tid, category, path, download, operator, show)
                await cur.execute(field, (caption, text_msg,))
                return await cur.fetchone()

    async def addUserMessage(self, chatid, userid, messageid):
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                field = self.HISTORY_MSG_FIX.format(chatid, userid, messageid)
                await cur.execute(field)
                return await cur.fetchone()

    async def getTicket(self, tid):
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute(self.GET_TICKET_OF_ID.format(tid))
                return await cur.fetchone()

    async def getTicketMessages(self, tid):  # get_history
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute(self.HISTORY_TICKET_CHAT.format(tid))
                return await cur.fetchall()

    async def getUserMessages(self, chatid, userid):
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute(self.HISTORY_OF_USER.format(chatid, userid))
                return await cur.fetchall()

    async def deleteUserMessages(self, userid):
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute(self.HISTORY_CLEAR.format(userid))
                return await cur.fetchone()

    async def get_status(self, uid, status):
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                str_status = ''
                if status != 1:
                    str_status = '0,3,4'
                else:
                    str_status = '1'
                await cur.execute(self.GET_STATUS.format(uid, str_status))
                return await cur.fetchall()


cmd = DBCommands()
