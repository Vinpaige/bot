import os
import discord
from discord.ext import commands
from mcstatus import MinecraftServer
import socket

# Lấy token từ biến môi trường
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

def check_port(ip, port, timeout=3):
    """Kiểm tra port có mở hay không"""
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except:
        return False

@bot.event
async def on_ready():
    print(f"Simo Info đã online: {bot.user}")

@bot.command()
async def infoserver(ctx, ip_port: str):
    """Check toàn bộ thông tin server Minecraft"""
    try:
        if ":" in ip_port:
            ip, port = ip_port.split(":")
            port = int(port)
        else:
            ip = ip_port
            port = 25565

        # Kiểm tra port
        if not check_port(ip, port):
            await ctx.send(f"❌ Server `{ip}:{port}` không thể kết nối hoặc port đóng.")
            return

        server = MinecraftServer(ip, port)
        status = server.status()

        # Lấy server brand/version
        try:
            query = server.query()
            brand = query.software or "Không xác định"
        except:
            brand = status.version.name  # fallback nếu query không bật

        # Lấy tên server từ MOTD
        motd = status.description
        server_name = motd.split("\n")[0] if "\n" in motd else motd

        # Tạo embed đẹp
        embed = discord.Embed(
            title=f"📡 Thông tin server Minecraft",
            description=f"**{server_name}**",
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url="https://i.imgur.com/2V8HjzZ.png")  # icon bot hoặc server (có thể đổi)
        embed.add_field(name="🌐 IP:Port", value=f"{ip}:{port}", inline=True)
        embed.add_field(name="👥 Người chơi", value=f"{status.players.online}/{status.players.max}", inline=True)
        embed.add_field(name="🛠 Phiên bản", value=brand, inline=True)
        embed.add_field(name="📜 MOTD", value=f"```{motd}```", inline=False)
        embed.add_field(name="📌 Ghi chú", value=brand, inline=False)
        embed.set_footer(text="Simo Info - Bot Minecraft Server Checker")

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"❌ Không thể kết nối đến server. Lỗi: {e}")

bot.run(TOKEN)
