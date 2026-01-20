from discord.ext import commands, tasks
import discord, requests, datetime, json, asyncio
import mongodb

icons = requests.get("https://api.brawlapi.com/v1/icons").json()

format = "%d.%m.%Y, %H:%M"

with open("languages/mapsTexts.json", "r", encoding="UTF-8") as f:
   mapsTexts = json.load(f)

# ENV Daten laden
with open("data/env.json", "r", encoding="UTF-8") as f:
  envData = json.load(f)
  
class getMaps(commands.Cog):
  
  def __init__(self, bot):
    self.bot = bot
    self.mapRota.start()


  @tasks.loop(minutes=15)
  async def mapRota(self):
    headers = {
      "Authorization": f"Bearer {envData['BsApi']}"
    }
    mapRota = requests.get("https://api.brawlstars.com/v1/events/rotation", headers=headers).json()
    
    embeds = {"active" : {"german" : [], "english" : [], "french" : [], "spanish" : [], "russian" : []},
               "upcoming" : {"german" : [], "english" : [], "french" : [], "spanish" : [], "russian" : []}}

    # Aktuelle Zeit für Vergleich
    now = datetime.datetime.now(datetime.timezone.utc)

    # Events nach active und upcoming trennen
    activeEvents = []
    upcomingEvents = []
    
    for event in mapRota:
      startTime = datetime.datetime.strptime(event["startTime"], "%Y%m%dT%H%M%S.%fZ").replace(tzinfo=datetime.timezone.utc)
      endTime = datetime.datetime.strptime(event["endTime"], "%Y%m%dT%H%M%S.%fZ").replace(tzinfo=datetime.timezone.utc)
      
      if startTime <= now < endTime:
        activeEvents.append(event)
      elif startTime > now:
        upcomingEvents.append(event)

    # Active Maps
    for language in embeds["active"]:
      for event in activeEvents:
        # Solo Showdown überspringen
        if event["event"]["mode"] == "soloShowdown":
          continue
        
        # Mode Name formatieren
        eventName = event["event"]["mode"]
        
        embed = discord.Embed(title=event["event"]["map"], description=eventName)
        endTime = datetime.datetime.strptime(event["endTime"], "%Y%m%dT%H%M%S.%fZ").replace(tzinfo=datetime.timezone.utc)
        embed.description += f'\n{mapsTexts["ends"][language]} {endTime.strftime(format)} UTC'
        embeds["active"][language].append(embed)
        if len(embeds["active"][language]) == 10:
          break
      
      if embeds["active"][language]:
        embeds["active"][language][-1].set_footer(text=mapsTexts["footer"][language].format(lastUpdate=datetime.datetime.now().strftime(format)))

    # Upcoming Maps
    for language in embeds["upcoming"]:
      for event in upcomingEvents:
        # Solo Showdown überspringen
        if event["event"]["mode"] == "soloShowdown":
          continue
        
        # Mode Name formatieren
        eventName = event["event"]["mode"]
        
        embed = discord.Embed(title=event["event"]["map"], description=eventName)
        startTime = datetime.datetime.strptime(event["startTime"], "%Y%m%dT%H%M%S.%fZ").replace(tzinfo=datetime.timezone.utc)
        embed.description += f'\n{mapsTexts["starts"][language]} {startTime.strftime(format)} UTC'
        embeds["upcoming"][language].append(embed)
        if len(embeds["upcoming"][language]) == 10:
          break

      if embeds["upcoming"][language]:
        embeds["upcoming"][language][-1].set_footer(text=mapsTexts["footer"][language].format(lastUpdate=datetime.datetime.now().strftime(format)))


    for guild in self.bot.guilds:
      # Sprache suchen
      options = mongodb.findGuildOptions(guild.id)
      language = options["language"]
            
      # Kanal suchen
      currentMapsChannel = None
      nextMapsChannel = None
      
      i = 0
      while (not currentMapsChannel or not nextMapsChannel) and i < len(guild.text_channels):
        if "current-maps" in guild.text_channels[i].name.lower():
          currentMapsChannel = guild.text_channels[i]
        elif "next-maps" in guild.text_channels[i].name.lower():
          nextMapsChannel = guild.text_channels[i]
        i += 1

      if currentMapsChannel:
        messages = [message async for message in currentMapsChannel.history()]
        if not messages:
          await currentMapsChannel.send(f'# {mapsTexts["activeMapsTitle"][language]}', embeds=embeds["active"][language])
        for msg in messages:
            if msg.author != self.bot.user:
                await msg.delete()
            else:
                await msg.edit(content=f'# {mapsTexts["activeMapsTitle"][language]}', embeds=embeds["active"][language])
                break

      if nextMapsChannel:
        messages = [message async for message in nextMapsChannel.history()]
        if not messages:
          await nextMapsChannel.send(f'# {mapsTexts["upcomingMapsTitle"][language]}', embeds=embeds["upcoming"][language])
        for msg in messages:
            if msg.author != self.bot.user:
                await msg.delete()
            else:
                await msg.edit(content=f'# {mapsTexts["upcomingMapsTitle"][language]}', embeds=embeds["upcoming"][language])
                break
      await asyncio.sleep(10)


async def setup(bot):
  await bot.add_cog(getMaps(bot))
