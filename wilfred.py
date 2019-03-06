# -*- coding: utf-8 -*-
import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import time
from discord.voice_client import VoiceClient
import _thread as thread
import random

#time.sleep(30) #Give Server time to init networking [Since this is now being autoran under SystemD] 
token = ""
buildVersion = "060319.In-Dev"

from secrets import * #Token will be stored in here so I don't accidentally leak the admin token for my Discord again...

#color schemes
primary = 0x55FF55
secondary = 0x04bfbf
reds = 0xf93b3b


Loop = False
isLooped = False

raffles = False
enteries = [] #Please for the love of god can we find a better way of doing this

training = []
battleInProgress = False

gate =  440205836208439348
casual = 473276007860797453

disabled_commands = [] #
rCooldowns = []
admin_bypass = [513115137184366597]
cooldown = []
ignore_list = []

Client = discord.Client()
bot_prefix = "!"
client = commands.Bot(command_prefix=bot_prefix, case_insensitive=True)
client.remove_command("help")

#-----Helpers-----

#"/home/pi/varsity-discord/"+

def execute_query(table, query):
    conn = sqlite3.connect("/home/rsa-key-20190102/"+table)
    #conn = sqlite3.connect(table)
    c = conn.cursor()
    c.execute(query)
    conn.commit()
    c.close()
    conn.close()

def db_query(table, query):
    conn = sqlite3.connect("/home/rsa-key-20190102/"+table)
    #conn = sqlite3.connect(table)
    c = conn.cursor()
    c.execute(query)
    result = c.fetchall()
    c.close()
    conn.close()
    return result

def cinfo(text): #Info Level Log Output
    print("[" +str(time.ctime()) +"] [INFO] " +text)

def cwarn(text): #Warn Level Log Output
    print("[" +str(time.ctime()) +"] [WARNING] " +text)

def cerror(text): #Error Level Log Output
    print("[" +str(time.ctime()) +"] [ERROR] " +text)

def cdebug(text): #Error Level Log Output
    print("[" +str(time.ctime()) +"] [DEBUG] " +text)  

async def error(reason, channel, details=None):
    em = discord.Embed(title="Error", description="An error occurred when attempting to perform that request. Please check the Syntax and try again.\nError: `%s`" % reason, colour=0xFF5555)
    msg = await channel.send(embed=em)

async def warn(reason, channel, details=None):
    em = discord.Embed(title="Warning", description="The command produced the following warning: `%s`" % reason, colour=reds)
    msg = await channel.send(embed=em)

#<@&511270956983910401>

#-----Permissions-----
async def hasPerms(level, ctx, *, giveOutput = True):
    perms = False

    if level <= 32:
        if 440208840269758484 in [role.id for role in ctx.author.roles]:
            return True
        else:
            if giveOutput:
                output=discord.Embed(title="Insufficient Permissions", description="This command requires permission group <@&440208840269758484>", colour=reds)
            perms = False
            
    if level <= 16:
        if 511270956983910401 in [role.id for role in ctx.author.roles]:
            return True
        else:
            if giveOutput:
                output=discord.Embed(title="Insufficient Permissions", description="This command requires permission group <@&511270956983910401>", colour=reds)
            perms = False

    if level <= 6:
        if 515995445537931275 in [role.id for role in ctx.author.roles]:
            return True
        else:
            if giveOutput:
                output=discord.Embed(title="Insufficient Permissions", description="This command requires permission group <@&515995445537931275>", colour=reds)
            perms = False

    if level <= 5:
        if 515995448918540358 in [role.id for role in ctx.author.roles]:
            return True
        else:
            if giveOutput:
                output=discord.Embed(title="Insufficient Permissions", description="This command requires permission group <@&515995448918540358>", colour=reds)
            perms = False


    if level <= 4:
        if 515995451518877697 in [role.id for role in ctx.author.roles]:
            return True
        else:
            if giveOutput:
                output=discord.Embed(title="Insufficient Permissions", description="This command requires permission group <@&515995451518877697>", colour=reds)
            perms = False            

    if level <= 3:
        if 515995453632806928 in [role.id for role in ctx.author.roles]:
            return True
        else:
            if giveOutput:
                output=discord.Embed(title="Insufficient Permissions", description="This command requires permission group <@&515995453632806928>", colour=reds)
            perms = False        

    if level <= 2:
        if 515995454274535455 in [role.id for role in ctx.author.roles]:
            return True
        else:
            if giveOutput:
                output=discord.Embed(title="Insufficient Permissions", description="This command requires permission group <@&515995454274535455>", colour=reds)
            perms = False

    if level <= 1:
        if 484495458602057730 in [role.id for role in ctx.author.roles]:
            return True
        else:
            if giveOutput:
                output=discord.Embed(title="Insufficient Permissions", description="This command requires permission group <@&484495458602057730>", colour=reds)
            perms = False
        
    if giveOutput and not perms:
        await ctx.channel.send(embed=output)

    return perms    
      
#-----Processing-----
    
import sqlite3

def insert_db_user(member):
    try:
        execute_query("varsity.db", "INSERT INTO Members (UserID) VALUES ('%s')" % (member.id))
    except:
        cwarn("User already exists in Database")
        try:
            cinfo(member.name)
        except:
            pass
        
def give_item(item, member):
    items_current = fetch_items(member.id)[0][0]
    if items_current is None:
        items_new = item+"_"
    else:    
        items_new = items_current + item +"_"
    execute_query("varsity.db", "UPDATE Members SET items = '%s' WHERE UserID = %s" % (items_new, str(member.id)))

def balance_formatter(balance):
    cBalance = "{:,}".format(balance)
    sBalance = cBalance.split(",")
    if len(sBalance) == 0:
        return str(balance)
    elif len(sBalance) == 2:
        sign = "K"
    elif len(sBalance) == 3:
        sign = "M"
    elif len(sBalance) == 4:
        sign = "B"
    elif len(sBalance) == 5:
        sign = "T"
    elif len(sBalance) >= 6:
        sign = "Q"
    fBalance = sBalance[0] + "." + sBalance[1][0:2] + sign
    return fBalance
    
    
    
def set_coins(user, coins):
    user_id = user.id
    execute_query("varsity.db", "UPDATE Members SET Balance = %s WHERE UserID = %s" % (str(coins), str(user_id)))

def set_coins_id(user_id, coins):
    execute_query("varsity.db", "UPDATE Members SET Balance = %s WHERE UserID = %s" % (str(coins), str(user_id)))
    
def fetch_items(userID):
    return db_query("varsity.db", "SELECT items FROM Members WHERE UserID = %s" % (str(userID)))

def fetch_coins(user):
    user_id = user.id
    coins = db_query("varsity.db", "SELECT Balance FROM Members WHERE UserID = %s" % (str(user_id)))[0][0]
    return coins

def fetch_coins_id(user_id):
    coins = db_query("varsity.db", "SELECT Balance FROM Members WHERE UserID = %s" % (str(user_id)))[0][0]
    return coins

def add_coins(user, amount):
    current_coins = fetch_coins(user)
    new_coins = int(current_coins) + int(amount)
    set_coins(user, new_coins)

def add_coins_id(user_id, amount):
    current_coins = fetch_coins_id(user_id)
    new_coins = int(current_coins) + int(amount)
    set_coins_id(user_id, new_coins)    

def get_profile(userID):
    profile = db_query("varsity.db", "SELECT Balance, Level, expTotal, Badges, profileColour, profileHashtag, exp, statAtk, statDef, statHp FROM Members WHERE UserID = %s" % (userID))[0]
    return profile

def level_up(userID, level):
    execute_query("varsity.db", "UPDATE Members SET Level = %s WHERE UserID = %s" % (str(level), str(userID)))   

async def check_level_up(userID, guild, channel):
    Checking = True 
    while Checking: 
        level_data = db_query("varsity.db", "SELECT Exp, Level FROM Members WHERE UserID = %s" % (str(userID)))[0]
        Exp = level_data[0]
        lvl = level_data[1]
        Required = 5 * (lvl * lvl) + (50 * lvl) + 100
        if Exp >= Required:
            level_up(userID, lvl+1)
            sub_exp_only(userID, Required)
            lvl = lvl+1
            if lvl == 10:
                new_role = discord.utils.get(guild.roles, name="Uber Regular")
                user = discord.utils.get(guild.members, id=userID)
                await user.add_roles(new_role)
                add_coins(user, 10000)
                await channel.send(embed=discord.Embed(title="Level Up!", description="Congratulations %s! You've reached Level 10! That means you've unlocked the `Uber Regular` role! You've also been awarded $10000 for your achievement!" % (user.mention), color=0xF1C40F))  
            if lvl == 20:
                new_role = discord.utils.get(guild.roles, name="Outstandingly Regular")
                user = discord.utils.get(guild.members, id=userID)
                await user.add_roles(new_role)
                add_coins(user, 20000)
                await channel.send(embed=discord.Embed(title="Level Up!", description="Congratulations %s! You've reached Level 20! That means you've unlocked the `Outstandingly Regular` role! You've also been awarded $20000 for your achievement!" % (user.mention), color=0xE91E63))
            if lvl == 30:
                new_role = discord.utils.get(guild.roles, name="Super! Outstandingly Regular")
                user = discord.utils.get(guild.members, id=userID)
                await user.add_roles(new_role)
                add_coins(user, 30000)
                await channel.send(embed=discord.Embed(title="Level Up!", description="Congratulations %s! You've reached Level 30! That means you've unlocked the `Super Outstandingly Regular` role! You've also been awarded $30000 for your achievement!" % (user.mention), color=0xE67E22))
            if lvl == 40:
                new_role = discord.utils.get(guild.roles, name="Ultra Super Outstandingly Regular")
                user = discord.utils.get(guild.members, id=userID)
                await user.add_roles(new_role)
                add_coins(user, 40000)
                await channel.send(embed=discord.Embed(title="Level Up!", description="Congratulations %s! You've reached Level 40! That means you've unlocked the `Ultra Super Outstandingly Regular` role! You've also been awarded $40000 for your achievement!" % (user.mention), color=0xE74C3C))
            if lvl == 50:
                new_role = discord.utils.get(guild.roles, name="Extremely Ultra Super Outstandingly Regular")
                user = discord.utils.get(guild.members, id=userID)
                await user.add_roles(new_role)
                add_coins(user, 50000)
                await channel.send(embed=discord.Embed(title="Level Up!", description="Congratulations %s! You've reached Level 50! That means you've unlocked the `Extremely Ultra Super Outstandingly Regular` role! You've also been awarded $50000 for your achievement!" % (user.mention), color=0x992D22))
        else:
            Checking = False
            
            
def fetch_exps(userID):
    return db_query("varsity.db", "SELECT Exp, ExpTotal FROM Members WHERE UserID = %s" % (str(userID)))[0]

def set_exp(userID, amount):
    execute_query("varsity.db", "UPDATE Members SET Exp = %s WHERE UserID = %s" % (str(amount),str(userID)))

def set_exp_max(userID, amount):
    execute_query("varsity.db", "UPDATE Members SET ExpTotal = %s WHERE UserID = %s" % (str(amount),str(userID)))    

def sub_exp_only(userID, amount):
    current_exps = fetch_exps(userID)
    new_exp = int(current_exps[0])-amount
    set_exp(userID, new_exp)

def add_exp(userID, amount):
    current_exps = fetch_exps(userID)
    new_exp = int(current_exps[0])+amount
    new_max = int(current_exps[1])+amount
    set_exp(userID, new_exp)
    set_exp_max(userID, new_max)

