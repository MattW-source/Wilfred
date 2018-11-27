# -*- coding: utf-8 -*-
import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import time
from discord.voice_client import VoiceClient
import _thread as thread
import random

time.sleep(30) #Give Server time to init networking [Since this is now being autoran under SystemD] 

import pyspeedtest
st = pyspeedtest.SpeedTest()
conCooldown = False
from secrets import * #Token will be stored in here so I don't accidentally leak the admin token for my Discord again...

gate =  440205836208439348
casual = 473276007860797453

disabled_commands = []
rCooldowns = []
admin_bypass = [513115137184366597]
cooldown = []
ignore_list = ["388022143931383818", "426489102838530050", "427869023552667649"]

Client = discord.Client()
bot_prefix = "!"
client = commands.Bot(command_prefix=bot_prefix, case_insensitive=True)
client.remove_command("help")

#-----Helpers-----

#"/home/pi/varsity-discord/"+

def execute_query(table, query):
    conn = sqlite3.connect("/home/pi/varsity-discord/"+table)
    #conn = sqlite3.connect(table)
    c = conn.cursor()
    c.execute(query)
    conn.commit()
    c.close()
    conn.close()

def db_query(table, query):
    conn = sqlite3.connect("/home/pi/varsity-discord/"+table)
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
    if not details is None:
        eEm = discord.Embed(title="Error Report", description="An unexpected error occurred in `%s`.\nMessage: `%s`\nError: `%s`" % (channel.name, details.contents, reason), colour=0xFF5555)
        await client.get_channel(498910225475305483).send(embed=eEm)
#-----Processing-----
    
import sqlite3

def insert_db_user(member):
    try:
        execute_query("varsity.db", "INSERT INTO Members (UserID) VALUES ('%s')" % (member.id))
    except:
        warn("User already exists in Database")
        try:
            info(member.name)
        except:
            pass
        
def set_coins(user, coins):
    user_id = user.id
    execute_query("varsity.db", "UPDATE Members SET Balance = %s WHERE UserID = %s" % (str(coins), str(user_id)))


def fetch_coins(user):
    user_id = user.id
    coins = db_query("varsity.db", "SELECT Balance FROM Members WHERE UserID = %s" % (str(user_id)))[0][0]
    return coins

def add_coins(user, amount):
    current_coins = fetch_coins(user)
    new_coins = int(current_coins) + int(amount)
    set_coins(user, new_coins)

def get_profile(userID):
    profile = db_query("varsity.db", "SELECT Balance, Level, expTotal, Badges FROM Members WHERE UserID = %s" % (userID))[0]
    return profile

def level_up(userID, level):
    execute_query("varsity.db", "UPDATE Members SET Level = %s WHERE UserID = %s" % (str(level), str(userID)))   

async def check_level_up(userID, guild, channel):
    Checking = True 
    while Checking: 
        level_data = db_query("varsity.db", "SELECT Exp, Level FROM Members WHERE UserID = %s" % (str(userID)))[0]
        Exp = level_data[0]
        lvl = level_data[1]
        Required = 5 * (lvl ^ 2) + 50 * lvl + 100
        if Exp >= Required:
            level_up(userID, lvl+1)
            sub_exp_only(userID, Required)
            lvl = lvl+1
            if lvl == 10:
                new_role = discord.utils.get(guild.roles, name="Uber Regular")
                user = discord.utils.get(guild.members, id=userID)
                await user.add_roles(new_role)
                add_coins(user, 10000)
                await channel.send(embed=discord.Embed(title="Level Up!", description="Congratulations %s! You've reached Level 10! That means you've unlocked the `Uber Regular` role! You've also been awarded $10000 for your achievement!" % (user.mention)))  
            if lvl == 20:
                new_role = discord.utils.get(guild.roles, name="Outstandingly Regular")
                user = discord.utils.get(guild.members, id=userID)
                await user.add_roles(new_role)
                add_coins(user, 20000)
                await channel.send(embed=discord.Embed(title="Level Up!", description="Congratulations %s! You've reached Level 20! That means you've unlocked the `Outstandingly Regular` role! You've also been awarded $20000 for your achievement!" % (user.mention)))
            if lvl == 30:
                new_role = discord.utils.get(guild.roles, name="Super Outstandingly Regular")
                user = discord.utils.get(guild.members, id=userID)
                await user.add_roles(new_role)
                add_coins(user, 30000)
                await channel.send(embed=discord.Embed(title="Level Up!", description="Congratulations %s! You've reached Level 30! That means you've unlocked the `Super Outstandingly Regular` role! You've also been awarded $30000 for your achievement!" % (user.mention)))
            if lvl == 40:
                new_role = discord.utils.get(guild.roles, name="Ultra Super Outstandingly Regular")
                user = discord.utils.get(guild.members, id=userID)
                await user.add_roles(new_role)
                add_coins(user, 40000)
                await channel.send(embed=discord.Embed(title="Level Up!", description="Congratulations %s! You've reached Level 40! That means you've unlocked the `Ultra Super Outstandingly Regular` role! You've also been awarded $40000 for your achievement!" % (user.mention)))
            if lvl == 50:
                new_role = discord.utils.get(guild.roles, name="Extremely Ultra Super Outstandingly Regular")
                user = discord.utils.get(guild.members, id=userID)
                await user.add_roles(new_role)
                add_coins(user, 50000)
                await channel.send(embed=discord.Embed(title="Level Up!", description="Congratulations %s! You've reached Level 50! That means you've unlocked the `Extremely Ultra Super Outstandingly Regular` role! You've also been awarded $50000 for your achievement!" % (user.mention)))
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

