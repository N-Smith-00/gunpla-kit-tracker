import discord
import sqlite3
from discord.ext import commands
from discord import app_commands
from config.config import BOT_TOKEN, VALID_SCALES
from typing import Optional
from contextlib import contextmanager

import database.kit_queries as kit_q
from database.db_connection import get_conn

from database.db_helpers import format_query_results

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

class Database:
    def __init__(self):
        self.connection = get_conn()
    
    @contextmanager
    def cursor(self):
        cursor = self.connection.cursor()
        try:
            yield cursor
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()
    
    def close(self):
        self.connection.close()
        
db = Database()

@bot.event
async def on_ready():
    print(f'logged in as {bot.user}')
    
    
@bot.command()
async def sync(ctx:commands.Context, guild_id:Optional[str]):
    try:
        if guild_id:
            guild = discord.Object(id=int(guild_id))
        else:
            guild = ctx.guild
        
        tree.copy_global_to(guild=guild)
        await tree.sync(guild=guild)

        await ctx.send(f"Slash commands have been synced for guild {guild.name}")
    except Exception as e:
        await ctx.send(f"Error syncing commands: {str(e)}")

@bot.command()
async def sql(ctx:commands.Context):
    if ctx.author.id == 276105538008514560:
        try:
            with db.cursor() as cursor:
                cursor.execute(ctx.message.content.removeprefix('!sql '))
        except Exception as e:
            await ctx.reply(e, ephemeral=True, delete_after=10)
    
@bot.command()
async def close(ctx:commands.Context):
    db.close()
    await bot.close()
    
@tree.command(name="add_kit", description="adds a new kit to the database")
@app_commands.describe(
    kit_name="The name of the kit",
    grade="Grade of the kit (optional, defaults to NOGRADE)",
    brand="Brand name (optional)",
    scale="Scale of the kit (optional)"
)
async def add_kit(interaction:discord.Interaction, kit_name:str, grade:Optional[str]="NOGRADE", brand:Optional[str]=None, scale:Optional[str]="nonscale"):
    if scale not in VALID_SCALES:
        await interaction.response.send_message("Scale is invalid")
        return
    try:
        with db.cursor() as cursor:
            cursor.execute(f"INSERT INTO kit (name, grade, scale, brand) VALUES (?,?,?,?)", (kit_name.title(), 
                                                                                             grade.upper() if grade is not None else "NO_GRADE", 
                                                                                             scale.lower() if scale is not None else "nonscale", 
                                                                                             brand.capitalize() if brand is not None else None))
    except sqlite3.IntegrityError as e:
        print(f"error {e}")
        if e.sqlite_errorcode == 2067:
            await interaction.response.send_message(f"Kit already added")
        else:
            await interaction.response.send_message(f"Database error occurred")
        return
    except Exception as e:
        print(f"error {e}")
        return
    await interaction.response.send_message(f"{grade} {kit_name} {scale} has been added, can now add store listings and accessories")

@tree.command(name="add_accessory", description="adds a new accessory to the database")
@app_commands.describe(
    accessory_name="The name of accessory",
    kit_id="The id of the kit it is for",
    brand="Brand name (optional)"
)
async def add_accessory(interaction:discord.Interaction, accessory_name:str, kit_id:int, brand:Optional[str]=None):
    try:
        with db.cursor() as cursor:
            cursor.execute("INSERT INTO accessory (kit_id, name, brand) VALUES (?, ?, ?)", (kit_id, 
                                                                                            accessory_name.title(), 
                                                                                            brand.capitalize() if brand is not None else None))
    except sqlite3.IntegrityError as e:
        print(f'error: {e}')
        if e.sqlite_errorcode == 2067:
            await interaction.response.send_message(f"Kit already added")
        else:
            await interaction.response.send_message(f"Database error occurred")
        return
    except Exception as e:
        print(f"error {e}")
        return
    with db.cursor() as cursor:
        cursor.execute('SELECT name, grade FROM kit WHERE kit_id = ?', (kit_id,))
        (kit_name, grade) = cursor.fetchone()
    await interaction.response.send_message(f"{accessory_name} for {grade} {kit_name} has been added, can now add store listings")

class Remove(discord.ui.View):
    def __init__(self, id:int, table:str):
        super().__init__()
        self.table = table
        self.id = id
    
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction:discord.Interaction, button:discord.ui.Button):
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT grade, name, scale FROM ? WHERE kit_id = ?", (self.table, self.id))
                (grade, name, scale) = cursor.fetchone()
                cursor.execute("DELETE FROM ? WHERE kit_id = ?", (self.table, self.id))
        except Exception as e:
            print(e)
        await interaction.response.send_message(f"{grade} {name} {scale} has been removed from the database")
        self.stop()
        
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction:discord.Interaction, button:discord.ui.Button):
        print('cancel')
        await interaction.response.send_message("action canceled")
        self.stop()

