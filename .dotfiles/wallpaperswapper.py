from datetime import datetime
import os

now = datetime.now()

if now.hour > 20:
    bg = "night.jpg"
elif now.hour > 16:
    bg = "low.jpg"
elif now.hour > 10:
    bg = "day.jpg"
elif now.hour > 6:
    bg = "low.jpg"

wallpaper_dir = os.path.expanduser("/home/kenzie/.dotfiles/bg")
wallpaper_path = os.path.join(wallpaper_dir, bg)

command = f"feh --bg-fill '{wallpaper_path}'"
os.system(command)
