import json
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


#init file manager
data = {}
current_dir = 'root'
data[current_dir] = []
board_id = -1
CHANNEL_ID = -1



def create_board(info=""):
    """ Generates main page to display files and directories
    Args:
        info(str): you can choose a string to display in the information section (default is empty)
    """
    global current_dir
    borad_text = "💠 <b>current directory :</b> {0} \n\n".format(current_dir)
    for item in data[current_dir]:
        if item['type'] == 'dir':
            dir_name = item['name'].rsplit('/', 1)[1]
            borad_text += "📂 {0} \n".format(dir_name)
        else:
            borad_text += "🗄 {0}-{1}\n".format(item['name'],item['id'])

    return borad_text+"\n\n 💢 {0}".format(info)
        



def start(update: Update, context: CallbackContext) -> None:
    """Sends an empty board when the command /start is issued"""
    global board_id
    chat_id = update.message.chat_id

    clear_history(update, update.message.chat_id, update.message.message_id)
    board_id = update.message.bot.send_message(chat_id =chat_id ,text =create_board(),parse_mode=ParseMode.HTML).message_id
    



def list_items(update: Update, context: CallbackContext) -> None:
    """Lists items in current directory when the command /ls is issued"""
    global board_id
    global current_dir
    chat_id = update.message.chat_id
    clear_history(update, update.message.chat_id, update.message.message_id)
    update.message.bot.edit_message_text(chat_id = chat_id, message_id=board_id, text=create_board(),parse_mode=ParseMode.HTML)




def remove_file(update: Update, context: CallbackContext) -> None:
    """Removes specific file in the current directory when the command /rm is issued"""
    global board_id
    global current_dir
    chat_id = update.message.chat_id
    file_name = update.message.text.split(' ')[1]

    clear_history(update, update.message.chat_id, update.message.message_id)
    for i in range(len(data[current_dir])):
            if data[current_dir][i]['type'] == 'file' and data[current_dir][i]['id'] == file_name:
                    del data[current_dir][i]
                    break
    update.message.bot.edit_message_text(chat_id = chat_id, message_id=board_id, text=create_board(),parse_mode=ParseMode.HTML)




def remove_dir(update: Update, context: CallbackContext) -> None:
    """Removes specific directory in the current directory when the command /rmdir is issued"""
    global board_id
    global current_dir
    chat_id = update.message.chat_id
    dir_name = str(current_dir+'/'+update.message.text.split(' ')[1])

    clear_history(update, update.message.chat_id, update.message.message_id)
    if dir_name in data:
            del data[dir_name]
            for i in range(len(data[current_dir])):
                    if data[current_dir][i]['name'] == dir_name:
                            del data[current_dir][i]
                            break
    update.message.bot.edit_message_text(chat_id = chat_id, message_id=board_id, text=create_board(),parse_mode=ParseMode.HTML)




def create_directory(update: Update, context: CallbackContext) -> None:
    """Creates a new directory in the current directory when the command /rm is issued"""
    global current_dir
    global board_id
    chat_id = update.message.chat_id
    new_dir_name = update.message.text.split(' ')[1]
    dir_name = str(current_dir+'/'+new_dir_name)
    
    clear_history(update, update.message.chat_id, update.message.message_id)
    if dir_name in data:
            update.message.bot.edit_message_text(chat_id = chat_id, message_id=board_id, text=create_board(),parse_mode=ParseMode.HTML)
    else:
            data[dir_name] = []
            data[current_dir].append({
                                    'name': dir_name,
                                    'type' : 'dir'})
            update.message.bot.edit_message_text(chat_id = chat_id, message_id=board_id, text=create_board() ,parse_mode=ParseMode.HTML)



def change_directory(update: Update, context: CallbackContext) -> None:
    """Changes directory when the command /cd is issued"""
    global current_dir
    global board_id
    chat_id = update.message.chat_id
    destination_dir = update.message.text.split(' ')[1]
    previous_dir = current_dir.rsplit('/', 1)[0]
    
    clear_history(update, update.message.chat_id, update.message.message_id)
    if destination_dir == '.':
            current_dir = previous_dir
            update.message.bot.edit_message_text(chat_id = chat_id, message_id=board_id, text=create_board(),parse_mode=ParseMode.HTML)

    elif current_dir+'/'+destination_dir in data:
            current_dir = current_dir+'/'+destination_dir
            update.message.bot.edit_message_text(chat_id = chat_id, message_id=board_id, text=create_board(),parse_mode=ParseMode.HTML)
    else:
            update.message.bot.edit_message_text(chat_id = chat_id, message_id=board_id, text=create_board(),parse_mode=ParseMode.HTML)

    



def add_file(update: Update, context: CallbackContext) -> None:
    """Saves the received file"""
    global current_dir
    global CHANNEL_ID
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    file_id = update.message.bot.forward_message(CHANNEL_ID, from_chat_id=chat_id, message_id=message_id).message_id
    clear_history(update, update.message.chat_id, update.message.message_id)

    if update.message.audio:
        file_name = update.message.audio.file_name
    if update.message.document:
        file_name = update.message.document.file_name
    if update.message.video:
        file_name = update.message.video.file_name
    if update.message.voice:
        file_name = update.message.voice.file_unique_id

      
    data[current_dir].append({
                            'id'   : str(file_id),
                            'name' : file_name,
                            'type' : 'file'
                            })
    update.message.bot.edit_message_text(chat_id = chat_id, message_id=board_id, text=create_board(),parse_mode=ParseMode.HTML)
 



def get_files(update: Update, context: CallbackContext) -> None:
    """Sends specific file in the current directory when the command /get is issued"""
    global current_dir
    global CHANNEL_ID
    chat_id = update.message.chat_id
    file_name = update.message.text.split(' ')[1]
    clear_history(update, update.message.chat_id, update.message.message_id)

    for e in data[current_dir]:
        if e['type'] == 'file' and e['id'] == file_name:
            update.message.bot.forward_message(chat_id, from_chat_id=CHANNEL_ID, message_id=e['id'])
  


def clear_history(update, chat_id,message_id):
    """Clears received messages in chat"""
    update.message.bot.delete_message(chat_id=chat_id,message_id=message_id)
     


def main():
    """Starts the bot"""
    # Create the Updater and pass it your bot's token.
    updater = Updater("")

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
  
    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.all & ~Filters.command & ~Filters.text ,add_file))
    dispatcher.add_handler(MessageHandler(Filters.text ,clear_history))
    

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()