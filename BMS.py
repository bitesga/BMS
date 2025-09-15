import os, discord, json
from discord.ext import commands
from cogs.Utility import View, LinkButton, buildLanguageEmbed
import mongodb
import asyncio

# Texte languages
with open("languages/findTeamsTexts.json", "r", encoding="UTF-8") as f:
  findTeamsTexts = json.load(f)

with open("languages/generalTexts.json", "r", encoding="UTF-8") as f:
   generalTexts = json.load(f)
   
class BMates(commands.Bot):
  
  def __init__(self, intents):
    super().__init__(command_prefix="-------", intents=intents, activity=discord.Activity(type=discord.ActivityType.playing, name="with good mates"))
    

  async def on_ready(self):
    print("Bot rasiert alles")
    for f in os.listdir('./cogs'):
      if f.endswith('.py'):
        await bot.load_extension(f'cogs.{f[:-3]}')
    await self.tree.sync()


  async def on_guild_join(self, guild: discord.guild):
    options = mongodb.findGuildOptions(guild.id)
    language = options["language"]
    
    # Only Read permission definieren
    onlyRead = {
      guild.default_role: discord.PermissionOverwrite(send_messages=False),
    }
    
    await asyncio.sleep(3)

    # Map Rota Kanäle erstellen 
    try:            
      # Kanäle suchen
      currentMapsChannel = None
      nextMapsChannel = None
      i = 0
      while (not currentMapsChannel or not nextMapsChannel) and i < len(guild.text_channels):
        if "current-maps" in guild.text_channels[i].name.lower():
          currentMapsChannel = guild.text_channels[i]
        elif "next-maps" in guild.text_channels[i].name.lower():
          nextMapsChannel = guild.text_channels[i]
        i += 1

      # Erstellen und eine Nachricht senden falls nicht vorhanden
      if not currentMapsChannel:
        currentMapsChannel = await guild.create_text_channel("current-maps", overwrites=onlyRead, topic="Active Maps!")
        await currentMapsChannel.send(generalTexts["currentSoon"][language])
      if not nextMapsChannel:
        nextMapsChannel = await guild.create_text_channel("next-maps", overwrites=onlyRead, topic="Predicted Upcoming Maps!")
        await nextMapsChannel.send(generalTexts["upcomingSoon"][language])
      

      # Find Mates Kanäle erstellen
      
      # Kategorie erstmal finden
      findMatesCategory = None
      i = 0
      while not findMatesCategory and i < len(guild.categories):
        if "findmates" in guild.categories[i].name.lower().replace(" ", ""):
          findMatesCategory = guild.categories[i]
        i += 1

      # Erstellen falls nicht da
      if not findMatesCategory:
        findMatesCategory = await guild.create_category_channel("Find Mates")

      # Kanäle erstmal finden
      findMatesChannel = None
      teamInquiriesChannel = None
      findEsportChannel = None
      i = 0
      while (not findMatesChannel or not teamInquiriesChannel or not findEsportChannel) and i < len(findMatesCategory.text_channels):
        if "find-mates" in findMatesCategory.text_channels[i].name.lower():
          findMatesChannel = findMatesCategory.text_channels[i]
        elif "team-inquiries" in findMatesCategory.text_channels[i].name.lower():
          teamInquiriesChannel = findMatesCategory.text_channels[i]
        elif "find-esport" in findMatesCategory.text_channels[i].name.lower():
          findEsportChannel = findMatesCategory.text_channels[i]
        i += 1

      if not findMatesChannel:
        findMatesChannel = await findMatesCategory.create_text_channel("find-mates", overwrites=onlyRead, topic="find a team to join here")
      if not findEsportChannel:
        findEsportChannel = await findMatesCategory.create_text_channel("find-esport", overwrites=onlyRead, topic="find an esport team or players here")
      if not teamInquiriesChannel:
        teamInquiriesChannel = await findMatesCategory.create_text_channel("team-inquiries", topic="run /find_mates to post your search!")

        await teamInquiriesChannel.send(embed=buildLanguageEmbed("findTeamsAnnouncement", language))

      
      systemChannel = guild.system_channel
      if systemChannel:
        await systemChannel.send(embed=buildLanguageEmbed("welcome", language), view=View([LinkButton("Linktree", "https://linktr.ee/bsystems", "<:Linktree:1218980236260278292>")]))
    except:
      pass
      

intents = discord.Intents.default()
bot = BMates(intents=intents)
with open("data/env.json", "r") as f:
  env = json.load(f)
bot.run(env['TOKEN'])

