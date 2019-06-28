# Wumpus Hack
![wumpus](https://cdn.discordapp.com/attachments/594036341810135040/594036469987803157/wumpusos-removebg-preview.png)

Wumpus hack is a Discord bot made in python 3.6 that is a game all inside of discord. The bot simulates an operating system for each user called WumpOS. With WumpOS, you can send email, Buy PC parts, set up firewalls, mine crypto currency, connect to other user's PCs, hack other people's PCs, and steal their money, leave funny messages on your friend's PC, and much more.[official discord server](https://discord.gg/m75eCse)

# Table of contents
- [Team](#Team)
- [Setup](#Setup)
- [Commands](#Commands)
- [Configuration options](#Configuration-options)
- [License](#License)

## Team
Wumpus Hack has been developed by a team of four people.

1.) Polar#5893
-Programmer

2.) KAJ7#0001
-Programmer

3.) Larvey#0001
-Programmer

4.) Ita Ash#8916
-Graphic Designer


## Setup
You can do all these steps to run your own instance of WUmpusHack, or join a server with the Official bot and get right to hacking!
[official discord server](https://discord.gg/m75eCse)

1. Make sure you have python 3.6+
2. Close the repo, or download the .zip file.
3. open a terminal, and type `pip install -U discord.py` to install discord, and then `pip install Python-Trivia-API`
4. Download and get a MongoDB running, or use a free host (https://cloud.mongodb.com/)
5. Fill out the config.py, with a bot token, Mongo URI, prefix, and tick speed
6. open terminal, navigate to the directory with the bot, (cd <folder name>) and type `py bot.py`
7. add your bot account to a server, and start hacking away!

## Commands
#### All these commands are used in a DM with the bot, if not, msgs will be sent to DMs
`Connect` - Connects to another PC.

`Disonnect` - Disconnects from another PC.

`system editcm <msg>` - Edits your connection message.

`Github` - Sends a link to the github repository.

`Invite` - Sends a link to invite me.

`Login` - Logs onto your computer.

`Logout` - Logs out of your computer.

`Reset` - Resets all of your stats

`Support` - Sends an invite link to the support server.

`Breach` / Hack - Breach into someones computer/system.

`Print` - Print a message in your computers log.

`System / Stats / Sys` - Shows your system information.


### Government websites

`store.gov` - buy and upgrade your pc!

`help.gov` - this network.

`mail.gov` - see your inbox, and send messages.


## Configuration options
|var name|Description|
|------|-----------|
|TOKEN|The bot token|
|URI|the MongoDB URI string|
|PREFIX|the prefix(s) the bot will respond to|
|TICK_SPEED|how fast the bot gives money, and checks for cooldowns. (not recommended lower than 4)|

## License
WumpusHack - Copyright (C) 2019  WumpusHack Dev team

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see the [License](https://github.com/KAJdev/WumpusHack/blob/master/LICENSE).
