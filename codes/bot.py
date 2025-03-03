import discord
from discord.ext import commands, tasks
#from discord_slash import SlashCommand  # pip install -U discord-py-slash-command
from discord.utils import get
import random
import sqlite3
from datetime import datetime
from datetime import timedelta
import time
import asyncio
import tic_tac_toe
import requests
from bs4 import BeautifulSoup
from googletrans import Translator # pip install googletrans==3.1.0a0

intents = discord.Intents(messages = True, guilds = True, reactions = True, members = True, presences = True)
client = commands.Bot(command_prefix = ".",intents = intents)

max_points = 50
max_pay = 5
gif_cost = 5
link_cost = 4
reaction_cost = 2

max_level = 30

beginning_mcoins_in_market = 10000
total_mcoins_in_market = 10000
mcoin_value = 1
mining_balance = 0

warnings_renew_frequency = 7 # days

guild_id = -1 # fill
log_channel_id = -1 # fill
chat_channel_id = -1 # fill

is_playing_game = False
is_market_opened = False
 
class UserManager():
    
    def __init__(self):

        self.create_connection()

    def create_connection(self):

        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()

        task = "Create table if not exists UserInfo (UserName TEXT, Points INT, Warnings INT, Id INT, Pay INT, DailyEarnedPoints INT)"
        self.cursor.execute(task)

        self.connection.commit()

    def shut_down_connection(self):
        
        self.connection.close()

    def get_user_info(self, name):

        task = "Select * from UserInfo where UserName = ?"
        self.cursor.execute(task, (name,))
        user = self.cursor.fetchall()

        if len(user) == 0:
            print(f"No user named '{name}'") 
        else:
            return user[0]

    def get_user_info_from_id(self, id):
        
        task = "Select * from UserInfo where Id = ?"
        self.cursor.execute(task, (id,))
        user = self.cursor.fetchall()

        if len(user) == 0:
            print(f"No user with id: '{id}'") 
        else:
            return user[0]

    def check_user(self, name):

        task = "Select * from UserInfo where UserName = ?"
        self.cursor.execute(task, (name,))
        user = self.cursor.fetchall()

        if len(user) == 0:
            return False
        else:
            return True

    def check_user_from_id(self, id):
        task = "Select * from UserInfo where Id = ?"
        self.cursor.execute(task, (id,))
        user = self.cursor.fetchall()

        if len(user) == 0:
            return False
        else:
            return True

    def get_all_user_names(self):
        
        task = "Select * from UserInfo"
        self.cursor.execute(task)
        users = self.cursor.fetchall()
        user_names = []

        for user in users:
            user_names.append(user[0])

        return user_names

    def add_user(self, name, id):

        task = "Insert into UserInfo Values(?,?,?,?,?,?)"
        self.cursor.execute(task,(name, max_points, 0, id, max_pay,0))
        print(f"User '{name} has added to the users database'")

        self.connection.commit()

    def delete_user(self, name):

        task = "Delete from UserInfo where UserName = ?"
        self.cursor.execute(task, (name,))
        print(f"User '{name} has been removed from the users database'")

        self.connection.commit()

    def increase_daily_points(self, name, amount):

        user = self.get_user_info(name)
        daily_points = user[5]
 
        daily_points += amount

        task = "Update UserInfo set DailyEarnedPoints = ? where UserName = ?"
        self.cursor.execute(task, (daily_points, name))
        self.connection.commit()

        print(f"{name} has {daily_points} daily earned points.")

    def set_daily_points(self, name, amount):

        task = "Update UserInfo set DailyEarnedPoints = ? where UserName = ?"
        self.cursor.execute(task, (amount, name))
        self.connection.commit()

    def set_warnings(self, name, amount):

        if self.check_user(name):
            
            task = "Update UserInfo set Warnings = ? where UserName = ?"
            self.cursor.execute(task, (amount, name))
            self.connection.commit()

        else:
            print(f"There isn't a user called {name}")

    def add_warning(self, name):

        if self.check_user(name): #yeri değiştirilebilir.

            user = self.get_user_info(name)

            warnings = user[2]
            warnings += 1

            task2 = "Update UserInfo set Warnings = ? where UserName = ?"
            self.cursor.execute(task2, (warnings, name))
            self.connection.commit()
        else:
            print(f"There isn't a user called {name}")

    def remove_warning(self, name, amount=1):

        if self.check_user(name): #yeri değiştirilebilir.

            user = self.get_user_info(name)

            warnings = user[2]
            warnings -= amount

            task2 = "Update UserInfo set Warnings = ? where UserName = ?"
            self.cursor.execute(task2, (warnings, name))
            self.connection.commit()
        else:
            print(f"There isn't a user called {name}")

    def increase_points(self,name, amount, should_increase_daily_points = True):
        
        user = self.get_user_info(name)
        points = user[1]
 
        points += amount

        task = "Update UserInfo set Points = ? where UserName = ?"
        self.cursor.execute(task, (points, name))
        self.connection.commit()

        if should_increase_daily_points:
            self.increase_daily_points(name, amount)

        print(f"Increased {name}'s points")

    def decrease_points(self, name, amount = 1):
          
        user = self.get_user_info(name)
        points = user[1]
 
        points -= amount

        task = "Update UserInfo set Points = ? where UserName = ?"
        self.cursor.execute(task, (points, name))
        self.connection.commit()
        print(f"Decreased {name}'s points")

    def set_points(self, name, amount):

        task = "Update UserInfo set Points = ? where UserName = ?"
        self.cursor.execute(task, (amount, name))
        self.connection.commit()
        print(f"Set {name}'s points to {amount}")

    def set_pay(self, name, amount):

        task = "Update UserInfo set Pay = ? where UserName = ?"
        self.cursor.execute(task, (amount, name))
        self.connection.commit()
        print(f"Set {name}'s pay to {amount}")

    def decrease_pay(self, name, amount = 1):
        user = self.get_user_info(name)
        pay = user[4]
 
        pay -= amount

        task = "Update UserInfo set Pay = ? where UserName = ?"
        self.cursor.execute(task, (pay, name))
        self.connection.commit()
        print(f"Decreased {name}'s pay.")

    def get_ordered_list_by_daily_eared_points(self):

        task = "Select * from UserInfo"
        self.cursor.execute(task)
        users = self.cursor.fetchall()
        user_names = []

        for user in users:
            user_names.append([user[0], user[5]]) # name, daily earned points

        for i in range(len(user_names)):    # sorting the list from bigger to smaller
            
            for user in range(0, len(user_names) - 1):
                
                if user_names[user][1] < user_names[user + 1][1]: 
                    
                    temp = user_names[user]
                    user_names[user] = user_names[user + 1]
                    user_names[user + 1] = temp

        return user_names
                
user_manager = UserManager()

class ServerManager():

    def __init__(self):

        self.create_connection()

    def create_connection(self):

        self.connection = sqlite3.connect("server.db")
        self.cursor = self.connection.cursor()

        task = "Create table if not exists ServerInfo (Id INT, LastRenewPointsDay INT, LastRenewWarningsDay TEXT)"
        self.cursor.execute(task)

        self.connection.commit()
    
    def shut_down_connection(self):
        
        self.connection.close()

    async def renew(self):

        task = "Select * from ServerInfo where Id = ?"
        self.cursor.execute(task, (1,))
        data = self.cursor.fetchall()
        current_day = int(datetime.now().day)

        if len(data) == 0:
            
            now = datetime.now()
            date_today = now.strftime("%d/%m/%Y %H:%M:%S")

            task2 = "Insert into ServerInfo Values(?,?,?)"
            self.cursor.execute(task2,(1, current_day,date_today))
            self.connection.commit()

            for user in user_manager.get_all_user_names(): #renew

                user_manager.set_points(user, max_points)
                user_manager.set_pay(user, 1)
                user_manager.set_daily_points(user, 0)
                user_manager.set_warnings(user, 0)
                market_manager.set_mpoints(user_manager.get_user_info(user)[3], 0)
                market_manager.set_mcoins(user_manager.get_user_info(user)[3], 0)

        else:
            if not data[0][1] == current_day:
        
                task3 = "Update ServerInfo set LastRenewPointsDay = ? where Id = ?" # change database
                self.cursor.execute(task3, (current_day, 1))
                self.connection.commit()
                ordered_list = user_manager.get_ordered_list_by_daily_eared_points()

                for user in user_manager.get_all_user_names(): # renew
                    user_manager.set_points(user, max_points)
                    user_manager.set_pay(user, 1)
                    user_manager.set_daily_points(user, 0)
                    market_manager.set_mpoints(user_manager.get_user_info(user)[3], 0)
                    market_manager.set_mcoins(user_manager.get_user_info(user)[3], 0)


                if ordered_list[0][1] >= 20:
                    mini_game_manager.increase_exp(ordered_list[0][0], 150)
                if ordered_list[1][1] >= 20:
                    mini_game_manager.increase_exp(ordered_list[1][0], 100)
                if ordered_list[2][1] >= 20:
                    mini_game_manager.increase_exp(ordered_list[2][0], 50)

                now = datetime.now()
                last_renew_warnings_day_string = data[0][2]
                last_renew_warnings_day = datetime.strptime(last_renew_warnings_day_string, "%d/%m/%Y %H:%M:%S")

                difference = now - last_renew_warnings_day
                
                if difference.days >= warnings_renew_frequency:
                    
                    for user in user_manager.get_all_user_names(): # renew warnings
                        user_manager.set_warnings(user, 0)
                        await moderation.remove_mute(user_manager.get_user_info(user)[3])

                    date_today = now.strftime("%d/%m/%Y %H:%M:%S")
                    
                    task = "Update ServerInfo set LastRenewWarningsDay = ? where Id = ?"
                    self.cursor.execute(task, (date_today, 1))
                    self.connection.commit()

                    print("All warnings have been renewed")
            
                print("All points have been renewed")
                print("All pays have been renewed")

server_manager = ServerManager()

class MiniGameManager():

    def __init__(self):

        self.needed_exp_for_level = {}
        self.bet_multiplier_for_level = {}

        self.create_connection()
        self.create_level_system()

    def create_connection(self):

        self.connection = sqlite3.connect("games.db")
        self.cursor = self.connection.cursor()

        task = "Create table if not exists GameInfo (UserName TEXT, Exp INT, Level INT, BetMultiplier FLOAT, SlotWinChanceMultiplier FLOAT)"   #bet multiplier from shop buy
        self.cursor.execute(task)

        self.connection.commit()
    
    def shut_down_connection(self):
        
        self.connection.close()

    def create_level_system(self):

        self.bet_multiplier_for_level[1] = 0   
        bet_multiplier = 0.5    # 2 x (100 + bet_multiplier) / 100
        add = bet_multiplier
        
        needed_exp = 200      # earned exp = round((100 - win_chance) / 5)

        for i in range(2, max_level + 1):
            
            self.bet_multiplier_for_level[i] = bet_multiplier
            bet_multiplier += add
    
            if i % 5 == 0:
                add += 0.5

            self.needed_exp_for_level[i] = needed_exp
            needed_exp = round(needed_exp * 10/9)

    def get_user_info(self, name):

        task = "Select * from GameInfo where UserName = ?"
        self.cursor.execute(task, (name,))
        user = self.cursor.fetchall()

        if len(user) == 0:
            print(f"No user named '{name}'") 
        else:
            return user[0]

    def check_user(self, name):

        task = "Select * from GameInfo where UserName = ?"
        self.cursor.execute(task, (name,))
        user = self.cursor.fetchall()

        if len(user) == 0:
            return False
        else:
            return True

    def add_user(self, name):

        task = "Insert into GameInfo Values(?,?,?,?,?)"
        self.cursor.execute(task,(name, 0, 1, 0, 0))

        self.connection.commit()

    def delete_user(self, name):

        task = "Delete from GameInfo where UserName = ?"
        self.cursor.execute(task, (name,))

        self.connection.commit()

    def get_ordered_users_by_level(self):

        task = "Select * from GameInfo"
        self.cursor.execute(task)
        users = self.cursor.fetchall()
        user_names = []

        for user in users:
            if user[0] in user_manager.get_all_user_names():
                user_names.append([user[0],user[2], user[1]]) #level, exp

        for i in range(len(user_names)):    # sorting the list from bigger to smaller
            
            for user in range(0, len(user_names) - 1):
                
                if user_names[user][1] < user_names[user + 1][1]:  #check level
                    
                    temp = user_names[user]
                    user_names[user] = user_names[user + 1]
                    user_names[user + 1] = temp
                
                elif user_names[user][1] == user_names[user + 1][1]:   #check EXP if the levels are equal
                    
                    if user_names[user][2] < user_names[user + 1][2]:
                        
                        temp = user_names[user]
                        user_names[user] = user_names[user + 1]
                        user_names[user + 1] = temp

        return user_names

    def increase_exp(self, name, amount):
        
        user = self.get_user_info(name)

        if not user[2] == max_level:  #only increase exp if the user is not at max level
            exp = user[1]
    
            exp += amount

            if exp > self.needed_exp_for_level[user[2] + 1]:
                exp -= self.needed_exp_for_level[user[2] + 1]
                self.increase_level(name)

                updated_user = self.get_user_info(name)
                if updated_user[2] == max_level:
                    exp = 0

            task = "Update GameInfo set Exp = ? where UserName = ?"
            self.cursor.execute(task, (exp, name))
            self.connection.commit()
            print(f"Increased {name}'s exp")

    def decrease_exp(self, name, amount):
        
        user = self.get_user_info(name)
        exp = user[1]
 
        exp -= amount

        task = "Update GameInfo set Exp = ? where UserName = ?"
        self.cursor.execute(task, (exp, name))
        self.connection.commit()
        print(f"Decreased {name}'s exp")

    def set_exp(self, name, amount):

        task = "Update GameInfo set Exp = ? where UserName = ?"
        self.cursor.execute(task, (amount, name))
        self.connection.commit()
        print(f"Set {name}'s exp to {amount}")

    def increase_level(self, name, amount = 1):
        
        user = self.get_user_info(name)
        level = user[2]
 
        level += amount

        task = "Update GameInfo set Level = ? where UserName = ?"
        self.cursor.execute(task, (level, name))
        self.connection.commit()
        print(f"Increased {name}'s level")

    def set_level(self, name, amount):

        task = "Update GameInfo set Level = ? where UserName = ?"
        self.cursor.execute(task, (amount, name))
        self.connection.commit()
        print(f"Set {name}'s level to {amount}")

