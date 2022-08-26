### Main file used to dictate the 
### commands and controls for the bot

### Imports
import discord
import os
import search
import command_help
from dotenv import load_dotenv
from discord.ext import commands
import asyncio

### References from other files
command_helper = command_help.command_help_functions()
search_class = search.search_functions()

### Token from another file for security
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

### Bot and command prefix
bot = commands.Bot(command_prefix = '$')

#On bot startup
@bot.event
async def on_ready():
  print(f'{bot.user} is now online!') #Have the bot print it's ready when it comes online

#Personal command to see all servers the bot is in
@bot.command(name = 'list')
@commands.is_owner()
async def list_servers(ctx):
  guild_id = []
  guild_name = []
  for guild in bot.guilds: #Append guild names and ids to 2 seperate arrays
    guild_id.append(guild.id)
    guild_name.append(guild.name)
  await ctx.send(guild_id)
  await ctx.send(guild_name)
  #Print out the lists of servers and their ids

#Personal command to make the bot leave servers
@bot.command(name = 'leave')
@commands.is_owner()
async def leave(ctx, *, guild_name):
  guild = discord.utils.get(bot.guilds, name=guild_name) # Get the guild by name
  if guild is None:
      print("No guild with that name found.") # No guild found
      return
  await guild.leave() # Guild found
  await ctx.send(f"I left: {guild.name}!")

#Function for people to see the format of available commands
@bot.command(name = 'commands')
@commands.cooldown(rate=1, per=8)
async def help_list(ctx):
  embedVar = discord.Embed(title = 'Commands')
  embedVar.add_field(name = '$stats', value = '{username} {game mode (optional)}', inline = False)
  embedVar.add_field(name = '$session', value = '{username} {game mode (optional)}', inline = False)
  embedVar.add_field(name = '$vehicle', value = '{username} {game mode} {vehicle}', inline = False)
  embedVar.add_field(name = 'Cooldown', value = 'Bot has an 8 second cooldown!', inline = True)
  await ctx.send(embed = embedVar)

#Command to see either general or game mode specific statistics of a player
@bot.command(name = 'stats')
@commands.cooldown(rate=1, per=8)
async def search_stats(ctx, search_name, game_mode = ''):
  if game_mode == '': #If game mode is empty, then search up the general stats of the player
    numbers, time, squadron = search_class.search_general_stats(search_name)
    if numbers == []: #Error
      await ctx.send('No such person exists')
      return None
    formatted_outputAB, formatted_outputRB, formatted_outputSB = command_helper.general_stats_format(numbers)
    embedVar = discord.Embed(title = '{squadron_ls} {search_name_ls}'.format(search_name_ls = search_name, squadron_ls = squadron) + ' General Stats')
    embedVar.add_field(name = 'Arcade Stats', value = formatted_outputAB)
    embedVar.add_field(name = 'Realistic Stats', value = formatted_outputRB)
    embedVar.add_field(name = 'Simulator Stats', value = formatted_outputSB)
    embedVar.add_field(name = 'Last Update', value = time[0], inline = False)
    await ctx.send(embed = embedVar)
  if game_mode != '': #If game mode is not empty, then search up specific stats the player has in that game mode, along with their favorite vehicle
    numbers, stats, squadron, vehicle = search_class.search_gamemode_stats(search_name, game_mode)
    if numbers == []: #Error
      await ctx.send('No such person exists')
      return None
    if game_mode == 'AB':
        game_mode = 'Arcade Battles'
    if game_mode == 'RB':
        game_mode = 'Realistic Battles'
    if game_mode == 'SB':
        game_mode = 'Simulator Battles'
    embedVar = discord.Embed(title = '{squadron_ls} {search_name_ls}'.format(search_name_ls = search_name, squadron_ls = squadron))
    embedVar.add_field(name = game_mode, value = command_helper.detailed_stats_format(numbers))
    if vehicle == '':
      embedVar.add_field(name = 'Favorite Vehicle', value = 'Game mode not played enough')
    else:
      embedVar.add_field(name = 'Favorite Vehicle \n' + vehicle, value = command_helper.search_vehicle_format(stats))
    await ctx.send(embed = embedVar)

