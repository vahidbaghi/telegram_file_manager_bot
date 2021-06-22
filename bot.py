import json
from telegram import Update, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, Bot
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import sqlite3
import re


# Initialize root directory
data = {}
MAIN_DIR_NAME = 'root' # 
current_dir = MAIN_DIR_NAME
data[current_dir] = []

board_id = -1  # Initialized By sending the /start command
CHANNEL_ID = -100  # Shows the channel ID (https://bit.ly/2NbJAHD)
sent_messages_id = []  # Holds the ID of the messages sent by the bot

def create_board():
    """ Generate main page to display files and directories)"""
    global current_dir

    sql = "SELECT name, type, id FROM info WHERE parent = ?"
    rows = do_sql_query(sql,[current_dir],is_select_query=True)
    borad_text = "💠 {0} \n\n".format(current_dir)
    num_files = 0
    num_dirs = 0
    for row in rows:
        if row[1] == 'dir':
            borad_text += "📂 {0} \n".format(row[0])
            num_dirs+=1
        else:
            borad_text += "🗄 {0}-{1}\n".format(row[2], row[0])
            num_files+=1

    return borad_text+"\n\n💢 {0} Files , {1} Dirs".format(num_files,num_dirs)


def get_inline_keyboard():
    """Return Inline Keyboard"""
    keyboard = [
    [
        InlineKeyboardButton("❇️ Home", callback_data='home_button'),
        InlineKeyboardButton("🔙 Back", callback_data='back_button'),
    ],
    [InlineKeyboardButton("🗑 Clear History", callback_data='clear_history')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def do_sql_query(query, values, is_select_query = False, has_regex = False):
    """ Connects to the database, executes the query, and returns results, if any.s
    Args:
        query(str): query to execute
        values(list): a list of parameters in the query
        is_select_query(boolean): Indicates whether the sent query is 'select query' or not
        has_regex(boolean): Indicates whether the sent query contains regex or not
    """
    try:
        conn = sqlite3.connect('Data.db')
        if has_regex:
            conn.create_function("REGEXP", 2, regexp)
        cursor = conn.cursor()
        cursor.execute(query,values)
        if is_select_query:
            rows = cursor.fetchall()
            return rows
    finally:
        conn.commit()
        cursor.close()
    


def start(update: Update, context: CallbackContext) -> None:
    """Send an empty board when the command /start is issued"""
    global board_id
    chat_id = update.message.chat_id
    clear_history(update, update.message.chat_id, update.message.message_id)
    update.message.bot.send_message(chat_id=chat_id, text=create_board(), parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard()).message_id
    board_id = update.message.bot.send_message(chat_id=chat_id, text=create_board(), parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard()).message_id


def list_items(update: Update, context: CallbackContext) -> None:
    """List items in current directory when the command /ls is issued"""
    global board_id
    global current_dir
    chat_id = update.message.chat_id
    clear_history(update, update.message.chat_id, update.message.message_id)
    update.message.bot.edit_message_text(chat_id=chat_id, message_id=board_id, text=create_board(
    ), parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard())


def remove_file(update: Update, context: CallbackContext) -> None:
    """Remove specific file in the current directory when the command /rm is issued"""
    global board_id
    global current_dir
    chat_id = update.message.chat_id
    message_text = update.message.text
    dir_name = message_text.split("-r")[1].strip() if len(message_text.split("-r"))>=2 else ' '.join(message_text.split(" ")[1:]).strip()
    clear_history(update, update.message.chat_id, update.message.message_id)
    
    if len(message_text.split("-r"))>=2:
        sql = "DELETE FROM info WHERE parent = ? AND type = 'file' AND ( name REGEXP ? OR id REGEXP ?)"
        values = [current_dir,dir_name,dir_name]
    else:
        sql = "DELETE FROM info WHERE parent = ? AND type = 'file' AND ( name = ? OR id = ?)"
        values = [current_dir,dir_name,dir_name]
    do_sql_query(sql,values,has_regex=True)

    update.message.bot.edit_message_text(chat_id=chat_id, message_id=board_id, text=create_board(), parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard())
        

def regexp(regex, expression):
    """ Receives an expression and specifies if it matches the received regex or not
    Args:
        regex(str): sent regex
        expression(str): The expression sent to check if it matches the regex
    """
    try:
        return True if re.match(regex,expression) else False
    except Exception as e:
        return False


def remove_dir(update: Update, context: CallbackContext) -> None:
    """Remove specific directory in the current directory when the command /rmdir is issued"""
    global board_id
    global current_dir
    chat_id = update.message.chat_id
    message_text = update.message.text
    dir_name = message_text.split("-r")[1].strip() if len(message_text.split("-r"))>=2 else ' '.join(message_text.split(" ")[1:]).strip()

    clear_history(update, update.message.chat_id, update.message.message_id)

    
    if len(message_text.split("-r"))>=2:
        sql = "DELETE FROM info WHERE name REGEXP ? AND parent = ? AND type = 'dir'"
        values = [dir_name,current_dir]
    else:
        sql = "DELETE FROM info WHERE name = ? AND parent = ? AND type = 'dir'"
        values = [dir_name,current_dir]
    do_sql_query(sql,values,has_regex=True)

    update.message.bot.edit_message_text(chat_id=chat_id, message_id=board_id, text=create_board(
    ), parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard())


def is_directory_exists(dir_name):
    """ Determines if the directory name sent exists in the current directory
    Args:
        dir_name(str): directory name
    """
    global current_dir
    
    sql = "SELECT COUNT(*) FROM info WHERE name = ? AND parent = ?"
    values = [dir_name,current_dir]
    count = do_sql_query(sql,values,is_select_query=True)[0]
    return True if int(count[0])>0 else False


def create_directory(update: Update, context: CallbackContext) -> None:
    """Create a new directory in the current directory when the command /rm is issued"""
    global current_dir
    global board_id
    chat_id = update.message.chat_id
    new_dir_name = ' '.join(update.message.text.split(' ')[1:])

    clear_history(update, update.message.chat_id, update.message.message_id)
    if is_directory_exists(new_dir_name):
        update.message.bot.edit_message_text(chat_id=chat_id, message_id=board_id, text=create_board(), parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard())
    else:
        sql = "INSERT INTO info (parent, name, type, id) VALUES (?,?,?,?)"
        values = [current_dir,new_dir_name,"dir","null"]
        do_sql_query(sql,values)
        update.message.bot.edit_message_text(chat_id=chat_id, message_id=board_id, text=create_board(), parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard())


def change_directory(update: Update, context: CallbackContext) -> None:
    """Change directory when the command /cd is issued"""
    global current_dir
    global board_id
    chat_id = update.message.chat_id
    destination_dir = ' '.join(update.message.text.split(' ')[1:])
    previous_dir = current_dir.rsplit('/', 1)[0]

    clear_history(update, update.message.chat_id, update.message.message_id)
    if destination_dir == '.':
        current_dir = previous_dir
        update.message.bot.edit_message_text(chat_id=chat_id, message_id=board_id, text=create_board(
        ), parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard())

    elif is_directory_exists(destination_dir):
        current_dir = current_dir+'/'+destination_dir
        update.message.bot.edit_message_text(chat_id=chat_id, message_id=board_id, text=create_board(
        ), parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard())
    else:
        update.message.bot.edit_message_text(chat_id=chat_id, message_id=board_id, text=create_board(
        ), parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard())

def get_file_name(update):
    if update.message.text:
            year = str(update.message.date.year)
            month = str(update.message.date.month)
            day = str(update.message.date.day)
            return  "(Text Message)-"+year+"/"+month+"/"+day
    elif update.message.audio:
        return  update.message.audio.file_name
    elif update.message.document:
        return  update.message.document.file_name
    elif update.message.video:
        return  update.message.video.file_name
    elif update.message.voice:
        return  update.message.voice.file_unique_id
    elif update.message.photo:
        # The best quality of an image is selected when several different qualities are available
        return  update.message.photo[len(
            update.message.photo)-1].file_unique_id


def add_file(update: Update, context: CallbackContext) -> None:
    """Save the received file"""
    global current_dir
    global board_id
    global CHANNEL_ID

    chat_id = update.message.chat_id
    message_id = update.message.message_id
    file_id = update.message.bot.forward_message(CHANNEL_ID, from_chat_id=chat_id, message_id=message_id).message_id

    clear_history(update, update.message.chat_id, update.message.message_id)
    
    # For messages forwarded from channels or from anonymous administrators, information about the original sender chat.
    if update.message.forward_from_chat:
        name = update.message.forward_from_chat.username if update.message.forward_from_chat.username else update.message.forward_from_chat.title
        file_name =  name+"-"+get_file_name(update)
    # For forwarded messages, sender of the original message.
    elif update.message.forward_from:
        file_name = update.message.forward_from.username +"-"+get_file_name(update)
    # Sender’s name for messages forwarded from users who disallow adding a link to their account in forwarded messages.
    elif update.message.forward_sender_name:
        file_name = update.message.forward_sender_name +"-"+get_file_name(update)
    # Sender, empty for messages sent to channels.
    elif update.message.from_user:
        file_name = update.message.from_user.username +"-"+get_file_name(update)
    else:
        file_name = get_file_name(update)


    sql = "INSERT INTO info (parent, name, type, id) VALUES (?,?,?,?)"
    values = [current_dir,file_name,"file",str(file_id)]
    do_sql_query(sql,values)

    update.message.bot.edit_message_text(chat_id=chat_id, message_id=board_id, text=create_board(), parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard())



def rename_file(update: Update, context: CallbackContext) -> None:
    """Rename specific file in the current directory when the command /rename is issued"""
    global current_dir
    global board_id

    chat_id = update.message.chat_id
    old_name = update.message.text.split(' ')[1]
    new_name = update.message.text.split(' ')[2]
    clear_history(update, update.message.chat_id, update.message.message_id)

    sql = "UPDATE info SET name = ? WHERE type = 'file' AND  (name = ? OR id = ?)"
    values = [new_name,old_name,old_name]
    do_sql_query(sql,values)

    update.message.bot.edit_message_text(chat_id=chat_id, message_id=board_id, text=create_board(
    ), parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard())


def rename_dir(update: Update, context: CallbackContext) -> None:
    """Rename specific directory in the current directory when the command /rename is issued"""
    global current_dir
    global board_id

    chat_id = update.message.chat_id
    recieved_params = update.message.text[5:]
    old_name = recieved_params.split(",")[0]
    new_name = recieved_params.split(",")[1]
    clear_history(update, update.message.chat_id, update.message.message_id)

    sql = "UPDATE info SET name = ? WHERE type = 'dir' AND  name = ?"
    values = [new_name,old_name]
    do_sql_query(sql,values)

    update.message.bot.edit_message_text(chat_id=chat_id, message_id=board_id, text=create_board(), parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard())


def is_desired_name(query, item_name="", item_id=""):
    return re.match(query.split("-r")[0], item_name) if '-r' in query else item_id == query or item_name == query


def get_files(update: Update, context: CallbackContext) -> None:
    """Send specific file in the current directory when the command /get is issued"""
    global current_dir
    global CHANNEL_ID
    chat_id = update.message.chat_id
    message_text = update.message.text
    dir_name = message_text.split("-r")[1].strip() if len(message_text.split("-r"))>=2 else ' '.join(message_text.split(" ")[1:]).strip()
    
    clear_history(update, update.message.chat_id, update.message.message_id)


    if len(message_text.split("-r"))>=2:
        sql = "SELECT id FROM info WHERE parent = ? AND type = 'file' AND ( name REGEXP ? OR id REGEXP ?)"
        values = [current_dir,dir_name,dir_name]
    else:
        sql = "SELECT id FROM info WHERE parent = '"+current_dir+"' AND type = 'file' AND ( name = '"+dir_name+"' OR id = '"+dir_name+"')"
        values = [current_dir,dir_name,dir_name]
    file_ids = do_sql_query(sql,values,is_select_query=True,has_regex=True)

    for id in file_ids:
         message_id = update.message.bot.forward_message(chat_id, from_chat_id=CHANNEL_ID, message_id=id[0]).message_id
         sent_messages_id.append(message_id)


def clear_history(update, chat_id, message_id):
    """Clears received messages in chat"""
    update.message.bot.delete_message(chat_id=chat_id, message_id=message_id)


def clear_illegal_commands(update: Update, context: CallbackContext) -> None:
    """Clears illegal messages and commands in chat"""
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    update.message.bot.delete_message(chat_id=chat_id, message_id=message_id)


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    """Arranges buttons in the Inline keyboard"""
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


def Inline_buttons(update: Update, context: CallbackContext) -> None:
    """Responses to buttons clicked in the inline keyboard"""
    query = update.callback_query
    chat_id = query.message.chat_id
    global current_dir

    if query.data == 'clear_history':
        if len(sent_messages_id) > 0:
            for mid in sent_messages_id:
                clear_history(query, chat_id, mid)
            sent_messages_id.clear()
            query.answer(text='Items removed!')
        else:
            query.answer(text='There is no item to remove!')

    elif query.data =='back_button':
        previous_dir = current_dir.rsplit('/', 1)[0]
        current_dir = previous_dir
        update.callback_query.edit_message_text(text=create_board(), parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard())
        query.answer(text=current_dir)

    elif query.data == 'home_button':
        current_dir = MAIN_DIR_NAME
        update.callback_query.edit_message_text(text=create_board(), parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard())
        query.answer(text=MAIN_DIR_NAME)


def main():
    """Starts the bot"""
    # Create the Updater and pass it your bot's token.
    updater = Updater("TOKEN")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("mkdir", create_directory))
    dispatcher.add_handler(CommandHandler("cd", change_directory))
    dispatcher.add_handler(CommandHandler("rm", remove_file))
    dispatcher.add_handler(CommandHandler("rmdir", remove_dir))
    dispatcher.add_handler(CommandHandler("ls", list_items))
    dispatcher.add_handler(CommandHandler("get", get_files))
    dispatcher.add_handler(CommandHandler("rnf", rename_file))
    dispatcher.add_handler(CommandHandler("rnd", rename_dir))

    dispatcher.add_handler(MessageHandler(
        Filters.all & ~Filters.command, add_file))
    dispatcher.add_handler(MessageHandler(
        Filters.text | Filters.command, clear_illegal_commands))
    dispatcher.add_handler(CallbackQueryHandler(Inline_buttons))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
