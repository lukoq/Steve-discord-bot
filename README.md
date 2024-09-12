# Steve-discord-bot

A bot that allows you to play youtube videos on your discord server.

## Commands

* !hello - Steve says hello.
* !help - Shows the help message.
* !ping - Check if the bot is online.
* !play - Steve plays the song.
* !question - Type your questions.
* !say - Make the bot say something.
* !skip - Skip the song.
* !stop - Disconnect the bot.

## Getting Started

### Setting up your bot

* Sign in [Discord's developers portal](https://discord.com/developers)
* Create a new application
* Generate an authorisation token and paste it into the bottom of your _main.py_ file
```
bot.run('your_token')
```
* Navigate to to the "OAuth2" page
* In the "OAuth2 URL Generator" section select the "application.command" and "bot" checkboxes
* Under the "Bot Permissions" part, check "Send Messages", "Connect" and "Speak"
* Copy the URL that got generated and paste it into your browser, then select your server from the dropdown and complete the captcha.
* Then run your code
