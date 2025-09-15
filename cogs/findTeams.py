from discord.ext import commands
import discord, requests, json
from discord import app_commands
from cogs.Utility import View, LinkButton
import mongodb
import asyncio

# EnvData laden
with open("data/env.json", "r", encoding="UTF-8") as f:
  envData = json.load(f)

# Emoji Listen laden
with open("data/modeEmojis.json", "r", encoding="UTF-8") as f:
  modeEmojis = json.load(f)

with open("data/esportEmojis.json", "r", encoding="UTF-8") as f:
  esportEmojis = json.load(f)

# Texte languages
with open("languages/findTeamsTexts.json", "r", encoding="UTF-8") as f:
  findTeamsTexts = json.load(f)

with open("languages/generalTexts.json", "r", encoding="UTF-8") as f:
   generalTexts = json.load(f)


gamemodeChoices = []
for i, gamemode in enumerate(modeEmojis, start=1):
  gamemodeChoices.append(app_commands.Choice(name=gamemode, value=i))


async def sendToAllGuilds(bot, interaction, categoryName, channelName, embeds, view, language):
  for i, guild in enumerate(bot.guilds, start=1):
    # Sprache suchen
    options = mongodb.findGuildOptions(guild.id)
    guildLanguage = options["language"]

    # Kategorie suchen
    category = None
    i = 0
    while not category and i < len(guild.categories):
      if categoryName in guild.categories[i].name.lower().replace(" ", ""):
        category = guild.categories[i]
      i += 1

    if not category:
      continue
          
    # Kanal suchen
    channel = None
    i = 0
    while not channel and i < len(category.text_channels):
      if channelName in category.text_channels[i].name.lower():
        channel = category.text_channels[i]
      i += 1

    
    # Nachricht posten wenn Kanal gefunden wurde
    if channel:
      await channel.send(embeds=embeds[guildLanguage], view=view)

    # Avoid Rate limiting
    await asyncio.sleep(5)

  await interaction.channel.send(findTeamsTexts["postSent"][language])

# Formular zum Ausfüllen, erstellt den Suchbeitrag
class FindMatesModalGerman(discord.ui.Modal):
  def __init__(self, bot, trophies, gameMode, language):
    super().__init__(title="Neue Team Suche erstellen")
    self.bot = bot
    self.trophies = trophies
    self.language = language
    self.gameMode = gameMode

  teamCode = discord.ui.TextInput(label="Team-Code", placeholder="X??????", style=discord.TextStyle.short, min_length=4, max_length=25)
  trophyRange = discord.ui.TextInput(label="Gewünschter Trophäenbereich", placeholder="z.B. 600-750", style=discord.TextStyle.short, max_length=11, required=False)
  region = discord.ui.TextInput(label="Region", placeholder="EMEA/NA/SA/APAC", style=discord.TextStyle.short, max_length=5, required=False)
  note = discord.ui.TextInput(label="Zusätzliche Informationen", placeholder="nur Leute mit Verstand bitte. Ich bin um 12:00 Uhr offline", style=discord.TextStyle.long, max_length=999, required=False)

  async def on_submit(self, interaction: discord.Interaction):
    await handleFindMatesSubmit(interaction, self.bot, self.gameMode.value, self.teamCode.value, self.trophyRange.value, self.region.value, self.note.value, self.trophies, self.language)

# Formulario para completar, crea la publicación de búsqueda
class FindMatesModalSpanish(discord.ui.Modal):
  def __init__(self, bot, trophies, gameMode, language):
    super().__init__(title="Publicar nueva consulta")
    self.bot = bot
    self.trophies = trophies
    self.language = language
    self.gameMode = gameMode

  teamCode = discord.ui.TextInput(label="Código de equipo", placeholder="X??????", style=discord.TextStyle.short, min_length=4, max_length=25)
  trophyRange = discord.ui.TextInput(label="Rango de trofeos deseado", placeholder="p. ej. 600-750", style=discord.TextStyle.short, max_length=11, required=False)
  region = discord.ui.TextInput(label="Región", placeholder="EMEA/NA/SA/APAC", style=discord.TextStyle.short, max_length=5, required=False)
  note = discord.ui.TextInput(label="Información adicional", placeholder="solo personas con cerebro por favor. Estaré fuera de línea a las 12:00", style=discord.TextStyle.long, max_length=999, required=False)

  async def on_submit(self, interaction: discord.Interaction):
    await handleFindMatesSubmit(interaction, self.bot, self.gameMode.value, self.teamCode.value, self.trophyRange.value, self.region.value, self.note.value, self.trophies, self.language)

