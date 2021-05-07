import discord
import logging
import miniupnpc

logging.basicConfig(level=logging.INFO)

login_token = None
with open("token.secret") as creds:
    login_token = creds.readline().strip()

if login_token is None:
    logging.log("Failed to load token")

client = discord.Client()


async def send_message(message, channel):
    try:
        await channel.send(message)
    except Exception as e:
        logging.error("Caught exception sending message", e)


async def get_ip(channel):
    try:
        upnp_client = miniupnpc.UPnP()
        upnp_client.discoverdelay = 200
        upnp_client.discover()
        upnp_client.selectigd()
        await send_message(f"The server is currently located at `{upnp_client.externalipaddress()}:2567`", channel)
    except Exception as e:
        logging.error("Could not obtain IP Address", e)
        await send_message(
            "I'm sorry, I could not obtain the current IP address of the server. There may be an internet outage in "
            "Cambridge.",
            channel
        )


async def process_command(message, command, args):
    if command == "ip":
        await get_ip(message.channel)
    else:
        await usage(message.channel)


async def usage(channel):
    await send_message("I bring tidings!\nI am the bot you can use to get information about this server. As of now" +
                       "you can use the following commands:\n```" +
                       "help - display this information\n" +
                       "ip - discover the ip address of the server\n" +
                       "```",
                       channel
                       )


@client.event
async def on_ready():
    logging.info(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('/hugin'):
        parts = message.content.split(' ')
        if len(parts) < 2:
            await usage(message.channel)
            return
        command = parts[1].strip()

        args = []
        if len(parts) > 2:
            args = map(lambda p: p.strip(), parts[2:])

        await process_command(message, command, args)


client.run(login_token)