def add_booster(userID, multiplier, expires):
    execute_query("varsity.db", "INSERT INTO boosters (userID, multiplier, expires) VALUES (%s, %s, %s)" % (str(userID), str(multiplier), str(expires)))

def get_booster(userID):
    boost = db_query("varsity.db", "SELECT multiplier FROM boosters WHERE userID = %s AND isActive = 1" % (str(userID)))
    if len(boost) == 0:
        return 1
    else:
        return boost[0][0]
    
def get_rank(user):
    rank = []
    if "Moderators" in [role.name for role in user.roles]:
        rank.append("Moderators")
        rank.append("https://cdn.discordapp.com/emojis/522185928618409988.png")
    elif "Developer" in [role.name for role in user.roles]:
        rank.append("Developer")
        rank.append("https://cdn.discordapp.com/emojis/522183358050992148.png")        
    else:
        rank.append("Member")
        rank.append("https://cdn.discordapp.com/emojis/486269178047627266.png")

    return rank

def time_phaser(seconds):
    output = ""
    print(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24) 
    if d > 0:
        output = output + str(d) + " Days "
    if h > 0:
        output = output + str(h) + " Hours "
    if m > 0:
        output = output + str(m) + " Minutes "
    if s > 0:
        output = output + str(round(s, 0)) + " Seconds "
    return output
#-----Commands-----

#--Gate Commands--

#!accept
@Bot.command(client)
async def accept(ctx):
    if ctx.message.channel.id == gate:
        await user_accept_rules(ctx.message.author)

#!decline
@Bot.command(client)
async def deny(ctx):
    if ctx.message.channel.id == gate:
        await ctx.message.author.kick()

#--Profile/Economy/User Commands--

#!daily
@Bot.command(client)
async def daily(ctx):
    if await hasPerms(1, ctx):

        message = ctx.message

        otime = int(time.time())

        streak = db_query("varsity.db", "SELECT dailyRewardStreak FROM Members WHERE UserID=%s" % (str(message.author.id)))[0][0]

        levelBoost = int(round(db_query("varsity.db", "SELECT Level FROM Members WHERE UserID=%s" % (str(message.author.id)))[0][0]/5, 0))

        timeLast = db_query("varsity.db", "SELECT dailyRewardClaimed FROM Members WHERE UserID=%s" % (str(message.author.id)))[0][0]
        timeNew = timeLast + (3600*20)

        timeStreakReset = timeLast + (3600*40)

        if not otime > timeNew:
            wait = time_phaser(timeNew - otime) 
            await message.channel.send("Please wait **%s**before using this again" % (str(wait)))
            return False

        if otime > timeStreakReset:
            streak = 0
            execute_query("varsity.db", "UPDATE Members SET dailyRewardStreak = 0 WHERE UserID=%s" % (str(message.author.id)))
        else:
            if not streak == 5:
                streak = streak + 1
                execute_query("varsity.db", "UPDATE Members SET dailyRewardStreak = %s WHERE UserID=%s" % (str(streak), str(message.author.id)))
            

        execute_query("varsity.db", "UPDATE Members SET dailyRewardClaimed = %s WHERE UserID=%s" % (str(otime), str(message.author.id)))
        
        commons = ["c25000", "e500"]
        uncommons = ["c50000", "c75000", "e1000"]
        rares = ["c100000", "e2500", "m215"]
        legendaries = ["c500000", "e5000", "m230", "m310"]
        mythicals = ["c1000000", "e10000", "m260", "m330"]
        rewards = []
        rewardMsgs = []

        def getReward(reward):
            if reward[0] == "c":
                return "$" + "".join(reward[1:])
            elif reward[0] == "e":
                return "".join(reward[1:]) + " EXP"
            elif reward[0] == "i":
                return " ".join(reward.split(" ")[1:])
            elif reward[0] == "b":
                return "A Badge"
            elif reward[0] == "m":
                multiplier = reward[1]
                expires = int("".join(reward[2:]))
                return str(multiplier) + "* Booster [" + str(expires) + " Minutes]"
                
        async def applyReward(reward):
            if reward[0] == "c":
                add_coins(message.author, int("".join(reward[1:])))
            elif reward[0] == "e":
                add_exp(message.author.id, int("".join(reward[1:])))
            elif reward[0] == "i":
                give_item(getReward(reward), message.author)
            elif reward[0] == "b":
                user = message.author
                current_badges = get_profile(str(user.id))[3]
                new_badges = current_badges + "".join(reward[1:]) +" _ _"
                execute_query("varsity.db", "UPDATE Members SET Badges = '%s' WHERE UserID = %s" % (new_badges, str(user.id)))
            elif reward[0] == "m":
                user = message.author
                multiplier = reward[1]
                expires = time.time() + int("".join(reward[2:]))
                add_booser(user.id, multiplier, expires)
                
        #rewards.append("b <:festive2018:526858321991303176>")
        #em = discord.Embed(title="[1] MYTHICAL", description="Mythical Festive 2018 Badge", color=0xFF5555)
        #rewardMsgs.append(await message.channel.send(embed=em))
        for count in range(1,4):
            rewardLevel = random.randint(1, 50) + streak + levelBoost
            if message.author.id == 479263631586885633:
                rewardLevel = rewardLevel + 7
            if rewardLevel <= 20:
                reward = random.choice(commons)
                rewardText = getReward(reward)
                rewards.append(reward)
                em = discord.Embed(title="[%s] COMMON" % (str(count)), description="Common %s" % (rewardText), color=0xFFFFFF) 
            elif rewardLevel <= 35:
                reward = random.choice(uncommons)
                rewardText = getReward(reward)
                rewards.append(reward)
                em = discord.Embed(title="[%s] UNCOMMON" % (str(count)), description="Uncommon %s" % (rewardText), color=0x55FFFF) 
            elif rewardLevel <= 45:
                reward = random.choice(rares)
                rewardText = getReward(reward)
                rewards.append(reward)
                em = discord.Embed(title="[%s] RARE" % (str(count)), description="Rare %s" % (rewardText), color=0xFF55FF) 
            elif rewardLevel <= 50:
                reward = random.choice(legendaries)
                rewardText = getReward(reward)
                rewards.append(reward)
                em = discord.Embed(title="[%s] LEGENDARY" % (str(count)), description="Legendary %s" % (rewardText), color=0x55FF55) 
            elif rewardLevel >= 50:
                reward = random.choice(mythicals)
                rewardText = getReward(reward)
                rewards.append(reward)
                em = discord.Embed(title="[%s] MYTHICAL" % (str(count)), description="Mythical %s" % (rewardText), color=0xFF5555)

            rewardMsg = await message.channel.send(embed=em)
            rewardMsgs.append(rewardMsg)
            await asyncio.sleep(0.5)

        em = discord.Embed(title="Selection", description="Choose your reward", colour=0xFFFF55)

        msg = await message.channel.send(embed=em)

        await msg.add_reaction("1⃣")
        await msg.add_reaction("2⃣")
        await msg.add_reaction("3⃣")


        def check(reaction, user):
            return (user.id == message.author.id) and (str(reaction.emoji) == "1⃣" or str(reaction.emoji) == "2⃣" or str(reaction.emoji) == "3⃣")
        
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            pass
        else:
            if str(reaction.emoji) == "1⃣":
                for count in range(0, 3):
                    if not count == 0:
                        await rewardMsgs[count].delete()
                        await asyncio.sleep(1)
                await asyncio.sleep(1)
                await msg.delete()
                await asyncio.sleep(1)
                await rewardMsgs[0].delete()
                await message.channel.send("**Congratulations! You've unlocked __%s__**" % (getReward(rewards[0])))
                await applyReward(rewards[0])
            if str(reaction.emoji) == "2⃣":
                for count in range(0, 3):
                    if not count == 1:
                        await rewardMsgs[count].delete()
                        await asyncio.sleep(1)
                await asyncio.sleep(1)
                await msg.delete()
                await asyncio.sleep(1)
                await rewardMsgs[1].delete()
                
                await message.channel.send("**Congratulations! You've unlocked __%s__**" % (getReward(rewards[1])))
                await applyReward(rewards[1])
            if str(reaction.emoji) == "3⃣":
                for count in range(0, 3):
                    if not count == 2:
                        await rewardMsgs[count].delete()
                        await asyncio.sleep(1)
                await asyncio.sleep(1)
                await msg.delete()
                await asyncio.sleep(1)
                await rewardMsgs[2].delete()
                await message.channel.send("**Congratulations! You've unlocked __%s__**" % (getReward(rewards[2])))
                await applyReward(rewards[2])
                

                



        ## 1⃣ 2⃣ 3⃣

        

        

                

            
#!shop
@Bot.command(client)
async def shop(ctx):
    if await hasPerms(1, ctx):
        message = ctx.message
        em = discord.Embed(title="Shop", description="The following items are currently available for purchase:", color=reds)
        em.add_field(name="1) 1 Week Custom Role [$5m]", value="Show off your coolness with a custom hoisted role for 1 week! After purchase please contact a moderator regarding the name of the role. The role will be blue. Role names must be appropriate")
        em.add_field(name="2) 1 Week Royalty Role [$3m]", value="Show off how rich you are with the Royalty Role. You'll be given a bright green name which comes with immense bragging rights! Expires after 7 Days")
        em.add_field(name="3) 1 Day Royalty Role [$1m]", value="Show off how rich you are with the Royalty Role. You'll be given a bright green name which comes with immense bragging rights! Expires after 24 hours")
        em.add_field(name="4) 24 Hour 2* Personal Multiplier [$2m]", value="Boost your exp by 2 for 24 hours. Activates immeidately after purchase")
        em.add_field(name="5) 1 Hour 3* Personal Multiplier [$2m]", value="Boost your exp by 3 for 1 hour. Activates immediately after purchase")
        em.add_field(name="6) 1 Hour 2* Global Multiplier [$500k]", value="Boost the exp earned for everyone in the whole server for 1 hour. Activates immediately after purchase")
        #em.set_footer(text="PURCHASING COMING SOON - PRICES SUBJECT TO CHANGE") 
        await message.channel.send(embed=em)