# Formulaire à remplir, crée la publication de recherche
class FindMatesModalFrench(discord.ui.Modal):
  def __init__(self, bot, trophies, gameMode, language):
    super().__init__(title="Poster une nouvelle demande")
    self.bot = bot
    self.trophies = trophies
    self.language = language
    self.gameMode = gameMode

  teamCode = discord.ui.TextInput(label="Code d'équipe", placeholder="X??????", style=discord.TextStyle.short, min_length=4, max_length=25)
  trophyRange = discord.ui.TextInput(label="Plage de trophées souhaitée", placeholder="par exemple, 600-750", style=discord.TextStyle.short, max_length=11, required=False)
  region = discord.ui.TextInput(label="Région", placeholder="EMEA/NA/SA/APAC", style=discord.TextStyle.short, max_length=5, required=False)
  note = discord.ui.TextInput(label="Informations supplémentaires", placeholder="seulement les personnes ayant un cerveau s'il vous plaît. Je serai hors ligne à 12h00", style=discord.TextStyle.long, max_length=999, required=False)

  async def on_submit(self, interaction: discord.Interaction):
    await handleFindMatesSubmit(interaction, self.bot, self.gameMode.value, self.teamCode.value, self.trophyRange.value, self.region.value, self.note.value, self.trophies, self.language)

# Форма для заполнения, создающая поиск
class FindMatesModalRussian(discord.ui.Modal):
  def __init__(self, bot, trophies, gameMode, language):
    super().__init__(title="Опубликовать новый запрос")
    self.bot = bot
    self.trophies = trophies
    self.language = language
    self.gameMode = gameMode

  teamCode = discord.ui.TextInput(label="Код команды", placeholder="X??????", style=discord.TextStyle.short, min_length=4, max_length=25)
  trophyRange = discord.ui.TextInput(label="Желаемый диапазон трофеев", placeholder="например, 600-750", style=discord.TextStyle.short, max_length=11, required=False)
  region = discord.ui.TextInput(label="Регион", placeholder="EMEA/NA/SA/APAC", style=discord.TextStyle.short, max_length=5, required=False)
  note = discord.ui.TextInput(label="Дополнительная информация", placeholder="только люди с умом, пожалуйста. Я буду оффлайн в 12:00", style=discord.TextStyle.long, max_length=999, required=False)

  async def on_submit(self, interaction: discord.Interaction):
    await handleFindMatesSubmit(interaction, self.bot, self.gameMode.value, self.teamCode.value, self.trophyRange.value, self.region.value, self.note.value, self.trophies, self.language)

# Formular to fill out, creates the Search post
class FindMatesModalEnglish(discord.ui.Modal):
  def __init__(self, bot, trophies, gameMode, language):
    super().__init__(title="Post New Inquiry")
    self.bot = bot
    self.trophies = trophies
    self.language = language
    self.gameMode = gameMode

  teamCode = discord.ui.TextInput(label="Team Code", placeholder="X??????", style=discord.TextStyle.short, min_length=4, max_length=25)
  trophyRange = discord.ui.TextInput(label="Desired trophy range", placeholder="e.g. 600-750", style=discord.TextStyle.short, max_length=11, required=False)
  region = discord.ui.TextInput(label="Region", placeholder="EMEA/NA/SA/APAC", style=discord.TextStyle.short, max_length=5, required=False)
  note = discord.ui.TextInput(label="Additional Info", placeholder="only people with brain pls. Ill be offline at 12:00", style=discord.TextStyle.long, max_length=999, required=False)

  async def on_submit(self, interaction: discord.Interaction):
    await handleFindMatesSubmit(interaction, self.bot, self.gameMode, self.teamCode.value, self.trophyRange.value, self.region.value, self.note.value, self.trophies, self.language)

