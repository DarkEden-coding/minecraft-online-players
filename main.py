import discord
from discord.ext import tasks
from discord import app_commands
from mcstatus import JavaServer
import time

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

last_update_players = []

server_address = "numbereater.com"
status_channel = 1179990041494294648
log_channel = 1179991971234848860
debug_channel = 1180938049480310804
guild_id = 1176557788491685908


def send_error_message(error):
    user = client.fetch_user(806281289040396288)
    client.get_channel(debug_channel).send(f"Error: {str(error)} {user.mention}")


def get_server_info():
    while True:
        try:
            server = JavaServer.lookup(server_address)
            query = server.query()
            status = server.status()
            online_players = status.players.online
            return online_players, query.players.names
        except Exception as e:
            send_error_message(e)


# Function to update the client's status message
async def update_client_status():
    online_players, specific_players = get_server_info()
    await client.change_presence(
        activity=discord.Game(name=f"{online_players} players online")
    )


async def player_log_logs():
    global last_update_players

    _, specific_players = get_server_info()

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
    online_players, specific_players = get_server_info()
    specific_players = ", ".join(specific_players)
    message_content = f"The server has {online_players} players online\nThe server has the following players online: {specific_players}"

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
    guild=discord.Object(id=guild_id),
)  # Add the guild ids in which the slash command will appear. If it should be in all, remove the argument,
# but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def online_players(ctx):
    online_players, specific_players = get_server_info()
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
    await tree.sync(guild=discord.Object(id=guild_id))
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
client.run("MTE3OTU3OTkwOTQwOTA5NTczMQ.GYq1ws.IP9snYfpr9TK0oMywv-Zlmfbu_HII9nFGwMaCM")