@Bot.command(client)
async def buy(ctx):
    if await hasPerms(1, ctx):
        message = ctx.message
        args = message.content.split()
        if args[1] == "1":
            if fetch_coins(message.author) >= 5000000:
                em = discord.Embed(title="Purchase Complete", description="You have successfully purchased `1 Week Custom Role`.\nNote: `Please contact a moderator for your role`", color=reds)
                add_coins(message.author, -5000000)
                await message.channel.send(embed=em)
            else:
                await message.channel.send("Insufficient Funds")
        if args[1] == "2":
            if fetch_coins(message.author) >= 3000000:
                em = discord.Embed(title="Purchase Complete", description="You have successfully purchased `1 Week Royalty Role`.\nNote: `Please contact a moderator for your role`", color=reds)
                add_coins(message.author, -3000000)
                await message.channel.send(embed=em)
            else:
                await message.channel.send("Insufficient Funds")
        if args[1] == "3":
            if fetch_coins(message.author) >= 1000000:
                em = discord.Embed(title="Purchase Complete", description="You have successfully purchased `1 Day Royalty Role`.\nNote: `Please contact a moderator for your role`", color=reds)
                add_coins(message.author, -1000000)
                await message.channel.send(embed=em)
            else:
                await message.channel.send("Insufficient Funds")
        if args[1] == "4":
            if get_booster(message.author.id) > 1:
                await error("You already have an active exp booster", ctx.message.channel)
            elif fetch_coins(message.author) >= 2000000:
                em = discord.Embed(title="Purchase Complete", description="You have successfully purchased `24 Hour 2* Personal Multiplier`.", color=reds)
                add_coins(message.author, -2000000)
                await message.channel.send(embed=em)
                add_booster(message.author.id, 2, time.time()+86400)
                #execute_query("varsity.db", "UPDATE Members SET expPersonalBoost = 2 WHERE UserID = %s" % (message.author.id))
            else:
                await message.channel.send("Insufficient Funds")
        if args[1] == "5":
            if get_booster(message.author.id) > 1:
                await error("You already have an active exp booster", ctx.message.channel)
            elif fetch_coins(message.author) >= 2000000:
                em = discord.Embed(title="Purchase Complete", description="You have successfully purchased `1 Hour 3* Personal Multiplier`.", color=reds)
                add_coins(message.author, -2000000)
                await message.channel.send(embed=em)
                add_booster(message.author.id, 3, time.time()+3600)
            else:
                await message.channel.send("Insufficient Funds")        
        if args[1] == "6":
            if fetch_coins(message.author) >= 500000:
                if get_booster(1) > 1:
                    await error("There is already an active booster", ctx.message.channel)
                else:    
                    em = discord.Embed(title="Purchase Complete", value="You have successfully purchased `1 Hour 2* Global Multipler`.", color=reds)
                    add_coins(message.author, -500000)
                    await message.channel.send(embed=em)
                    add_booster(1, 2, time.time()+3600)
            else:
                await message.channel.send("Insufficient Funds")        
     
#!help
@Bot.command(client)
async def help(ctx):
    if await hasPerms(1, ctx):
        helpEm = discord.Embed(title="!help", description="Shows the list of commands", color=primary)
        specialCommands = ""
        if await hasPerms(2, ctx, giveOutput=False):
            specialCommands = specialCommands + "!cookie <@user>\n"
            specialCommands = specialCommands + "!battle <@user>\n"
            specialCommands = specialCommands + "!train {stat}\n"
        if await hasPerms(3, ctx, giveOutput=False):
            specialCommands = specialCommands + "!hug <@user>\n"
        if await hasPerms(4, ctx, giveOutput=False):
            specialCommands = specialCommands + "!fight <@user>\n"
        if await hasPerms(5, ctx, giveOutput=False):
            specialCommands = specialCommands + "!slap <@user>\n"
        if await hasPerms(6, ctx, giveOutput=False):
            specialCommands = specialCommands + "!embed {message}\n"
        if await hasPerms(16, ctx, giveOutput=False):
            specialCommands = specialCommands + "!kitten\n"
        helpEm.add_field(name="<:member:486269178047627266> User Commands", value="!debug\n!daily\n!coinflip <bet>\n!shop\n!profile [@user]\n!pay <@user> <amount>\n!ransack <@user> <amount>\n!ping\n!balance\n!tag <tag>\n!suggest <suggestion>\n!comment <suggestion-id> <comment>\n" + specialCommands, inline=False)
        if await hasPerms(32, ctx, giveOutput=False) or ctx.message.author.id in admin_bypass:
            helpEm.add_field(name="<:Staff:522185091187867668> Moderation Commands", value="!punish <@user> {reason}\n!suggestion <suggestion-id> <attribute> <value>\n!enable <command>\n!disable <command>\n!badge <add|remove> <emoji> <@user>\n!statmod <@user> <set|add|sub> <balance|exp|statwipe> {amount}\n!announce <type> <message>\n!raffle <minutes> <item>\n!giveitem <@user> <item> <amount>", inline=False)
        await ctx.message.channel.send(embed=helpEm)

#!rewards
@Bot.command(client, aliases=["levels"])
async def rewards(ctx):
    '''
    Show rewards that can be unlocked from levelling up.

    Required Permission Level: @Regular
    '''
    levelRewards = """**Level 10**
!cookie
!battle
!train

**Level 20**
!hug

**Level 30**
!fight

**Level 40**
!slap

**Level 50**
!embed"""

    embed=discord.Embed(title="Level Rewards", description=levelRewards, colour=primary)
    await ctx.send(embed=embed)

#!profile
@Bot.command(client)
async def profile(ctx):
    if await hasPerms(1, ctx):
        message = ctx.message
        args = message.content.split()
        
        if len(args) <= 1:
            user = message.author
            profile = get_profile(str(message.author.id))
            
        else:
            if args[1].upper() == "OPTIONS":
                if len(args) == 2:
                    cosmetics = db_query("varsity.db", "SELECT cosmetics FROM Members WHERE UserID = %s" % (str(message.author.id)))[0][0]
                    colours = "- `default`\n"
                    hashtags = ""
                    pictures = "- `default`\n"
                    if not cosmetics is None:
                        cosmetics = cosmetics.split("_")
                        

                        for item in cosmetics:
                            itemName = "".join(item[1:]) 
                            if item[0] == "c":
                                colours = colours + "- `%s`\n" % (itemName)
                            if item[0] == "h":
                                hashtags = hashtags + "- `%s`\n" % (itemName)
                            if item[0] == "p":
                                pictures = pictures + "- `%s`\n" % (itemName)
                    if len(hashtags) == 0:
                        hashtags = "None"
                    embed=discord.Embed(title="Profile Options", description="You can change the following settings", colour=0xFFFF55)
                    embed.add_field(name="Colour", value=colours)
                    embed.add_field(name="Hashtag", value=hashtags)
                    embed.add_field(name="Profile Picture", value=pictures)
                    await message.channel.send(embed=embed)
                elif args[2].upper() == "COLOUR":
                    lColours = ["default", "0xFFFF55", "cyan", "secondary", "light red", "0xFF5555", "green", "0x00AA00"]
                    cosmetics = db_query("varsity.db", "SELECT cosmetics FROM Members WHERE UserID = %s" % (str(message.author.id)))[0][0]
                    sCosmetics = cosmetics.split("_")
                    if "c"+args[3] in sCosmetics:
                        execute_query("varsity.db", "UPDATE Members set profileColour = '%s' WHERE UserID = %s" % (lColours[lColours.index(args[3].lower())+1], str(message.author.id)))
                        await message.channel.send("**Successfully Updated Profile Colour!**")
                    else:
                        await message.channel.send("Error: **You have not unlocked this colour**")

                elif args[2].upper() == "HASHTAG":
                    cosmetics = db_query("varsity.db", "SELECT cosmetics FROM Members WHERE UserID = %s" % (str(message.author.id)))[0][0]
                    sCosmetics = cosmetics.split("_")
                    if "h"+args[3] in sCosmetics:
                        execute_query("varsity.db", "UPDATE Members set profileHashtag = '%s' WHERE UserID = %s" % (args[3], str(message.author.id)))
                        await message.channel.send("**Successfully Updated Profile Hashtag!**")
                    else:
                        await message.channel.send("Error: **You have not unlocked this hashtag**") 
                return 
            else:    
                user = discord.utils.get(message.guild.members, mention=args[1])
                profile = get_profile(str(user.id))
                if user.id == 472063067014823938:
                    await error("[418] I'm a teapot", message.channel)
                    return
        em = discord.Embed(title=user.name, colour=eval(profile[4]))

        exps = db_query("varsity.db", "SELECT UserID FROM Members WHERE NOT UserID = 472063067014823938 AND NOT UserID = 1 ORDER BY expTotal DESC")
        lpos = 1
        for userl in exps:
            if not userl[0] == user.id:
                lpos = lpos + 1
            else:
                break

        bals = db_query("varsity.db", "SELECT UserID FROM Members WHERE NOT UserID = 472063067014823938 AND NOT UserID = 1 ORDER BY Balance DESC")
        bpos = 1
        for userb in bals:
            if not userb[0] == user.id:
                bpos = bpos + 1
            else:
                break        
        

        rank = get_rank(user)
        em.set_author(name=rank[0], icon_url=rank[1])

        badges = profile[3]

        exp = profile[6]
        expCost = 5 * (profile[1]*profile[1]) + 50 * profile[1] + 100 

        em.add_field(name=badges, value="_ _ _ _ ")
        em.set_thumbnail(url=user.avatar_url)
        em.add_field(name="_ _ _ _", value="_ _ _ _")
        em.add_field(name="Level", value=str(profile[1])+" [**" + str(exp) + "/" + str(expCost)+"**]")
        em.add_field(name="Experience", value=str(profile[2])+ " [**#" + str(lpos) + "**]")

        em.add_field(name="Member Since", value=str(user.joined_at)[0:19])
        em.add_field(name="Balance", value="$"+str(balance_formatter(int(profile[0])))+" [**#%s**]" % (str(bpos)))
        if not profile[5] is None:    
            em.set_footer(text="#"+profile[5])

        await message.channel.send(embed=em)
        
        
@Bot.command(client, aliases=["bal"])
async def balance(ctx):
    if await hasPerms(1, ctx):
        profile = get_profile(str(ctx.message.author.id))
        uBalance = profile[0]
        balances = db_query("varsity.db", "SELECT Balance FROM Members WHERE NOT UserID = 1 AND NOT UserID = 472063067014823938 ORDER BY Balance DESC")
        total_balance = 0
        highest_balance = balances[0][0]
        for balance in balances:
            total_balance = total_balance+balance[0]
        em = discord.Embed(title="Balance", description="You currently have **$%s**\nThe server total is **$%s**\nThe server average is **$%s**" % (str("{:,}".format(uBalance)), str("{:,}".format(total_balance)), str("{:,}".format(int(round(total_balance/len(ctx.message.guild.members),0))))), color=primary)   
        em.set_footer(text="You currently contribute to %s%s of the economy" % (str(round((uBalance/total_balance)*100, 2)), "%")) 
        await ctx.message.channel.send(embed=em)

#!pay
@Bot.command(client)
async def pay(ctx):
    if await hasPerms(1, ctx):
        message = ctx.message
        args = message.content.split()
        balance = fetch_coins(message.author)
        if int(args[2]) > balance:
            await message.channel.send("Transaction Rejected\n_ - _ `Insufficient Funds`")
        else:
            user = discord.utils.get(message.guild.members, mention=args[1])
            if int(args[2]) <= 0:
                await error("[400] Amount must be higher than 0", message.channel)
                return False
            else:
                amount = args[2]
                
            em = discord.Embed(title="Transaction", description="Please confirm your payment of $%s to %s **Y/N**" % (str(amount), str(user.mention)), colour=primary)
            await message.channel.send(embed=em)

            def check(m):
                return m.author.id == message.author.id

            try:
                msg = await client.wait_for('message', check=check, timeout=30.0)
            except asyncio.TimeoutError:
                await channel.send("No Response - Transaction Cancelled")
            else:
                if msg.content.upper() == "Y" or msg.content.upper() == "YES":
                    add_coins(message.author, -int(amount))
                    add_coins(user, int(amount))
                    await message.channel.send(":ok_hand: Transaction Complete")
                elif msg.content.upper() == "N" or msg.content.upper() == "NO":
                        await message.channel.send("Transaction Declined")
                else:
                    await message.channel.send("Invalid Response - Transaction Cancelled")

            