async def handleFindMatesSubmit(interaction, bot, gameMode, teamCode, trophyRange, region, note, trophies, language):
    await interaction.response.send_message(findTeamsTexts["sendingPosts"][language], ephemeral=True, delete_after=30)
    
    embeds = {"german" : [], "english" : [], "french" : [], "spanish" : [], "russian" : []}
    
    for embedlanguage in embeds:
      # Titel mit user name darunter die trophäen des users
      searchPost = f"## <a:Announcement:1216306085565042710> `{interaction.user}`\n"
      searchPost += f"<:Trophy:1223277455821902046> **{trophies}**\n"
      # Gamemode anheften
      if gameMode:
        searchPost += f"{modeEmojis[gameMode]} **{gameMode}**\n"
      
      
      # Trophy Range anheften
      if trophyRange:
        searchPost += f"<:list:1216305645083689111> **{trophyRange}**\n"
      # Region anheften
      if region:
        searchPost += f"<a:Global:1223361709729779896> **{region.upper()}**\n"
      # Team Code anheften
      searchPost += f"<:right_arrow:1216305900961271859> **{teamCode.upper()}**\n"
      # Notiz anheften
      if note:
        searchPost += f"### <:info:1216306156222287894> `{note}` <:info:1216306156222287894>"

      # Embed erstellen
      embed = discord.Embed(title="", description=searchPost, color=int("ffffff", 16))
      embed.set_author(name=findTeamsTexts["newInquiry"][embedlanguage], icon_url=interaction.user.display_avatar.url)
      embed.set_footer(text=findTeamsTexts["sentFrom"][embedlanguage].format(guild=interaction.guild), icon_url=interaction.guild.icon.url)

      embeds[embedlanguage].append(embed)

    JoinButton = LinkButton(findTeamsTexts["joinTeam"][language], f"https://link.brawlstars.com/invite/gameroom/en?tag={teamCode}", "<:BrawlStar:1216305064231174185>")

    await sendToAllGuilds(bot, interaction, "findmates", "find-mates", embeds, View([JoinButton]), language)


# Formulaire à remplir, crée la publication de recherche esport
class FindEsportModalFrench(discord.ui.Modal):
  def __init__(self, bot, language):
    super().__init__(title="Poster une nouvelle demande esport")
    self.bot = bot
    self.language = language

  position = discord.ui.TextInput(label="Recherche", placeholder="player/team/scrim/manager/analyst/coach", style=discord.TextStyle.short, min_length=4, max_length=10)
  region = discord.ui.TextInput(label="Région", placeholder="EMEA/NA/SA/APAC", style=discord.TextStyle.short, min_length=2, max_length=5, required=False)
  tier = discord.ui.TextInput(label="Niveau", placeholder="D/C/B/A/S/SS+", style=discord.TextStyle.short, min_length=1, max_length=3, required=False)
  note = discord.ui.TextInput(label="Informations supplémentaires", placeholder="doit parler anglais/devrait avoir x revenus", style=discord.TextStyle.paragraph, max_length=999, required=False)

  async def on_submit(self, interaction: discord.Interaction):
    await handleFindEsportSubmit(interaction, self.bot, self.position.value, self.region.value, self.tier.value, self.note.value, self.language)

# Форма для заполнения, создающая пост поиска электронного спорта
class FindEsportModalRussian(discord.ui.Modal):
  def __init__(self, bot, language):
    super().__init__(title="Создать новый запрос по электронному спорту")
    self.bot = bot
    self.language = language

  position = discord.ui.TextInput(label="Ищу", placeholder="player/team/scrim/manager/analyst/coach", style=discord.TextStyle.short, min_length=4, max_length=10)
  region = discord.ui.TextInput(label="Регион", placeholder="EMEA/NA/SA/APAC", style=discord.TextStyle.short, min_length=2, max_length=5, required=False)
  tier = discord.ui.TextInput(label="Уровень", placeholder="D/C/B/A/S/SS+", style=discord.TextStyle.short, min_length=1, max_length=3, required=False)
  note = discord.ui.TextInput(label="Дополнительная информация", placeholder="должен говорить по-английски/должен иметь доход x", style=discord.TextStyle.paragraph, max_length=999, required=False)

  async def on_submit(self, interaction: discord.Interaction):
    await handleFindEsportSubmit(interaction, self.bot, self.position.value, self.region.value, self.tier.value, self.note.value, self.language)

