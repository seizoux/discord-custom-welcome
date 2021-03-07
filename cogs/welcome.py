
import discord
from discord.ext import commands
import datetime

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Welcome Loaded")



    @commands.Cog.listener()
    async def on_member_join(self, member):
        guilid = str(member.guild.id)
        guil = member.guild
        data = await self.bot.pg_con.fetch("SELECT * FROM welcome WHERE guild_id = $1", guilid)
        if not data:
            await guil.system_channel.send(f"**Welcome {member.mention} in `{guil.name}`**!")
            if guil.system.channel == None:
                return
        else:
            msg = data[0]["msg"]
            rolen = data[0]["role_name"]
            role = data[0]["role"]
            chan = data[0]["channel"]
            embed = data[0]["embed"]
            welcome = data[0]["welc"]

            channel = await self.bot.fetch_channel(chan)

            if not msg:
                return

            namespace = {"{name}": member.name, "{member}": f"{member.name}#{member.discriminator}",
            "{mention}": member.mention,
            "{count}": member.guild.member_count,
            "{created}": member.created_at.strftime("%m/%d/%Y"),
            "{age}": f"{(datetime.datetime.utcnow() - member.created_at).days} days",
            "{guild}": member.guild.name}

            def replace_all(m: str) -> str:
                for k in namespace.keys():
                    m = m.replace(k, str(namespace[k]))
                return m

            msg = replace_all(msg)

            if welcome == "off":
                return
            elif welcome == "on":
                if embed == "on":
                    em = discord.Embed(description = f"{msg}", color = 0xffcff1)
                    em.set_author(name=f"{member.name}", icon_url=f"{member.avatar_url}")
                    em.set_thumbnail(url=guil.icon_url)
                    if guil.banner_url == True:
                        em.set_image(url=guil.banner_url)
                    else:
                        pass
                    em.set_footer(text="Joined at")
                    em.timestamp = datetime.datetime.utcnow()
                    if not channel:
                        try:
                            await guil.system_channel.send(embed=em)
                            if member.guild.system_channel == None:
                                return
                        except Exception:
                            pass
                    elif channel:
                        await channel.send(embed=em)
                elif embed == "off":
                    if not channel:
                        await guil.system_channel.send(msg)
                        if member.guild.system_channel == None:
                            return
                    elif channel:
                        await channel.send(msg)
                
                if role == "off":
                    pass
                if role == "on":
                    if not rolen:
                        pass
                    else:
                        rol = discord.utils.get(member.guild.roles, name = rolen)
                        await member.add_roles(rol)


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setwelc(self, ctx):
        guild = str(ctx.guild.id)
        data = await self.bot.pg_con.fetch("SELECT * FROM welcome WHERE guild_id = $1", guild)

        if not data:
            await self.bot.pg_con.fetch("INSERT INTO welcome (guild_id) VALUES ($1)", guild)


        em = discord.Embed(title="Custom welcome config!", description="Hi! Here you can set your **custom welcome message** for this guild! First of all, only members with **administrator** permission can set it! If you **don't** set it, when a member join here, i send a message in the **guild system channel** (__where you get advice for server boosts for example__), and if you don't have a system channel, i don't send **any** welcome message.\nSo, if you want to set your custom welcome, click on the **reaction below**, and start the configuration! ❤", color = 0xffcff1)
        em.set_thumbnail(url=self.bot.user.avatar_url)
        em.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        em.timestamp = datetime.datetime.utcnow()
        msg = await ctx.send(embed=em)
        await msg.add_reaction("<:cm:804092594329223199>")

        def check(payload):
            return payload.message_id == msg.id and payload.emoji.name == "cm" and payload.user_id == ctx.author.id
            
        payload = await self.bot.wait_for("raw_reaction_add", check=check)
        em = discord.Embed(title="1) The message", description="What message did i need to send when someone join here? Send it (you can also use discord markdown)", color = 0xffcff1)
        await msg.edit(embed=em)

        msg1 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel == ctx.channel)

        if len(msg1.content) > 2000:
            ln = len(msg1.content)
            return await ctx.send(f"Seems you've sent a message which the lenght is {ln}. The discord limit is `2000`, so resend `ami setwelc` and try to make it shorter.")
        else:
            mex1 = str(msg1.content)
            await self.bot.pg_con.execute("UPDATE welcome SET msg = $1 WHERE guild_id = $2", mex1, guild)
            em = discord.Embed(title="2) The channel", description="Where i need to send this message? Send the **`Channel ID`** (right click on the channel and `Copy ID`) (see the gif to know how to enable developer mode)", color = 0xffcff1)
            em.set_image(url="https://i.imgur.com/nhE8sQa.gif")
            await msg.edit(embed=em)

        msg2 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel == ctx.channel)

        if msg2.content.isdigit():
            mex2 = str(msg2.content)
            await self.bot.pg_con.execute("UPDATE welcome SET channel = $1 WHERE guild_id = $2", mex2, guild)
            em = discord.Embed(title="3) The role", description="What role i need to give to new members? Send the role name (with capital and lowercase letters, and be sure the role exist, or i don't give any role.)", color = 0xffcff1)
            await msg.edit(embed=em)
        else:
            return await ctx.send("This isn't a channel ID, send `ami setwelc` again and send a valid channel ID")

        msg3 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel == ctx.channel)

        if msg3:
            mex3 = str(msg3.content)
            await self.bot.pg_con.execute("UPDATE welcome SET role_name = $1 WHERE guild_id = $2", mex3, guild)
            em = discord.Embed(title="4) The embed", description="You want the welcome message in an embed? Send `yes` to have it, or `no` to have a normal messagee.", color = 0xffcff1)
            await msg.edit(embed=em)

        msg4 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel == ctx.channel)

        if msg4.content in ("yes", "Yes"):
            mex4 = "on"
            await self.bot.pg_con.execute("UPDATE welcome SET embed = $1 WHERE guild_id = $2", mex4, guild)
            em = discord.Embed(title="Configuration done! Check next", description="Alright! You've finished the custom welcome config!\nTo enable or disable something, use `ami welcset` and see all welcome settings!", color=0xffcff1)
            await msg.edit(embed=em)
            return

        if msg4.content in ("no", "No"):
            mex4 = "off"
            await self.bot.pg_con.execute("UPDATE welcome SET embed = $1 WHERE guild_id = $2", mex4, guild)
            em = discord.Embed(title="Configuration done! Check next", description="Alright! You've finished the custom welcome config!\nTo enable or disable something, use `ami welcset` and see all welcome settings!", color=0xffcff1)
            await msg.edit(embed=em)
            return

        else:
            await ctx.send("I said `yes` or `no`.. aight, i'll set it on `no`.")
            await self.bot.pg_con.execute("UPDATE welcome SET embed = $1 WHERE guild_id = $2", "off", guild)
            em = discord.Embed(title="Configuration done! Check next", description="Alright! You've finished the custom welcome config!\nTo enable or disable something, use `ami welcset` and see all welcome settings!", color=0xffcff1)
            await msg.edit(embed=em)

    @commands.command()
    async def welcset(self, ctx):
        guild = str(ctx.guild.id)
        data = await self.bot.pg_con.fetch("SELECT * FROM welcome WHERE guild_id = $1", guild)

        if not data:
            await self.bot.pg_con.fetch("INSERT INTO welcome (guild_id) VALUES ($1)", guild)

        msg = data[0]["msg"]
        rolen = data[0]["role_name"]
        role = data[0]["role"]
        channel = data[0]["channel"]
        embed = data[0]["embed"]
        welcome = data[0]["welc"]

        mex = "<:check:314349398811475968>"
        rl = "<:check:314349398811475968>"
        rle = "<:check:314349398811475968>"
        ch = "<:check:314349398811475968>"
        emb = "<:check:314349398811475968>"
        wel = "<:check:314349398811475968>"


        if not msg:
            mex = "<:empty:314349398723264512>"


        if not rolen:
            rl = "<:empty:314349398723264512>"


        if role == "off":
            rle = "<:xmark:314349398824058880>"
        elif role == "on":
            rle = "<:check:314349398811475968>"
        elif role == None:
            rle = "<:empty:314349398723264512>"


        if not channel:
            rl = "<:empty:314349398723264512>"


        if embed == "off":
            emb = "<:xmark:314349398824058880>"
        elif embed == "on":
            emb = "<:check:314349398811475968>"
        elif embed == None:
            emb = "<:empty:314349398723264512>"

        if welcome == "off":
            wel = "<:xmark:314349398824058880>"
        elif welcome == "on":
            wel = "<:check:314349398811475968>"
        elif welcome == None:
            wel = "<:empty:314349398723264512>"

        guil = ctx.guild
        em = discord.Embed(title="Welcome settings", description="Here you can see all welcome settings for this guild!\n<:check:314349398811475968> = On\n<:xmark:314349398824058880> = Off\n<:empty:314349398723264512> = Empty", color=0xffcff1)
        em.add_field(name=f"{guil.name} settings", value = f"`Message` = {mex}\n`Role Name` = {rl}\n`Role Assign` = {rle}\n`Channel` = {ch}\n`Embed` = {emb}\n`Welcome` = {wel}")
        em.set_footer(text='Check welcome category in "ami help" for more info!')
        await ctx.send(embed=em)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setmex(self, ctx, *, args):
        guild = str(ctx.guild.id)
        data = await self.bot.pg_con.fetch("SELECT * FROM welcome WHERE guild_id = $1", guild)

        if not data:
            return await ctx.send("This guild isn't in the database. Send `ami setwelc` to config the custom help")
        
        mex = str(args)
        await ctx.send("<a:6093_Animated_Checkmark:811660600568315925> **`WELCOME MESSAGE UPDATED!`**")
        await self.bot.pg_con.execute("UPDATE welcome SET msg = $1 WHERE guild_id = $2", mex, guild)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setrolename(self, ctx, *, args):
        guild = str(ctx.guild.id)
        data = await self.bot.pg_con.fetch("SELECT * FROM welcome WHERE guild_id = $1", guild)

        if not data:
            return await ctx.send("This guild isn't in the database. Send `ami setwelc` to config the custom help")
        
        mex = str(args)
        await ctx.send("<a:6093_Animated_Checkmark:811660600568315925> **`WELCOME ROLE NAME UPDATED!`**")
        await self.bot.pg_con.execute("UPDATE welcome SET role_name = $1 WHERE guild_id = $2", mex, guild)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setassign(self, ctx, *, args):
        guild = str(ctx.guild.id)
        data = await self.bot.pg_con.fetch("SELECT * FROM welcome WHERE guild_id = $1", guild)

        if not data:
            return await ctx.send("This guild isn't in the database. Send `ami setwelc` to config the custom help")
        
        if args == "off":
            mex = str(args)
            await ctx.send("<a:6093_Animated_Checkmark:811660600568315925> **`WELCOME ROLE ASSIGN DISABLED!`**")
            await self.bot.pg_con.execute("UPDATE welcome SET role = $1 WHERE guild_id = $2", mex, guild)
        elif args == "on":
            mex = str(args)
            await ctx.send("<a:6093_Animated_Checkmark:811660600568315925> **`WELCOME ROLE ASSIGN ENABLED!`**")
            await self.bot.pg_con.execute("UPDATE welcome SET role = $1 WHERE guild_id = $2", mex, guild)
        else:
            return await ctx.send("Only `on/off` accepted for this command.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setchannel(self, ctx, *, args):
        guild = str(ctx.guild.id)
        data = await self.bot.pg_con.fetch("SELECT * FROM welcome WHERE guild_id = $1", guild)

        if not data:
            return await ctx.send("This guild isn't in the database. Send `ami setwelc` to config the custom help")
        
        if args.isdigit():
            mex = str(args)
            await ctx.send("<a:6093_Animated_Checkmark:811660600568315925> **`WELCOME MESSAGE CHANNEL UPDATED!`**")
            await self.bot.pg_con.execute("UPDATE welcome SET channel = $1 WHERE guild_id = $2", mex, guild)
        else:
            return await ctx.send("This isn't a channel ID, be sure to send a valid channel ID!")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def emb(self, ctx, *, args):
        guild = str(ctx.guild.id)
        data = await self.bot.pg_con.fetch("SELECT * FROM welcome WHERE guild_id = $1", guild)

        if not data:
            return await ctx.send("This guild isn't in the database. Send `ami setwelc` to config the custom help")
        
        if args == "off":
            mex = str(args)
            await ctx.send("<a:6093_Animated_Checkmark:811660600568315925> **`WELCOME MESSAGE EMBED DISABLED!`**")
            await self.bot.pg_con.execute("UPDATE welcome SET embed = $1 WHERE guild_id = $2", mex, guild)
        elif args == "on":
            mex = str(args)
            await ctx.send("<a:6093_Animated_Checkmark:811660600568315925> **`WELCOME MESSAGE EMBED ENABLED!`**")
            await self.bot.pg_con.execute("UPDATE welcome SET embed = $1 WHERE guild_id = $2", mex, guild)
        else:
            return await ctx.send("Only `on/off` accepted for this command.")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def wel(self, ctx, *, args):
        guild = str(ctx.guild.id)
        data = await self.bot.pg_con.fetch("SELECT * FROM welcome WHERE guild_id = $1", guild)

        if not data:
            return await ctx.send("This guild isn't in the database. Send `ami setwelc` to config the custom help")
        
        if args == "off":
            mex = str(args)
            await ctx.send("<a:6093_Animated_Checkmark:811660600568315925> **`WELCOME DISABLED!`**")
            await self.bot.pg_con.execute("UPDATE welcome SET welc = $1 WHERE guild_id = $2", mex, guild)
        elif args == "on":
            mex = str(args)
            await ctx.send("<a:6093_Animated_Checkmark:811660600568315925> **`WELCOME ENABLED!`**")
            await self.bot.pg_con.execute("UPDATE welcome SET welc = $1 WHERE guild_id = $2", mex, guild)
        else:
            return await ctx.send("Only `on/off` accepted for this command.")


        

    @commands.Cog.listener()
    async def on_guild_join(self,guild):
        try:
            await guild.system_channel.send("<:thanks:739614671774154843> **Hello guys!**\n```py\nPrefix = ami\nSee all my commands = ami help\nVersion = 1.1.2\nCommands category = Music, Economy, Modration, Fun, Utility, Image(s)\nDeveloper = Daishiky#0828\nWebsite = https://ami.6te.net/#\n```")
        except Exception:
            pass

        channel = self.bot.get_channel(817439941902467103)
        em = discord.Embed(title="Added in a new guild!", description = f"**Guild name** : `{guild.name}`\n\n**Guild members** : `{guild.member_count}`\n\n**Owner** : `{guild.owner}` - (`{guild.owner_id}`)\n\n**Guild region** : `{guild.region}`\n\n**Guild created at** : `{guild.created_at}`", color = 0xffcff1)
        if guild.icon_url:
            em.set_thumbnail(url=guild.icon_url)
        else:
            pass
        if guild.banner_url:
            em.set_image(url=guild.banner_url)
        else:
            pass
        await channel.send(embed=em)

    @commands.Cog.listener()
    async def on_guild_remove(self,guild):
        channel = self.bot.get_channel(817439941902467103)
        em = discord.Embed(title=f"Got removed from `{guild.name}`..", color = 0xffcff1)
        if guild.icon_url:
            em.set_thumbnail(url=guild.icon_url)
        else:
            pass
        if guild.banner_url:
            em.set_image(url=guild.banner_url)
        else:
            pass
        await channel.send(embed=em)


def setup(bot):
    bot.add_cog(Welcome(bot))