#!ransack
@Bot.command(client)
async def ransack(ctx):
    if await hasPerms(1, ctx):
        message = ctx.message

        otime = int(time.time())

        timeLast = db_query("varsity.db", "SELECT lastRansack FROM Members WHERE UserID=%s" % (str(message.author.id)))[0][0]
        timeNew = timeLast + (3600*0.25)

        if not otime > timeNew:
            wait = time_phaser(timeNew - otime) 
            await message.channel.send("Please wait **%s**before using this again" % (str(wait)))
            return False
            
        args = message.content.split(" ")
        if len(args) <= 1:
            await error("Invalid Command Usage - Not enough args", ctx.message.channel)
            return
        user = discord.utils.get(message.guild.members, mention=args[1])
        targetTimeLast = db_query("varsity.db", "SELECT lastGotRansackTime, lastGotRansackAmount FROM Members WHERE UserID=%s" % (str(user.id)))[0]
        targetTimeNew = targetTimeLast[0] + (3600 * (targetTimeLast[1]/10000))

        if not otime > targetTimeNew:
            wait = time_phaser(targetTimeNew - otime)
            await message.channel.send("This user cannot be ransacked for another **%s**" % (str(wait)))
            return False
        
        amount = int(args[2])
        if fetch_coins(user) < amount:
            await error("[400] Target User Does Not Have Enough Balance!", message.channel)
        elif fetch_coins(message.author) < amount:
            await error("[400] You don't have enough balance for this!", message.channel)
        elif amount < 25000:
            await error("[400] Amount must be above $25000", message.channel) 
        elif message.author == user:
            await error("[403] You cannot ransack yourself!", message.channel)
        else:
            execute_query("varsity.db", "UPDATE Members SET lastRansack = %s WHERE UserID=%s" % (str(otime), str(message.author.id)))
            chance = random.randint(1, int(round(amount/10000, 0)))
            if chance == 1: #(Harry I see what you did there...)
                add_coins(user, -amount)
                add_coins(message.author, amount)
                await message.channel.send(embed=discord.Embed(title="Ransack", description="Congrats! You successfully ransacked **%s** for **$%s**!\nYou may try again in 15 minutes." % (user.name, str(amount)), color=primary)) 
                execute_query("varsity.db", "UPDATE Members SET lastGotRansackTime = %s WHERE UserID = %s" % (str(otime), str(user.id)))
                execute_query("varsity.db", "UPDATE Members SET lastGotRansackAmount = %s WHERE UserID = %s" % (str(amount), str(user.id)))
            else:
                add_coins(message.author, -amount)
                await message.channel.send(embed=discord.Embed(title="Ransack", description="You failed to ransack **%s** and were fined **$%s** for your attempt!\nYou may try again in 15 minutes." % (user.name, str(amount)), color=0xFF5555))
                add_coins(user, int(round(amount/2, 0)))



#!tag
@Bot.command(client)
async def tag(ctx):
    if await hasPerms(2, ctx):
        message = ctx.message
        args = message.content.split()
        if len(args) <= 1:
            await error("Invalid Command Usage - Not enough args", ctx.message.channel)
            return
        if args[1].upper().startswith("TOKEN"):
            em = discord.Embed(title="Tokens", description='''**__DO NOT SHARE YOUR TOKEN!__** Doing so may result in your bot being hacked. We don't take responsibility for your bot being hacked. If for some reason you do leak it, immediately change it as it will automatically invalidate the previous token.''', color=0xffd343)
            await message.channel.send(embed=em)
        elif args[1].upper().startswith("PING"):
            em = discord.Embed(title="Ping Pong", description='''Don't ping or DM Members for help with your script. Just ask it in the correct help channel, and someone will see it eventually. Also, please refrain from pinging the @Staff role, as some staff members do not code, and would rather not be pinged for this type of stuff.''', color=0xffd343)
            await message.channel.send(embed=em)
        elif args[1].upper().startswith("PYTHON"):
            em = discord.Embed(title="Python Downloads and Docs", description='''**Python 3.6.5 Download:** https://www.python.org/downloads/release/python-365/
    **Python 3.7 Download:** https://www.python.org/downloads/release/python-370/
    **Python 3 Documentation:** https://docs.python.org/3/
    ''', color=0xffd343)
            await message.channel.send(embed=em)
        elif args[1].upper().startswith("QUESTION"):
            em = discord.Embed(title="Asking Questions", description='''Please don't post one message saying "Help something don't work" and wait for a response. Most people prefer to judge whether the issue is in their grasp or something they can handle in the time they've got. To allow us to help you, please provide as much information as possible when posting your issue, for example - What the error is, error logs and your code with sensitive information removed. (Please use code blocks for these thing)''', color=0xffd343)
            await message.channel.send(embed=em)
        elif args[1].upper().startswith("ANSWERING"):
            em = discord.Embed(title="Answering Questions", description='''Please only answer questions that you actually know the answer to, don't respond with things that you guess are correct, it doesn't help anyone. Please don't contradict someone's answer with what you believe is the "better" way of doing something, it confuses everyone. Just don't do it.

    Also, We've seen some smartass answers and argument over whose way is better and it's annoying and not helpful.

    If you are caught doing this and we feel it is best if you didn't type in help channels, we'll revoke your permissions to use them.''', color=0xffd343)
            await message.channel.send(embed=em)
            
    
#!suggest
@Bot.command(client)
async def suggest(ctx):
    if await hasPerms(2, ctx):
        message = ctx.message
        args = message.content.split(" ")
        if len(args) <= 1:
            await error("Invalid Command Usage - Not enough args", ctx.message.channel)
            return
        em = discord.Embed(title="Suggestion", description="Created by %s" % (message.author.name), color=reds)
        em.add_field(name="Status", value="Pending")
        em.add_field(name="Assigned To", value="None")
        em.add_field(name="Content", value=" ".join(args[1:]))
        suggestion = await client.get_channel(483767654914588683).send(embed=em)
        em.set_footer(text="Suggestion ID: %s" % (str(suggestion.id)))
        await suggestion.edit(embed=em)
        await message.channel.send(content="Suggestion Submitted", embed=suggestion.embeds[0])
        await message.delete()

#!items
@Bot.command(client)
async def items(ctx):
    if await hasPerms(1, ctx):
        args = ctx.message.content.split(" ")
        items = fetch_items(ctx.message.author.id)
        if len(args) == 1:

            em = discord.Embed(title="Items", description="You currently have the following items:", color=secondary)

            if items[0][0] is None or len(items[0][0]) == 0:
                em.add_field(name="No Items", value="We couldn't find any items for you.")
            else:    
                itemParse = items[0][0].split("_")
                itemStr = "\n".join(itemParse)
                em.add_field(name="Items", value=itemStr)
            em.set_footer(text="Use !items use <item> to use an item")    
            await ctx.message.channel.send(embed=em)
        elif args[1].upper() == "USE":
            item = " ".join(args[2:])
            itemParse = items[0][0].upper().split("_")
            if not item.upper() in itemParse:
                await ctx.message.channel("You do not have this item")
                return
            if item.upper() == "MAGICAL RANSACK KEY":
                """
                This Key Will Allow The User To Ransack 25% Of A Users Balance Without Fail
                """
                await ctx.message.channel.send("Please tag the user you would like to ransack or type 'N' to exit")

                def check(m):
                    return m.author == ctx.message.author
                try:
                    msg = await client.wait_for('message', check=check, timeout=30)
                except asyncio.TimeoutError:
                    await ctx.message.channel.send("Timed Out")
                else:
                    if msg.content.upper() == "N":
                        await msg.channel.send("Cancelled")
                    else:
                        target = discord.utils.get(msg.guild.members, mention=msg.content)
                        if target is None:
                            await msg.channel.send("Invalid User")
                        else:
                            balance = fetch_coins(target)
                            nicked = int(round(balance*0.25, 0))
                            add_coins(target, -nicked)
                            add_coins(msg.author, nicked)
                            await msg.channel.send("Successfully ransacked %s for $%s!" % (target.mention, str(nicked)))

                            items = fetch_items(ctx.message.author.id)
                            itemParse = items[0][0].split("_")
                            index = 0
                            for items in itemParse:
                                if items.upper() == item.upper():
                                    itemParse.pop(index)
                                    break
                                else:
                                    index = index + 1
                            if len(itemParse) == 0:
                                execute_query("varsity.db", "UPDATE Members SET Items = Null WHERE UserID = %s" % (str(ctx.message.author.id)))
                            else:    
                                itemsDb = "_".join(itemParse)
                                execute_query("varsity.db", "UPDATE Members SET Items = '%s' WHERE UserID = %s" % (itemsDb, str(ctx.message.author.id)))
            elif item.upper() == "MYTHICAL RANSACK KEY":
                """
                This Key Will Allow The User To Ransack 50% Of A Users Balance Without Fail
                """
                await ctx.message.channel.send("Please tag the user you would like to ransack or type 'N' to exit")

                def check(m):
                    return m.author == ctx.message.author
                try:
                    msg = await client.wait_for('message', check=check, timeout=30)
                except asyncio.TimeoutError:
                    await ctx.message.channel.send("Timed Out")
                else:
                    if msg.content.upper() == "N":
                        await msg.channel.send("Cancelled")
                    else:
                        target = discord.utils.get(msg.guild.members, mention=msg.content)
                        if target is None:
                            await msg.channel.send("Invalid User")
                        else:
                            balance = fetch_coins(target)
                            nicked = int(round(balance*0.5, 0))
                            add_coins(target, -nicked)
                            add_coins(msg.author, nicked)
                            await msg.channel.send("Successfully ransacked %s for $%s!" % (target.mention, str(nicked)))

                            items = fetch_items(ctx.message.author.id)
                            itemParse = items[0][0].split("_")
                            index = 0
                            for items in itemParse:
                                if items.upper() == item.upper():
                                    itemParse.pop(index)
                                    break
                                else:
                                    index = index + 1
                            itemsDb = "_".join(itemParse)
                            execute_query("varsity.db", "UPDATE Members SET Items = '%s' WHERE UserID = %s" % (itemsDb, str(ctx.message.author.id)))
            else:
                ctx.message.channel.send("Invalid Item")
                            

                
        
        
@Bot.command(client)
async def ban(ctx):
    if await hasPerms(3, ctx):
        if fetch_coins(ctx.message.author) >= 15000 or "Moderators" in [role.name for role in ctx.message.author.roles]:
            args = ctx.message.content.split(" ")
            target = discord.utils.get(ctx.message.guild.members, mention=args[1])
            issuer = ctx.message.author
            reason = " ".join(args[2:])
            em = discord.Embed(title="Punish", description="**%s** has banned **%s** for **9001 Days** for `%s`" % (issuer.name, target.name, reason), color=primary)
            await ctx.send(embed=em)
            if not "Moderators" in [role.name for role in ctx.message.author.roles]:
                add_coins(ctx.message.author, -15000)
    

#--Connection Commands--

#!ping
@Bot.command(client)
async def ping(ctx):
    if await hasPerms(1, ctx):
        chance = random.randint(1,25)
        if chance == 1:
            pongStr = "The API is shit!"
        else:
            pongStr = "Pong!"
        start = time.time() * 1000
        msg = await ctx.message.channel.send(pongStr)
        end = time.time() * 1000
        await msg.edit(content=pongStr + " `%sms`" % (str(int(round(end-start, 0))))+" **[SUBSCRIBE TO __PEWDIEPIE__]**")