def get_rank(user):
    rank = []
    if "Admin" in [role.name for role in user.roles]:
        rank.append("Admin")
        rank.append("https://cdn.discordapp.com/emojis/486269879327129601.png")
    elif "Moderator" in [role.name for role in user.roles]:
        rank.append("Moderator")
        rank.append("https://cdn.discordapp.com/emojis/486269879327129601.png")
    elif "Contributor" in [role.name for role in user.roles]:
        rank.append("Contributor")
        rank.append("https://cdn.discordapp.com/emojis/486265111795728384.png")
    elif "Artist" in [role.name for role in user.roles]:
        rank.append("Artist")
        rank.append("https://cdn.discordapp.com/emojis/486266771418906626.png")
    else:
        rank.append("Member")
        rank.append("https://cdn.discordapp.com/emojis/486269178047627266.png")

    return rank


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

#--Event Commands--
#!tot
'''@Bot.command(client)
async def tot(ctx):
    message = ctx.message
    if fetch_coins(ctx.message.author) >= 2500:
        add_coins(ctx.message.author, -2500)
        treat = random.choice([True, False, False])
        if treat:
            treatItem = random.choice(["c3000", "c5000", "c7500", "c10000", "c12500", "c15000", "r1", "b<:Halloween2018:500684505829605386>"])
            if treatItem[0] == "r":
                rankUpChance = random.randint(1, 2)
                rank = db_query("varsity.db", "SELECT Rank from Members WHERE UserID = %s" % (str(message.author.id)))[0][0]
                if rankUpChance == 1 and not rank == "X":
                    new_rank = db_query("varsity.db", "SELECT RankName FROM ranks WHERE RankID = '%s'" % (str(db_query("varsity.db", "SELECT RankID FROM ranks WHERE RankName = '%s'" % (rank))[0][0]+1)))[0][0]
                    execute_query("varsity.db", "UPDATE Members SET Rank = '%s' WHERE UserID = %s" % (new_rank, str(message.author.id)))
                    em = discord.Embed(title="Treat!", description="Congratulations! You've been ranked up to Rank %s" % (new_rank), colour=0xE67E22)
                    await message.channel.send(embed=em)
                else:
                    treatItem = random.choice(["c3000", "c5000", "c7500", "c10000", "c12500", "c15000"])
            if treatItem[0] == "b":
                badge = "".join(treatItem[1:])
                current_badges = get_profile(str(message.author.id))[3]
                if not badge in current_badges:
                    new_badges = current_badges + badge +" _ _"
                    execute_query("varsity.db", "UPDATE Members SET Badges = '%s' WHERE UserID = %s" % (new_badges, str(message.author.id)))
                    em = discord.Embed(title="Treat!", description="Congratulations! You've unlocked the %s badge! You can view it on your profile!" % (badge), colour=0xE67E22)
                    await message.channel.send(embed=em)
                else:    
                    treatItem = random.choice(["c3000", "c5000", "c7500", "c10000", "c12500", "c15000"]) 
            if treatItem[0] == "c":
                add_coins(message.author, int("".join(treatItem[1:])))
                em = discord.Embed(title="Treat!", description="Congrats! You've been given $%s!" % ("".join(treatItem[1:])), colour=0xE67E22)
                await message.channel.send(embed=em)

        else:
            trickItem = random.randint(1,3)
            if trickItem == 1: #remove half their balance (so very evil)
                balance = fetch_coins(message.author)
                try:
                    new_balance = int(int(balance)/2)
                except ZeroDivisionError:
                    new_balance = 0
                set_coins(message.author, new_balance)
                em = discord.Embed(title="Trick!", description="Oh no! Evil goblins stole half your money! You now have $%s" % (str(new_balance)), colour=0x9B59B6)
            else:
                em = discord.Embed(title="Trick!", description="Oh no! You got nothing!", colour=0x9B59B6)
            await message.channel.send(embed=em)
    else:
        await message.channel.send("Not enough funds, you need $2500 to do this!")
                                       
                    
'''