# Command to find the player's statistics in their last gaming session
@bot.command(name = 'session')
@commands.cooldown(rate=1, per=8)
async def search_session(ctx, search_name: str = None, game_mode: str = None):
  if game_mode == None: # If search type is empty, just bring up general last session stats
    result, gametype, squadron, custom_url = search_class.search_session(search_name)
    if result == []: # Error
      await ctx.send('No such person exists')
      return None
    if search_name == None: # Error
      await ctx.send('Error in input!')
      return None
    embedVar = discord.Embed(title = '{squadron_ls} {search_name_ls}'.format(search_name_ls = search_name, squadron_ls = squadron), url = '{url}'.format(url = custom_url))
    i = 0
    for item in gametype: # For each gamemode returned by the command (there are 3 max)
      embedVar.add_field(name = item, value = command_helper.last_session_format(result[i:i + 7]))
      i = i + 7
    await ctx.send(embed = embedVar)
  if game_mode != None:
    user_msg = ctx.message
    pages = []
    i = 0
    result, squadron, vehicles, custom_url = search_class.search_session_vehicles(search_name, game_mode)
    if result == []:
      await ctx.send('No updates!')
    for item in vehicles: # Create a new page in the embed for every vehicle that comes up from the search
      embedVar = discord.Embed(title = '{squadron_ls} {search_name_ls}'.format(search_name_ls = search_name, squadron_ls = squadron), url = '{url}'.format(url = custom_url))
      embedVar.add_field(name = '{item_ls}'.format(item_ls = item), value = command_helper.search_session_vehicle_format(result[i:i + 7]))
      i = i + 7
      pages.append(embedVar)
    index = 0
    buttons = ["◀️", "🛑", "▶️"] # Buttons used for pagination + deleting the embed
    message = await ctx.send(embed=pages[index])
    for button in buttons: # Add the buttons as reactions
      await message.add_reaction(button)
    while True: # While the message is present, define message pagination, lock pagination to original message sender, and time out the reactions after they are not touched for 60 seconds
      try:
        reaction, user = await bot.wait_for('reaction_add', check = lambda reaction, user: user == ctx.author and reaction.message == message and reaction.emoji in buttons, timeout = 60.0)
      except asyncio.TimeoutError:
        embed = pages[index]
        await message.clear_reactions()
      else:
        previous_page = index
        if reaction.emoji == "◀️":
          if index > 0:
            index -= 1
        elif reaction.emoji == "▶️":
          if index < len(pages)-1:
            index += 1
        elif reaction.emoji == "🛑":
          await message.delete()
          await user_msg.delete()
        for button in buttons:
          await message.remove_reaction(button, ctx.author)
        if index != previous_page:
          await message.edit(embed = pages[index])
    
# Caps sensitive command to search for vehicle specific statistics for a player
@bot.command(name = 'vehicle')
@commands.cooldown(rate=1, per=8)
async def search_vehicle(ctx, search_name: str = None, game_mode: str = None, *, search_vehicle: str = None):
  if search_name == None: # Error
    await ctx.send('Error in input!')
    return None
  if game_mode == None: # Error
    await ctx.send('Error in input!')
    return None
  if search_vehicle == None: # Error
    await ctx.send('Error in input!')
    return None
  user_msg = ctx.message
  result, vehicles, squadron, custom_url = search_class.search_vehicles(search_name, game_mode, search_vehicle)
  if result == []: # Error
      await ctx.send('Error!')
      return None
  pages = []
  i = 0
  for item in vehicles: #Create a new page in the embed for every vehicle that comes up from the search
    embedVar = discord.Embed(title = '{squadron_ls} {search_name_ls}'.format(search_name_ls = search_name, squadron_ls = squadron), url = '{url}'.format(url = custom_url))
    embedVar.add_field(name = '{item_ls}'.format(item_ls = item), value = command_helper.search_vehicle_format(result[i:i + 11]))
    i = i + 11
    pages.append(embedVar)
  index = 0
  buttons = ["◀️", "🛑", "▶️"] #Buttons used for pagination + deleting the embed
  message = await ctx.send(embed=pages[index])
  for button in buttons: #Add the buttons as reactions
    await message.add_reaction(button)
  while True: #While the message is present, define message pagination, lock pagination to original message sender, and time out the reactions after they are not touched for 60 seconds
    try:
      reaction, user = await bot.wait_for('reaction_add', check = lambda reaction, user: user == ctx.author and reaction.message == message and reaction.emoji in buttons, timeout = 60.0)
    except asyncio.TimeoutError:
      embed = pages[index]
      await message.clear_reactions()
    else:
      previous_page = index
      if reaction.emoji == "◀️":
        if index > 0:
          index -= 1
      elif reaction.emoji == "▶️":
        if index < len(pages)-1:
          index += 1
      elif reaction.emoji == "🛑":
        await message.delete()
        await user_msg.delete()
      for button in buttons:
        await message.remove_reaction(button, ctx.author)
      if index != previous_page:
        await message.edit(embed = pages[index])

bot.run(TOKEN)