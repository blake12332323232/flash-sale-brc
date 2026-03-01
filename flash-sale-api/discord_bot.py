import discord
import requests

BOT_TOKEN = "MTQ3NzQ3NDc3Mzk1NjAzNDcxMQ.GzGjnD.p9ZQYdztHvjjD5F3B0b-LfP972yRk4QL6SW91k"
API_SERVER = "https://flash-sale-brc.onrender.com/update-price"
SECRET = "BlueRidgeSecureKey"
DISCORD_ADMIN_ROLE = "Admin"

bot = discord.Bot(intents=discord.Intents.default())

tier_mapping = {
    "Bronze": 123456789,
    "Silver": 987654321,
    "Gold": 555555555,
    "Diamond": 111222333
}

@bot.tree.command(name="setprice", description="Set tier gamepass price (optional flash sale)")
@discord.option("tier", description="Tier name (Bronze/Silver/Gold/Diamond)", type=str, required=True)
@discord.option("price", description="Price in Robux", type=int, required=True)
@discord.option("duration", description="Flash sale in seconds (optional)", type=int, required=False)
async def setprice(interaction: discord.Interaction, tier: str, price: int, duration: int = None):
    if not any(role.name == DISCORD_ADMIN_ROLE for role in interaction.user.roles):
        await interaction.response.send_message("❌ You do not have permission.", ephemeral=True)
        return
    if tier not in tier_mapping:
        await interaction.response.send_message("❌ Invalid tier!", ephemeral=True)
        return

    gamepass_id = tier_mapping[tier]
    payload = {"secret": SECRET, "gamepassId": gamepass_id, "price": price}
    if duration:
        payload["duration"] = duration

    try:
        r = requests.post(API_SERVER, json=payload)
        if r.status_code == 200:
            msg = f"✅ Tier `{tier}` price set to {price} R$"
            if duration:
                msg += f" for `{duration}` seconds (flash sale)"
            await interaction.response.send_message(msg, ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Failed: {r.text}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

bot.run(BOT_TOKEN)