mini_game_manager = MiniGameManager()

class Moderation():

    def __init__(self):

        self.create_connection()

    def create_connection(self):

        self.connection = sqlite3.connect("moderation.db")
        self.cursor = self.connection.cursor()

        task = "Create table if not exists Moderation (Id Int, IsMuted INT, MuteEndDate TEXT)" # 1 -> True, 0 -> False
        self.cursor.execute(task)

        self.connection.commit()
    
    def shut_down_connection(self):
        
        self.connection.close()

    def get_user_info(self, id):

        task = "Select * from Moderation where Id = ?"
        self.cursor.execute(task, (id,))
        user = self.cursor.fetchall()

        return user[0]

    def add_user(self, id):

        task = "Insert into Moderation Values(?,?,?)"
        now = datetime.now()
        date_today = now.strftime("%d/%m/%Y %H:%M:%S")

        self.cursor.execute(task,(id, 0, date_today))
        print(f"User '{client.get_user(id).name} has added to the moderation database'")

        self.connection.commit()

    def delete_user(self, id):

        task = "Delete from Moderation where Id = ?"
        self.cursor.execute(task, (id,))
        print(f"User '{client.get_user(id).name} has been removed from the moderation database'")

        self.connection.commit()

    def check_user(self, id):
        task = "Select * from Moderation where Id = ?"
        self.cursor.execute(task, (id,))
        user = self.cursor.fetchall()

        if len(user) == 0:
            return False
        else:
            return True

    def get_all_users(self):
        
        task = "Select * from Moderation"
        self.cursor.execute(task)
        users = self.cursor.fetchall()
        
        return users

    def add_mute(self, id, mute_end_date_string):

        task = "Update Moderation set IsMuted = ? where Id = ?"
        self.cursor.execute(task, (1, id))
        self.connection.commit()
        
        task = "Update Moderation set MuteEndDate = ? where Id = ?"
        self.cursor.execute(task, (mute_end_date_string, id))
        self.connection.commit()

    async def remove_mute(self, id):

        while True:
            try:
                role_muted = discord.utils.get(client.get_guild(guild_id).roles, name = "Muted")
                member = discord.utils.get(client.get_all_members(), id=id)
                
                if role_muted in member.roles:
                    await member.remove_roles(role_muted)  # remove the mute from the user

                task = "Update Moderation set IsMuted = ? where Id = ?"
                self.cursor.execute(task, (0, id))
                self.connection.commit()

                print("User " + client.get_user(id).name + " has unmuted")
                break
            
            except:
                print("Couldn't find role 'Muted'.")


    async def moderate_mutes(self):
        
        while not client.is_closed():
            
            for user in self.get_all_users():

                if user[1] == 1: # if the user is muted
                    
                    now = datetime.now()
                    mute_end_date = datetime.strptime(user[2], "%d/%m/%Y %H:%M:%S")
                    difference = mute_end_date - now

                    if difference.total_seconds() <= 0: # if the mute duration is over
                        
                        await self.remove_mute(user[0])

            await asyncio.sleep(60)

moderation = Moderation()

class MarketManager():

    def __init__(self):

        self.create_connection()

    def create_connection(self):

        self.connection = sqlite3.connect("market.db")
        self.cursor = self.connection.cursor()

        task = "Create table if not exists MarketInfo (Id Int, MPoints REAL, MCoins REAL)" 
        self.cursor.execute(task)

        self.connection.commit()
    
    def shut_down_connection(self):
        
        self.connection.close()

    def get_user_info(self, id):

        task = "Select * from MarketInfo where Id = ?"
        self.cursor.execute(task, (id,))
        user = self.cursor.fetchall()

        return user[0]

    def add_user(self, id):

        task = "Insert into MarketInfo Values(?,?,?)"
       
        self.cursor.execute(task,(id, 0, 0))
        print(f"User '{client.get_user(id).name} has added to the market database'")

        self.connection.commit()

    def delete_user(self, id):

        task = "Delete from MarketInfo where Id = ?"
        self.cursor.execute(task, (id,))
        print(f"User '{client.get_user(id).name} has been removed from the market database'")

        self.connection.commit()

    def check_user(self, id):
        task = "Select * from MarketInfo where Id = ?"
        self.cursor.execute(task, (id,))
        user = self.cursor.fetchall()

        if len(user) == 0:
            return False
        else:
            return True

    def get_all_users(self):
        
        task = "Select * from MarketInfo"
        self.cursor.execute(task)
        users = self.cursor.fetchall()
        
        return users

    def increase_mpoints(self, id, amount):
        
        user = self.get_user_info(id)
        mpoints = user[1]
 
        mpoints += amount

        task = "Update MarketInfo set MPoints = ? where Id = ?"
        self.cursor.execute(task, (mpoints, id))
        self.connection.commit()

    def decrease_mpoints(self, id, amount):
          
        user = self.get_user_info(id)
        mpoints = user[1]
 
        mpoints -= amount

        task = "Update MarketInfo set MPoints = ? where Id = ?"
        self.cursor.execute(task, (mpoints, id))
        self.connection.commit()

    def set_mpoints(self, id, amount):

        task = "Update MarketInfo set MPoints = ? where Id = ?"
        self.cursor.execute(task, (amount, id))
        self.connection.commit()

    def increase_mcoins(self, id, amount):
        
        user = self.get_user_info(id)
        mcoins = user[2]
 
        mcoins += amount

        task = "Update MarketInfo set MCoins = ? where Id = ?"
        self.cursor.execute(task, (mcoins, id))
        self.connection.commit()

    def decrease_mcoins(self, id, amount):
          
        user = self.get_user_info(id)
        mcoins = user[2]
 
        mcoins -= amount

        task = "Update MarketInfo set MCoins = ? where Id = ?"
        self.cursor.execute(task, (mcoins, id))
        self.connection.commit()

    def set_mcoins(self, id, amount):

        task = "Update MarketInfo set MCoins = ? where Id = ?"
        self.cursor.execute(task, (amount, id))
        self.connection.commit()

    def get_ordered_list_by_mpoints(self):

        task = "Select * from MarketInfo"
        self.cursor.execute(task)
        users = self.cursor.fetchall()
        user_names = []

        for user in users:
            user_names.append([user[0], user[1]]) #id, MPoints

        for i in range(len(user_names)):    #sorting the list from bigger to smaller
            
            for user in range(0, len(user_names) - 1):
                
                if user_names[user][1] < user_names[user + 1][1]: 
                    
                    temp = user_names[user]
                    user_names[user] = user_names[user + 1]
                    user_names[user + 1] = temp

        return user_names

market_manager = MarketManager()

@client.event
async def on_ready():
    
    print("Bot is ready")
    await check_time.start()

#@slash.slash(name="test", description="test test test")
#@client.command()
#async def test(ctx):
#    await ctx.send("deneme deneme deneme")

@client.event
async def on_member_join(member):
    
    embed=discord.Embed(title="MBot Log", color=0x16abb6)  
    embed.add_field(name="Log Type:", value="Member Join", inline=False)
    embed.add_field(name="Joined member: ", value= "<@" + str(member.id) + ">" + " - " + str(member), inline=False)
    embed.add_field(name="Time:", value=datetime.strftime(datetime.now(),"%H.%M"), inline=False)
    embed.add_field(name="Date:", value=datetime.strftime(datetime.now(),"%d.%m.%Y"), inline=False)
    
    embed.set_thumbnail(url = member.avatar_url)
    
    log_channel = client.get_channel(log_channel_id)
    await log_channel.send(embed=embed)

@client.event
async def on_member_remove(member):
    
    embed=discord.Embed(title="MBot Log", color=0x16abb6)  
    embed.add_field(name="Log Type:", value="Member Leave", inline=False)
    embed.add_field(name="Leaved member: ", value= str(member), inline=False)
    embed.add_field(name="Time:", value=datetime.strftime(datetime.now(),"%H.%M"), inline=False)
    embed.add_field(name="Date:", value=datetime.strftime(datetime.now(),"%d.%m.%Y"), inline=False)
    
    embed.set_thumbnail(url = member.avatar_url)
    
    log_channel = client.get_channel(log_channel_id)
    await log_channel.send(embed=embed)

@client.event
async def on_reaction_add(reaction, member):
    
    if str(member) == "MEE6#4876" or str(member) == "Groovy#7254" or str(member) == "FredBoat♪♪#7284" or str(member) == "MBot#3059":
        return

    if str(reaction.message.author) == "MBot#3059": # Don't decrease points
        
        emojis_num = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣"]

        if emojis_num[0] == str(reaction.message.reactions[0]):
            
            if not str(reaction) in emojis_num:
                await reaction.remove(member)

        elif "✅" == str(reaction.message.reactions[0]):
            
            if not str(reaction) == "✅" and not str(reaction) == "❌":
                await reaction.remove(member)

        return

    print(reaction.message.author)
    msg = "\"**" + str(member) + "**\" has added a \"**reaction**\"."
    log_channel = client.get_channel(log_channel_id)
    await log_channel.send(msg)

    if user_manager.check_user(str(member)):
        user = user_manager.get_user_info(str(member))
            
        if user[1] > reaction_cost:
            user_manager.decrease_points(user[0], reaction_cost)
            return
            
        else:
            print(f"User '{user[0]}' has not enough points")
            await reaction.remove(member)
    else:
        print(f"There isn't a user called {str(member)}")

@client.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.MemberNotFound):
        await ctx.send("Unknown user")

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing arguments")

    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have access to this command.\nYou can type '.memberCommands' to learn more about accessible commands.")

    elif isinstance(error, commands.BadArgument):
        await ctx.send("Wrong type of argument")

    elif isinstance(error, commands.CommandOnCooldown):
        minutes, seconds = divmod(error.retry_after, 60)
        
        if minutes > 0:
            msg = "**Still on cooldown**, please try again in {} minutes and {:.0f} seconds.".format(int(minutes), seconds) # rounds up to nearest integer.
        else:
            msg = "**Still on cooldown**, please try again in {:.0f} seconds.".format(seconds)

        await ctx.send(msg)

#@commands.has_role('Kurul')
@client.command()
@commands.has_permissions(administrator = True)
async def updateServerInfo(ctx):
    
    guild = ctx.guild
    user_id = "<@" + str(ctx.author.id) + ">"

    for member in guild.members:  #member.name?
        if not str(member) == "MBot#3059" and not str(member) == "MEE6#4876" and not str(member) == "Groovy#7254" and not str(member) == "FredBoat♪♪#7284":
            
            if not user_manager.check_user(str(member)):
                user_manager.add_user(str(member), member.id)
            
            if not moderation.check_user(member.id):
                moderation.add_user(member.id)

            if not mini_game_manager.check_user(str(member)):
                mini_game_manager.add_user(str(member))

            if not market_manager.check_user(member.id):
                market_manager.add_user(member.id)

    for user_name in user_manager.get_all_user_names():
        if not user_name in [str(member) for member in guild.members]:
           
            moderation.delete_user(user_manager.get_user_info(user_name)[3]) # we are deleting the user data from users and moderation databases but we don't delete him from the minigames database.
            market_manager.delete_user(user_manager.get_user_info(user_name)[3])
            user_manager.delete_user(user_name)

    embed=discord.Embed(title="MBot Log", color=0x16abb6)  #Log embedleri için renk bu
    embed.add_field(name="Log Type:", value="Command Use", inline=False)
    embed.add_field(name="Used Command: ", value=".updateServerInfo", inline=False)
    embed.add_field(name="Used by:", value= (user_id + " - " + str(ctx.author)), inline=False)
    embed.add_field(name="Time:", value=datetime.strftime(datetime.now(),"%H.%M"), inline=False)
    embed.add_field(name="Date:", value=datetime.strftime(datetime.now(),"%d.%m.%Y"), inline=False)
    embed.add_field(name="Used Channel:", value=str(ctx.channel), inline=False)
    
    embed.set_thumbnail(url = ctx.author.avatar_url)
    embed.set_footer(icon_url = ctx.author.avatar_url, text = f"Requested by {ctx.author.display_name}")

    log_channel = client.get_channel(log_channel_id)
    await log_channel.send(embed=embed)

    #print(ctx.guild.get_member("Shock Wave#8342"))       

