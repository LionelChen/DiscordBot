import discord
from discord.ext import commands
from discord.utils import get
import random

description = '''Balance bot'''

bot = commands.Bot(command_prefix='$', description=description)
balance = {}
salary = {}
salary_ratio = 0.75 #Adjust salary ratio here
gift_ratio = 0.8


def read_balance():
    try:
        s = open('balance.txt', 'r', encoding="utf-8").read()
    except FileNotFoundError:
        s = open('balance.txt', 'w', encoding="utf-8")
    global balance
    try:
        balance = eval(s)
    except SyntaxError:
        print("Error, balance file empty")
        balance = {}
    except TypeError:
        print("Error, balance file empty")
        balance = {}


def save_balance():
    f = open("balance.txt", "w", encoding="utf-8")
    global balance
    f.write(str(balance))
    f.close()


def read_salary():
    s = open('salary.txt', 'r', encoding="utf-8").read()
    global salary
    salary = eval(s)


def save_salary():
    f = open("salary.txt", "w", encoding="utf-8")
    global salary
    f.write(str(salary))
    f.close()


def award_salary(user: discord.user, amount):
    global salary
    usr_id = user.id
    usr_name = user.name
    usr_dis = user.discriminator

    if usr_id in salary:
        salary[usr_id]["UsrBalance"] += amount * salary_ratio
    else:
        # User does not exist, creating new
        salary[usr_id] = {"UserName": usr_name+usr_dis, "UsrBalance": amount * salary_ratio}

    save_salary()


def gift_salary(user: discord.user, amount):
    global salary
    usr_id = user.id
    usr_name = user.name
    usr_dis = user.discriminator

    if usr_id in salary:
        salary[usr_id]["UsrBalance"] += amount * gift_ratio
    else:
        # User does not exist, creating new
        salary[usr_id] = {"UserName": usr_name+usr_dis, "UsrBalance": amount * salary_ratio}

    save_salary()


def revoke_salary(user: discord.user, amount):
    global salary
    usr_id = user.id
    usr_name = user.name
    usr_dis = user.discriminator

    if usr_id in salary:
        salary[usr_id]["UsrBalance"] -= amount * salary_ratio

    save_salary()


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    read_balance()
    read_salary()


@bot.command(pass_context=True, aliases=['添加余额'])
@commands.has_role("管理")
async def add(ctx, usr: discord.User, amount: int):
    """Add balance to user"""
    usr_id = usr.id
    usr_name = usr.name
    usr_dis = usr.discriminator

    if amount <= 0:
        await ctx.send("Amount must >= 1")
    elif usr_id in balance:
        print("User exists, adding balance")
        await ctx.send("User exists, balance before:" + str(balance[usr_id]["UsrBalance"]))
        balance[usr_id]["UsrBalance"] += amount
        await ctx.send("Succeed. Balance now:" + str(balance[usr_id]["UsrBalance"]))
        save_balance()

    else:
        # When usr does not exist
        await ctx.send("User does not exist, creating new.")
        role = get(ctx.guild.roles, name="老板")
        print(type(role))
        member = discord.utils.get(ctx.guild.members, name=usr_name)
        await member.add_roles(role)
        balance[usr_id] = {"UserName": usr_name+usr_dis, "UsrBalance": amount}
        print(balance)
        await ctx.send("Done! New balance:" + str(balance[usr_id]["UsrBalance"]))
        save_balance()


@bot.command(pass_context=True, aliases=['减少余额'])
@commands.has_any_role("管理", "接待", "男陪玩", "女陪玩")
async def deduct(ctx, usr: discord.User, amount: int):
    """substract balance from user"""
    usr_id = usr.id
    usr_name = usr.name
    usr_dis = usr.discriminator

    await ctx.send("Salary goes to:" + ctx.author.name)

    if amount <= 0:
        # Amount <= 0, abort.
        await ctx.send("Error: Amount must >= 1, abort.")
    elif usr_id in balance:
        # Amount normal, subtract usr balance.
        balance[usr_id]["UsrBalance"] -= amount
        save_balance()
        # Award token to salary file
        award_salary(ctx.author, amount)
        await ctx.send("已记录")
    else:
        # When usr does not exist
        await ctx.send("User does not exist, creating new.")
        balance[usr_id] = {"UserName": usr_name + usr_dis, "UsrBalance": -amount}
        await ctx.send("Done! New balance:" + str(balance[usr_id]["UsrBalance"]))
        save_balance()