@Bot.command(client)
async def debug(ctx):
    if await hasPerms(1, ctx):
        em = discord.Embed(title="Debug", description="Debug Information", color=reds)
        em.add_field(name="Latency", value="`Pinging...`")
        em.add_field(name="Requests Per Second", value="`%s`" % (str(random.randint(1,3))+"."+ str(random.randint(1,9))))
        em.add_field(name="DB Queue Length", value="`%s`" % (str(random.randint(21,173)))) 
        em.add_field(name="Error Logs", value="```Unable to reach logging server...```") #Logging server borked
        start = time.time()*1000
        msg = await ctx.message.channel.send(embed=em)
        end = time.time()*1000
        ping = int(round(end - start, 0))
        nEm = msg.embeds[0].set_field_at(0, name="Latency", value="`%sms`" % (str(ping)))
        await msg.edit(embed=nEm)
    
    
                 
    

#--Level Commands--

#!cookie
@Bot.command(client)
async def cookie(ctx):
    if await hasPerms(2, ctx):
        args = ctx.message.content.split()
        cookie_type = random.choice(["just gave you a chocolate chip cookie!", "just gave you a oat cookie!", "just gave you a super sized cookie!", "just gave you a lemon cookie!"])
        await ctx.message.channel.send("%s - %s %s :cookie:" % (args[1], ctx.message.author.mention, cookie_type))
       

#!nick
@Bot.command(client)
async def nick(ctx):
    if await hasPerms(2, ctx):
        args = ctx.message.content.split()
        message = ctx.message
        
        otime = time.time()
        timeLast = db_query("varsity.db", "SELECT lastNick FROM Members WHERE UserID=%s" % (str(message.author.id)))[0][0]
        timeNew = timeLast + (3600*72)
        if not otime > timeNew:
            wait = time_phaser(timeNew - otime) 
            await message.channel.send("Please wait **%s**before using this again" % (str(wait)))
        else:
            await message.delete()
            em = discord.Embed(title="Nickname", description="""Nickname Rules:
**Nothing Inappropriate**
**No Profanity**
**No Impersonation**

Failure to comply will result in access to this command being revoked.

**You may only change your nickname once every three days so please make sure it is correct!**
_Staff will not reverse it for you_

You can reset your nickname by typing "reset".

Please type your new nickname below or type "cancel" to exit.""", color=primary)
            try:
                menu = await message.author.send(embed=em)
                def check(m):
                    return m.channel == menu.channel and m.author == message.author

                msg = await client.wait_for('message', check=check)
                if len(msg.content) > 32:
                    await message.author.send("**Error whilst setting nickname, nickname is too long** (Max 32 Characters)")
                elif msg.content.lower() == "cancel":
                    await message.author.send("**Cancelled**")
                elif msg.content.lower() == "reset":
                    await message.author.edit(nick=None, reason="Nickname Change Command") 
                elif len(msg.content) < 3:
                    await message.author.send("**Error whilst setting nickname, nickname is too short** (Min 3 Characters)")
                else:
                    await message.author.edit(nick=msg.content, reason="Nickname Change Command")
                    execute_query("varsity.db", "UPDATE Members SET lastNick = %s WHERE UserID=%s" % (str(otime), str(message.author.id)))
                    await message.author.send(":ok_hand: **Your nickname has been updated!**")
                    
            except Exception as e:
                await message.channel.send("Unable to send prompt, please allow private messages from the server")
                if "Moderators" in [role.name for role in message.author.roles]:
                    await message.channel.send(e)

            
            
#!hug
@Bot.command(client)
async def slap(ctx):
    if await hasPerms(5, ctx):
        args = ctx.message.content.split()
        await ctx.message.channel.send("%s has just slapped %s!" % (ctx.message.author.mention, args[1]))
        
#!hug
@Bot.command(client)
async def hug(ctx):
    if await hasPerms(3, ctx):
        args = ctx.message.content.split()
        hug_type = random.choice(["just gave you a big hug!", "just gave you a big big hug!", "just gave you a tight squeeze!", "just gave you a bog standard hug!"])
        await ctx.message.channel.send("%s - %s %s :hugging:" % (args[1], ctx.message.author.mention, hug_type))
      



#!fight
@Bot.command(client)
async def fight(ctx):
    #await error("This command has been disabled by the Administration Team as it causes too many issues with our rate limit", ctx.message.channel)
    #return
    message = ctx.message
    args = message.content.split()
    if await hasPerms(4, ctx):
        global battleInProgress
        if battleInProgress:
            await error("A Fight Is Already In Progress, Please Wait", message.channel)
            return
            
        battleInProgress = True
        loss = 0
        rounds = 1
        init = message.author.mention
        target = " ".join(args[1:])
        fight = "%s has challenged %s to a fight!" % (init, target) + "\n"
        fightEm = discord.Embed(title="Fight!", description=fight, colour=0x5555FF) 
        fMessage = await message.channel.send(embed=fightEm)
        while not (loss == 1) and not (rounds > 5): 
            fight = fight + random.choice(["%s threw a chair at %s" % (init, target), "%s whacked %s with a stick" % (init, target), "%s slapped %s to the floor" % (init, target), "%s threw %s through a wall" % (init, target), "%s bitch slapped %s" % (init, target), "%s used dark magic against %s" % (init, target), "%s used the infinity gauntlet" % (init), "%s used fake news on %s" % (init, target), "%s ran %s over with a truck" % (init, target), "%s ate %s and threw them up again" % (init, target), "%s savagely roasted %s for sunday lunch" % (init, target), "%s performed a windows update on %s" % (init, target), "%s used the might of Zeus" % (init), "%s trapped %s in Flex Tape" % (init, target), "%s built a wall!" % (init)])+"\n"
            fightEm = discord.Embed(title="Fight!", description=fight, colour=0x5555FF) 
            await fMessage.edit(embed=fightEm)
            await asyncio.sleep(2)
            loss = random.randint(1, 3)
            if loss == 1:
                fight = fight + "%s accepts defeat! %s has won the fight!" % (target, init)
            elif rounds == 5:
                fight = fight + "The fight has ended in a draw!"
            else:
                fight = fight +"%s does not giveup and continues the fight!" % (target) + "\n"

            fightEm = discord.Embed(title="Fight!", description=fight, colour=0x5555FF)
            await fMessage.edit(embed=fightEm)
            
            temp = target
            target = init
            init = temp
            rounds = rounds + 1
            await asyncio.sleep(4)
        battleInProgress = False         
#!fight
@Bot.command(client)
async def battle(ctx):
    if await hasPerms(2, ctx): 
        global battleInProgress
        moves = ["Bitch Slap", "Fake News", "Flex Tape", "A Trap", "Windows Update", "A Chair", "Train Delays", "The Infinity Gauntlet", "Dark Magic"] 
        message = ctx.message
        args = message.content.split()
        if len(args) <= 1:
            await error("Invalid Command Usage - Not enough args", ctx.message.channel)
            return
        else: 
            if battleInProgress:
                await error("A Battle Is Already In Progress, Please Wait", message.channel)
                return
            try:
                battleInProgress = True
                target = discord.utils.get(message.guild.members, mention=args[1])
                user = message.author
                userStats = db_query("varsity.db", "SELECT statAtk, statDef, statHp FROM Members WHERE UserID = %s" % (str(user.id)))[0]
                userHp = userStats[2]
                userMaxHp = userStats[2]
                targetStats = db_query("varsity.db", "SELECT statAtk, statDef, statHp FROM Members WHERE UserID = %s" % (str(target.id)))[0]
                targetHp = targetStats[2]
                targetMaxHp = targetStats[2]
                userField = "%s [%s/%s]" % (user.name, userHp, userMaxHp)
                targetField = "%s [%s/%s]" % (target.name, targetHp, targetMaxHp)
                em = discord.Embed(title="Fight", color=reds)
                em.add_field(name=userField, value="Attack: "+str(userStats[0])+"\nDefense: "+str(userStats[1]))
                em.add_field(name=targetField, value="Attack: "+str(targetStats[0])+"\nDefense: "+str(targetStats[1]))
                fightMsg = await message.channel.send(embed=em)
                complete = False
                attackLog = ""
                em.add_field(name="Battle Log:", value=attackLog, inline=False)
                while not complete:
                    move = random.choice(moves)
                    attackDam = int(random.randint(round(userStats[0]/2, 0), userStats[0]+2) - round(targetStats[1]/10, 0))
                    if attackDam < 3:
                            attackDam = 3
                    targetHp = targetHp - attackDam
                    if targetHp <= 0:
                        targetHp = 0
                        complete = True
                    attackLog = attackLog + "%s used %s **(%s Damage)**\n" % (user.name, move, attackDam)
                    #em.add_field(name="Battle Log:", value=attackLog)
                    targetField = "%s [%s/%s]" % (target.name, targetHp, targetMaxHp)
                    em.set_field_at(1, name=targetField, value="Attack: "+str(targetStats[0])+"\nDefense: "+str(targetStats[1]))
                    em.set_field_at(2, name="Battle Log:", value=attackLog)
                    await fightMsg.edit(embed=em)

                    await asyncio.sleep(0.5)

                    if not complete:
                        move = random.choice(moves)
                        attackDam = int(random.randint(round(targetStats[0]/2, 0), targetStats[0]+2) - round(userStats[1]/10, 0))
                        if attackDam < 3:
                            attackDam = 3
                        userHp = userHp - attackDam
                        if userHp <= 0:
                            userHp = 0
                            complete = True
                        attackLog = attackLog + "%s used %s **(%s Damage)**\n" % (target.name, move, attackDam)
                        #em.add_field(name="Battle Log:", value=attackLog)
                        targetField = "%s [%s/%s]" % (user.name, userHp, userMaxHp)
                        em.set_field_at(0, name=targetField, value="Attack: "+str(userStats[0])+"\nDefense: "+str(userStats[1]))
                        em.set_field_at(2, name="Battle Log:", value=attackLog)
                        await fightMsg.edit(embed=em)

                    await asyncio.sleep(1)
                if targetHp == 0:
                    attackLog = attackLog + "**%s has won the battle!**" % (user.name)
                elif userHp == 0:
                    attackLog = attackLog + "**%s has won the battle!**" % (target.name)
                em.set_field_at(2, name="Battle Log:", value=attackLog)
                await fightMsg.edit(embed=em)
            except:
                pass
        battleInProgress = False

@Bot.command(client)
async def embed(ctx):
    if await hasPerms(6, ctx):
        args = ctx.message.content.split(" ")
        contents = " ".join(args[1:])
        author = ctx.message.author
        em = discord.Embed(title="_ _", description=contents, colour=secondary)
        em.set_author(name=author.name, icon_url=author.avatar_url)
        await ctx.send(embed=em)

@Bot.command(client)
async def kitten(ctx):
    if await hasPerms(16, ctx):
        imgUrl = random.choice(["https://media.tenor.com/images/fe9cdda998e9d121f318c2d938c9c6a2/tenor.gif", "https://media.giphy.com/media/kvrvnB158J4fm/giphy.gif", "https://media.giphy.com/media/r1OyZ5NfRJigg/giphy.gif", "https://media.giphy.com/media/4rep3f9ih9u12/giphy.gif"])
        em = discord.Embed(title="Kitten", image=imgUrl, colour=secondary)
        em.set_image(url=imgUrl)
        await ctx.send(embed=em)
    
        
