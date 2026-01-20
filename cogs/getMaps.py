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


  def format_mode_name(self, mode):
    """Formatiert camelCase Mode Namen zu Title Case mit Leerzeichen"""
    # Füge Leerzeichen vor Großbuchstaben ein
    formatted = ""
    for i, char in enumerate(mode):
      if i > 0 and char.isupper():
        formatted += " "
      formatted += char
    # Erste Buchstabe groß, Rest wie es ist
    return formatted[0].upper() + formatted[1:]

  @tasks.loop(minutes=15)
  async def mapRota(self):
    mapRota = requests.get("https://api.brawlify.com/v1/events").json()["active"]
    
    embeds = {"active" : {"german" : [], "english" : [], "french" : [], "spanish" : [], "russian" : []},
               "upcoming" : {"german" : [], "english" : [], "french" : [], "spanish" : [], "russian" : []}}

    # Aktuelle Zeit für Vergleich
    now = datetime.datetime.now(datetime.timezone.utc)

    # Events nach active und upcoming trennen
    activeEvents = []
    upcomingEvents = []
    
    for event in mapRota:
      startTime = datetime.datetime.fromisoformat(event["startTime"].replace("Z", "+00:00"))
      endTime = datetime.datetime.fromisoformat(event["endTime"].replace("Z", "+00:00"))
      
      if startTime <= now < endTime:
        activeEvents.append(event)
      elif startTime > now:
        upcomingEvents.append(event)

    # Active Maps
    for language in embeds["active"]:
      for event in activeEvents:
        # Solo Showdown überspringen
        if event["map"]["gameMode"]["hash"] == "solo-showdown":
          continue
        
        # Mode Name verwenden (schon formatiert von API)
        eventName = event["map"]["gameMode"]["name"]
        
        embed = discord.Embed(title=event["map"]["name"], description=eventName)
        endTime = datetime.datetime.fromisoformat(event["endTime"].replace("Z", "+00:00"))
        
        # Verbleibende Zeit berechnen
        timeLeft = endTime - now
        hoursLeft = int(timeLeft.total_seconds() / 3600)
        minutesLeft = int((timeLeft.total_seconds() % 3600) / 60)
        
        if hoursLeft > 0:
          embed.description += f'\n{mapsTexts["ends"][language]} {hoursLeft}h {minutesLeft}m'
        else:
          embed.description += f'\n{mapsTexts["ends"][language]} {minutesLeft}m'
        
        # Set image (Map) und thumbnail (Environment/Game Mode)
        if event["map"].get("imageUrl"):
          embed.set_image(url=event["map"]["imageUrl"])
        if event["map"].get("environment") and event["map"]["environment"].get("imageUrl"):
          embed.set_thumbnail(url=event["map"]["environment"]["imageUrl"])
        
        embeds["active"][language].append(embed)
        if len(embeds["active"][language]) == 10:
          break

    # Upcoming Maps
    for language in embeds["upcoming"]:
      if not upcomingEvents:
        # Leeres Embed wenn keine upcoming Events
        embed = discord.Embed(title="No Upcoming Data", description="There are currently no upcoming events available.")
        embeds["upcoming"][language].append(embed)
      else:
        for event in upcomingEvents:
          # Solo Showdown überspringen
          if event["map"]["gameMode"]["hash"] == "solo-showdown":
            continue
          
          # Mode Name verwenden (schon formatiert von API)
          eventName = event["map"]["gameMode"]["name"]
          
          embed = discord.Embed(title=event["map"]["name"], description=eventName)
          startTime = datetime.datetime.fromisoformat(event["startTime"].replace("Z", "+00:00"))
          
          # Zeit bis Start berechnen
          timeUntil = startTime - now
          hoursUntil = int(timeUntil.total_seconds() / 3600)
          minutesUntil = int((timeUntil.total_seconds() % 3600) / 60)
          
          if hoursUntil > 0:
            embed.description += f'\n{mapsTexts["starts"][language]} {hoursUntil}h {minutesUntil}m'
          else:
            embed.description += f'\n{mapsTexts["starts"][language]} {minutesUntil}m'
          
          # Set image (Map) und thumbnail (Environment/Game Mode)
          if event["map"].get("imageUrl"):
            embed.set_image(url=event["map"]["imageUrl"])
          if event["map"].get("environment") and event["map"]["environment"].get("imageUrl"):
            embed.set_thumbnail(url=event["map"]["environment"]["imageUrl"])
          
          embeds["upcoming"][language].append(embed)
          if len(embeds["upcoming"][language]) == 10:
            break


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
