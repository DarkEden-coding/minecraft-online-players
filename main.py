import discord
from discord.ext import tasks
from discord import app_commands
from mcstatus import JavaServer
import time
from constants import discord_bot_token

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

last_update_players = []

server_address = "numbereater.com"
status_channel = 1179990041494294648
log_channel = 1179991971234848860
debug_channel = 1180938049480310804


async def send_error_message(error):
    await client.get_channel(debug_channel).send(f"Error: {str(error)}")


async def get_server_info():
    while True:
        try:
            server = JavaServer.lookup(server_address)
            query = server.query()
            status = server.status()
            online_players = status.players.online
            # check to make sure the objects are the correct types
            check = (online_players, query.players.names)
            try:
                assert isinstance(check, tuple)
                assert isinstance(check[0], int)
                assert isinstance(check[1], list)
            except AssertionError as e:
                await send_error_message(e)
                continue
            return online_players, query.players.names
        except Exception as e:
            await send_error_message(e)
            return 0, []


# Function to update the client's status message
async def update_client_status():
    online_players, specific_players = await get_server_info()
    await client.change_presence(
        activity=discord.Game(name=f"{online_players} players online")
    )


async def player_log_logs():
    global last_update_players

    _, specific_players = await get_server_info()

    # Find the strings in list1 that are not in list2
    difference1 = [item for item in specific_players if item not in last_update_players]

    for player in difference1:
        await client.get_channel(log_channel).send(
            f"{player} has logged into the server!"
        )

    # Find the strings in list2 that are not in list1
    difference2 = [item for item in last_update_players if item not in specific_players]

    for player in difference2:
        await client.get_channel(log_channel).send(
            f"{player} has logged out of the server"
        )

    last_update_players = specific_players


async def update_online_message():
    channel = client.get_channel(status_channel)
    online_players, specific_players = await get_server_info()
    specific_players = ", ".join(specific_players)
    message_content = f"The server has {online_players} players online\nThe server has the following players online: {specific_players}".strip()

    # send message to debug channel, uses current time and date
    await client.get_channel(debug_channel).send(
        f"Online players updated at {time.strftime('%H:%M:%S %d/%m/%Y')}"
    )

    # Check if a previous message exists
    existing_message = None
    async for message in channel.history(limit=None):
        if message.author == client.user:
            existing_message = message
            break

    # If a previous message exists, update it; otherwise, send a new message
    if existing_message:
        # check if the existing message text is the same as the new message text
        if existing_message.content != message_content:
            # delete the existing message and send a new one
            await existing_message.delete()
            await channel.send(message_content)
    else:
        await channel.send(message_content)


@tree.command(
    name="online-players",
    description="Gets the online players",
)  # Add the guild ids in which the slash command will appear. If it should be in all, remove the argument,
# but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def online_players(ctx):
    online_players, specific_players = await get_server_info()
    specific_players = ", ".join(specific_players)
    print(f"The server has {online_players} players online")
    print(f"The server has the following players online: {specific_players}")
    await ctx.response.send_message(
        f"The server has {online_players} players online\nThe server has the "
        f"following players online: {specific_players}"
    )


# Bot event: When the client is ready
@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user.name}")
    # Start a background task to update the status every minute
    update_client.start()


# Schedule the update_client_status function to run every minute
@tasks.loop(minutes=0.08)
async def update_client():
    await update_client_status()
    await update_online_message()
    await player_log_logs()


# Start the client with your client token
client.run(discord_bot_token)