@client.command()
async def profile(ctx):

    position = 0
    sorted_list = mini_game_manager.get_ordered_users_by_level()
    for i in range(len(sorted_list)):
        if sorted_list[i][0] == str(ctx.author):
            position = i + 1

    user_info = mini_game_manager.get_user_info(str(ctx.author))
   
    embed=discord.Embed(title="Profile", description="Profile of " + str(ctx.author.display_name), color=0x2293c3)
    embed.add_field(name="Level", value= str(user_info[2]), inline=True)
    
    if mini_game_manager.get_user_info(str(ctx.author))[2] == max_level:
        embed.add_field(name="EXP", value= "Max Level", inline=True)
    else:
        embed.add_field(name="EXP", value= str(user_info[1]) + "/" + str(mini_game_manager.needed_exp_for_level[user_info[2] + 1]), inline=True)

    embed.add_field(name="Rank", value= "#" + str(position), inline=False)

    embed.add_field(name="Win Multiplier Bonus", value="%+" + str(user_info[3] + mini_game_manager.bet_multiplier_for_level[user_info[2]]), inline=False)
    embed.add_field(name="Slots Win Chance Bonus", value= "%+" + str(user_info[4]), inline=True)

    embed.set_thumbnail(url = ctx.author.avatar_url)
    await ctx.send(embed=embed)

@client.command()
async def hangman(ctx):

    global is_playing_game

    if is_playing_game:
        return

    is_playing_game = True
    hangman_word = "" 

    url = "https://www.mit.edu/~ecprice/wordlist.10000"
    response = requests.get(url)
    WORDS = response.content.decode().splitlines()
    
    min_word_length = 5

    translator = Translator()

    while True:
        
        random_word = random.choice(WORDS)

        if len(random_word) >= min_word_length:

            try:
                word = translator.translate(random_word, dest="tr")

                if not word.text.lower() == random_word:

                    hangman_word = word.text.lower()
                    print(random_word)
                    break

            except:
                continue

    print(hangman_word)
    
    alphabet = ['a', 'b', 'c', 'ç', 'd', 'e', 'f', 'g', 'ğ','h', 'ı' ,'i', 'j', 'k', 'l', 'm', 'n', 'o', 'ö' ,'p', 'q', 'r', 's', 'ş', 't', 'u', 'ü', 'v', 'w', 'x', 'y', 'z']

    current_picture = 0
    guess_timeout = 120 # as seconds
    used_letters = [] 

    pictures = ["hangman/0.jpg", "hangman/1.jpg", "hangman/2.jpg", "hangman/3.jpg","hangman/4.jpg", "hangman/5.jpg", "hangman/6.jpg","hangman/7.jpg","hangman/8.jpg","hangman/9.jpg","hangman/10.jpg"]

    guess_board = ["_" for i in range(len(hangman_word))]

    for i in range(len(hangman_word)):
        if hangman_word[i] == " ":
            guess_board[i] = " / "

    game_embed = discord.Embed(title="Hangman", color=0x16abb6)
    game_embed.add_field(name="How to Play?", value="To win, you need to guess the random Turkish word.\nType only '[letter]' if you want to guess a letter (without double quotes)\nType 'guess [word/words]' if you want to guess the whole word (without double quotes)", inline=False)
    
    if len(used_letters) >= 2:
        text = ",".join(used_letters)
        game_embed.add_field(name="Used Letters", value=text,inline=False)

    elif len(used_letters) == 0:
        game_embed.add_field(name="Used Letters", value="None",inline=False)

    elif len(used_letters) == 1:
        game_embed.add_field(name="Used Letters", value=used_letters[0],inline=False)
    
    word = ""
    for letter in guess_board:
        word += letter

    embed_word = ""
    for letter in word:
        if letter == "_":
            embed_word += "\\"
        embed_word += letter
        embed_word += " "

    game_embed.add_field(name="Word", value=embed_word,inline=False)
    game_embed_message = await ctx.send(embed=game_embed)

    board = await ctx.send(file=discord.File(pictures[current_picture]))

    def check(msg):

        if not str(msg.author) == str(ctx.author):
            return False

        if not msg.channel == ctx.channel:
            return False

        return True

    game_end = False
    win = False

    while not game_end:
        
        game_embed = discord.Embed(title="Hangman", color=0x16abb6)
        game_embed.add_field(name="How to Play?", value="To win, you need to guess the random Turkish word.\nType only '[letter]' if you want to guess a letter (without double quotes)\nType 'guess [word/words]' if you want to guess the whole word (without double quotes)", inline=False)
        
        if len(used_letters) >= 2:
            text = ",".join(used_letters)
            game_embed.add_field(name="Used Letters", value=text,inline=False)

        elif len(used_letters) == 0:
            game_embed.add_field(name="Used Letters", value="None",inline=False)

        elif len(used_letters) == 1:
            game_embed.add_field(name="Used Letters", value=used_letters[0],inline=False)

        word = ""
        for letter in guess_board:
            word += letter

        embed_word = ""
        for letter in word:
            if letter == "_":
                embed_word += "\\"
            embed_word += letter
            embed_word += " "

        game_embed.add_field(name="Word", value=embed_word,inline=False)
        
        await game_embed_message.edit(embed=game_embed)
        
        start_time = time.time()

        while (time.time() - start_time) < guess_timeout:
            
            try:
                msg = await client.wait_for("message",timeout=guess_timeout,check= check)
            
            except asyncio.TimeoutError:
                await ctx.send("Game has ended. No responses so far.")
                is_playing_game = False
                return
            
            else:
                try:
                
                    words = []
                    word = ""
                    
                    for letter in range(len(msg.content)):
                        
                        if msg.content[letter] == " ":
                            words.append(word)
                            word = ""
                        elif letter == len(msg.content) - 1:
                            word += msg.content[letter]
                            words.append(word)
                        else:
                            word += msg.content[letter]

                    if len(words) == 1 and len(words[0]) == 1: # letter guess
                        
                        if words[0] in alphabet:
                            
                            if words[0] in used_letters:
                                
                                await msg.delete()
                                temp = await ctx.send("You have already made a guess with this letter.")
                                await asyncio.sleep(2)
                                await temp.delete()
                                
                                break

                            if words[0] in hangman_word:
                                
                                for letter in range(len(hangman_word)):
                                    if words[0] == hangman_word[letter]:
                                        guess_board[letter] = words[0]
                                
                                if not "_" in guess_board:
                                    
                                    game_end = True
                                    win = True

                                used_letters.append(words[0])
                                await msg.delete() 

                                break

                            else:
                                
                                if current_picture == len(pictures) - 2: # check game end
                                    
                                    game_end = True
                                    win = False
                                
                                current_picture += 1
                                used_letters.append(words[0]) 
                                
                                await board.delete()
                                board = await ctx.send(file=discord.File(pictures[current_picture]))

                                await msg.delete()
                                temp = await ctx.send("Wrong Guess!")
                                await asyncio.sleep(2)
                                await temp.delete()
                    
                                break
                                
                        else:
                            
                            await msg.delete()
                            temp = await ctx.send("Invalid syntax")
                            await asyncio.sleep(2)
                            await temp.delete()
                            
                            break


                    elif words[0].lower() == "guess" and len(words) >= 2: # word guess
                        
                        text = ""
                        for i in words[1:]:
                            text += i.lower()
                            text += " "

                        if text == (hangman_word.lower() + " "):
                            
                            game_end = True
                            win = True

                            for i in range(len(hangman_word)):
                                if hangman_word[i] == " ":
                                    guess_board[i] = " / "
                                else:
                                    guess_board[i] = hangman_word[i]

                            await msg.delete()
                            break

                        if current_picture == len(pictures) - 2: # check game end
                                    
                            game_end = True
                            win = False

                            current_picture += 1
                            
                            await board.delete()
                            board = await ctx.send(file=discord.File(pictures[current_picture]))
                            await msg.delete()

                            break

                        else:
                            current_picture += 1
                            
                            await board.delete()
                            board = await ctx.send(file=discord.File(pictures[current_picture]))
                            
                            await msg.delete()
                            temp = await ctx.send("Wrong Guess!")
                            await asyncio.sleep(2)
                            await temp.delete()
                            
                            break

                    else:
                        
                        await msg.delete()
                        temp = await ctx.send("Invalid syntax")
                        await asyncio.sleep(2)
                        await temp.delete()
                        
                        break

                except:
                    print("Invalid message")
                    await msg.delete()
                    break

    game_embed = discord.Embed(title="Hangman", color=0x16abb6)
    game_embed.add_field(name="How to Play?", value="To win, you need to guess the random Turkish word.\nType only '[letter]' if you want to guess a letter (without double quotes)\nType 'guess [word/words]' if you want to guess the whole word (without double quotes)", inline=False)
        
    word = ""
    for letter in guess_board:
        word += letter

    if len(used_letters) >= 2:
        text = ",".join(used_letters)
        game_embed.add_field(name="Used Letters", value=text,inline=False)

    elif len(used_letters) == 0:
        game_embed.add_field(name="Used Letters", value="None",inline=False)

    elif len(used_letters) == 1:
        game_embed.add_field(name="Used Letters", value=used_letters[0],inline=False)

    embed_word = ""
    for letter in word:
        if letter == "_":
            embed_word += "\\"
        embed_word += letter
        embed_word += " "

    game_embed.add_field(name="Word", value=embed_word,inline=False)
        
    await game_embed_message.edit(embed=game_embed)
    await asyncio.sleep(1)

    if win:
        await ctx.send("You Won!")
    else:
        await ctx.send("You Lost! The word was '" + hangman_word + "'.")

    is_playing_game = False

