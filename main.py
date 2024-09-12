import discord
from discord import ClientException
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

youtube_dl.utils.bug_reports_message = lambda: ''

queue = []

# Options for yt-dlp
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')


@bot.command(name='hello', help="Steve says hello")
async def hello(ctx):
    await ctx.send('Hi! I am Steve.')


@bot.command(name='question', help='Type your questions')
async def question(ctx, *, query):
    responses = {
        "question 1": "answer 1",
        "question 2": "answer 2",
        "question 3": "answer 3",
        "question 4": "answer 4",
    }

    response = responses.get(query.lower(), "I don't have an answer to this question")
    await ctx.send(response)


@bot.command(name='ping', help="Check if the bot is online")
async def ping(ctx):
    await ctx.send('Pong!')


@bot.command(name='say', help='Make the bot say something')
async def say(ctx, *, message):
    await ctx.send(message)


@bot.command(name='play', help='Steve plays the song')
async def play(ctx, url):
    try:
        voice_channel = ctx.author.voice.channel
    except AttributeError:
        await ctx.send("You must be in the voice channel!")
        return

    if not ctx.voice_client:
        await voice_channel.connect()

    def check_queue(error):
        if len(queue) > 0:
            next_song = queue.pop(0)
            ctx.voice_client.play(next_song, after=check_queue)
            bot.loop.create_task(ctx.send(f'Now playing: {next_song.title}'))
        elif error:
            print(f'Player error: {error}')

    try:
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)

            if ctx.voice_client.is_playing():
                queue.append(player)
                await ctx.send(f'Now something else is playing. {player.title} will be played later.')
            else:
                ctx.voice_client.play(player, after=check_queue)
                await ctx.send(f'Now playing: {player.title}')
    except ClientException as e:
        await ctx.send(f'Error: {str(e)}')


@bot.command(name='skip', help='Skip the song')
async def skip(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        if not len(queue) == 0:
            await ctx.send("The song was skipped.")
        else:
            await ctx.send("You don't have any songs in the queue. Steve can't play anything.")
            await ctx.voice_client.disconnect()


@bot.command(name='stop', help='Disconnect the bot')
async def stop(ctx):
    await ctx.send("Steve is off.")
    await ctx.voice_client.disconnect()


@bot.command(name='queue', help='Check the queue')
async def stop(ctx):
    await ctx.send('Your queue:')
    for song in queue:
        await ctx.send(f'{song.title}')


bot.run('your_token')