@Bot.command(client)
async def train(ctx):
    if await hasPerms(2, ctx):
        global training
        message = ctx.message
        args = message.content.split()
        user = message.author
        userStats = db_query("varsity.db", "SELECT statAtk, statDef, statHp FROM Members WHERE UserID = %s" % (str(user.id)))[0]
    
        if message.author.id in training:
            await error("Please react to previous confirmation box before preforming this action again", message.channel)
            return
        training.append(message.author.id)
        if len(args) == 1:
            em=discord.Embed(title="Stats", description="`Attack: %s` **[Upgrade Cost: `$%s`]**\n`Defense: %s` **[Upgrade Cost: `$%s`]**\n`HP: %s` **[Upgrade Cost: `$%s`]**" % (str(userStats[0]), str(userStats[0]*1000), str(userStats[1]), str(userStats[1]*1000), str(userStats[2]), str(userStats[2]*1000)), color=primary)
            await message.channel.send(embed=em)
        elif args[1].upper() == "ATTACK":
            if not fetch_coins(user) >= userStats[0]*1000:
                await message.channel.send("Insufficient Funds")
            elif userStats[0] >= 300:
                await message.channel.send("Cannot Upgrade Past 300")
            else:    
                em=discord.Embed(tile="Train", description="Train **Attack** `%s` **---->** `%s` for **$%s**?\nThis transaction cannot be reversed!" % (str(userStats[0]), str(userStats[0]+5), str(userStats[0]*1000)), color=primary)
                confirmation = await message.channel.send(embed=em)
                await confirmation.add_reaction("\U0001F44D")
                await confirmation.add_reaction("\U0001F44E")

                def check(reaction, user):
                    return user == message.author and (str(reaction.emoji) == '\U0001F44D' or str(reaction.emoji) == "\U0001F44E")
                try:
                    reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
                except asyncio.TimeoutError:
                    await message.channel.send('Timed Out')
                else:
                    if str(reaction.emoji) == "\U0001F44D":
                        attackNew = userStats[0] + 5
                        execute_query("varsity.db", "UPDATE Members SET statAtk = %s WHERE UserID = %s" % (str(attackNew), str(user.id)))
                        add_coins(user, -userStats[0]*1000)
                        await message.channel.send("Success") 
                    elif str(reaction.emoji) == "\U0001F44E":
                        await message.channel.send("Cancelled") 
                                      
                        
                await confirmation.clear_reactions()
        elif args[1].upper() == "DEFENSE":
            if not fetch_coins(user) >= userStats[1]*1000:
                await message.channel.send("Insufficient Funds")
            elif userStats[1] >= 300:
                await message.channel.send("Cannot Upgrade Past 300")    
            else:    
                em=discord.Embed(tile="Train", description="Train **Defense** `%s` **---->** `%s` for **$%s**?\nThis transaction cannot be reversed!" % (str(userStats[1]), str(userStats[1]+5), str(userStats[1]*1000)), color=primary)
                confirmation = await message.channel.send(embed=em)
                await confirmation.add_reaction("\U0001F44D")
                await confirmation.add_reaction("\U0001F44E")

                def check(reaction, user):
                    return user == message.author and (str(reaction.emoji) == '\U0001F44D' or str(reaction.emoji) == "\U0001F44E")
                try:
                    reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
                except asyncio.TimeoutError:
                    await message.channel.send('Timed Out')
                else:
                    if str(reaction.emoji) == "\U0001F44D":
                        defenseNew = userStats[1] + 5
                        execute_query("varsity.db", "UPDATE Members SET statDef = %s WHERE UserID = %s" % (str(defenseNew), str(user.id)))
                        add_coins(user, -userStats[1]*1000)
                        await message.channel.send("Success") 
                    elif str(reaction.emoji) == "\U0001F44E":
                        await message.channel.send("Cancelled")
                        
                await confirmation.clear_reactions()
        elif args[1].upper() == "HP":
            if not fetch_coins(user) >= userStats[2]*1000:
                await message.channel.send("Insufficient Funds")
            elif userStats[0] >= 450:
                await message.channel.send("Cannot Upgrade Past 450")    
            else:    
                em=discord.Embed(tile="Train", description="Train **Hit Points** `%s` **---->** `%s` for **$%s**?\nThis transaction cannot be reversed!" % (str(userStats[2]), str(userStats[2]+5), str(userStats[2]*1000)), color=primary)
                confirmation = await message.channel.send(embed=em)
                await confirmation.add_reaction("\U0001F44D")
                await confirmation.add_reaction("\U0001F44E")

                def check(reaction, user):
                    return user == message.author and (str(reaction.emoji) == '\U0001F44D' or str(reaction.emoji) == "\U0001F44E")
                try:
                    reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
                except asyncio.TimeoutError:
                    await message.channel.send('Timed Out')
                else:
                    if str(reaction.emoji) == "\U0001F44D":
                        hpNew = userStats[2] + 5
                        execute_query("varsity.db", "UPDATE Members SET statHp = %s WHERE UserID = %s" % (str(hpNew), str(user.id)))
                        add_coins(user, -userStats[2]*1000)
                        await message.channel.send("Success") 
                    elif str(reaction.emoji) == "\U0001F44E":
                        await message.channel.send("Cancelled")
                        
                await confirmation.clear_reactions()
    training.remove(message.author.id)
            
#!quickmaths
@Bot.command(client)
async def quickmaths(ctx):
    if await hasPerms(2, ctx):
        await ctx.send("**2+2 IS __4__! MINUS 1 THAT'S __3__! __*QUICK MATHS!*__**")

#--Admin Commands--

#!badge
@Bot.command(client)
async def badge(ctx):
    if await hasPerms(32, ctx):
        message = ctx.message
        args = message.content.split()
        user = discord.utils.get(message.guild.members, mention=args[3])
        if args[1].upper() == "ADD":
            badge = args[2]
            current_badges = get_profile(str(user.id))[3]
            new_badges = current_badges + args[2] +" _ _"
            execute_query("varsity.db", "UPDATE Members SET Badges = '%s' WHERE UserID = %s" % (new_badges, str(user.id)))
            await message.channel.send(":ok_hand: Successfully added %s to **%s**'s profile!" % (badge, user.name))
                
        if args[1].upper() == "REMOVE":
            badge = args[2] + " _ _"
            current_badges = get_profile(str(user.id))[3]
            new_badges = current_badges.replace(badge, '')
            execute_query("varsity.db", "UPDATE Members SET Badges = '%s' WHERE UserID = %s" % (new_badges, str(user.id)))
            await message.channel.send(":ok_hand: Successfully removed %s from **%s**'s profile!" % (badge, user.name))
            

#!disable
@Bot.command(client)
async def disable(ctx, *args):
    '''
    Allow the Moderation Team to temporarily disable a command.

    Required Permission: @Moderator
    Required Arguments: Command

    '''
    if await hasPerms(32, ctx):
        message = ctx.message
        args = message.content.split()
        command = "!"+args[1].lower()
        if command == "!disable" or command == "!enable":
            await error("[401] You cannot disable that command!", message.channel)
        else:    
            disabledCommands = db_query("varsity.db", "SELECT command FROM disabledCommands WHERE command = '%s'" % (command))
            if len(disabledCommands) == 0:
                execute_query("varsity.db", "INSERT INTO disabledCommands VALUES ('%s')" % (command)) 
                await ctx.send(":ok_hand: Successfully disabled `%s`" % command)
            else:
                await ctx.send("Hmm, Looks as if that command is already disabled.")
        
#!enable    
@Bot.command(client)
async def enable(ctx, *args):
    '''
    Allow the Moderation Team to enable a command that was prviously disabled.

    Required Permission: @Moderator
    Required Arguments: Command

    '''
    if await hasPerms(32, ctx):
        message = ctx.message
        args = message.content.split()
        command = "!"+args[1]
        disabledCommands = db_query("varsity.db", "SELECT command FROM disabledCommands WHERE command = '%s'" % (command))
        if len(disabledCommands) == 0:
            await ctx.send("Hmm, Doesn't look like that command is disabled at the moment.")
        else:    
            execute_query("varsity.db", "DELETE FROM disabledCommands WHERE command = '%s'" % (command)) 
            await ctx.send(":ok_hand: Successfully enabled `%s`" % command)
        

@Bot.command(client)
async def statmod(ctx, *args):
    '''
    Allow the Moderation Team to manually edit the stats stored in the database for a specified user.

    Required Permission: @Moderator
    Required Arguments: User Mention
    Optional Arguments: Modifier, Stat

    '''
    if await hasPerms(32, ctx):
        message = ctx.message
        args = message.content.split()
        user = discord.utils.get(message.guild.members, mention=args[1])
        profile = get_profile(user.id)
        if len(args) == 2:
            em = discord.Embed(title="Statmod", description="You are able to modify the following stats for user %s" % (user.name), color=reds)
            em.add_field(name="balance", value=str(profile[0]))
            em.add_field(name="profileColour", value=str(profile[4]))
            em.add_field(name="profileHashtag", value=str(profile[5]))
            em.add_field(name="exp", value=str(profile[2]))
            em.add_field(name="statAtk", value=str(profile[7]))
            em.add_field(name="statDef", value=str(profile[8]))
            em.add_field(name="statHp", value=str(profile[9]))
            await message.channel.send(embed=em)
        elif len(args) == 1:
            await ctx.send("Invalid Usage, Please supply a user")
        else:   
            subcommand = args[2]
            
            if subcommand.upper() == "SET":
                if args[3].upper() == "BALANCE":
                    set_coins(user, int(args[4]))
                    await message.channel.send(":ok_hand: Successfully set %s's balance to $%s" % (user.mention, args[4]))
                elif args[3].upper() == "PROFILECOLOUR":
                    execute_query("varsity.db", "UPDATE Members SET profileColour = '%s' WHERE UserID = %s" % (str(args[4]), str(user.id)))
                    await message.channel.send(":ok_hand: Successfully set %s's profile colour to %s" % (str(user.mention), str(args[4])))
                elif args[3].upper() == "PROFILEHASHTAG":
                    execute_query("varsity.db", "UPDATE Members SET profileHashtag = '%s' WHERE UserID = %s" % (str(args[4]), str(user.id)))
                    await message.channel.send(":ok_hand: Successfully set %s's profile hashtag to %s" % (str(user.mention), str(args[4])))
                elif args[3].upper() == "STATATK":
                    execute_query("varsity.db", "UPDATE Members SET statAtk = %s WHERE UserID = %s" % (str(args[4]), str(user.id)))
                    await message.channel.send(":ok_hand: Successfully set %s's attack stat to %s" % (str(user.mention), str(args[4])))
                elif args[3].upper() == "STATDEF":
                    execute_query("varsity.db", "UPDATE Members SET statDef = %s WHERE UserID = %s" % (str(args[4]), str(user.id)))
                    await message.channel.send(":ok_hand: Successfully set %s's attack stat to %s" % (str(user.mention), str(args[4])))
                elif args[3].upper() == "STATHP":
                    execute_query("varsity.db", "UPDATE Members SET statDef = %s WHERE UserID = %s" % (str(args[4]), str(user.id)))
                    await message.channel.send(":ok_hand: Successfully set %s's attack stat to %s" % (str(user.mention), str(args[4])))
                else:
                    await message.channel.send("%s does not support SET modifier" % (args[3].lower()))    

            elif subcommand.upper() == "ADD":
                if args[3].upper() == "BALANCE":
                    add_coins(user, int(args[4]))
                    await message.channel.send(":ok_hand: Successfully added $%s to %s's balance!" % (args[4], user.mention))
                elif args[3].upper() == "STATATK":
                    new = int(args[4]) + int(profile[7])
                    execute_query("varsity.db", "UPDATE Members SET statAtk = %s WHERE UserID = %s" % (str(new), str(user.id)))
                    await message.channel.send(":ok_hand: Successfully added %s to %s's attack stat!" % (str(new), str(user.mention)))
                elif args[3].upper() == "STATDEF":
                    new = int(args[4]) + int(profile[8])
                    execute_query("varsity.db", "UPDATE Members SET statDef = %s WHERE UserID = %s" % (str(new), str(user.id)))
                    await message.channel.send(":ok_hand: Successfully added %s to %s's defense stat!" % (str(new), str(user.mention)))
                elif args[3].upper() == "STATHP":
                    new = int(args[4]) + int(profile[9])
                    execute_query("varsity.db", "UPDATE Members SET statDef = %s WHERE UserID = %s" % (str(new), str(user.id)))
                    await message.channel.send(":ok_hand: Successfully added %s to %s's health stat !" % (str(new), str(user.mention)))
                elif args[3].upper() == "EXP":
                    add_exp(user.id, int(args[4]))
                    await message.channel.send(":ok_hand: Successfully added %s to %s's exp!" % (str(args[4]), str(user.mention)))
                else:
                    await message.channel.send("%s does not support ADD modifier" % (args[3].lower()))  
                    
            elif subcommand.upper() == "WIPE":
                em = discord.Embed(title="STAT WIPE", description="You are about to wipe the stats of %s!\n\n This will completely reset their stats as if they were a new user.\n**THIS OPERATION CANNOT BE REVERSED**\n\n**Punishments will not be reset**\n\nPlease wait **15 Seconds** before confirming this action." % (user.mention), colour=0xAA0000)
                em.set_thumbnail(url="https://www.freeiconspng.com/uploads/status-warning-icon-png-29.png")
                confirmation = await message.channel.send(embed=em)
                await asyncio.sleep(15)
                await confirmation.add_reaction("\U0001F44D")
                await confirmation.add_reaction("\U0001F44E")

                def check(reaction, actor):
                    return actor == message.author and (str(reaction.emoji) == '\U0001F44D' or str(reaction.emoji) == "\U0001F44E")
                try:
                    reaction, actor = await client.wait_for('reaction_add', timeout=60.0, check=check)
                except asyncio.TimeoutError:
                    await message.channel.send('Timed Out')
                    await confirmation.clear_reactions()
                else:
                    if str(reaction.emoji) == "\U0001F44D":
                        execute_query("varsity.db", "DELETE FROM Members WHERE UserID = %s" % (user.id))
                        insert_db_user(user) #Recreates the user with default stats
                        await message.channel.send(":ok_hand: Complete! %s's Stats have been wiped!" % (user.mention))
                        
                    elif str(reaction.emoji) == "\U0001F44E":
                        await message.channel.send("Operation Cancelled")
                    await confirmation.clear_reactions()
            else:
                em = discord.Embed(title="Statmod", description="You are able to modify the following stats for user %s" % (user.name), color=reds)
                em.add_field(name="balance", value=str(profile[0]))
                em.add_field(name="profileColour", value=str(profile[4]))
                em.add_field(name="profileHashtag", value=str(profile[5]))
                em.add_field(name="exp", value=str(profile[2]))
                em.add_field(name="statAtk", value=str(profile[7]))
                em.add_field(name="statDef", value=str(profile[8]))
                em.add_field(name="statHp", value=str(profile[9]))
                await message.channel.send(embed=em)
         