# Formulario para completar, crea la publicación de búsqueda de Esport
class FindEsportModalSpanish(discord.ui.Modal):
  def __init__(self, bot, language):
    super().__init__(title="Publicar nueva consulta de Esport")
    self.bot = bot
    self.language = language

  position = discord.ui.TextInput(label="Buscando", placeholder="player/scrim/team/manager/analyst/coach", style=discord.TextStyle.short, min_length=4, max_length=10)
  region = discord.ui.TextInput(label="Región", placeholder="EMEA/NA/SA/APAC", style=discord.TextStyle.short, min_length=2, max_length=5, required=False)
  tier = discord.ui.TextInput(label="Nivel", placeholder="D/C/B/A/S/SS+", style=discord.TextStyle.short, min_length=1, max_length=3, required=False)
  note = discord.ui.TextInput(label="Información adicional", placeholder="debe hablar inglés/debería tener x ingresos", style=discord.TextStyle.paragraph, max_length=999, required=False)

  async def on_submit(self, interaction: discord.Interaction):
    await handleFindEsportSubmit(interaction, self.bot, self.position.value, self.region.value, self.tier.value, self.note.value, self.language)

# Formular zum Ausfüllen, erstellt den Suchbeitrag für Esport
class FindEsportModalGerman(discord.ui.Modal):
  def __init__(self, bot, language):
    super().__init__(title="Neue Esport-Suche veröffentlichen")
    self.bot = bot
    self.language = language

  position = discord.ui.TextInput(label="Suche nach", placeholder="player/scrim/team/manager/analyst/coach", style=discord.TextStyle.short, min_length=4, max_length=10)
  region = discord.ui.TextInput(label="Region", placeholder="EMEA/NA/SA/APAC", style=discord.TextStyle.short, min_length=2, max_length=5, required=False)
  tier = discord.ui.TextInput(label="Tier", placeholder="D/C/B/A/S/SS+", style=discord.TextStyle.short, min_length=1, max_length=3, required=False)
  note = discord.ui.TextInput(label="Zusätzliche Informationen", placeholder="muss Englisch sprechen/sollte x Einnahmen haben", style=discord.TextStyle.paragraph, max_length=999, required=False)

  async def on_submit(self, interaction: discord.Interaction):
    await handleFindEsportSubmit(interaction, self.bot, self.position.value, self.region.value, self.tier.value, self.note.value, self.language)

# Formular to fill out, creates the Search post
class findEsportModalEnglish(discord.ui.Modal):
  def __init__(self, bot, language):
    super().__init__(title="Post New Esport Inquiry")
    self.bot = bot
    self.language = language

  position = discord.ui.TextInput(label="Searching for", placeholder="player/scrim/team/manager/analyst/coach", style=discord.TextStyle.short, min_length=4, max_length=10)
  region = discord.ui.TextInput(label="Region", placeholder="EMEA/NA/SA/APAC", style=discord.TextStyle.short, min_length=2, max_length=5, required=False)
  tier = discord.ui.TextInput(label="Tier", placeholder="D/C/B/A/S/SS+", style=discord.TextStyle.short, min_length=1, max_length=3, required=False)
  note = discord.ui.TextInput(label="Additional Info", placeholder="must speak english/should have x earnings", style=discord.TextStyle.paragraph, max_length=999, required=False)

  async def on_submit(self, interaction: discord.Interaction):
    await handleFindEsportSubmit(interaction, self.bot, self.position.value, self.region.value, self.tier.value, self.note.value, self.language)

async def handleFindEsportSubmit(interaction, bot, position, region, tier, note, language):
    # Positions Validität prüfen
    if not position.lower() in ["manager", "coach", "analyst" ,"player", "team", "scrim"]:
      return await interaction.response.send_message(findTeamsTexts["unknownPosition"][language].format(pos=position.capitalize()), ephemeral=True, delete_after=3)
      
    await interaction.response.send_message(findTeamsTexts["sendingPosts"][language], ephemeral=True, delete_after=10)

    embeds = {"german" : [], "english" : [], "french" : [], "spanish" : [], "russian" : []}

    for embedlanguage in embeds:
      # Titel mit user name
      searchPost = f"## <a:Announcement:1216306085565042710> `{interaction.user}`\n"
      
      # Gesuchtes Position anheften
      searchPost += f"🔎 **{position.upper()}** {esportEmojis[position.lower()]}\n"
      
      # Region anheften
      if region:
        searchPost += f"<a:Global:1223361709729779896> **{region.upper()}**\n"
      # Tier anheften
      tier = tier.upper()
      if tier:
        if tier in ["D", "C", "B", "A", "S", "SS+"]:
          searchPost += f"{esportEmojis[tier]} **TIER**\n"
      # Notiz anheften
      if note:
        searchPost += f"### <:info:1216306156222287894> `{note}` <:info:1216306156222287894>"

      # Embed bauen
      embed = discord.Embed(title="", description=searchPost, color=int("ffffff", 16))
      embed.set_author(name=findTeamsTexts["newEsportInquiry"][embedlanguage], icon_url=interaction.user.display_avatar.url)
      embed.set_footer(text=findTeamsTexts["sentFrom"][embedlanguage].format(guild=interaction.guild), icon_url=interaction.guild.icon.url)

      embeds[embedlanguage].append(embed)

    
    await sendToAllGuilds(bot, interaction, "findmates", "find-esport", embeds, None, language)