@Bot.command(client)
async def buy(ctx):
    message = ctx.message
    args = message.content.split(" ")
    try:
        if args[1].upper() == "ELF-ROLE":
            balance = fetch_coins(message.author)
            if balance > 50000:
                confirmation = await message.channel.send("You are about to purchase temporary custom role `Christmas Elf`, This role will expire in `At the end of the Christmas Event (Jan 6th)` This will cost `$50000`\n**WARNING IF YOU HAVE ALREADY RECEIVED THIS ROLE DO NOT PURCHASE AGAIN AS YOU WILL BE CHARGED**")
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
                        add_coins(user, -50000)
                        role = discord.utils.get(message.guild.roles, name="Christmas Elf")
                        await user.add_roles(role)
                    elif str(reaction.emoji) == "\U0001F44E":
                        await message.channel.send("Declined")
                await confirmation.clear_reactions()
            else:
                await message.channel.send("Insufficient Funds") 
        else:
            await message.channel.send('''The following things are available for purchase

    `ELF-ROLE` - Christmas Event Custom Role - `$50000`'''
    )
    except IndexError:
        await message.channel.send('''The following things are available for purchase

    `ELF-ROLE` - Christmas Event Custom Role - `$50000`'''
    )
        
            
            
        
    

#--Profile/Economy/User Commands--

#!daily
@Bot.command(client)
async def daily(ctx):
    return

    message = ctx.message
    
    commons = ["c3000"]
    uncommons = ["c5000", "c7500"]
    rares = ["c10000"]
    legendaries = ["c12500"]
    mythicals = ["c15000"]
    rewards = []
    rewardMsgs = []

    def getReward(reward):
        if reward[0] == "c":
            return "$" + "".join(reward[1:])
    
    for count in range(1,4):
        rewardLevel = random.randint(1, 20)
        if rewardLevel <= 7:
            reward = random.choice(commons)
            rewardText = getReward(reward)
            rewards.append(reward)
            em = discord.Embed(title="[%s] COMMON" % (str(count)), description="Common %s" % (rewardText), color=0xAAAAAA) 
        elif rewardLevel <= 14:
            reward = random.choice(uncommons)
            rewardText = getReward(reward)
            rewards.append(reward)
            em = discord.Embed(title="[%s] UNCOMMON" % (str(count)), description="Uncommon %s" % (rewardText), color=0x00AA00) 
        elif rewardLevel <= 17:
            reward = random.choice(rares)
            rewardText = getReward(reward)
            rewards.append(reward)
            em = discord.Embed(title="[%s] RARE" % (str(count)), description="Rare %s" % (rewardText), color=0xAA00AA) 
        elif rewardLevel <= 19:
            reward = random.choice(legendaries)
            rewardText = getReward(reward)
            rewards.append(reward)
            em = discord.Embed(title="[%s] LEGENDARY" % (str(count)), description="Legendary %s" % (rewardText), color=0xFFAA00) 
        elif rewardLevel == 20:
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
            

            



    ## 1⃣ 2⃣ 3⃣

    

    

            

            
            
        

