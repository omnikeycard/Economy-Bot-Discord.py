import asyncio
import random
import sqlite3
import time
from random import randint

import discord
from monopolist_config import work_images, token #work_images - 291 строка, token - токен бота
from discord.ext import commands

bot = commands.Bot(command_prefix = '.')
bot.remove_command('help')
connection = sqlite3.connect("Server.db")
cursor = connection.cursor()

@bot.event
async def on_ready():
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
        name TEXT,
        id INT,
        cash INT,
        rep INT
    )""")
    connection.commit()
    g = bot.get_guild(696354089851813978)
    members = await g.fetch_members(limit=3000, after=None).flatten()
    for guild in bot.guilds:
        for member in members:
            if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
                cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0)")
            else:
                pass
    connection.commit()
    cursor.execute("SELECT * FROM users")
    table = cursor.fetchall()
    print(f'Название сервера: {guild.name}')
    print('Бот подключен к базе данных пользователей')
    connection.commit()

@bot.event
async def on_member_join(member):
    if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
        cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0)")
        connection.commit()
    else:
        pass

@bot.command(aliases=['баланс','бал', 'Бал', 'Баланс'])
async def __баланс(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send(embed = discord.Embed(
            colour = discord.Colour(0x00FFFF),
            description = f'''Баланс пользователя **{ctx.author}** составляет **{cursor.execute(f'SELECT cash FROM users WHERE id = {ctx.author.id}').fetchone()[0]}** монеток'''
            ))
    else:
        await ctx.send(embed = discord.Embed(
            colour = discord.Colour(0x00FFFF),
            description = f'''Баланс пользователя **{member}** составляет **{cursor.execute(f'SELECT cash FROM users WHERE id = {member.id}').fetchone()[0]}** монеток'''
            ))

@bot.command(aliases=['выдать'])
@commands.has_any_role('👑Администратор👑')
async def __выдать(ctx, member: discord.Member = None, amount: int = None):
    if member is None:
        await ctx.send(f'**{ctx.author}**, укажите пользователя, которому нужно изменить баланс')
    else:
        if int(amount) is None:
            await ctx.send(f'**{ctx.author}**, укажите сумму')
        elif amount < 1:
            await ctx.send(f'**{ctx.author}**, укажите положительное число')
        else:
           cursor.execute('UPDATE users SET cash = cash + {} WHERE id = {}'.format(int(amount), member.id))
           await ctx.send('Успех!')
           connection.commit()

@bot.command(aliases=['забрать'])
@commands.has_any_role('👑Администратор👑')
async def __забрать(ctx, member: discord.Member = None, amount: int = None):
    if member is None:
        await ctx.send(f'**{ctx.author}**, укажите пользователя, которому нужно изменить баланс')
    else:
        if amount is None:
            await ctx.send(f'**{ctx.author}**, укажите сумму')
        elif amount == 'all':
            cursor.execute('UPDATE users SET cash = cash + {0} WHERE id = {member.id}')
            connection.commit()
        elif int(amount) < 1:
            await ctx.send(f'**{ctx.author}**, укажите положительное число')
        else:
           cursor.execute(f'UPDATE users SET cash = cash - {amount} WHERE id = {member.id}')
           await ctx.send('Успех!')
           connection.commit()

@bot.command(aliases=['подарить', 'отправить'])
async def __подарить(ctx, member: discord.Member = None, amount: int = None):
    if member is None:
        await ctx.send(f'**{ctx.author}**, укажите пользователя!')
    else:
        if amount is None:
            await ctx.send(f'**{ctx.author}**, укажите сумму')
        elif int(amount) < 1:
            await ctx.send(f'**{ctx.author}**, укажите положительное число')
        else:
            cursor.execute(f'UPDATE users SET cash = cash + {amount} WHERE id = {member.id}')
            cursor.execute(f'UPDATE users SET cash = cash - {amount} WHERE id = {ctx.author.id}')
            await ctx.send('Успех!')
            connection.commit()

@bot.command(aliases = ['магазин', 'Магазин'])
async def __магазин(ctx):
    shop = discord.Embed(
        colour = discord.Colour(0x00FFFF),
        title = 'Магазин',
        description = '''
**Роли:**
1) <@&696360882585862144> - 300 монеток/неделя
• Привелегия первого уровня

2) <@&696361124991467560> - 900 монеток/неделя
• Привелегия второго уровня

3) <@&776747039257133056> - 1500 монеток/48 часов
• Перемещает вас на видное место в списке онлайна

**Разное:**
4) Посадить любого человека в <#764420003700539422> на 1 час - 5000 монет
• Можно садить самого себя <:smile:709712917716533288>
''')
    shop.set_footer(text = 'Для покупки введите: .купить <номер товара>')
    await ctx.send(embed = shop)

@bot.command(aliases = ['купить', 'Купить'])
async def __купить(ctx, arg):

    if (arg == '1'):
        if cursor.execute(f'SELECT cash FROM users WHERE id = {ctx.author.id}').fetchone()[0] >= 100:
            cursor.execute(f"UPDATE users SET cash = cash - {100} WHERE id = {ctx.author.id}")
            connection.commit()

            author = ctx.author # получаем автора сообщения
            guild = bot.get_guild(696354089851813978) # получаем объект сервера
            role1 = guild.get_role(696360882585862144) # получаем объект роли
            await author.add_roles(role1)
            await ctx.send('Успех!')
            await asyncio.sleep(604800)
            await author.remove_roles(role1) 
        else:
            await ctx.send('На балансе недостаточно денег!')

    elif (arg == '2'):
        if cursor.execute(f'SELECT cash FROM users WHERE id = {ctx.author.id}').fetchone()[0] >= 300:
            cursor.execute(f"UPDATE users SET cash = cash - {300} WHERE id = {ctx.author.id}")
            connection.commit()

            author = ctx.author # получаем автора сообщения
            guild = bot.get_guild(696354089851813978) # получаем объект сервера
            role2 = guild.get_role(696361124991467560) # получаем объект роли
            await author.add_roles(role2)
            await ctx.send('Успех!')
            await asyncio.sleep(604800)
            await author.remove_roles(role2)
            
        else:
            await ctx.send('На балансе недостаточно денег!')

    elif (arg == '3'):
        if cursor.execute(f'SELECT cash FROM users WHERE id = {ctx.author.id}').fetchone()[0] >= 900:
            cursor.execute(f"UPDATE users SET cash = cash - {900} WHERE id = {ctx.author.id}")
            connection.commit()

            author = ctx.author # получаем автора сообщения
            guild = bot.get_guild(696354089851813978) # получаем объект сервера
            role3 = guild.get_role(776747039257133056) # получаем объект роли
            await author.add_roles(role3)
            await ctx.send('Успех!')
            await asyncio.sleep(172800)
            await author.remove_roles(role3)
            
        else:
            await ctx.send('На балансе недостаточно денег!')

    elif (arg == '4'):
        if cursor.execute(f'SELECT cash FROM users WHERE id = {ctx.author.id}').fetchone()[0] >= 5000:
            cursor.execute(f"UPDATE users SET cash = cash - {5000} WHERE id = {ctx.author.id}")
            connection.commit()
            await ctx.send('''Зовём мастера по тюрягам (разрешаю вам запинговать его до смерти)

<@678216429178322968>
<@678216429178322968>
<@678216429178322968>
<@678216429178322968>
<@678216429178322968>''')
        else:
            await ctx.send('На балансе недостаточно денег!')

@bot.command(aliases = ['топ', 'Топ'])
async def __топ(ctx):
    toplist = cursor.execute('SELECT cash, name FROM users').fetchall()
    toplist.sort(reverse = True, key = lambda toplist: toplist[0])

    member_0 = toplist[0]
    member_1 = toplist[1]
    member_2 = toplist[2]
    member_3 = toplist[3]
    member_4 = toplist[4]
    member_5 = toplist[5]
    member_6 = toplist[6]
    member_7 = toplist[7]
    member_8 = toplist[8]
    member_9 = toplist[9]

    embed = discord.Embed(
        title = 'ТОП-10 участников по балансу',
        description = f'''
1. {member_0}
2. {member_1}
3. {member_2}
4. {member_3}
5. {member_4}
6. {member_5}
7. {member_6}
8. {member_7}
9. {member_8}
10. {member_9}
''')
    await ctx.send(embed = embed)


@bot.command(aliases = ['профиль', 'я', 'Я', 'Профиль'])
async def __я(ctx, member: discord.Member = None):
    if member is None:
        profile_id = cursor.execute(f'SELECT id FROM users WHERE id = {ctx.author.id}').fetchone()[0]
        profile_cash = cursor.execute(f'SELECT cash FROM users WHERE id = {ctx.author.id}').fetchone()[0]
        profile_rep = cursor.execute(f'SELECT rep FROM users WHERE id = {ctx.author.id}').fetchone()[0]

        embed = discord.Embed(
            colour = discord.Colour(0x00FFFF),
            title = f'Профиль участника {ctx.author}',
            description = f'''
• **Никнейм:** <@{profile_id}>
• **ID:** {profile_id}

• **Баланс:** {profile_cash}
• **Репутация:** {profile_rep}
''')
        await ctx.send(embed = embed)
    else:
        profile_id = cursor.execute(f'SELECT id FROM users WHERE id = {member.id}').fetchone()[0]
        profile_cash = cursor.execute(f'SELECT cash FROM users WHERE id = {member.id}').fetchone()[0]
        profile_rep = cursor.execute(f'SELECT rep FROM users WHERE id = {member.id}').fetchone()[0]

        embed = discord.Embed(
            colour = discord.Colour(0x00FFFF),
            title = f'Профиль участника {member}',
            description = f'''
• **Никнейм:** <@{profile_id}>
• **ID:** {profile_id}

• **Баланс:** {profile_cash}
• **Репутация:** {profile_rep}
''')
        await ctx.send(embed = embed)

@bot.command(aliases = ['реп','Реп'])
@commands.cooldown(1, 604800, commands.BucketType.user)
async def __реп(ctx, arg, member: discord.Member = None):
    if member is None:
        await ctx.send('Укажите пользователя!')
    if member.id == ctx.author.id:
        embed = discord.Embed(description = '*Если вы не честны с самим собой, как вы можете быть честным с кем-то еще?*')
        embed.set_footer(text = '© Пол Уильямс')
        await ctx.send(embed = embed)
    else:
        if arg == '+':
            cursor.execute(f'UPDATE users SET rep = rep + {1} WHERE id = {member.id}')
            await ctx.send('Репутация начислена успешно!')
        elif arg == '-':
            cursor.execute(f'UPDATE users SET rep = rep - {1} WHERE id = {member.id}')
            await ctx.send('Репутация убавлена успешно!')
        else:
            await ctx.send('Укажите аргумент (`rep +` или `rep -`)')

@bot.command(aliases = ['работать', 'Работать'])
@commands.cooldown(1, 5400, commands.BucketType.user)
async def __работать(ctx):
    rancash = randint(1, 20)
    startwork_embed = discord.Embed(
        colour = discord.Colour(0x00FFFF),
        description = '**Вы начали работать. Конец смены настанет через полтора часа**')
    startwork_embed.set_author(name = ctx.author, icon_url = ctx.author.avatar_url)
    quantity_images = len(work_images)
    randimage = randint(1, quantity_images)
    startwork_embed.set_image(url=work_images[randimage])
    await ctx.send(embed = startwork_embed)
    await asyncio.sleep(5400)
    embed = discord.Embed(
        title = 'Конец рабочей смены',
        colour = discord.Colour(0x00FFFF),
        description = f'<@{ctx.author.id}>, спустя полтора часа вы отработали свои законные {rancash} монет. Они уже лежат у вас на балансе')
    embed.set_image(url = 'https://img1.goodfon.ru/original/2880x1800/4/34/background-cash-coins.jpg')
    embed.set_author(name = ctx.author, icon_url = ctx.author.avatar_url)
    await ctx.send(embed = embed)
    cursor.execute(f"UPDATE users SET cash = cash + {rancash} WHERE id = {ctx.author.id}")

@bot.command(aliases = ['помощь', 'Помощь'])
async def __помощь(ctx):
    await ctx.send(embed = discord.Embed(
        colour = discord.Colour(0x00FFFF),
        title = 'Список команд',
        description = '''

• `.помощь` - высвечивает эту команду

• `.баланс` (`.бал`) - показывает количество ваших монеток

• `.я` (`.профиль`) - показывает подробную информацию о вашем профиле - ID, никнейм, кол-во монеток и репутация. Можно использовать с упоминанием другого участника

• `.подарить <участник> <сумма>`, (`.отправить`) - передача монеток с вашего баланса любому другому участнику сервера

• `.магазин` - список товаров, которые можно приобрести за монетки

• `.топ` - список участников с самым высоким балансом

• `.реп +/- <member>` - добавляет или забирает у упомянутого участника один балл репутации. Команду можно использовать раз в 1 неделю на любого человека

• `.работать` - даёт возможность вам зарабатывать монетки самостоятельно

• `.казино` - информация о казино'''))

@bot.command(aliases = ['казино','Казино'])
async def __казино(ctx, amount: int = None):
        if amount is None:
            embed = discord.Embed(
                colour = discord.Colour(0x00FFFF),
                title = 'Казино',
                description = '''
Добро пожаловать в казино - место, где вы можете приумножить свой капитал, поставить на кон все деньги и либо заработать целое состояние, либо остаться ни с чем. Контролируйте свой азарт!

Чтобы поставить сумму - напишите команду `.казино 100`, где 100 - ваша ставка. При выигрыше поставленная сумма утраивается. Желаю вам удачи!''')
            embed.set_image(url = 'https://sun9-7.userapi.com/_5zRoSiIQttchdkkd3THvcReJz8TdF7pG2ctyw/iaWdrH1NaRs.jpg')
            embed.set_author(name = ctx.author, icon_url = ctx.author.avatar_url)
            await ctx.send(embed = embed)
        else:
            if cursor.execute(f'SELECT cash FROM users WHERE id = {ctx.author.id}').fetchone()[0] < 0:
                await ctx.send('Недостаточно денег')
            elif amount <= 0:
                await ctx.send('Укажите положительное число')
            elif amount > cursor.execute(f'SELECT cash FROM users WHERE id = {ctx.author.id}').fetchone()[0]:
                await ctx.send('Сумма ставки больше, чем ваш баланс')
            elif amount < 100:
                await ctx.send('Минимальная ставка - 100 монет')
            else:
                casino = randint(1, 100)
                await ctx.send('Крутим рулетку...')
                await asyncio.sleep(3)
                if casino <= 40:
                    cursor.execute(f'UPDATE users SET cash = cash + {amount*3} WHERE id = {ctx.author.id}')
                    await ctx.send(f'Поздравляю, вы победили! На ваш баланс было начислено **{amount*3}** монет')
                elif casino >= 41:
                    cursor.execute(f'UPDATE users SET cash = cash - {amount} WHERE id = {ctx.author.id}')
                    await ctx.send(f'В этот раз вам не повезло, вы проиграли поставленную сумму!')
                if cursor.execute(f'SELECT cash FROM users WHERE id = {ctx.author.id}').fetchone()[0] < 0:
                    cursor.execute(f'UPDATE users SET cash = cash = 0 WHERE id = {ctx.author.id}')
                connection.commit()
                
bot.run(token)