# The Commands
class findTeams(commands.Cog):

  def __init__(self, bot):
    self.bot = bot


  # Team Suche Quick
  @app_commands.command(description="post a new quick search")
  @app_commands.checks.cooldown(1, 60*5, key=lambda i: (i.user.id))
  async def quick_mates(self, interaction: discord.Interaction, team_code: str, info: str=None, bs_id: str=None):
    # Ausgewählte Sprache fetchen
    options = mongodb.findGuildOptions(interaction.guild.id)
    language = options["language"]
    
    # Nutzer Id fetchen
    user_options = mongodb.findUserOptions(interaction.user.id)
    bs_id = user_options["bs_id"]

    if not bs_id:
      return await interaction.response.send_message(generalTexts["noIdGiven"][language], ephemeral=True, delete_after=60)
    
    bs_id = bs_id.upper().replace(" ", "").replace("#", "")
    url = f"https://api.brawlstars.com/v1/players/%23{bs_id}"
    headers = {
        "Authorization": f"Bearer {envData['BsApi']}"
    }
    profileData = requests.get(url, headers=headers).json()

    if "trophies" in profileData:
      await interaction.response.send_message(findTeamsTexts["sendingPosts"][language], ephemeral=True, delete_after=10)
    
      embeds = {"german" : [], "english" : [], "french" : [], "spanish" : [], "russian" : []}
      
      for embedlanguage in embeds:
        # Titel mit user name darunter die trophäen des users
        searchPost = f"## <a:Announcement:1216306085565042710> `{interaction.user}`\n"
        searchPost += f"<:Trophy:1223277455821902046> **{profileData['trophies']}**\n"
        
        # Team Code anheften
        searchPost += f"<:right_arrow:1216305900961271859> **{team_code.upper()}**\n"
        # Notiz anheften
        if info:
          searchPost += f"### <:info:1216306156222287894> `{info}` <:info:1216306156222287894>"

        # Embed erstellen
        embed = discord.Embed(title="", description=searchPost, color=int("ffffff", 16))
        embed.set_author(name=findTeamsTexts["newInquiry"][embedlanguage], icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text=findTeamsTexts["sentFrom"][embedlanguage].format(guild=interaction.guild), icon_url=interaction.guild.icon.url)

        embeds[embedlanguage].append(embed)

      JoinButton = LinkButton(findTeamsTexts["joinTeam"][language], f"https://link.brawlstars.com/invite/gameroom/en?tag={team_code}", "<:BrawlStar:1216305064231174185>")

      await sendToAllGuilds(self.bot, interaction, "findmates", "find-mates", embeds, View([JoinButton]), language)
    else:
      await interaction.response.send_message(findTeamsTexts["noProfileFound"][language].format(bs_id = bs_id), ephemeral=True, delete_after=3)

  @quick_mates.error
  async def quick_mates_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(str(error), ephemeral=True)


  # allgemeine Team Suche
  @app_commands.command(description="post a new casual inquiry")
  @app_commands.choices(game_mode=gamemodeChoices)
  @app_commands.checks.cooldown(1, 60*5, key=lambda i: (i.user.id))
  async def find_mates(self, interaction: discord.Interaction, game_mode: app_commands.Choice[int]=None, bs_id: str=None):
    # Ausgewählte Sprache fetchen
    options = mongodb.findGuildOptions(interaction.guild.id)
    language = options["language"]

    # Nutzer Id fetchen
    user_options = mongodb.findUserOptions(interaction.user.id)
    bs_id = user_options["bs_id"]

    if not bs_id:
      return await interaction.response.send_message(generalTexts["noIdGiven"][language], ephemeral=True, delete_after=60)
    

    bs_id = bs_id.upper().replace(" ", "").replace("#", "")
    url = f"https://api.brawlstars.com/v1/players/%23{bs_id}"
    headers = {
        "Authorization": f"Bearer {envData['BsApi']}"
    }
    profileData = requests.get(url, headers=headers).json()

    if "trophies" in profileData:
      if game_mode:
        gameMode = game_mode.name
      else:
        gameMode = ""
      if language == "german":
        await interaction.response.send_modal(FindMatesModalGerman(self.bot, profileData["trophies"], gameMode, language))
      elif language == "english":
        await interaction.response.send_modal(FindMatesModalEnglish(self.bot, profileData["trophies"], gameMode, language))
      elif language == "spanish":
        await interaction.response.send_modal(FindMatesModalSpanish(self.bot, profileData["trophies"], gameMode, language))
      elif language == "russian":
        await interaction.response.send_modal(FindMatesModalRussian(self.bot, profileData["trophies"], gameMode, language))
      else:
        await interaction.response.send_modal(FindMatesModalFrench(self.bot, profileData["trophies"], gameMode, language))
    else:
      await interaction.response.send_message(findTeamsTexts["noProfileFound"][language].format(bs_id = bs_id), ephemeral=True, delete_after=3)

  @find_mates.error
  async def find_mates_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(str(error), ephemeral=True)


  # Esport Team Suche Command
  @app_commands.command(description="post a new esport inquiry")
  @app_commands.checks.cooldown(1, 60*5, key=lambda i: (i.user.id))
  async def find_esport(self, interaction: discord.Interaction):
    # Ausgewählte Sprache fetchen
    options = mongodb.findGuildOptions(interaction.guild.id)
    language = options["language"]

    if language == "german":
      await interaction.response.send_modal(FindEsportModalGerman(self.bot, language))
    elif language == "english":
      await interaction.response.send_modal(findEsportModalEnglish(self.bot, language))
    elif language == "spanish":
      await interaction.response.send_modal(FindEsportModalSpanish(self.bot, language))
    elif language == "russian":
      await interaction.response.send_modal(FindEsportModalRussian(self.bot, language))
    else:
      await interaction.response.send_modal(FindEsportModalFrench(self.bot, language))

  @find_esport.error
  async def find_esport_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(str(error), ephemeral=True)


  # Esport Team Suche Command
  @app_commands.command(description="remove your latest search posts")
  @app_commands.checks.cooldown(1, 60*5, key=lambda i: (i.user.id))
  async def cancel_search(self, interaction: discord.Interaction):
    # Ausgewählte Sprache fetchen
    options = mongodb.findGuildOptions(interaction.guild.id)
    language = options["language"]

    await interaction.response.send_message(findTeamsTexts["cancelStart"][language], ephemeral=True, delete_after=30)
    for guild in self.bot.guilds:
      # Kategorie suchen
      findMatesCategory = None
      i = 0
      while not findMatesCategory and i < len(guild.categories):
        if "FINDMATES" in guild.categories[i].name.upper().replace(" ", ""):
          findMatesCategory = guild.categories[i]
        i += 1

      if not findMatesCategory:
        continue
            
      # Kanäle erstmal finden
      findMatesChannel = None
      findEsportChannel = None
      i = 0
      while (not findMatesChannel or not findEsportChannel) and i < len(findMatesCategory.text_channels):
        if "find-mates" in findMatesCategory.text_channels[i].name.lower():
          findMatesChannel = findMatesCategory.text_channels[i]
        elif "find-esport" in findMatesCategory.text_channels[i].name.lower():
          findEsportChannel = findMatesCategory.text_channels[i]
        i += 1

      for channel in [findMatesChannel, findEsportChannel]:
        if channel:
          messages = [message async for message in channel.history(limit=25)]
          # Iteriere über letzte 25 Nachrichten und suche User Post
          msgdeleted = False
          i = 0
          if messages:
            while i < len(messages) and not msgdeleted:
              if messages[i].embeds:
                if messages[i].embeds[0].author.icon_url == interaction.user.display_avatar.url:
                  await messages[i].delete()
                  msgdeleted = True
              i += 1


    await interaction.edit_original_response(content=findTeamsTexts["cancelSuccessful"][language])

  @cancel_search.error
  async def cancel_search_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(str(error), ephemeral=True)

async def setup(bot):
  await bot.add_cog(findTeams(bot))