#!help
@Bot.command(client)
async def help(ctx):
    helpEm = discord.Embed(title="!help", description="Shows the list of commands", color=0x5555FF)
    helpEm.add_field(name=":tada: Event Commands", value="!buy <item>", inline=False)
    helpEm.add_field(name="<:member:486269178047627266> User Commands", value="!profile [@user]\n!pay <@user> <amount>\n!ransack <@user> <amount>\n!ping\n!connection", inline=False)
    specialCommands = ""
    if "☆" in [role.name for role in ctx.message.author.roles] or "Staff" in [role.name for role in ctx.message.author.roles] or ctx.message.author.id in admin_bypass:
        specialCommands = specialCommands + "!hug <@user>\n"
    if "☆☆" in [role.name for role in ctx.message.author.roles] or "Staff" in [role.name for role in ctx.message.author.roles] or ctx.message.author.id in admin_bypass:
        specialCommands = specialCommands + "!fight <@user>\n"
    if "☆" in [role.name for role in ctx.message.author.roles] or "☆☆" in [role.name for role in ctx.message.author.roles] or "☆☆☆" in [role.name for role in ctx.message.author.roles] or ctx.message.author.id in admin_bypass:     
        helpEm.add_field(name=":gem: Special Commands", value=specialCommands, inline=False)    
    if "Staff" in [role.name for role in ctx.message.author.roles] or ctx.message.author.id in admin_bypass:
        helpEm.add_field(name="<:mooderator:486269879327129601> Staff Commands", value="!warn <@user> <reason>\n!kick <@user> <reason>\n!mute <@user> <severity> <reason>\n!ban <@user> <severity> <reason>", inline=False)
    if "Admin" in [role.name for role in ctx.message.author.roles] or ctx.message.author.id in admin_bypass:
        helpEm.add_field(name="<:Staff:486271130148012055> Admin Commands", value="!enable <command>\n!disable <command>\n!badge <add|remove> <emoji> <@user>\n!statmod <@user> <set|add|sub> <balance|rank|tier|statwipe> {amount}", inline=False)
    await ctx.message.channel.send(embed=helpEm)

#!profile
@Bot.command(client)
async def profile(ctx):
    message = ctx.message
    args = message.content.split()
    
    if len(args) <= 1:
        user = message.author
        profile = get_profile(str(message.author.id))
        
    else:
        user = discord.utils.get(message.guild.members, mention=args[1])
        profile = get_profile(str(user.id))
        if user.id == 472063067014823938:
            await error("[418] I'm a teapot", message.channel)
            return
    em = discord.Embed(title=user.name, colour=0xFFFF55)


    rank = get_rank(user)
    em.set_author(name=rank[0], icon_url=rank[1])

    badges = profile[3]

    em.add_field(name=badges, value="_ _ _ _ ")
    em.set_thumbnail(url=user.avatar_url)
    em.add_field(name="_ _ _ _", value="_ _ _ _")
    em.add_field(name="Level", value=str(profile[1]))
    #em.add_field(name="Tier", value=profile[2])
    em.add_field(name="Experience", value=str(profile[2]))

    em.add_field(name="Member Since", value=str(user.joined_at)[0:19])
    em.add_field(name="Balance", value="$"+str(int(profile[0])))
    #em.set_footer(text="")

    await message.channel.send(embed=em)
    
@Bot.command(client)
async def balance(ctx):
    profile = get_profile(str(ctx.message.author.id))
    uBalance = profile[0]
    balances = db_query("varsity.db", "SELECT Balance FROM Members ORDER BY Balance DESC")
    total_balance = 0
    highest_balance = balances[0][0]
    for balance in balances:
        total_balance = total_balance+balance[0]
    em = discord.Embed(title="Balance", description="You currently have **$%s**\nThe server total is **$%s**\nThe highest balance is **$%s**" % (str(uBalance), str(total_balance), str(highest_balance)), color=0x55FF55)   
    await ctx.message.channel.send(embed=em)

