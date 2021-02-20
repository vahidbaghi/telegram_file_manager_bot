# Telegram File Manager Bot
 [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Introduction
Telegram gives you unlimited storage for your files. But it is difficult to categorize and manage files. 
This Telegram bot lets you categorize your files in telegram. When you send a file to the bot, it stores it on a private telegram channel that you created and retrieves it when you need it.

## Usage
To get started, you'll need a Telegram API Access Token, and you can get it here [@BotFather](https://t.me/botfather). Then, replace "TOKEN" with your token :
```
  # Create the Updater and pass it your bot's token.
    updater = Updater("TOKEN")
```
In order to save and retrieve files in a channel, first create a (private) channel in Telegram and then make the bot the channel admin. Then follow [this instruction](https://gist.github.com/mraaroncruz/e76d19f7d61d59419002db54030ebe35) to find the channel ID and paste it into CHANNEL_ID :
```
CHANNEL_ID = -100 # Shows the channel ID
```

| Commmand                           | Description                                                                                                                      |
| -----------------------------------|--------------------------------------------------------------------------------------------------------------------------------- |
| /start                             | Starts the bot and displays the main board  |
| /mkdir "directory name"            | Creates a directory named <directory name> in the current directory |
| /cd "directory name"               | Changes directory to <directory name>|
| /rm [-r] "file name"               | Removes <filename> file in the current list. The -r option allows you to use regular expressions|
| /rmdir [-r] "directory name"       | Removes <directory name> directory in the current list. The -r option allows you to use regular expressions|
| /get [-r] "file nmae or file id"   | Gets a specified file by <file name> or <file id> from the current directory. The -r option allows you to use regular expressions|
| /rnf "old name" "new name"         | Renames a specifed file <old name> to <new name>|
| /rnd "old name" "new name"         | Renames a specifed directory <old name> to <new name>|


## Installation

Clone the repository:

```
git clone https://github.com/vahidbaghi/telegram_file_manager_bot.git
cd telegram_file_manager_bot-main
```

Install dependencies

```
pip install -r requirements.txt
```
Run
```
python bot.py
```
## License

The project is available as open source under the terms of the [MIT License](https://opensource.org/licenses/MIT).