@client.command()
async def roulette(ctx, betting_time = 60):
    
    global is_playing_game

    if is_playing_game:
        return
    else:
        is_playing_game = True

    if betting_time <= 0:
        await ctx.send("Invalid arguments.")
        is_playing_game = False
        return

    chat_channel = client.get_channel(chat_channel_id)

    notification_embed = discord.Embed(color=0x16abb6)
    notification_embed.add_field(name=":loudspeaker:"+ ctx.author.display_name + " has started a 'Roulette' mini game.", value = "Players: 0")
    notification_embed_message = await chat_channel.send(embed=notification_embed)

    colors = [
        "red",
        "white",
        "green",
    ]

    bets = {}
    deleted_message_ids = []

    row_width = 9  # must be odd, max = 9 (because of the character limit of a message)
    min_lap = 1
    max_lap = 1

    emojis = [":white_large_square:", ":black_large_square:", ":red_square:", ":green_square:"]
    rows = []
    top_row = []   # we'll put \n later
    bottom_row = []

    green_chance = 2   #percent
    red_chance = (100 - green_chance) / 2
    winner = ""

    random_percent = random.randint(1,100)
    
    if random_percent <= green_chance:
        winner = "green"
    elif random_percent <= green_chance + red_chance:
        winner = "red"
    else:
        winner = "white"
    
    def get_visualized_board(rows):
        board = "*"

        for row in range(len(rows)):
            if not row == 0:
                board += "\n"

            for emoji in rows[row]:
                board += emoji

        board += "*"
        return board

    for i in range(row_width):
        
        if i == (row_width - 1) / 2:
            top_row.append(emojis[3])     #green
            if i % 2 == 0:
                 bottom_row.append(emojis[2])   #red
            else:
                bottom_row.append(emojis[0])   #white
           
        else:
            if i == 0 or i == row_width - 1:  #black
                top_row.append(emojis[1])
                bottom_row.append(emojis[1])
            elif i % 2 == 0:
                top_row.append(emojis[2])   #red
                bottom_row.append(emojis[2])
            else:
                top_row.append(emojis[0])    #white
                bottom_row.append(emojis[0])
    
    rows.append(top_row)

    middle_row = []
    for i in range(row_width - 2):
        if i % 2 == 0:   #red

            middle_row.append(emojis[2])
            for i in range(row_width - 2):
                middle_row.append(emojis[1])
            middle_row.append(emojis[2])

        else:  

            middle_row.append(emojis[0])
            for i in range(row_width - 2):
                middle_row.append(emojis[1])
            middle_row.append(emojis[0])
           
        rows.append(middle_row)
        middle_row = []

    rows.append(bottom_row)

    bet_embed=discord.Embed(title="Roulette", color=0x16abb6)  
    bet_embed.add_field(name="Bet Phase", value="Type your bets like 'bet [color] [bet]'\nGame will start at " + datetime.strftime(datetime.now() + timedelta(seconds=betting_time), "%H:%M:%S") + "\nAt least 3 people must join to start the game.", inline=False)
    bet_embed.add_field(name="Colors", value="'white': Bet Multiplier = x2\n'red': Bet Multiplier = x2\n'green' Multiplier = x50", inline=False)

    bet_embed_message = await ctx.send(embed=bet_embed)

    def check(msg):

        if str(msg.author) == "MBot#3059":
            return False

        if not msg.channel == ctx.channel:
            return False

        return True

    start_time = time.time()

    while (time.time() - start_time) < betting_time:
        
        try:
            msg = await client.wait_for("message",timeout=3.0,check= check)
           
        except asyncio.TimeoutError:
            continue
        
        else:
            try:
                deleted_message_ids.append(msg.id)

                words = []
                word = ""
                
                for letter in range(len(msg.content)):
                    
                    if msg.content[letter] == " ":
                        words.append(word)
                        word = ""
                    elif letter == len(msg.content) - 1:
                        word += msg.content[letter]
                        words.append(word)
                    else:
                        word += msg.content[letter]

                if len(words) == 3 and words[0] == "bet" and words[1] in colors:

                    try:
                        if user_manager.get_user_info(str(msg.author))[1] >= int(words[2]) and int(words[2]) > 0:
                                                
                            if not str(msg.author) in bets.keys():
                                bets[str(msg.author)] = [words[1], int(words[2])]  #[color, bet]
                                user_manager.decrease_points(str(msg.author), int(words[2]))
                                bet_embed.add_field(name=str(msg.author.display_name), value=" set bet to " + words[1] + " " + words[2] + " points.", inline=False)
                                
                                await bet_embed_message.edit(embed=bet_embed)

                            else:
                                if bets[str(msg.author)][0] == words[1]:
                                    bets[str(msg.author)][1] += int(words[2])
                                    user_manager.decrease_points(str(msg.author), int(words[2]))

                                    bet_embed.add_field(name=str(msg.author.display_name), value=" set bet to " + words[1] + " " + words[2] + " points.", inline=False)
                                    await bet_embed_message.edit(embed=bet_embed)

                            # update notification embed
                            notification_embed = discord.Embed(color=0x16abb6)
                            notification_embed.add_field(name=":loudspeaker:"+ ctx.author.display_name + " has started a 'Roulette' mini game.", value = "Players: " + str(len(bets)))
                            await notification_embed_message.edit(embed=notification_embed)
                                    
                        else:
                            print("Not enough points.")
                        
                    except:
                        print("Invalid number")
            except:
                print("Invalid message")
                
    for id in deleted_message_ids:
        msg = await ctx.fetch_message(id)
        await msg.delete()

    #await bet_embed_message.delete()
    await notification_embed_message.delete()
        
    if len(bets) < 3:
        
        await ctx.send("Not enough bets were played. Game has been cancelled.")
        is_playing_game = False
        
        # refund
        for player, data in bets.items():
            user_manager.increase_points(player, data[1], False) # don't increase daily earned points.

        return
    
    else:
        message = await ctx.send(get_visualized_board(rows))
        await asyncio.sleep(3)

    green_position = (row_width - 2) * 3 + (row_width - 1) / 2
    winner_square_number = 0
    lap = random.randint(min_lap,max_lap)

    if winner == "green":
        
        winner_square_number = (lap * (row_width-2) * 4) + green_position

    elif winner == "red":
        
        red_count = (2 * row_width) - 1
        square_number_in_lap = random.randrange(1, 2 * red_count, 2)
        winner_square_number = (lap * (row_width-2) * 4) + square_number_in_lap

    else:

        red_count = (2 * row_width) - 1
        white_count = (row_width - 2) * 4 - red_count - 1

        square_number_in_lap = random.randrange(2, 2 * white_count, 2)
        if square_number_in_lap % green_position == 0:   # we can't point out the green square if the white one wins.
            square_number_in_lap += 2

        winner_square_number = (lap * (row_width-2) * 4) + square_number_in_lap

    last_placed_arrow = []
    print(winner)
    print(winner_square_number)

    while winner_square_number > 0:
        
        arrow_emojis = [":arrow_left:", ":arrow_down:", ":arrow_right:", ":arrow_up:"]
        reduce_amount = 0
        
        if winner_square_number >= row_width - 2:
            
            reduce_amount = row_width - 2

        elif winner_square_number > 0:
            
            reduce_amount = winner_square_number

        if winner_square_number > 0:
        
            for i in range(reduce_amount):
                
                if not len(last_placed_arrow) == 0:
                    rows[last_placed_arrow[0]][last_placed_arrow[1]] = emojis[1]

                rows[i + 1][1] = arrow_emojis[0]
                last_placed_arrow = [i+1,1]
                await message.edit(content = emojis[1] * 3 + " *Rolling...*\n" + get_visualized_board(rows))
                await asyncio.sleep(0.5)

            winner_square_number -= reduce_amount

        if winner_square_number >= row_width - 2:

            reduce_amount = row_width - 2
            
        elif winner_square_number > 0:

            reduce_amount = winner_square_number

        if winner_square_number > 0:
        
            for i in range(reduce_amount):
                
                if not len(last_placed_arrow) == 0:
                    rows[last_placed_arrow[0]][last_placed_arrow[1]] = emojis[1]

                rows[-2][i + 1] = arrow_emojis[1]
                last_placed_arrow = [-2,i+1]
                await message.edit(content = emojis[1] * 3 + " *Rolling...*\n" + get_visualized_board(rows))
                await asyncio.sleep(0.5)

            winner_square_number -= reduce_amount

        if winner_square_number >= row_width - 2:
            
            reduce_amount = row_width - 2

        elif winner_square_number > 0:
            
            reduce_amount = winner_square_number

        if winner_square_number > 0:

            for i in range(row_width - 2, row_width - 2 - reduce_amount, -1):
                
                if not len(last_placed_arrow) == 0:
                    rows[last_placed_arrow[0]][last_placed_arrow[1]] = emojis[1]

                rows[i][-2] = arrow_emojis[2]
                last_placed_arrow = [i,-2]
                await message.edit(content = emojis[1] * 3 + " *Rolling...*\n" + get_visualized_board(rows))
                await asyncio.sleep(0.5)

            winner_square_number -= reduce_amount

        if winner_square_number >= row_width - 2:
            
            reduce_amount = row_width - 2

        elif winner_square_number > 0:
            
            reduce_amount = winner_square_number

        if winner_square_number > 0:
        
            for i in range(row_width - 2, row_width - 2 - reduce_amount, -1):
                
                if not len(last_placed_arrow) == 0:
                    rows[last_placed_arrow[0]][last_placed_arrow[1]] = emojis[1]

                rows[1][i] = arrow_emojis[3]
                last_placed_arrow = [1,i]
                await message.edit(content = emojis[1] * 3 + " *Rolling...*\n" + get_visualized_board(rows))
                await asyncio.sleep(0.5)

            winner_square_number -= reduce_amount
    
    await asyncio.sleep(2)
    await message.edit(content = emojis[1] * 2 + " *Game is Over!*\n" + get_visualized_board(rows))

    await asyncio.sleep(2)
    winners = []

    for member, value in bets.items():
        if value[0] == winner:
            winners.append(member)

    if len(winners) == 0:
        embed=discord.Embed(title="Game is over!", color=0x16abb6)  
        embed.add_field(name="Results", value="No one has won.", inline=False)
        await ctx.send(embed = embed)
        is_playing_game = False
        return

    bet_multiplier = 2
    win_chance = 0
        
    if winner == "green":
        bet_multiplier = 50
        win_chance = green_chance
    else:
        bet_multiplier = 2
        win_chance = red_chance

    result_board = ""
    for member in winners:
       
        multiplier = mini_game_manager.get_user_info(member)[3] + mini_game_manager.bet_multiplier_for_level[mini_game_manager.get_user_info(member)[2]]
        bet_multiplier = bet_multiplier * (100 + multiplier) / 100
        user_manager.increase_points(member, round(bets[member][1] * bet_multiplier))
        result_board += client.get_user(user_manager.get_user_info(member)[3]).name +" has won " +  str(round(bets[member][1] * bet_multiplier)) + " points.\n"
        
        mini_game_manager.increase_exp(member, round((100 - win_chance) / 5))
    
    embed2=discord.Embed(title="Game is over!", color=0x16abb6)  
    embed2.add_field(name="Results", value=result_board, inline=False)
    await ctx.send(embed = embed2)
    is_playing_game = False
    return