@Bot.command(client)
async def leaderboard(ctx):
    leaderboard = db_query("varsity.db", "SELECT UserID, Level, expTotal FROM Members WHERE NOT UserID = 472063067014823938 ORDER BY expTotal DESC")
    lbString = ""
    lbString = lbString + "**1st <@%s> - Level %s (%s exp)**\n_ _\n" % (str(leaderboard[0][0]), str(leaderboard[0][1]), str(leaderboard[0][2]))
    lbString = lbString + "**2nd <@%s> - Level %s (%s exp)**\n_ _\n" % (str(leaderboard[1][0]), str(leaderboard[1][1]), str(leaderboard[1][2]))
    lbString = lbString + "**3rd <@%s> - Level %s (%s exp)**\n_ _\n" % (str(leaderboard[2][0]), str(leaderboard[2][1]), str(leaderboard[2][2])) 
    for count in range(3,10):
        lbString = lbString + "%sth <@%s> - Level %s (%s exp)\n" % (str(count+1), str(leaderboard[count][0]), str(leaderboard[count][1]), str(leaderboard[count][2]))

    em = discord.Embed(title="Leaderboard", description=lbString, colour=0x55FF55)
    await ctx.message.channel.send(embed=em)
#!pay
@Bot.command(client)
async def pay(ctx):
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
            
        em = discord.Embed(title="Transaction", description="Please confirm your payment of $%s to %s **Y/N**" % (str(amount), str(user.mention)), colour=0x55FF55)
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

#!rankup
@Bot.command(client)
async def rankup(ctx):
    await error("This command is now depreciated", ctx.message.channel)
    return
    message = ctx.message
    args = message.content.split()
    rank = db_query("varsity.db", "SELECT Rank from Members WHERE UserID = %s" % (str(message.author.id)))[0][0]
    tier = db_query("varsity.db", "SELECT Tier from Members WHERE UserID = %s" % (str(message.author.id)))[0][0]
    if rank == "X":
        em = discord.Embed(title="Error!", description="You've already reached the highest rank. Try **!prestige**", colour=0xFF5555)
        await message.channel.send(embed=em)
    else:
        cost = db_query("varsity.db", "SELECT RankUpCost_%s FROM ranks WHERE RankID = '%s'" % (str(tier), str(db_query("varsity.db", "SELECT RankID FROM ranks WHERE RankName = '%s'" % (rank))[0][0]+1)))[0][0]
        balance = fetch_coins(message.author)
        if cost > balance:
            em = discord.Embed(title="Insufficient Funds!", description="You currently have $%s\nYou need $%s more to rank up!" % (str(balance), str(cost-balance)), colour=0xFF5555)
            await message.channel.send(embed=em)
        else:
            em = discord.Embed(title="Rank Up", description="You currently have $%s\nAfter you rank up you will have $%s\n\nAre you sure you want to rank up?*" % (str(balance), str(balance-cost)), colour=0x55FF55)
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
                    new_rank = db_query("varsity.db", "SELECT RankName FROM ranks WHERE RankID = '%s'" % (str(db_query("varsity.db", "SELECT RankID FROM ranks WHERE RankName = '%s'" % (rank))[0][0]+1)))[0][0]
                    add_coins(message.author, -cost)
                    execute_query("varsity.db", "UPDATE Members SET Rank = '%s' WHERE UserID = %s" % (new_rank, str(message.author.id)))
                    em = discord.Embed(title="Success!", description="Congratulations! You've ranked up to Rank %s" % (new_rank), colour=0x55FFFF)
                    await message.channel.send(embed=em)
                elif str(reaction.emoji) == "\U0001F44E":
                    await message.channel.send("Rankup Declined")
                await confirmation.clear_reactions()

#!ransack
@Bot.command(client)
async def ransack(ctx):
    global rCooldowns
    message = ctx.message
    args = message.content.split(" ")
    user = discord.utils.get(message.guild.members, mention=args[1])
    amount = int(args[2])
    if fetch_coins(user) < amount:
        await error("[400] Target User Does Not Have Enough Balance!", message.channel)
    elif fetch_coins(message.author) < amount:
        await error("[400] You don't have enough balance for this!", message.channel)
    elif amount < 2500:
        await error("[400] Amount must be above $2500", message.channel) 
    elif message.author.id in rCooldowns:
        await error("[403] This command is on cooldown", message.channel)
    elif message.author == user:
        await error("[403] You cannot ransack yourself!", message.channel)
    else:
        rCooldowns.append(message.author.id) 
        chance = random.randint(1, int(round(amount/1000, 0)))
        if chance == 1:
            add_coins(user, -amount)
            add_coins(message.author, amount)
            await message.channel.send("Congrats! You successfully ransacked **%s** for **$%s**!\nYou may try again in 1 hour." % (user.name, str(amount))) 
        else:
            add_coins(message.author, -amount)
            await message.channel.send("You failed to ransack **%s** and were fined **$%s** for your attempt!\nYou may try again in 1 hour." % (user.name, str(amount)))

        await asyncio.sleep(3600)
        rCooldowns.remove(message.author.id)