@Bot.command(client)
async def announce(ctx):
    if await hasPerms(32, ctx):
        args = ctx.message.content.split(" ")
    
        announcement = " ".join(args[2:])
        if args[1].upper() == "SERVER":
            role = discord.utils.get(ctx.message.guild.roles, name="Server Announcements")
            await role.edit(mentionable=True)
            await client.get_channel(473284532800454667).send("%s\n%s\n_ _\nSent By: **%s**" % (role.mention, announcement, str(ctx.message.author)))
            await role.edit(mentionable=False)
        if args[1].upper() == "SERVER-NOPING":
            await client.get_channel(473284532800454667).send("%s\n_ _\nSent By: **%s**" % (announcement, str(ctx.message.author)))
        if args[1].upper() == "WILFRED-DEV":
            role = discord.utils.get(ctx.message.guild.roles, name="Wilfred Development")
            await role.edit(mentionable=True)
            await client.get_channel(523991937200422933).send("%s\n%s\n_ _\nSent By: **%s**" % (role.mention, announcement, str(ctx.message.author)))
            await role.edit(mentionable=False)            
            

@Bot.command(client)
async def raffle(ctx):
    if await hasPerms(16, ctx):
        global enteries
        global raffles
        args = ctx.message.content.split(" ")
        item = " ".join(args[2:])
        time = int(args[1])*60
        em = discord.Embed(title="Raffle!", description="A Raffle Has Been Started! Type `!enter` to be in with a chance to win `%s`! Raffle closes in `%s Minutes`" % (item, str(args[1])), colour=0xFF55FF) 
        await ctx.message.channel.send(embed=em)
        raffles = True
        await asyncio.sleep(time)
        raffles = False
        winner = random.choice(enteries)
        em = discord.Embed(title="Raffle Winner!", description="Congratulations `%s`! You won `%s`!" % (winner, item), colour=0xFF55FF) 
        await ctx.message.channel.send(embed=em)
        enteries.clear()

@Bot.command(client)
async def giveall(ctx):
    if await hasPerms(32, ctx):
        args = ctx.message.content.split(" ")
        if args[1].upper() == "EXP":
            amount = args[2]
            for member in ctx.message.guild.members:
                try:
                    add_exp(member.id, int(amount))
                except:
                    await ctx.message.channel.send("Error occured for user %s" % (member))

                
@Bot.command(client)
async def giveitem(ctx):
    if await hasPerms(32, ctx):
        args = ctx.message.content.split(" ")
        member = discord.utils.get(ctx.message.guild.members, mention=args[1])
        if args[2].upper() == "EXP":
            amount = args[3]
            if int(amount) < 0:
                await error("Cannot Give Negative EXP!", ctx.message.channel)
            else:    
                add_exp(member.id, int(amount))
                await ctx.message.channel.send(":ok_hand: Successfully given `%s` **%s EXP**!" % (member.name, amount))

        elif args[2].upper() == "ELF-ROLE":
            role = discord.utils.get(ctx.message.guild.roles, name="Christmas Elf")
            await member.add_roles(role)
            await ctx.message.channel.send(":ok_hand: Successfully given `%s` **Christmas Elf Role**!" % (member.name))

        else:
            item = " ".join(args[2:])
            give_item(item, member)
            await ctx.message.channel.send(":ok_hand: Successfully given `%s` **%s**!" % (member.name, item))

@Bot.command(client)
async def multiplier(ctx):
    if await hasPerms(32, ctx):
        args = ctx.message.content.split(" ")
        multiplier = int(args[1])
        level_up(1, multiplier)
        await ctx.message.channel.send(":ok_hand:, Successfully set exp multiplier to %s" % (args[1]))

@Bot.command(client)
async def comment(ctx):
    if await hasPerms(2, ctx):
        args = ctx.message.content.split(" ")
        if len(args) <= 1:
            await error("Invalid Command Usage - Not enough args", ctx.message.channel)
            return
        suggestion = await client.get_channel(483767654914588683).get_message(int(args[1]))
        embed = suggestion.embeds[0]
        embed.add_field(name="%s's Comment" % (ctx.message.author.name), value=" ".join(args[2:]), inline=False)
        await suggestion.edit(embed=embed)
        await ctx.message.delete()


@Bot.command(client)
async def suggestion(ctx):
    if await hasPerms(32, ctx):
        args = ctx.message.content.split(" ")
        if len(args) <= 1:
            await error("Invalid Command Usage - Not enough args", ctx.message.channel)
            return
        if args[2].upper() == "STATUS":
            suggestion = await client.get_channel(483767654914588683).get_message(int(args[1]))
            embed = suggestion.embeds[0]
            embed.set_field_at(0, name="Status", value=args[3].capitalize())
        if args[2].upper() == "ASSIGN":
            suggestion = await client.get_channel(483767654914588683).get_message(int(args[1]))
            embed = suggestion.embeds[0]
            embed.set_field_at(1, name="Assigned To", value=args[3])
        if args[2].upper() == "COMMENT":
            suggestion = await client.get_channel(483767654914588683).get_message(int(args[1]))
            embed = suggestion.embeds[0]
            embed.add_field(name="Comment", value=" ".join(args[3:]), inline=False)
        await suggestion.edit(embed=embed)
        await ctx.message.delete()
            
            
        
#-----Event Listners-----        
        
@client.event
async def on_ready():
    global Loop
    print("active")
    execute_query("varsity.db", "UPDATE Members SET expPersonalBoost = 1")
    level_up(1, 1)
    activity=discord.Game(name="Wilfred %s" % (str(buildVersion)))
    await client.change_presence(activity=activity)
    channel = client.get_channel(521326677960294400)
    LBoardExp = await channel.get_message(521326939529805845)
    LBoardBal = await channel.get_message(521326947150856235)
    #LBoardEvent = await channel.get_message(521340954494631977)
    #LBoardRecords = await channel.get_message(526129403818672138)
    if Loop:
        return
    loop = True
    while True:
        try:
            leaderboard = db_query("varsity.db", "SELECT UserID, Level, expTotal FROM Members WHERE NOT UserID = 472063067014823938 AND NOT UserID = 1 ORDER BY expTotal DESC")
            index=0
            for userID in leaderboard:
                user = discord.utils.get(channel.guild.members, id=userID[0])
                try:
                    user.name
                except AttributeError:    
                    leaderboard.pop(index)
                index = index+1
            lbString = ""
            lbString = lbString + ":crown: **1st <@%s> - Level %s (%s exp)**\n_ _\n" % (str(leaderboard[0][0]), str(leaderboard[0][1]), str(leaderboard[0][2]))
            lbString = lbString + "**2nd <@%s> - Level %s (%s exp)**\n_ _\n" % (str(leaderboard[1][0]), str(leaderboard[1][1]), str(leaderboard[1][2]))
            lbString = lbString + "**3rd <@%s> - Level %s (%s exp)**\n_ _\n" % (str(leaderboard[2][0]), str(leaderboard[2][1]), str(leaderboard[2][2])) 
            for count in range(3,10):
                lbString = lbString + "%sth <@%s> - Level %s (%s exp)\n" % (str(count+1), str(leaderboard[count][0]), str(leaderboard[count][1]), str(leaderboard[count][2]))

            em = discord.Embed(title="Leaderboard", description=lbString, colour=secondary)
            em.add_field(name="Current EXP Multipler", value=str(get_booster(1)))
            em.set_footer(text="Last Updated: %s" % (time.strftime("%a, %H:%M:%S", time.gmtime()))) 
            await LBoardExp.edit(embed=em, content=None)

            leaderboard = db_query("varsity.db", "SELECT UserID, Balance FROM Members WHERE NOT UserID = 472063067014823938 AND NOT UserID = 1 ORDER BY Balance DESC")
            #stats = db_query("varsity.db", "SELECT mostBal, mostBalHeldBy FROM serverStats")[0]
            index = 0
            for userID in leaderboard:
                user = discord.utils.get(channel.guild.members, id=userID[0])
                try:
                    user.name
                except AttributeError:    
                    leaderboard.pop(index)
                index = index+1    
            lbString = ""
            lbString = lbString + ":crown: **1st <@%s> - $%s**\n_ _\n" % (str(leaderboard[0][0]), str(balance_formatter(leaderboard[0][1])))
            lbString = lbString + "**2nd <@%s> - $%s**\n_ _\n" % (str(leaderboard[1][0]), str(balance_formatter(leaderboard[1][1])))
            lbString = lbString + "**3rd <@%s> - $%s**\n_ _\n" % (str(leaderboard[2][0]), str(balance_formatter(leaderboard[2][1]))) 
            for count in range(3,10):
                lbString = lbString + "%sth <@%s> - $%s\n" % (str(count+1), str(leaderboard[count][0]), str(balance_formatter(leaderboard[count][1])))
            total_balance = 0    
            for balance in leaderboard:
                    total_balance = total_balance+balance[1]

            lbString = lbString + "_ _\nThe servers total balance is: **$%s**" % (balance_formatter(total_balance))        
            em = discord.Embed(title="Baltop", description=lbString, colour=secondary)
            em.set_footer(text="Last Updated: %s" % (time.strftime("%a, %H:%M:%S", time.gmtime()))) 
            await LBoardBal.edit(embed=em, content=None)

            multiplier = get_booster(1)
            for member in client.get_channel(529107387559444500).members:
                pMultiplier = get_booster(member.id)
                add_exp(member.id, 2*multiplier*pMultiplier)
            for member in client.get_channel(530196127388008448).members:
                pMultiplier = get_booster(member.id)
                add_exp(member.id, 2*multiplier*pMultiplier)

            multipliers = db_query("SELECT boosterId, expires FROM boosters WHERE isActive = 1")
            for multiplier in multiplier:
                if multiplier[1] < time.time():
                    execute_query("UPDATE boosters SET isActive = 0 WHERE boosterId = %s" % (str(multiplier[0]))) 
        except:
            pass #basically gonna stop the whole thing breaking
        await asyncio.sleep(60)
 