@tree.command(name="remove_kit", description="remove a kit from the database")
async def remove_kit(interaction:discord.Interaction, kit_id:int):  
    with db.cursor() as cursor:
        cursor.execute("SELECT grade, name, scale FROM kit WHERE kit_id = ?", (kit_id,))
        (grade, name, scale) = cursor.fetchone()
    await interaction.response.send_message(f"are you sure you want to remove {grade} {name} {scale} from the database?", ephemeral=True, view=Remove(kit_id, 'kit'))
    
@tree.command(name="remove_accessory", description="remove an accessory from the database")
async def remove_accessory(interaction:discord.Interaction, accessory_id:int):
    with db.cursor() as cursor:
        cursor.execute("SELECT name, brand FROM accessory WHERE accessory_id = ?", (accessory_id,))
        (name, brand) = cursor.fetchone()
    await interaction.response.send_message(f"are you sure you want to remove {name} from {brand} from the database", ephemeral=True, view=Remove(accessory_id, 'accessory'))

@tree.command(name="mark_as_bought", description="mark an item as bought")
async def mark_bought(interaction:discord.Interaction, type:str, item_id:int):
    if type.lower() == "kit":
        try:
            with db.cursor() as cursor:
                cursor.execute("UPDATE kit SET bought = ? WHERE kit_id = ?", (1, item_id))
                cursor.execute("SELECT grade, name FROM kit WHERE kit_id = ?", (item_id,))
                kit = cursor.fetchone()
            await interaction.response.send_message(f"{' '.join(kit)} has been marked as bought")
        except Exception as e:
            print(f"error: {e}")
    elif type.lower() == "accessory":
        try:
            with db.cursor() as cursor:
                cursor.execute("UPDATE accessory SET bought = ? WHERE accessory_id = ?", (1, item_id))
                cursor.execute("SELECT name, brand, kit_id FROM accessory WHERE accessory_id = ?", (item_id,))
                (name, brand, kit_id) = cursor.fetchone()
                cursor.execute("SELECT grade, name FROM kit WHERE kit_id = ?", (kit_id,))
                (grade, kit_name) = cursor.fetchone()
            await interaction.response.send_message(f'{name} from {brand} for {grade} {kit_name} has been marked as bought')
        except Exception as e:
            print(f'error: {e}')
    else:
        await interaction.response.send_message("invalid item type, please check it and try again")

@tree.command(name="mark_unpurchased", description="mark an item as unpurchased")
async def mark_unbought(interaction:discord.Interaction, type:str, item_id:int):
    if type.lower() == "kit":
        try:
            with db.cursor() as cursor:
                cursor.execute("UPDATE kit SET bought = ? WHERE kit_id = ?", (0, item_id))
                cursor.execute("SELECT grade, name FROM kit WHERE kit_id = ?", (item_id,))
                kit = cursor.fetchone()
            await interaction.response.send_message(f"{' '.join(kit)} has been marked as unpurchased")
        except Exception as e:
            print(f"error: {e}")
        pass
    elif type.lower() == "accessory":
        try:
            with db.cursor() as cursor:
                cursor.execute("UPDATE accessory SET bought = ? WHERE accessory_id = ?", (0, item_id))
                cursor.execute("SELECT name, brand, kit_id FROM accessory WHERE accessory_id = ?", (item_id,))
                (name, brand, kit_id) = cursor.fetchone()
                cursor.execute("SELECT grade, name FROM kit WHERE kit_id = ?", (kit_id,))
                (grade, kit_name) = cursor.fetchone()
            await interaction.response.send_message(f'{name} from {brand} for {grade} {kit_name} has been marked as unpurchased')
        except Exception as e:
            print(f'error: {e}')
    else:
        await interaction.response.send_message("invalid item type, please check it and try again")

@tree.command(name="search_kits", description="searches kits based on given criteria")
async def search_kits(interaction:discord.Interaction, name:Optional[str], grade:Optional[str], scale:Optional[str], brand:Optional[str]):
    query = kit_q.search_kit(name, grade, scale, brand)
    try:
        with db.cursor() as cursor:
            cursor.execute(query[0], query[1])
            q_res = cursor.fetchall()
            await interaction.response.send_message(format_query_results(cursor, q_res))
    except Exception as e:
        print(f'error: {e}')

if __name__ == "__main__":
    bot.run(BOT_TOKEN)