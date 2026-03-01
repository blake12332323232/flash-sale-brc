import os, threading, time
from flask import Flask, request, render_template, redirect, url_for, flash
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(16)

API_KEY = os.getenv("API_KEY")
SECRET = os.getenv("SECRET")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

FLASH_SALES = {}  # {gamepass_id: original_price}

# --- Helper Functions ---
def update_discord_embed(title, description, color=0x00aaff):
    embed = {"title": title, "description": description, "color": color}
    requests.post(DISCORD_WEBHOOK, json={"embeds":[embed]})

def revert_price(gamepass_id, original_price, duration):
    time.sleep(duration)
    url = f"https://apis.roblox.com/game-passes/v1/game-passes/{gamepass_id}/details"
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    requests.patch(url, json={"price": original_price}, headers=headers)
    update_discord_embed("Flash Sale Ended", f"Gamepass `{gamepass_id}` reverted to `{original_price}` R$", 0x00ff00)
    FLASH_SALES.pop(gamepass_id, None)

def set_gamepass_price(gamepass_id, price, duration=None):
    url = f"https://apis.roblox.com/game-passes/v1/game-passes/{gamepass_id}/details"
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    requests.patch(url, json={"price": price}, headers=headers)
    update_discord_embed("Gamepass Price Updated", f"Gamepass `{gamepass_id}` set to `{price}` R$", 0x00aaff)
    if duration:
        FLASH_SALES[gamepass_id] = price
        threading.Thread(target=revert_price, args=(gamepass_id, price, duration)).start()

# --- Routes ---
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        secret = request.form.get("secret")
        gamepass_id = int(request.form.get("gamepass"))
        price = int(request.form.get("price"))
        duration = request.form.get("duration")
        duration = int(duration) if duration else None

        if secret != SECRET:
            flash("❌ Invalid secret key!", "danger")
            return redirect(url_for("index"))

        set_gamepass_price(gamepass_id, price, duration)
        flash(f"✅ Gamepass {gamepass_id} price updated!", "success")
        return redirect(url_for("index"))

    return render_template("index.html", flash_sales=FLASH_SALES)

# Optional webhook route for Roblox purchases
@app.route("/purchase", methods=["POST"])
def purchase():
    data = request.json
    if data.get("secret") != SECRET:
        return "Unauthorized", 401
    user = data.get("username")
    gamepass_id = data.get("gamepassId")
    update_discord_embed("Gamepass Purchased", f"{user} bought gamepass `{gamepass_id}`")
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