#!prestige
@Bot.command(client)
async def prestige(ctx):
    await error("This command is now depreciated", ctx.message.channel)
    return
    message = ctx.message
    args = message.content.split()
    rank = db_query("varsity.db", "SELECT Rank from Members WHERE UserID = %s" % (str(message.author.id)))[0][0]
    tier = db_query("varsity.db", "SELECT Tier from Members WHERE UserID = %s" % (str(message.author.id)))[0][0]
    if not rank == "X":
        await error("[401] You need to reach rank X first!", message.channel)
    else:
        if tier == 3:
            await error("[401] You have reached max prestige!", message.channel) 
        else:
            em = discord.Embed(title="WARNING", description="Prestiging will reset your balance and rank back to defaults but will upgrade your tier and unlock new perks.\n\nRanking up again will cost more than it did last time!\n\nAre you sure you want to prestige? **Y/N**", colour=0xFF5555) 
            await message.channel.send(embed=em)

            def check(m):
                return m.author.id == message.author.id

            try:
                msg = await client.wait_for('message', check=check, timeout=30.0)
            except asyncio.TimeoutError:
                await channel.send("Did not respond in time, please try again!")
            else:
                if msg.content.upper() == "Y" or msg.content.upper() == "YES":
                    add_coins(message.author, -fetch_coins(message.author))
                    new_tier = tier + 1
                    execute_query("varsity.db", "UPDATE Members SET Tier = %s, Rank = 'I' where UserID = %s" % (str(new_tier), str(message.author.id)))
                    if new_tier == 1:
                        await message.author.add_roles(discord.utils.get(message.guild.roles, id=472094980350148608))
                    if new_tier == 2:
                        await message.author.add_roles(discord.utils.get(message.guild.roles, id=472095274618060831))
                    if new_tier == 3:
                        await message.author.add_roles(discord.utils.get(message.guild.roles, id=472095322378600458))
                    em = discord.Embed(title="Success!", description="Congratulations! You've prestiged to Tier %s!" % (new_tier), colour=0x55FFFF)
                    await message.channel.send(embed=em)
                    
                elif msg.content.upper() == "N" or msg.content.upper() == "NO":
                    await message.channel.send("Rankup Declined")
                else:
                    await message.channel.send("Invalid Response")
    
#--Connection Commands--

#!ping
@Bot.command(client)
async def ping(ctx):
    start = time.time() * 1000
    msg = await ctx.message.channel.send("Pong!")
    end = time.time() * 1000
    await msg.edit(content="Pong! `%sms`" % (str(int(round(end-start, 0)))))


#!connection
@Bot.command(client)
async def connection(ctx):
    message = ctx.message
    args = message.content.split()
    global conCooldown
    if not conCooldown:
        conCooldown = True
        async with message.channel.typing():
            ping = str(int(round(st.ping(), 0)))
            down = round((st.download()/1000000), 2)
            up = round((st.upload()/1000000), 2)
            em = discord.Embed(title="Connection Statistics", description="Current Connection Statistics", color=0x1671db)
            em.add_field(name="Ping", value="`%sms`" % ping)
            em.add_field(name="Download", value="`%s mbps`" % down)
            em.add_field(name="Upload", value="`%s mbps`" % up)
            await message.channel.send(embed=em)
        await asyncio.sleep(300)
        conCooldown = False
    else:
        await error("[429] Please wait before using this command again", message.channel)
                

#--Staff Commands--

#!hug
@Bot.command(client)
async def hug(ctx):
    args = ctx.message.content.split()
    if "Staff" in [role.name for role in ctx.message.author.roles] or "☆" in [role.name for role in ctx.message.author.roles] or "☆☆" in [role.name for role in ctx.message.author.roles] or "☆☆☆" in [role.name for role in ctx.message.author.roles]:
        hug_type = random.choice(["just gave you a big hug!", "just gave you a big big hug!", "just gave you a tight squeeze!", "just gave you a bog standard hug!"])
        await ctx.message.channel.send("%s - %s %s :hugging:" % (args[1], ctx.message.author.mention, hug_type))
    else:
        await error("[403] You do not have permission to use this command",ctx.message.channel)