@bot.command(pass_context=True, aliases=['礼物'])
@commands.has_any_role("管理", "接待", "男陪玩", "女陪玩")
async def gift(ctx, usr: discord.User, amount: int):
    """substract balance from user"""
    usr_id = usr.id
    usr_name = usr.name
    usr_dis = usr.discriminator

    await ctx.send("Salary goes to:" + ctx.author.name)

    if amount <= 0:
        # Amount <= 0, abort.
        await ctx.send("Error: Amount must >= 1, abort.")
    elif usr_id in balance:
        # Amount normal, subtract usr balance.
        balance[usr_id]["UsrBalance"] -= amount
        # Award token to salary file
        gift_salary(ctx.author, amount)
        await ctx.send("已记录")
    else:
        # When usr does not exist
        await ctx.send("User does not exist, creating new.")
        balance[usr_id] = {"UserName": usr_name + usr_dis, "UsrBalance": -amount}
        print(balance)
        await ctx.send("Done! New balance:" + str(balance[usr_id]["UsrBalance"]))
        save_balance()


@bot.command(pass_context=True, aliases=['撤回'])
@commands.has_any_role("管理", "接待", "男陪玩", "女陪玩")
async def revoke(ctx, usr: discord.User, amount: int):
    """revoke transaction"""
    usr_id = usr.id
    usr_name = usr.name
    usr_dis = usr.discriminator

    await ctx.send("Revoking last transaction from" + ctx.author.name)

    if amount <= 0:
        # Amount <= 0, abort.
        await ctx.send("Error: Amount must >= 1, abort.")
    elif usr_id in balance:
        # Amount normal, subtract usr balance.
        await ctx.send("User exists, balance before:" + str(balance[usr_id]["UsrBalance"]))
        balance[usr_id]["UsrBalance"] += amount
        await ctx.send("Succeed. Balance now:" + str(balance[usr_id]["UsrBalance"]))
        save_balance()
        # Award token to salary file
        revoke_salary(ctx.author, amount)
        await ctx.send(ctx.author.name + "#" + str(ctx.author.discriminator) + "'s salary got revoked by " + str(amount*salary_ratio))
    else:
        # When usr does not exist
        await ctx.send("User does not exist, check client's name again. Abort.")


@bot.command(pass_context=True, aliases=['查询余额'])
async def balance(ctx):
    """check user balance"""
    try:
        usr_id = ctx.author.id
        usr_name = ctx.author.name
        usr_dis = ctx.author.discriminator

        if usr_id in balance:
            await ctx.send("balance for " + usr_name + str(usr_dis) + ": " + str(balance[usr_id]["UsrBalance"]))
        else:
            # When usr does not exist
            await ctx.send("User does not exist, abort.")

    except commands.BadArgument:
        await ctx.send("User does not exist, abort.")




@bot.command(pass_context=True, aliases=['有钱吗'])
@commands.has_any_role("管理", "接待", "男陪玩", "女陪玩")
async def showbalance(ctx, usr: discord.User):
    """check user balance"""
    try:
        usr_id = usr.id
        usr_name = usr.name
        usr_dis = usr.discriminator

        if usr_id in balance:
            await ctx.send("balance for " + usr_name + str(usr_dis) + ": " + str(balance[usr_id]["UsrBalance"]))
        else:
            # When usr does not exist
            await ctx.send("User does not exist, abort.")

    except commands.BadArgument:
        await ctx.send("User does not exist, abort.")


@bot.command(pass_context=True, aliases=['工资'])
async def checksalary(ctx):
    """check user salary"""

    usr_id = ctx.author.id
    usr_name = ctx.author.name
    usr_dis = ctx.author.discriminator

    if ctx.author.id in salary:
        await ctx.send("salary balance for " + usr_name + "#" + str(usr_dis) + ": " + str(salary[usr_id]["UsrBalance"]))
    else:
        # When usr does not exist
        await ctx.send("User does not exist, abort.")



@bot.command(pass_context=True, aliases=['发工资'])
async def paysalary(ctx):
    """pay user salary"""

    usr_id = ctx.author.id
    usr_name = ctx.author.name
    usr_dis = ctx.author.discriminator

    if ctx.author.id in salary:
        await ctx.send("salary balance for " + usr_name + "#" + str(usr_dis) + ": " + str(salary[usr_id]["UsrBalance"]) + " is now 0")
        salary[usr_id]["UsrBalance"] = 0
        save_salary()
    else:
        # When usr does not exist
        await ctx.send("User does not exist, abort.")


@bot.command()
async def joined(ctx, member: discord.Member):
    """Says when a member joined."""
    await ctx.send('{0.name} joined in {0.joined_at}'.format(member))


@bot.group()
async def cool(ctx):
    """Says if a user is cool.
    In reality this just checks if a subcommand is being invoked.
    """
    if ctx.invoked_subcommand is None:
        await ctx.send('No, {0.subcommand_passed} is not cool'.format(ctx))


@cool.command(name='bot')
async def _bot(ctx):
    """Is the bot cool?"""
    await ctx.send('Yes, the bot is cool.')

bot.run('NjQxMzAyMTQxODc2NTY4MDY0.XcJK5g.wennaiON6AR_3TL_1J0DmE95TPE')