#Pre Command Invoke Processing
@client.event
async def on_message(message):
      
    mSplit = message.content.split()
    mList = []
    for word in mSplit:
        user = discord.utils.get(message.guild.members, mention=word.replace("@", "@!").replace("!!", "!")) #To prevent issues with mentioning not working in args for mobile users (A formatting issue on Discord's end which they refuse to fix...)
        if not user is None:
            if not user.nick is None:
                word = word.replace("@", "@!").replace("!!", "!")
        mList.append(word)
    message.content = " ".join(mList)
    
    args = message.content.split(" ")

    if args[0] in ["?playing", "?play", "?next", "?skip", "?playlist", "?register", "?volume", "?say"]:
        if await hasPerms(16, message):
            pass
        
    disabledCommands = db_query("varsity.db", "SELECT command FROM disabledCommands WHERE command = '%s'" % (command))
    if len(disabledCommands) > 0:
        await error("[423] This command is currently disabled", message.channel)
    else:
        channel = message.channel
        
        '''We'll keep this encase we want to enable it again for some random reason'''
        #for each in args:
        #    if each.upper()=="MAY":
        #        quote = random.choice(["The Government cannot just be consumed by Brexit. There is so much more to do", "My whole philosophy is about doing, not talking.", "I actually think I think better in high heels", "I've been clear that Brexit means Brexit", "I think we all agree that the comments Donald Trump made in relation to Muslims were divisive, unhelpful and wrong.", "There must be no attempts to remain inside the E.U., no attempts to rejoin it through the back door, and no second referendum.", "Strong and Stable leadership"])
        #        await message.channel.send(quote)
                         
        if message.channel.id == gate:
            await message.delete()        
      
        elif message.content.upper().startswith("!ENTER"):
            global raffles
            global enteries
            if raffles and not message.author.name in enteries:
                enteries.append(message.author.name)
                await message.channel.send("%s has been entered!" % (message.author.name))
            elif raffles:
                await message.channel.send("You are already entered")

        #--Role Commands--             

        elif message.content.upper().startswith("!WINDOWS"):
            role = discord.utils.get(message.guild.roles, name="Windows Insiders")
            if not role.name in [r.name for r in message.author.roles]:
                await message.author.add_roles(role)
                await message.channel.send("Successfully added you to the **Windows Insiders** announcement group")
            else:
                await message.author.remove_roles(role)
                await message.channel.send("Successfully removed you from the **Windows Insiders** announcement group")

        elif message.content.upper().startswith("!APPLE"):
            role = discord.utils.get(message.guild.roles, name="Apple Developers")
            if not role.name in [r.name for r in message.author.roles]:
                await message.author.add_roles(role)
                await message.channel.send("Successfully added you to the **Apple Developers** announcement group")
            else:
                await message.author.remove_roles(role)
                await message.channel.send("Successfully removed you from the **Apple Developers** announcement group")
                
        elif message.content.upper().startswith("!ANDROID"):
            role = discord.utils.get(message.guild.roles, name="Android Beta")
            if not role.name in [r.name for r in message.author.roles]:
                await message.author.add_roles(role)
                await message.channel.send("Successfully added you to the **Android Beta** announcement group")
            else:
                await message.author.remove_roles(role)
                await message.channel.send("Successfully removed you from the **Android Beta** announcement group")
                
        elif message.content.upper().startswith("!TECH"):
            role = discord.utils.get(message.guild.roles, name="Technology")
            if not role.name in [r.name for r in message.author.roles]:
                await message.author.add_roles(role)
                await message.channel.send("Successfully added you to the **Technology** announcement group")
            else:
                await message.author.remove_roles(role)
                await message.channel.send("Successfully removed you from the **Technology** announcement group")
                
        elif message.content.upper().startswith("!SERVER"):
            role = discord.utils.get(message.guild.roles, name="Server Announcements")
            if not role.name in [r.name for r in message.author.roles]:
                await message.author.add_roles(role)
                await message.channel.send("Successfully added you to the **Server Announcements** announcement group")
            else:
                await message.author.remove_roles(role)
                await message.channel.send("Successfully removed you from the **Server Announcements** announcement group")

        elif message.content.upper().startswith("!WILFRED"):
            role = discord.utils.get(message.guild.roles, name="Wilfred Development")
            if not role.name in [r.name for r in message.author.roles]:
                await message.author.add_roles(role)
                await message.channel.send("Successfully added you to the **Wilfred Development** announcement group")
            else:
                await message.author.remove_roles(role)
                await message.channel.send("Successfully removed you from the **Wilfred Development** announcement group")

        elif message.content.upper().startswith("!SUDO"): #This needs to be moved under cmd-ext; Will be done at later stage ~Frank
            if hasPerms(32, message):
                args = message.content.split()
                target = discord.utils.get(message.guild.members, mention=args[1])
                channel = client.get_channel(int(args[2]))
                contents = " ".join(args[3:])
                message.content = contents
                message.author = target
                message.channel = channel
       
        elif message.content.upper().startswith("W!UPDATE"):
            for member in message.guild.members:
                try:
                    #insert_db_user(member)
                    execute_query("varsity.db", "UPDATE Members SET displayName = '%s' WHERE UserID = %s" % (member.name, str(member.id)))
                except:
                    pass

    if message.channel.id in [473284192491536384, 483940602040549376]:
        hasMsg = db_query("varsity.db", "SELECT devMsg FROM Members WHERE UserID = %s" % (str(message.author.id)))[0][0]
        if hasMsg == 0:
            execute_query("varsity.db", "UPDATE Members SET devMsg = 1 WHERE UserID = %s" % (str(message.author.id)))
            em = discord.Embed(title="Welcome %s!" % (message.author.name), description="""Looks like you're new around here. Let's give you some pointers!

When you're seeking help please note the following:
- Be specific in what your issue is
- Provide error logs where applicable
- Is the issue something you can fix on your own? We are not going to spoon feed you.
- We are not going to write the code for you. If you're wondering how to do something Google it. We want to give people the ability to code independently

With that said, please be patient in waiting for a response, we have lives too!

You may also ping a proficient found in the channel topic for assistance.

Have fun!""", color=primary)

            await message.channel.send(embed=em)

    if message.channel.id == 473284044650577920:
        hasMsg = db_query("varsity.db", "SELECT cmdMsg FROM Members WHERE UserID = %s" % (str(message.author.id)))[0][0]
        if hasMsg == 0:
            execute_query("varsity.db", "UPDATE Members SET cmdMsg = 1 WHERE UserID = %s" % (str(message.author.id)))
            em = discord.Embed(title="Welcome %s!" % (message.author.name), description="""Looks like you're new around here. Let's give you some pointers!

To get started, use **!help** to list the commands available to you.

Please be reminded that this is a commands only channel, discussion is not permitted within here.

Have fun!""", color=primary)

            await message.channel.send(embed=em)

    if not "Restricted" in [role.name for role in message.author.roles]:
        await client.process_commands(message)        

    if not str(message.author.id) in ignore_list and not str(message.channel.id) in ignore_list and not "Restricted" in [role.name for role in message.author.roles] and not message.guild == None:
        if not message.author.id in cooldown:
            multiplier = get_booster(1)
            pMultiplier = get_booster(message.author.id)
            bal = db_query("varsity.db", "SELECT Balance FROM Members WHERE UserID = %s" % (str(message.author.id)))[0][0]
            level = get_profile(message.author.id)[1]
            cooldown.append(message.author.id)
            balances = db_query("varsity.db", "SELECT Balance FROM Members WHERE NOT UserID = 1 AND NOT UserID = 472063067014823938 ORDER BY Balance DESC")
            total_balance = 0
            for balance in balances:
                total_balance = total_balance+balance[0]
            coins_add = random.randint(25,50)*level*multiplier*pMultiplier    
            if (bal/total_balance) * 100 > 25:
                coins_add = coins_add * 0.15
            elif (bal/total_balance) * 100 > 15:
                coins_add = coins_add * 0.50
            elif (bal/total_balance) * 100 > 15:
                coins_add = coins_add * 0.75    
            add_coins(message.author, coins_add)
            exp_add = int(random.randint(15, 25)*multiplier*pMultiplier)
            add_exp(message.author.id, exp_add)
            await check_level_up(message.author.id, message.guild, message.channel)
            await asyncio.sleep(60)
            cooldown.remove(message.author.id)
  
    '''Not sure if we will need to keep this about or not, if exp algorithms ever get changed or something breaks we'll need this'''
    #if message.content.upper() =="W!LEVELFIX":
    #    execute_query("varsity.db", "UPDATE Members SET Level = 1")
    #    for member in message.guild.members:
    #        try:
    #            tExp = db_query("varsity.db", "SELECT ExpTotal FROM Members WHERE UserID = %s" % (str(member.id)))[0][0] 
    #            execute_query("varsity.db", "UPDATE Members SET Exp = %s WHERE UserID = %s" % (str(tExp), str(member.id))) 
    #            await check_level_up(member.id, message.guild, message.channel)
    #        except IndexError:
    #            await message.channel.send("Something went wrong with %s" % (member.name))
    #    await message.channel.send("Done")       
        




@client.event
async def on_member_join(member):
    insert_db_user(member)
    #role = discord.utils.get(member.guild.roles, name="-----===== Notif Roles =====-----")
    #member.add_roles(role)
        
async def user_accept_rules(member):
    channel = client.get_channel(casual)
    total_members = 0
    em = discord.Embed(title="Welcome!", description="Hello %s, Welcome to **Varsity Discord**! We hope you enjoy your time here!" % (member.name), colour=primary)
    em.set_footer(text="We now have %s Members!" % (len(member.guild.members)))
    await channel.send(embed=em)
    #reg_role = discord.utils.get(member.guild.roles, name="Member")
    default_role = discord.utils.get(member.guild.roles, name="Regular")
    await member.add_roles(default_role)
    #await member.add_roles(reg_role)        
        
        
        
        
        


    
print("Test")    
client.run(token) #logs into the bot