#!fight
@Bot.command(client)
async def fight(ctx):
    message = ctx.message
    args = message.content.split()
    if "Staff" in [role.name for role in message.author.roles] or "☆☆" in [role.name for role in ctx.message.author.roles] or "☆☆☆" in [role.name for role in ctx.message.author.roles]:
            loss = 0
            rounds = 1
            init = message.author.mention
            target = " ".join(args[1:])
            fight = "%s has challenged %s to a fight!" % (init, target) + "\n"
            fightEm = discord.Embed(title="Fight!", description=fight, colour=0x5555FF) 
            fMessage = await message.channel.send(embed=fightEm)
            while not (loss == 1) and not (rounds > 5): 
                fight = fight + random.choice(["%s threw a chair at %s" % (init, target), "%s whacked %s with a stick" % (init, target), "%s slapped %s to the floor" % (init, target), "%s threw %s through a wall" % (init, target), "%s bitch slapped %s" % (init, target), "%s used dark magic against %s" % (init, target), "%s used the infinity gauntlet" % (init), "%s used fake news on %s" % (init, target), "%s ran %s over with a truck" % (init, target), "%s ate %s and threw them up again" % (init, target), "%s savagely roasted %s for sunday lunch" % (init, target), "%s performed a windows update on %s" % (init, target), "%s used the might of Zeus" % (init), "%s trapped %s in Flex Tape" % (init, target)])+"\n"
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
    else:
        await error("[403] You do not have permission to use this command",message.channel)


#!quickmaths
@Bot.command(client)
async def quickmaths(ctx):
    if "Staff" in [role.name for role in ctx.message.author.roles]:
        await ctx.send("**2+2 IS __4__! MINUS 1 THAT'S __3__! __*QUICK MATHS!*__**")

#--Admin Commands--

#!badge
@Bot.command(client)
async def badge(ctx):
    message = ctx.message
    args = message.content.split()
    user = discord.utils.get(message.guild.members, mention=args[3])
    if "Admin" in [role.name for role in message.author.roles] or "Owner" in [role.name for role in message.author.roles] or ctx.message.author.id in admin_bypass:
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
            
    else:
        await error("[403] You do not have permission to use this command",message.channel)

#!disable
@Bot.command(client)
async def disable(ctx, *args):
    message = ctx.message
    args = message.content.split()
    if "Admin" in [role.name for role in message.author.roles] or "Owner" in [role.name for role in message.author.roles] or ctx.message.author.id in admin_bypass:
        command = "!"+args[1].lower()
        if command == "!disable" or command == "!enable":
            await error("[401] You cannot disable that command!", message.channel)
            return False
            
        if not command in disabled_commands:
            disabled_commands.append(command)
            await message.channel.send(":ok_hand: Successfully disabled `%s`" % command)
        else:
            await error("[403] You do not have permission to use this command",message.channel)

#!enable    
@Bot.command(client)
async def enable(ctx, *args):
    message = ctx.message
    args = message.content.split()
    if "Admin" in [role.name for role in message.author.roles] or "Owner" in [role.name for role in message.author.roles] or ctx.message.author.id in admin_bypass:
        command = "!"+args[1]
        if command in disabled_commands:
            disabled_commands.remove(command)
            await message.channel.send(":ok_hand: Successfully enabled `%s`" % command)
        else:
            await error("[409] This command is already enabled", message.channel)
    else:
            await error("[403] You do not have permission to use this command",message.channel)