@client.command()
@commands.has_permissions(administrator = True)
async def openMarket(ctx):

    global mcoin_value
    global total_mcoins_in_market
    global is_market_opened
    global mining_balance

    is_market_opened = True

    market_open_duration = 8 * 3600 # hours to seconds

    mcoins_change_needed_to_change_increase_rates = 75
    mcoins_change_needed_to_change_decrease_rates = 5
    change_rate = 3 # percent

    minimum_mcoin_value = 0.05
    peak = mcoin_value

    time_between_updates = 45 # seconds

    max_column_count = 16
    symbol_converter = {"i": "/", "d" : "\\", "s" : "_"}
    
    board = [[max_column_count//2, "s"] for i in range(max_column_count)] # [row, state]
    
    # state can be 'increasing' : 'i', 'decreasing' : 'd' or 'stable : 's'

    chat_channel = client.get_channel(chat_channel_id)

    notification_embed = discord.Embed(title=":loudspeaker:" + "Market Has Opened." ,color=0x16abb6)
    await chat_channel.send(embed=notification_embed)

    def add_board(new_state):

        for i in range(len(board) - 1):
        
            #board[i] = board[i+1]  it doesn't work?
            board[i][0] = board[i+1][0]
            board[i][1] = board[i+1][1]
       
        board[-1][1] = new_state

        if new_state == "i":

            if board[-2][1] == "s" or board[-2][1] == "d":
                board[-1][0] = board[-2][0]  # _/  \/
            else:
                board[-1][0] = board[-2][0] - 1
            
        elif new_state == "d":

            if board[-2][1] == "s" or board[-2][1] == "d":
                board[-1][0] = board[-2][0] + 1
            else:
                board[-1][0] = board[-2][0] # /\

        elif new_state == "s":

            if board[-2][1] == "s" or board[-2][1] == "d":
                board[-1][0] = board[-2][0] # \_ __
            else:
                board[-1][0] = board[-2][0] - 1 

        if board[-1][0] == -1:  
            for data in board:
                data[0] += 1

    def get_visualized_board():
        
        visualized_board = ""
        max_row_count = 0
        
        for data in board:
            if data[0] + 1 > max_row_count:
                max_row_count = data[0] + 1

        for row_num in range(max_row_count):
            visualized_row = [" " for i in range(max_column_count)]
            
            for col_num in range(len(board)):
                
                if board[col_num][0] == row_num:
                    visualized_row[col_num] = symbol_converter[board[col_num][1]]

            for char in visualized_row:
                visualized_board += char

            visualized_board += "\n"

        return visualized_board

    embed=discord.Embed(title="Market", color=0x16abb6)  
    embed.add_field(name="MCoin Value: ", value="{:.4f}".format(mcoin_value), inline=True)
    embed.add_field(name="Last Update:", value="0", inline=True)
    embed.add_field(name="Peak: ", value="{:.4f}".format(peak), inline=False)
    embed.add_field(name="Graph", value="```\n" + get_visualized_board() + "```", inline=False)
    market_graph_message = await ctx.send(embed=embed)

    #market_graph_message = await ctx.send("```\n" + get_visualized_board() + "```") 

    start_time = time.time()

    while (time.time() - start_time) < market_open_duration:

        await asyncio.sleep(time_between_updates)

        increase_chance = 50 # percent

        if total_mcoins_in_market > beginning_mcoins_in_market:

            increase_chance -= change_rate * ((total_mcoins_in_market - beginning_mcoins_in_market) // mcoins_change_needed_to_change_decrease_rates)

        elif total_mcoins_in_market < beginning_mcoins_in_market:

            increase_chance += change_rate * ((beginning_mcoins_in_market - total_mcoins_in_market) // mcoins_change_needed_to_change_increase_rates)

        if mining_balance > 0:

            increase_chance -= (mining_balance // 3) * 3

        elif mining_balance <= -5:

            mining_balance = 0
        
        if increase_chance > 80:
            increase_chance = 80

        elif increase_chance < 20:
            increase_chance = 20

        change_amount = 0
        random_num = random.randint(1,100)

        if random_num <= 5:
            change_amount = random.uniform(0.8,1)
        elif random_num <= 20:
            change_amount = random.uniform(0.5,0.8)
        elif random_num <= 40:
            change_amount = random.uniform(0.3,0.5)
        elif random_num <= 80:
            change_amount = random.uniform(0,0.3)
        else:
            change_amount = 0

        if mcoin_value < 0.1:
            increase_chance += 15

        print("Increase chance: " + str(increase_chance))
        print("Mining Balance: " + str(mining_balance))
        print("Total MCoins in Market: " + str(total_mcoins_in_market))
        
        random_num = random.randint(1,100)
        
        if change_amount == 0:
            add_board("s")
        
        elif random_num > increase_chance:
            
            if mcoin_value <= minimum_mcoin_value:
                mcoin_value /= 2
                change_amount = mcoin_value / 2
                add_board("d")

            elif mcoin_value - change_amount >= minimum_mcoin_value:
                mcoin_value -= change_amount
                add_board("d")
    
            else:
                mcoin_value = minimum_mcoin_value
                add_board("d")
                
        else:
            add_board("i")
            mcoin_value += change_amount

        if mcoin_value > peak:
            peak = mcoin_value

        embed=discord.Embed(title="Market", color=0x16abb6)  
        embed.add_field(name="MCoin Value: ", value="{:.4f}".format(mcoin_value), inline=True)

        if change_amount == 0:
            
            embed.add_field(name="Last Update:", value="0", inline=True)
        
        elif random_num > increase_chance:

            embed.add_field(name="Last Update:", value="-{:.4f}".format(change_amount), inline=True)
        
        else:

            embed.add_field(name="Last Update:", value="+{:.4f}".format(change_amount), inline=True)

        embed.add_field(name="Peak: ", value="{:.4f}".format(peak), inline=False)
        embed.add_field(name="Graph", value="```\n" + get_visualized_board() + "```", inline=False)
        await market_graph_message.edit(embed=embed)

    is_market_opened = False

@client.command(aliases=['mcoin','Mcoin','mCoin'])
async def MCoin(ctx, member: discord.Member = None):

    mentioned_member = ""
   
    if member is None:
        
        mentioned_member = ctx.author.name

        mpoints = market_manager.get_user_info(ctx.author.id)[1]
        mcoins = market_manager.get_user_info(ctx.author.id)[2]
        
    elif market_manager.check_user(member.id):
        
        mentioned_member = member.name

        mpoints = market_manager.get_user_info(member.id)[1]
        mcoins = market_manager.get_user_info(member.id)[2]

    else:
        await ctx.send("Unknown user")
        return

    #Disco
    embed=discord.Embed(title="Marketing Stats of " + str(mentioned_member), color=0x16abb6)
    embed.add_field(name="MCoins:", value="{:.4f}".format(mcoins), inline = False)
    embed.add_field(name="MPoints:", value="{:.4f}".format(mpoints), inline = False)
    embed.set_footer(icon_url = ctx.author.avatar_url, text = f"Requested by {ctx.author.display_name}")
    await ctx.send(embed=embed)

@client.command(aliases=['buycoin'])
async def buyCoin(ctx, amount : float): # buy mcoins with mpoints deposit, amount : mpoints

    global total_mcoins_in_market
    global mining_balance

    if not is_market_opened:
        await ctx.send("Market is closed.")
        return
    
    mpoints = market_manager.get_user_info(ctx.author.id)[1]
    mcoins = market_manager.get_user_info(ctx.author.id)[2]

    starting_mpoints = mpoints

    if amount <= 0 and not amount == -1: # -1 means all
        await ctx.send("Invalid argument")
        return

    if mpoints >= amount:

        if amount == -1 and not mpoints == 0: # using all MPoints
            
            increase_amount = mpoints / mcoin_value
            mpoints = 0

        else:

            increase_amount = amount / mcoin_value
            mpoints -= amount

        mcoins += increase_amount
        total_mcoins_in_market -= increase_amount

        market_manager.set_mpoints(ctx.author.id, mpoints)
        market_manager.set_mcoins(ctx.author.id, mcoins)

        mining_balance -= increase_amount / 10

        if amount == -1:

            await ctx.send("You bought {:.4f} MCoins with {:.4f} MPoints.".format(increase_amount, starting_mpoints))

        else:

            await ctx.send("You bought {:.4f} MCoins with {:.4f} MPoints.".format(increase_amount, amount))

    else:
        await ctx.send("Not enough MPoints.")

@client.command(aliases=['sellcoin'])
async def sellCoin(ctx, amount : float): # sell mcoins to mpoints withdraw

    global total_mcoins_in_market
    global mining_balance

    if not is_market_opened:
        await ctx.send("Market is closed.")
        return
    
    mpoints = market_manager.get_user_info(ctx.author.id)[1]
    mcoins = market_manager.get_user_info(ctx.author.id)[2]

    starting_mcoins = mcoins

    if amount <= 0 and not amount == -1:
        await ctx.send("Invalid argument")
        return

    if mcoins >= amount:

        if amount == -1 and not mcoins == 0: # selling all MCoins

            increase_amount = mcoins * mcoin_value
            total_mcoins_in_market += mcoins
            mcoins = 0
        
        else:

            increase_amount = amount * mcoin_value
            mcoins -= amount
            total_mcoins_in_market += amount

        mpoints += increase_amount

        market_manager.set_mpoints(ctx.author.id, mpoints)
        market_manager.set_mcoins(ctx.author.id, mcoins)

        if amount == -1:

            await ctx.send("You sold {:.4f} MCoins for {:.4f} MPoints.".format(starting_mcoins, increase_amount))

        else:

            await ctx.send("You sold {:.4f} MCoins for {:.4f} MPoints.".format(amount, increase_amount))

    else:
        await ctx.send("Not enough MCoins.")

@client.command()
async def exchange(ctx, amount : float): # buy mpoints with points

    global total_mcoins_in_market

    if not is_market_opened:
        await ctx.send("Market is closed.")
        return

    mpoints = market_manager.get_user_info(ctx.author.id)[1]
    points = user_manager.get_user_info_from_id(ctx.author.id)[1]

    if amount <= 0:
        await ctx.send("Invalid argument")
        return

    if points >= amount:
        
        points -= amount
        mpoints += amount

        market_manager.set_mpoints(ctx.author.id, mpoints)
        user_manager.set_points(str(ctx.author), int(points))

        await ctx.send("You exchanged {:.4f} MPoints for {:.4f} Points.".format(amount,amount))

    else:
        await ctx.send("Not enough Points.")

@commands.cooldown(1, 600, commands.BucketType.user) # 10 minutes cooldown for every user
@client.command()
async def mining(ctx):

    global total_mcoins_in_market
    global mining_balance

    if not is_market_opened:
        await ctx.send("Market is closed.")
        return

    mcoins = random.uniform(0.1,1)
    
    market_manager.increase_mcoins(ctx.author.id, mcoins)
    
    total_mcoins_in_market += mcoins
    mining_balance += 1
    
    await ctx.send("You found {:.4f} MCoin!".format(mcoins))

@client.command(aliases=['marketleaderboard'])
async def marketLeaderboard(ctx):

    text = "```bash\n"
    max_character = 0
    user_names = market_manager.get_ordered_list_by_mpoints()

    for i in range(5):
        
        if len(client.get_user(user_names[i][0]).name) > max_character:
            max_character = len(client.get_user(user_names[i][0]).name)

    for i in range(5):

        character = max_character - len(client.get_user(user_names[i][0]).name)
        text += str(i + 1) + "-) \"" + client.get_user(user_names[i][0]).name + "\"" + str("‎‎‏‏‎ ‎" * character) + " : " + "{:.4f}".format(user_names[i][1])
        text += "\n"

    text += "```"
     
    embed=discord.Embed(title="Market Leaderboard",description="Username - MPoints" ,color=0x16abb6)
    embed.add_field(name="Top 5", value=text, inline=False)

    embed.set_footer(text = datetime.strftime(datetime.now(),"%d.%m.%Y | %H:%M"))
    await ctx.send(embed=embed)

@client.command()
@commands.has_permissions(administrator = True)
async def members(ctx):
    
    names = user_manager.get_all_user_names() 
    text = "```\n" + "\n".join(names) + "\n```"
    await ctx.send(text)

    user_id = "<@" + str(ctx.author.id) + ">"

    embed=discord.Embed(title="MBot Log", color=0x16abb6)  #Log embedleri için renk bu
    embed.add_field(name="Log Type:", value="Command Use", inline=False)
    embed.add_field(name="Used Command: ", value=".members", inline=False)
    embed.add_field(name="Used by:", value= (user_id + " - " + str(ctx.author)), inline=False)
    embed.add_field(name="Time:", value=datetime.strftime(datetime.now(),"%H.%M"), inline=False)
    embed.add_field(name="Date:", value=datetime.strftime(datetime.now(),"%d.%m.%Y"), inline=False)
    embed.add_field(name="Used Channel:", value=str(ctx.channel), inline=False)
    
    embed.set_thumbnail(url = ctx.author.avatar_url)
    embed.set_footer(icon_url = ctx.author.avatar_url, text = f"Requested by {ctx.author.display_name}")

    log_channel = client.get_channel(log_channel_id)
    await log_channel.send(embed=embed)

@client.command()
@commands.has_permissions(administrator = True)
async def leaderboard(ctx):

    text = "```bash\n"
    max_character = 0
    user_names = mini_game_manager.get_ordered_users_by_level()

    for i in range(len(user_names)):
        
        if len(client.get_user(user_manager.get_user_info(user_names[i][0])[3]).name) > max_character:
            max_character = len(client.get_user(user_manager.get_user_info(user_names[i][0])[3]).name)

    for i in range(len(user_names)):
        
        character = max_character - len(client.get_user(user_manager.get_user_info(user_names[i][0])[3]).name)
        if (i + 1) < 10:
            text += str(i + 1) + "-)  \"" + client.get_user(user_manager.get_user_info(user_names[i][0])[3]).name + "\"" + str("‎‎‏‏‎ ‎" * character) + " : Level " + str(user_names[i][1])
        else:
            text += str(i + 1) + "-) \"" + client.get_user(user_manager.get_user_info(user_names[i][0])[3]).name + "\"" + str("‎‎‏‏‎ ‎" * character) + " : Level " + str(user_names[i][1])
        text += "\n"

        if (i + 1) % 5 == 0:
            
            embed=discord.Embed(title="Leaderboard", color=0x16abb6)
            text += "```"
            if (i+1) == 5:
                embed.add_field(name="Top 5", value=text, inline=False)
            else:
                embed.add_field(name=str(i - 4) + "-" + str(i+1), value=text, inline=False)
            text = "```bash\n"

            embed.set_footer(text = datetime.strftime(datetime.now(),"%d.%m.%Y | %H:%M"))
            await ctx.send(embed=embed)

@client.command(aliases=['dailyleaderboard'])
async def dailyLeaderboard(ctx):

    text = "```bash\n"
    max_character = 0
    user_names = user_manager.get_ordered_list_by_daily_eared_points()

    for i in range(5):
        
        if len(client.get_user(user_manager.get_user_info(user_names[i][0])[3]).name) > max_character:
            max_character = len(client.get_user(user_manager.get_user_info(user_names[i][0])[3]).name)

    for i in range(5):

        character = max_character - len(client.get_user(user_manager.get_user_info(user_names[i][0])[3]).name)
        text += str(i + 1) + "-) \"" + client.get_user(user_manager.get_user_info(user_names[i][0])[3]).name + "\"" + str("‎‎‏‏‎ ‎" * character) + " : " + str(user_names[i][1])
        text += "\n"

    text += "```"
     
    embed=discord.Embed(title="Daily Leaderboard",description="Username - Daily Earned Points" ,color=0x16abb6)
    embed.add_field(name="Top 5", value=text, inline=False)

    embed.set_footer(text = datetime.strftime(datetime.now(),"%d.%m.%Y | %H:%M"))
    await ctx.send(embed=embed)

@client.command(aliases=['horserace'])
async def horseRace(ctx, betting_time = 60):

    global is_playing_game

    if is_playing_game:
        return
    else:
        is_playing_game = True

    if betting_time <= 0:
        await ctx.send("Invalid arguments.")
        is_playing_game = False
        return

    chat_channel = client.get_channel(chat_channel_id)

    notification_embed = discord.Embed(color=0x16abb6)
    notification_embed.add_field(name=":loudspeaker:"+ ctx.author.display_name + " has started a 'Horse Race' mini game.", value = "Players: 0")
    notification_embed_message = await chat_channel.send(embed=notification_embed)

    start_time = time.time()

    horses = [
        "düldül",
        "at",
        "dıgıdık",
        "friday",
        "horsea",
        "koptagel"
    ]

    bets = {}
    deleted_message_ids = []

    bet_embed=discord.Embed(title="Horse Race", color=0x16abb6)  
    bet_embed.add_field(name="Bet Phase", value="Type your bets like 'bet [horse_name] [bet]'\nGame will start at " + datetime.strftime(datetime.now() + timedelta(seconds=betting_time), "%H:%M:%S") + "\nAt least 3 people must join to start the game.", inline=False)
    bet_embed.add_field(name="Horses", value="\n".join(horses), inline=False)

    bet_embed_message = await ctx.send(embed=bet_embed)


    def check(msg):

        if str(msg.author) == "MBot#3059":
            return False

        if not msg.channel == ctx.channel:
            return False

        return True
            
    while (time.time() - start_time) < betting_time:
        
        try:
            msg = await client.wait_for("message",timeout=3.0,check= check)
           
        except asyncio.TimeoutError:
            continue
        
        else:
            try:
                deleted_message_ids.append(msg.id)

                words = []
                word = ""
                
                for letter in range(len(msg.content)):
                    
                    if msg.content[letter] == " ":
                        words.append(word)
                        word = ""
                    elif letter == len(msg.content) - 1:
                        word += msg.content[letter]
                        words.append(word)
                    else:
                        word += msg.content[letter]

                if len(words) == 3 and words[0] == "bet" and words[1] in horses:

                    try:
                        if user_manager.get_user_info(str(msg.author))[1] >= int(words[2]) and int(words[2]) > 0:
                        
                            if not str(msg.author) in bets.keys():
                                bets[str(msg.author)] = [words[1], int(words[2])]  #[horse, bet]
                                user_manager.decrease_points(str(msg.author), int(words[2]))
                                bet_embed.add_field(name=str(msg.author.display_name), value=" set bet to " + words[1] + " " + words[2] + " points.", inline=False)
                                
                                await bet_embed_message.edit(embed=bet_embed)

                            else:
                                if bets[str(msg.author)][0] == words[1]:
                                    bets[str(msg.author)][1] += int(words[2])
                                    user_manager.decrease_points(str(msg.author), int(words[2]))

                                    bet_embed.add_field(name=str(msg.author.display_name), value=" set bet to " + words[1] + " " + words[2] + " points.", inline=False)
                                    await bet_embed_message.edit(embed=bet_embed)

                            # update notification embed
                            notification_embed = discord.Embed(color=0x16abb6)
                            notification_embed.add_field(name=":loudspeaker:"+ ctx.author.display_name + " has started a 'Horse Race' mini game.", value = "Players: " + str(len(bets)))
                            await notification_embed_message.edit(embed=notification_embed)
                                    
                        else:
                            print("Not enough points.")
                        
                    except:
                        print("Invalid number")
            except:
                print("Invalid message")
                
    for id in deleted_message_ids:
        msg = await ctx.fetch_message(id)
        await msg.delete()

    #await bet_embed_message.delete()
    await notification_embed_message.delete()

    def get_race_board(l1,l2,l3,l4,l5,l6):

        row1 = horses[0] + "  : " + l1
        row2 = horses[1] + "  : " + l2
        row3 = horses[2] + " : " + l3
        row4 = horses[3] + ": " + l4
        row5 = horses[4] + "  : " + l5
        row6 = horses[5] + ": " + l6

        race_board = "```\n" + row1 + "\n" + row2 + "\n" + row3 + "\n" + row4 + "\n" + row5 + "\n" + row6 + "\n```"

        return race_board

    line1= "■" + str("-" * 9)
    line2= "■" + str("-" * 9)
    line3= "■" + str("-" * 9)
    line4= "■" + str("-" * 9)
    line5= "■" + str("-" * 9)
    line6= "■" + str("-" * 9)
    lines = [line1,line2,line3,line4,line5,line6]

    winner_horse = ""
    winners = []
    
    if len(bets) < 3:
        await ctx.send("Not bets were played. Game has been cancelled.")
        is_playing_game = False

        # refund
        for player, data in bets.items():
            user_manager.increase_points(player, data[1], False) # don't increase daily earned points.

        return
    
    else:
        embed1=discord.Embed(title="Horse Race", color=0x16abb6)  
        embed1.add_field(name="Race is starting...", value=get_race_board(*lines), inline=False)
        message = await ctx.send(embed=embed1)

    await asyncio.sleep(3)
    game_end = False

    while not game_end:
        
        await asyncio.sleep(2)
        
        horse_location = 0

        move_num = random.randint(0, 5)
        move = lines[move_num]

        for letter in range(len(move)):
            if move[letter] == "■":
                horse_location = letter
   
        new_line = ""
        for letter in range(len(move)):
            
            if letter == horse_location + 1:
                new_line += "■"
    
            else:
                new_line += "-"
       
        lines[move_num] = new_line
    
        embed2=discord.Embed(title="Horse Race", color=0x16abb6) 
        embed2.add_field(name="Good Luck!", value=get_race_board(*lines), inline=False)
        await message.edit(embed=embed2)

        for line in range(len(lines)):
            if (lines[line])[-1] == "■":
                winner_horse = horses[line]
                await asyncio.sleep(2)

                embed2=discord.Embed(title="Horse Race", color=0x16abb6)  
                embed2.add_field(name="Yeehaa", value=get_race_board(*lines), inline=False)
                embed2.add_field(name="Winner Horse", value=winner_horse, inline=False)
                await message.edit(embed=embed2)
                game_end = True
                break

    for name, value in bets.items():
        if value[0] == winner_horse:
            winners.append(name)

    if len(winners) == 0:
        embed4=discord.Embed(title="Race is over!", color=0x16abb6)  
        embed4.add_field(name="Results", value="No one has won.", inline=False)
        await ctx.send(embed = embed4)
        is_playing_game = False
        return

    total_bets_played = 0
    winner_bets_played = 0

    for bet in bets.values():
        total_bets_played += bet[1]

    for winner in winners:
        winner_bets_played += bets[winner][1]

    winner_multiple = total_bets_played / winner_bets_played

    result_board = ""

    for winner in winners:
        
        multiplier = mini_game_manager.get_user_info(winner)[3] + mini_game_manager.bet_multiplier_for_level[mini_game_manager.get_user_info(winner)[2]]
        winner_multiple = winner_multiple * (100 + multiplier) / 100

        user_manager.increase_points(winner, round(bets[winner][1] * winner_multiple))
        result_board += client.get_user(user_manager.get_user_info(winner)[3]).name +" has won " +  str(round(bets[winner][1] * winner_multiple)) + " points.\n"

        mini_game_manager.increase_exp(winner, round((100 - 1/6 * 100) / 5))

    embed3=discord.Embed(title="Race is over!", color=0x16abb6)  
    embed3.add_field(name="Results", value=result_board, inline=False)
    await ctx.send(embed = embed3)
    is_playing_game = False
    return

@client.command()
async def slots(ctx, bet: int):
    
    if bet <= 0:
        await ctx.send("Bet must be a positive integer.")
        return

    if user_manager.get_user_info(str(ctx.author))[1] < bet:
        await ctx.send("You don't have enough points.")
        return

    user_manager.decrease_points(str(ctx.author), bet)
    
    symbols = [":cherries:", ":lemon:", ":grapes:",":tangerine:"]
    symbol1 = ""
    symbol2 = ""
    symbol3 = ""
    
    lose_chance = 0.55
    pair_chance = 0.25

    random_num = random.uniform(0,1)

    bonus = (1 - lose_chance - pair_chance) * (100 + mini_game_manager.get_user_info(str(ctx.author))[4]) / 100
    bonus -= (1 - lose_chance - pair_chance)

    if random_num <= lose_chance - bonus:

        symbol1 = random.choice(symbols)
        symbols.remove(symbol1)

        symbol2 = random.choice(symbols)
        symbols.remove(symbol2)

        symbol3 = random.choice(symbols)

    elif random_num <= lose_chance + pair_chance - bonus:  #Double match
        
        selected_symbols = ["","",""]
        indexs = [0,1,2]

        index1 = random.choice(indexs)
        indexs.remove(index1)

        index2 = random.choice(indexs)
        indexs.remove(index2)

        selected_pair = random.choice(symbols)
        selected_symbols[index1] = selected_pair
        selected_symbols[index2] = selected_pair
        
        symbols.remove(selected_pair)
        selected_symbols[random.choice(indexs)] = random.choice(symbols)

        symbol1 = selected_symbols[0]
        symbol2 = selected_symbols[1]
        symbol3 = selected_symbols[2]

    else:  #Triple match

        selected_symbol = random.choice(symbols)
        symbol1 = selected_symbol
        symbol2 = selected_symbol
        symbol3 = selected_symbol

    embed1=discord.Embed(title="Slot Machine",description="Spinning..." ,color=0x16abb6)  
    embed1.add_field(name="Slot1", value=symbol1, inline=True)
    message = await ctx.send(embed=embed1)

    await asyncio.sleep(5)

    embed2=discord.Embed(title="Slot Machine",description="Spinning..." ,color=0x16abb6)  
    embed2.add_field(name="Slot1", value=symbol1, inline=True)
    embed2.add_field(name="Slot2", value=symbol2, inline=True)
    await message.edit(embed=embed2)

    await asyncio.sleep(5)

    embed3=discord.Embed(title="Slot Machine", color=0x16abb6)  
    embed3.add_field(name="Slot1", value=symbol1, inline=True)
    embed3.add_field(name="Slot2", value=symbol2, inline=True)
    embed3.add_field(name="Slot3", value=symbol3, inline=True)
    await message.edit(embed=embed3)

    await asyncio.sleep(1)

    if symbol1 == symbol2 and symbol2 == symbol3:

        multiplier = mini_game_manager.get_user_info(str(ctx.author))[3] + mini_game_manager.bet_multiplier_for_level[mini_game_manager.get_user_info(str(ctx.author))[2]]
        winner_multiplier = 2 * (100 + multiplier) / 100

        embed3.add_field(name="Result", value= "All of the symbols are matching! You won {} points.".format(str(round(bet * winner_multiplier))), inline=False)
        await message.edit(embed=embed3)
        
        user_manager.increase_points(str(ctx.author), round(bet * winner_multiplier))

        mini_game_manager.increase_exp(str(ctx.author), round(((100 - ((1 - lose_chance - pair_chance) * 100)) / 5) - 3))
        return

    else:
        symbol_count = {}
        
        for symbol in [symbol1,symbol2, symbol3]:
            if symbol in symbol_count.keys():
                symbol_count[symbol] +=1
            else:
                symbol_count[symbol] = 1

        for count in symbol_count.values():
            if count == 2:
                embed3.add_field(name="Result", value= "2 symbols are matching. You didn't lose or win anything.", inline=False)
                await message.edit(embed=embed3)
                
                user_manager.increase_points(str(ctx.author), bet, False)
                return

        embed3.add_field(name="Result", value= "None of the symbols are matching.You lost {} points.".format(bet), inline=False)
        await message.edit(embed=embed3)
        
        return

@client.command()
@commands.has_permissions(administrator = True)
async def mute(ctx, member : discord.Member, time = "0"):
    
    if time == "0":

        role_muted = discord.utils.get(ctx.guild.roles, name = "Muted")
        
        await member.add_roles(role_muted)
        
        embed=discord.Embed(title="User Muted!", description="**{0}** was muted by **{1}**!".format(member.mention, ctx.author.mention), color=0x16abb6)
        await ctx.send(embed=embed)

    else:
        times = {"s" : 1, "m" : 60 , "h" : 3600, "d" : 3600 * 24, "w" : 3600 * 24 * 7}

        if time[-1] in times.keys():
            try:
                if int(time[:-1]) > 0:

                    role_muted = discord.utils.get(ctx.guild.roles, name = "Muted")
                    await member.add_roles(role_muted)

                    embed=discord.Embed(title="User Muted!", description="**{0}** was muted by **{1}** for {2} {3}!".format(member.mention, ctx.author.mention, time[:-1], time[-1]), color=0x16abb6)
                    await ctx.send(embed=embed)
                
                    await asyncio.sleep(int(time[:-1]) * times[time[-1]])
                    await member.remove_roles(role_muted)

                    embed=discord.Embed(title="User Unmuted!", description="**{0}** was unmuted by **{1}**!".format(member.mention, ctx.author.mention), color=0x16abb6)
                    await ctx.send(embed=embed)

                else:
                    await ctx.send("Invalid argument")
                    return

            except:
                await ctx.send("Invalid argument")
                return

        else:
            await ctx.send("Invalid argument")
            return

@client.command()
@commands.has_permissions(administrator = True)
async def unmute(ctx, member : discord.Member):
    
    role_muted = discord.utils.get(ctx.guild.roles, name = "Muted")
   
    await member.remove_roles(role_muted)

    embed=discord.Embed(title="User Unmuted!", description="**{0}** was unmuted by **{1}**!".format(member.mention, ctx.author.mention), color=0x16abb6)
    await ctx.send(embed=embed)

@client.command()
@commands.has_permissions(administrator = True)
async def voteCheck(ctx, vote):
    
    embed=discord.Embed(title="Oylama", color=0x22c3a8)
    embed.add_field(name=vote, value=".", inline=False)
    message = await ctx.send(embed=embed)

    await message.add_reaction("✅")
    await message.add_reaction("❌")

    await ctx.message.delete()

@client.command()
@commands.has_permissions(administrator = True)
async def vote(ctx, *args):

    if len(args) > 8:
        await ctx.send("Too many options, maxiumum options you can add for each voting is 8.")
        return

    emojis = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣"]
    embed=discord.Embed(title="Voting", color=0x22c3a8)

    for i in range(len(args)):
        embed.add_field(name=emojis[i], value=args[i], inline=False)

    message = await ctx.send(embed=embed)

    for i in range(len(args)):
        await message.add_reaction(emojis[i])

    await ctx.message.delete()
    
@client.command()
@commands.has_permissions(administrator = True)
async def deleteUser(ctx, name):
    
    if user_manager.check_user(name):
        user_manager.delete_user(name)
        msg = "User \"**" + name + "**\" has been deleted from the databases."
    
    if moderation.check_user(user_manager.get_user_info(name)[3]):
        moderation.delete_user(user_manager.get_user_info(name)[3])

    if mini_game_manager.check_user(name):
        mini_game_manager.delete_user(name)

    else:
        print(f"There isn't a user called {name}")
        msg = "Could not delete the user. There isn't a user called \"**" + name + "**\"."

    log_channel = client.get_channel(log_channel_id)
    await log_channel.send(msg)

@client.command()
@commands.has_permissions(administrator = True)
async def setLevel(ctx, member: discord.Member, amount : int): 

    person = ""
    if user_manager.check_user_from_id(member.id):

        if amount >= 1 and amount <= max_level:
            person = user_manager.get_user_info_from_id(member.id)[0]
            mini_game_manager.set_level(user_manager.get_user_info_from_id(member.id)[0], amount)
            mini_game_manager.set_exp(user_manager.get_user_info_from_id(member.id)[0], 0)

            member_id = "<@" + str(member.id) + ">"
            user_id = "<@" + str(ctx.author.id) + ">"

        else:
            await ctx.send("Invalid Argument")
            return

    else:
        await ctx.send("Unknown user")
        return

    embed=discord.Embed(title="MBot Log", color=0x16abb6)  #Log embedleri için renk bu
    embed.add_field(name="Log Type:", value="Command Use", inline=False)
    embed.add_field(name="Used Command: ", value=".setLevel", inline=False)
    embed.add_field(name="Used by:", value= (user_id + " - " + str(ctx.author)), inline=False)
    embed.add_field(name="Used for:", value=(member_id + " - " + person), inline=False)
    embed.add_field(name="Level: ", value=amount, inline=False)
    embed.add_field(name="Time:", value=datetime.strftime(datetime.now(),"%H.%M"), inline=False)
    embed.add_field(name="Date:", value=datetime.strftime(datetime.now(),"%d.%m.%Y"), inline=False)
    embed.add_field(name="Used Channel:", value=str(ctx.channel), inline=False)
    
    embed.set_thumbnail(url = member.avatar_url)
    embed.set_footer(icon_url = ctx.author.avatar_url, text = f"Requested by {ctx.author.display_name}")

    log_channel = client.get_channel(log_channel_id)
    await log_channel.send(embed=embed)

@client.command()
@commands.has_permissions(administrator = True)
async def increaseEXP(ctx, member: discord.Member, amount : int): 

    person = ""
    if user_manager.check_user_from_id(member.id):

        if amount >= 1:
            person = user_manager.get_user_info_from_id(member.id)[0]
            mini_game_manager.increase_exp(user_manager.get_user_info_from_id(member.id)[0], amount)

            member_id = "<@" + str(member.id) + ">"
            user_id = "<@" + str(ctx.author.id) + ">"

        else:
            await ctx.send("Invalid Argument")
            return

    else:
        await ctx.send("Unknown user")
        return

    embed=discord.Embed(title="MBot Log", color=0x16abb6)  #Log embedleri için renk bu
    embed.add_field(name="Log Type:", value="Command Use", inline=False)
    embed.add_field(name="Used Command: ", value=".increaseEXP", inline=False)
    embed.add_field(name="Used by:", value= (user_id + " - " + str(ctx.author)), inline=False)
    embed.add_field(name="Used for:", value=(member_id + " - " + person), inline=False)
    embed.add_field(name="Increased amount: ", value=amount, inline=False)
    embed.add_field(name="Time:", value=datetime.strftime(datetime.now(),"%H.%M"), inline=False)
    embed.add_field(name="Date:", value=datetime.strftime(datetime.now(),"%d.%m.%Y"), inline=False)
    embed.add_field(name="Used Channel:", value=str(ctx.channel), inline=False)
    
    embed.set_thumbnail(url = member.avatar_url)
    embed.set_footer(icon_url = ctx.author.avatar_url, text = f"Requested by {ctx.author.display_name}")

    log_channel = client.get_channel(log_channel_id)
    await log_channel.send(embed=embed)

@client.command()
@commands.has_permissions(administrator = True)
async def warn(ctx, member: discord.Member, reason = "Not specified"):

    min_mute_duration = 15 # minutes
    min_warnings_to_get_muted = 3
    
    author_user_name = user_manager.get_user_info_from_id(member.id)[0]
    user_manager.add_warning(author_user_name)

    embed=discord.Embed(title="Warning", color=0x16abb6)
    embed.add_field(name=member.display_name + " has been warned", value="*Reason:* " + reason, inline=False)
    embed.add_field(name="Active Warnings",value=str(user_manager.get_user_info_from_id(member.id)[2]) + " warnings")

    embed.set_thumbnail(url = member.avatar_url)
    embed.set_footer(text = datetime.strftime(datetime.now(),"%d.%m.%Y | %H.%M"))

    await ctx.send(embed=embed)

    print("Warned" + member.display_name + ".Warnings: " + str(user_manager.get_user_info(author_user_name)[2]))

    if user_manager.get_user_info_from_id(member.id)[2] >= min_warnings_to_get_muted:
        
        mute_duration = min_mute_duration * pow(2, (user_manager.get_user_info_from_id(member.id)[2] - min_warnings_to_get_muted)) # as minutes
        now = datetime.now()
        
        mute_end_date = now + timedelta(minutes=mute_duration)
        mute_end_date_string = mute_end_date.strftime("%d/%m/%Y %H:%M:%S")
     
        role_muted = discord.utils.get(client.get_guild(guild_id).roles, name = "Muted")
        user = discord.utils.get(client.get_all_members(), id=member.id)

        if not role_muted in user.roles:
            await user.add_roles(role_muted) # mute the user
        
        moderation.add_mute(member.id,mute_end_date_string)

        print("User " + member.display_name + " has muted for " + str(mute_duration) + " minutes.")

@client.command()
@commands.has_permissions(administrator = True)
async def removeWarning(ctx, member: discord.Member, remove_amount=1):

    author_user_name = user_manager.get_user_info_from_id(member.id)[0]

    if user_manager.get_user_info(author_user_name)[2] >= remove_amount:

        user_manager.remove_warning(author_user_name, remove_amount)

        print("Removed warning from " + member.display_name + ".Warnings: " + str(user_manager.get_user_info(author_user_name)[2]))

    else:
        print("Can't remove warnings." + member.display_name + " has" + str(user_manager.get_user_info(author_user_name)[2]) + " warnings.")

@client.command()
@commands.has_permissions(administrator = True)
async def setPoints(ctx, member: discord.Member, amount): 

    person = ""
    if user_manager.check_user_from_id(member.id):
        person = user_manager.get_user_info_from_id(member.id)[0]
        user_manager.set_points(str(user_manager.get_user_info_from_id(member.id)[0]), amount)

        member_id = "<@" + str(member.id) + ">"
        user_id = "<@" + str(ctx.author.id) + ">"

    else:
        await ctx.send("Unknown user")
        return

    embed=discord.Embed(title="MBot Log", color=0x16abb6)  #Log embedleri için renk bu
    embed.add_field(name="Log Type:", value="Command Use", inline=False)
    embed.add_field(name="Used Command: ", value=".setPoints", inline=False)
    embed.add_field(name="Used by:", value= (user_id + " - " + str(ctx.author)), inline=False)
    embed.add_field(name="Used for:", value=(member_id + " - " + person), inline=False)
    embed.add_field(name="Points: ", value=amount, inline=False)
    embed.add_field(name="Time:", value=datetime.strftime(datetime.now(),"%H.%M"), inline=False)
    embed.add_field(name="Date:", value=datetime.strftime(datetime.now(),"%d.%m.%Y"), inline=False)
    embed.add_field(name="Used Channel:", value=str(ctx.channel), inline=False)
    
    embed.set_thumbnail(url = member.avatar_url)
    embed.set_footer(icon_url = ctx.author.avatar_url, text = f"Requested by {ctx.author.display_name}")

    log_channel = client.get_channel(log_channel_id)
    await log_channel.send(embed=embed)

    #await ctx.send(str(ctx.author.display_name))  Nick gösteriyor!!!
    #await ctx.send("<@" + "340437546104389643" + ">")  Kullanıcı için mention!!!!

@client.command()
async def pay(ctx, member: discord.Member, pay_value = 5):

    if pay_value <= 0:
        await ctx.send("Pay must be a positive integer.")
        return

    if pay_value > max_pay:
        await ctx.send("Pay must be smaller than " + str(max_pay) + ".")
        return
        
    if user_manager.get_user_info(str(ctx.author))[1] >= pay_value:   #check points
        
        if user_manager.get_user_info(str(ctx.author))[4] > 0:  #check pay
            
            user_manager.decrease_points(str(ctx.author), pay_value)
            user_manager.increase_points(user_manager.get_user_info_from_id(member.id)[0], pay_value)
            user_manager.decrease_pay(str(ctx.author), 1)
            await ctx.send(ctx.author.mention + " has paid " + member.mention)
        else:
            
            await ctx.send("You can only send points once a day.")

    else:
        
        await ctx.send("You don't have enough points")

@client.command()
async def points(ctx, member: discord.Member = None):
    
    member_id = ""
    points = 0
    mentioned_member = None
    user_id = "<@" + str(ctx.author.id) + ">"

    person = ""
    if member is None:
        person = str(ctx.author)
        member_id = "<@" + str(ctx.author.id) + ">"
        mentioned_member = client.get_user(ctx.author.id)

        points = user_manager.get_user_info(str(ctx.message.author))[1]
        
    elif user_manager.check_user_from_id(member.id):
        person = user_manager.get_user_info_from_id(member.id)[0]
        member_id = "<@" + str(member.id) + ">"
        mentioned_member = member

        points = user_manager.get_user_info_from_id(member.id)[1]

    else:
        await ctx.send("Unknown user")
        return

    #Disco
    embed=discord.Embed(title="Points", description= member_id + " has " + str(points) + " points.",color=0x16abb6)
    embed.set_footer(icon_url = ctx.author.avatar_url, text = f"Requested by {ctx.author.display_name}")
    await ctx.send(embed=embed)
    
    #Log
    embed=discord.Embed(title="MBot Log", color=0x16abb6)  #Log embedleri için renk bu
    embed.add_field(name="Log Type:", value="Command Use", inline=False)
    embed.add_field(name="Used Command: ", value=".points", inline=False)
    embed.add_field(name="Used by:", value= (user_id + " - " + str(ctx.author)), inline=False)
    embed.add_field(name="Used for:", value=(member_id + " - " + person), inline=False)
    embed.add_field(name="Points: ", value=points, inline=False)
    embed.add_field(name="Time:", value=datetime.strftime(datetime.now(),"%H.%M"), inline=False)
    embed.add_field(name="Date:", value=datetime.strftime(datetime.now(),"%d.%m.%Y"), inline=False)
    embed.add_field(name="Used Channel:", value=str(ctx.channel), inline=False)
    embed.set_thumbnail(url = mentioned_member.avatar_url)
    embed.set_footer(icon_url = ctx.author.avatar_url, text = f"Requested by {ctx.author.display_name}")

    log_channel = client.get_channel(log_channel_id)
    await log_channel.send(embed=embed)

    #await ctx.send(str(ctx.author.display_name))  Nick gösteriyor!!!
    #await ctx.send("<@" + "340437546104389643" + ">")  Kullanıcı için mention!!!!

@client.command()
async def ping(ctx):  #Botun gecikmesini,pingini, milisaniye cinsinden gösterir.
    
    ping_ = str(round(client.latency * 1000))
    user_id = "<@" + str(ctx.author.id) + ">"
    await ctx.send(f"Ping: {ping_}ms")
    
    embed=discord.Embed(title="MBot Log", color=0x16abb6)
    embed.add_field(name="Log Type:", value="Command Use", inline=False)
    embed.add_field(name="Used Command: ", value=".ping", inline=False)
    embed.add_field(name="Used by:", value=(user_id + " - " + str(ctx.author)), inline=False)
    embed.add_field(name="Ping:", value=ping_, inline=False)
    embed.add_field(name="Time:", value=datetime.strftime(datetime.now(),"%H.%M"), inline=False)
    embed.add_field(name="Date:", value=datetime.strftime(datetime.now(),"%d.%m.%Y"), inline=False)
    embed.add_field(name="Used Channel:", value=ctx.channel, inline=False)
    embed.set_thumbnail(url = ctx.author.avatar_url)
    embed.set_footer(icon_url = ctx.author.avatar_url, text = f"Requested by {ctx.author.display_name}")

    log_channel = client.get_channel(log_channel_id)
    await log_channel.send(embed=embed)

@client.command()
async def lottery(ctx, *args):

    winner = random.choice(args)
    await ctx.send(f"Winner: {winner}")
    
    arguments = "\n".join(args)
    user_id = "<@" + str(ctx.author.id) + ">"

    embed=discord.Embed(title="MBot Log", color=0x16abb6)
    embed.add_field(name="Log Type:", value="Command Use", inline=False)
    embed.add_field(name="Used Command: ", value=".lottery", inline=False)
    embed.add_field(name="Used by:", value=(user_id + " - " + str(ctx.author)), inline=False)
    embed.add_field(name="Arguments", value=arguments, inline=False)
    embed.add_field(name="Winner", value=winner, inline=False)
    embed.add_field(name="Time:", value=datetime.strftime(datetime.now(),"%H.%M"), inline=False)
    embed.add_field(name="Date:", value=datetime.strftime(datetime.now(),"%d.%m.%Y"), inline=False)
    embed.add_field(name="Used Channel:", value=ctx.channel, inline=False)
    embed.set_thumbnail(url = ctx.author.avatar_url)
    embed.set_footer(icon_url = ctx.author.avatar_url, text = f"Requested by {ctx.author.display_name}")

    log_channel = client.get_channel(log_channel_id)
    await log_channel.send(embed=embed)
    
@client.command()
@commands.has_permissions(administrator = True)
async def say(ctx, *, args):
    
    await ctx.message.delete()
    await ctx.send(f"{args}")

    user_id = "<@" + str(ctx.author.id) + ">"
        
    embed=discord.Embed(title="MBot Log", color=0x16abb6)  #Log embedleri için renk bu
    embed.add_field(name="Log Type:", value="Command Use", inline=False)
    embed.add_field(name="Used Command: ", value=".say", inline=False)
    embed.add_field(name="Used by:", value=(user_id + " - " + str(ctx.author)), inline=False)
    embed.add_field(name="Content:", value=args, inline=False)
    embed.add_field(name="Time:", value=datetime.strftime(datetime.now(),"%H.%M"), inline=False)
    embed.add_field(name="Date:", value=datetime.strftime(datetime.now(),"%d.%m.%Y"), inline=False)
    embed.add_field(name="Used Channel:", value=str(ctx.channel), inline=False)
        
    embed.set_thumbnail(url = ctx.author.avatar_url)
    embed.set_footer(icon_url = ctx.author.avatar_url, text = f"Requested by {ctx.author.display_name}")

    log_channel = client.get_channel(log_channel_id)
    await log_channel.send(embed=embed)

@client.command()
async def warnings(ctx):
    
    min_mute_duration = 15 # minutes
    min_warnings_to_get_muted = 3

    active_warnings = user_manager.get_user_info(str(ctx.author))[2]
    mute_duration = min_mute_duration * pow(2, (active_warnings - min_warnings_to_get_muted))

    embed=discord.Embed(title="Warnings", description= ctx.author.mention + " has " + str(active_warnings) + " warnings.",color=0x16abb6)
    
    if active_warnings >= 2:
        embed.add_field(name="Next Mute Duration", value=str(mute_duration), inline=False)
    
    embed.set_footer(icon_url = ctx.author.avatar_url, text = f"Requested by {ctx.author.display_name}")
    await ctx.send(embed=embed)

@client.command()
@commands.has_permissions(administrator = True)
async def clear(ctx, amount = 1):

    await ctx.channel.purge(limit=amount)

@client.command(aliases=['ttt'])
async def ticTacToe(ctx, member: discord.Member, bet = 0):

    #  send invite (30 seconds of waiting time)
    #  accept invite
    #  determine the symbols, make the player who send the invite's symbol to "x" and the other's "o" 
    #  start with the player whose symbol is "x"  **************
    #  check game end after every move
    #  loop turns and end game check
    #  after every turn print the visualized board
    #  if the game ends, print the winner.
    #  Show remaining time

    if bet < 0:
            await ctx.send("Bet must be a positive integer.")
            return
    elif bet > 0:
        if user_manager.get_user_info_from_id(ctx.author.id)[1] < bet or user_manager.get_user_info_from_id(member.id)[1] < bet:
            await ctx.send("Players don't have enough points.")
            return

    user_id = "<@" + str(ctx.author.id) + ">"

    if bet > 0:
        await ctx.send(user_id + " challenged " + member.mention + " in tic-tac-toe. Bet = " + str(bet) + " points. Type 'Accept' to accept the challenge. You have 30 seconds to accept.")
    else:
        await ctx.send(user_id + " challenged " + member.mention + " in tic-tac-toe. Type 'Accept' to accept the challenge. You have 30 seconds to accept.")
    
    try:
        msg = await client.wait_for("message", timeout=30.0, check= lambda message: message.author.id == member.id and message.channel == ctx.channel)
    
    except asyncio.TimeoutError:
        await ctx.send(member.mention + "didn't respond in time.")
        return
    
    else:
        if "accept" in str(msg.content).lower():
            #starter = random.choice([member.mention, user_id])
            await ctx.send("Challenge accepted! " + user_id + " is 'x' and " + member.mention + " is 'o'.")
        else:
            await ctx.send("Challange denied.")
            return

    turn = "x"

    turn_player_id = ctx.author.id
    directions = {"l" : 0, "m" : 1, "r" : 2}  #for columns
    game_manager = tic_tac_toe.GameManager()

    while True:
        
        if turn == "x":

            turn_player_id = ctx.author.id
            turn = "o"

        else:

            turn_player_id = member.id
            turn = "x"
        
        while True:

            turn_player_mention = None

            visualized_board = game_manager.get_visualized_board()
            await ctx.send("```\n" + visualized_board + "\n```")
            
            if turn_player_id == ctx.author.id:
                await ctx.send("It is " + user_id + "'s turn. Type your move.")
                turn_player_mention = user_id
            else:
                await ctx.send("It is " + member.mention + "'s turn. Type your move.")
                turn_player_mention = member.mention

            try:
                msg = await client.wait_for("message", timeout=60.0, check= lambda message: message.author.id == turn_player_id and message.channel == ctx.channel)
        
            except asyncio.TimeoutError:
                await ctx.send(turn_player_mention  + "didn't played in time. Game has ended.")
                return

            else:
                if len(str(msg.content)) == 2:
                        
                    if not str(msg.content)[1] == "0" and not str(msg.content)[1] == "1" and not str(msg.content)[1] == "2":
                        await ctx.send("Invalid move, please type a valid move.")
                        continue

                    if not str(msg.content)[0] in directions.keys():
                        
                        await ctx.send("Invalid move, please type a valid move.")
                        continue
                    
                    else:
 
                        move_x = int(str(msg.content)[1])
                        move_y = directions[str(msg.content)[0]]

                        if not game_manager.check_if_empty(move_x,move_y):
                            await ctx.send("Invalid move, please type a valid move.")
                            continue
                        else:
                            symbol = ""
                            if turn == "x":
                                symbol = "o"
                            else:
                                symbol = "x"

                            game_manager.make_a_move(symbol,move_x,move_y)
                            break

                else:
                    await ctx.send("Invalid move, please type a valid move.")
                    continue

        if game_manager.check_game_end()[0]:

            visualized_board = game_manager.get_visualized_board()
            await ctx.send("```\n" + visualized_board + "\n```")
            
            if game_manager.check_game_end()[1] == "draw":
                await ctx.send("It is a draw.")
                return

            winner = ""
            loser = ""
            winner_id = 0
            loser_id = 0
            # Decrease and increase points
            
            if game_manager.check_game_end()[1] == "x":
                winner = user_id
                loser = member.mention
                winner_id = ctx.author.id
                loser_id = member.id
            else:
                winner = member.mention
                loser = user_id
                winner_id = member.id
                loser_id = ctx.author.id

            await ctx.send("Congratulations! " + winner + " has won.")

            if bet > 0:
                user_manager.decrease_points(user_manager.get_user_info_from_id(loser_id)[0], bet)
                user_manager.increase_points(user_manager.get_user_info_from_id(winner_id)[0], bet)
                await ctx.send(winner + " has won " + str(bet) + " points.\n" + loser + " has lost " + str(bet) + " points.")
            
            return    

@client.command()
@commands.has_permissions(administrator = True)
async def adminCommands(ctx):
    
    embed=discord.Embed(title="Admin Commands", description="Commands that only admins can use", color=0x296dc7)
    embed.add_field(name=".updateServerInfo", value="Updates database", inline=False)
    embed.add_field(name=".members", value="Shows the usernames in database", inline=False)
    embed.add_field(name=".deleteUser [username]", value="Deletes a user from database", inline=False)
    embed.add_field(name=".setPoints [name] [value]", value="Changes the points of a user", inline=False)
    embed.add_field(name=".setLevel [name] [value]", value="Changes the level of a user", inline=False)
    embed.add_field(name=".increaseEXP [name] [value]", value="Increases user's EXP.", inline=False)
    embed.add_field(name=".say [message]", value="Sends a bot message ", inline=False)
    embed.add_field(name=".clear [amount]", value="Clears messages", inline=False)
    embed.add_field(name=".voteCheck [vote_argument]", value="Starts a yes/no type voting", inline=False)
    embed.add_field(name=".vote [*arguments]", value="Starts a voting with several options", inline=False)
    embed.add_field(name=".mute [member]", value="Mutes a member", inline=False)
    embed.add_field(name=".unmute [member]", value="Unmutes a member", inline=False)
    embed.add_field(name=".leaderboard", value="Shows the current ranking in the server", inline=False)
    embed.add_field(name=".warn [member] [reason(optional)]", value="Increases the warnings of a user.", inline=False)
    embed.add_field(name=".removeWarning [member]", value="Decreases the warnings of a user.", inline=False)
    embed.add_field(name=".openMarket", value="Opens the MCoin market and starts a live graph.", inline=False)

    await ctx.send(embed=embed)

@client.command(aliases=['membercommands'])
async def memberCommands(ctx):
    
    embed=discord.Embed(title="Member Commands", description="Commands that everyone can use", color=0x296dc7)
    embed.add_field(name=".points [member(optional)]", value="Shows your points", inline=False)
    embed.add_field(name=".ping", value="Shows your connection delay", inline=False)
    embed.add_field(name=".lottery [participants]", value="Returns a random argument from given arguments", inline=False)
    embed.add_field(name=".pay [member] [value(optional, max 5)]", value="Gives points to the member from your points. Can only be used once a day", inline=False)
    embed.add_field(name=".ticTacToe/ttt [member] [bet(optional)]", value="Sends a Tic-Tac-Toe game invite to your opponent", inline=False)
    embed.add_field(name=".slots [bet]", value="Starts a slot machine game. 2 symbols match: no gain, 3 symbols match: +bet points", inline=False)
    embed.add_field(name=".profile", value="Shows your profile", inline=False)
    embed.add_field(name=".dailyLeaderboard", value="Shows the daily ranking in the server of the total points earned by the user today. At the end of the day; the first one will get 150, the second one will get 100 and the third one will get 50 EXP", inline=False)
    embed.add_field(name=".hangman", value="Starts a 'hangman' mini game.", inline=False)
    embed.add_field(name=".roulette", value="Starts a 'roulette' mini game.", inline=False)
    embed.add_field(name=".horseRace", value="Starts a 'horse race' mini game.", inline=False)
    embed.add_field(name=".warnings", value="Shows how many warnings you have and the next mute duration when you get your next warning.", inline=False)
    embed.add_field(name=".MCoin [member(optional)]", value="Shows your MPoints and MCoins", inline=False)
    embed.add_field(name=".buyCoin [amount]", value="Buys you MCoin with your MPoints. You can only do this action while the market is opened.", inline=False)
    embed.add_field(name=".sellCoin [amount]", value="Sells your MCoin to MPoints. You can only do this action while the market is opened.", inline=False)
    embed.add_field(name=".exchange [amount]", value="Sells your Points to MPoints. You can only do this action while the market is opened.", inline=False)
    embed.add_field(name=".marketLeaderboard", value="Shows today's market leaderboard.", inline=False)
    embed.add_field(name=".mining", value="Mine MCoin. There is a 10 minutes cooldown between each mining.", inline=False)

    await ctx.send(embed=embed)

@client.event
async def on_message_delete(message):

    if str(message.author) == "MBot#3059" or str(message.author) == "MEE6#4876" or str(message.author) == "Groovy#7254" or str(message.author) == "FredBoat♪♪#7284":
        return
    
    if message.content.startswith(".say"):
        return

    user_id = "<@" + str(message.author.id) + ">"

    try:
        msg = "```bash\n\"" + message.content + "\"\n```"
        
        embed=discord.Embed(title="MBot Log", color=0x16abb6)
        embed.add_field(name="Log Type:", value="Message Delete", inline=False)
        embed.add_field(name="Deleted by: ", value=(user_id + " - " + str(message.author)), inline=False)
        embed.add_field(name="Deleted Content:", value=msg, inline=False)
        embed.add_field(name="Time:", value=datetime.strftime(datetime.now(),"%H.%M"), inline=False)
        embed.add_field(name="Date:", value=datetime.strftime(datetime.now(),"%d.%m.%Y"), inline=False)
        embed.add_field(name="Deleted Channel:", value=message.channel, inline=False)
        embed.set_thumbnail(url = message.author.avatar_url)

        log_channel = client.get_channel(log_channel_id)
        await log_channel.send(embed=embed)
    
    except:
        print("Can't display images or gifs in logs.")

@client.event
async def on_message(message):
    
    if message.author == client.user:
        return

    if str(message.author) == "MEE6#4876" or str(message.author) == "Groovy#7254" or str(message.author) == "FredBoat♪♪#7284":
        return

    if str(message.content).startswith("-p") and message.channel.id == 699670554311000194:  # disco channel
        return

    if message.attachments:
        if message.attachments[0].url.endswith('gif'): #It won't let the members to send downloaded gifs.
            if user_manager.check_user(str(message.author)):
        
                user = user_manager.get_user_info(str(message.author))
            
                if user[1] >= gif_cost:
                    user_manager.decrease_points(user[0], gif_cost)
                    return
                
                else:
                    print(f"User '{user[0]}' has not enough points")
                    await message.delete()
                    return
        
            else:
                print(f"There isn't a user called {str(message.author)}")

    if "https://" in message.content:
        value = 0

        if "lichess" in message.content and not "tenor.com" in message.content and not "gif" in message.content:
            return
        
        if "https://discordapp.com/channels/" in message.content:
            return

        if "tenor.com" in message.content or "gif" in message.content:
            value = gif_cost
           
        else:
            value = link_cost

        if user_manager.check_user(str(message.author)):
            
            user = user_manager.get_user_info(str(message.author))
                
            if user[1] >= value:
                user_manager.decrease_points(user[0], value)
                return
                
            else:
                print(f"User '{user[0]}' has not enough points")
                await message.delete()
                return

        else:
             print(f"There isn't a user called {str(message.author)}")
        
    #if message.content[0] == ":" and message.content[-1] == ":":
        #await message.delete()
        #await message.channel.send("Emoji atmak yasaktır!")
    await client.process_commands(message)  # Bu komut zorunlu, yoksa komutlar çalışmıyor.

@tasks.loop(hours = 1.0)
async def check_time():
    await server_manager.renew()
   
client.loop.create_task(moderation.moderate_mutes())

TOKEN = "FILL HERE WITH THE TOKEN OF THE BOT" # fill
client.run(TOKEN)
