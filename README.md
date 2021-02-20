# Telegram File Manager Bot
[![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.png?v=103)](https://github.com/ellerbrock/open-source-badges/)
[![MIT Licence](https://badges.frapsoft.com/os/mit/mit.png?v=103)](https://opensource.org/licenses/mit-license.php)

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