@Bot.command(client)
async def statmod(ctx, *args):
    try:
        message = ctx.message
        args = message.content.split()
        if "Admin" in [role.name for role in message.author.roles] or ctx.message.author.id in admin_bypass:
            user = discord.utils.get(message.guild.members, mention=args[1])
            subcommand = args[2]
            if subcommand.upper() == "SET":
                if args[3].upper() == "BALANCE":
                    set_coins(user, int(args[4]))
                    await message.channel.send(":ok_hand: Successfully set %s's balance to $%s" % (user.mention, args[4]))

            elif subcommand.upper() == "ADD":
                if args[3].upper() == "BALANCE":
                    add_coins(user, int(args[4]))
                    await message.channel.send(":ok_hand: Successfully added $%s to %s's balance!" % (args[4], user.mention))

            elif subcommand.upper() == "SUB":
                if args[3].upper() == "BALANCE":
                    add_coins(user, -int(args[4]))
                    await message.channel.send(":ok_hand: Successfully negated $%s to %s's balance!" % (args[4], user.mention))    

            elif subcommand.upper() == "WIPE":
                em = discord.Embed(title="STAT WIPE", description="You are about to wipe the stats of %s!\n\n This will completely reset their stats as if they were a new user.\n**THIS OPERATION CANNOT BE REVERSED**\n\n**Punishments will not be reset**\n\nPlease wait **15 Seconds** before confirming this action." % (user.mention), colour=0xAA0000)
                em.set_thumbnail(url="https://www.freeiconspng.com/uploads/status-warning-icon-png-29.png")
                confirmation = await message.channel.send(embed=em)
                await asyncio.sleep(15)
                await confirmation.add_reaction("\U0001F44D")
                await confirmation.add_reaction("\U0001F44E")

                def check(reaction, user):
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
    except:
        await error("[400] Invalid Usage.`\n_ _\nCommand Syntax:\n `!statmod <@user> <set|add|sub> <balance|rank|tier|statwipe> {amount}", message.channel)
            
@Bot.command(client)
async def announce(ctx):
    args = ctx.message.content.split(" ")
    if "Admin" in [role.name for role in ctx.message.author.roles]:
        if args[1].upper() == "SERVER":
            announcement = " ".join(args[2:])
            role = discord.utils.get(ctx.message.guild.roles, name="Server Announcements")
            await role.edit(mentionable=True)
            await client.get_channel(473284532800454667).send("%s\n%s\n_ _\nSent By: **%s**" % (role.mention, announcement, str(ctx.message.author)))
            await role.edit(mentionable=False)
            
        
#-----Command Register------


#-----Event Listners-----        
        
@client.event
async def on_ready():
    print("active")
    #await client.change_presence(status=discord.Status.invisible)

    

@client.event
async def on_message(message):
    try:

        #print(message.content)

        global conCooldown
        global disabled_commands

        args = message.content.split(" ")

        if args[0].lower() in disabled_commands:
            await error("[423] This command is currently disabled", message.channel)
            return False
        channel = message.channel
                         
        if message.channel.id == gate:
            await message.delete()        
      
        #elif message.content.upper().startswith("!RANSACK"):
        #    await error("[501] Not Implemented", message.channel)

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

       
        elif message.content.upper().startswith("W!UPDATE"):
            for member in message.guild.members:
                insert_db_user(member)
                await member.add_roles(discord.utils.get(member.guild.roles, name="-----===== Notif Roles =====-----"))

        await client.process_commands(message)

        if not str(message.author.id) in ignore_list:
            if not message.author.id in cooldown:
                    
                cooldown.append(message.author.id)
                coins_add = random.randint(50,75)
                add_coins(message.author, coins_add)
                exp_add = random.randint(15, 25)
                add_exp(message.author.id, exp_add)
                await check_level_up(message.author.id, message.guild, message.channel)
                await asyncio.sleep(60)
                cooldown.remove(message.author.id)

        
                        

    except Exception as e:
        await error("[500] %s" % (e), message.channel, message)
        




@client.event
async def on_member_join(member):
    insert_db_user(member)

        
async def user_accept_rules(member):
    channel = client.get_channel(casual)
    em = discord.Embed(title="Welcome!", description="Hello %s, Welcome to **Varsity Discord**! - Make sure you read all the information in <#473284512378388481>! We hope you enjoy your time here!" % (member.name), colour=0x55FF55)
    em.set_footer(text="We now have %s Members!" % (len(member.guild.members)))
    await channel.send(embed=em)
    reg_role = discord.utils.get(member.guild.roles, name="Member")
    default_role = discord.utils.get(member.guild.roles, name="Regular")
    await member.add_roles(default_role)
    await member.add_roles(reg_role)        
        
        
        
        
        


    
print("Test")    
client.run(token) #logs into the bot
