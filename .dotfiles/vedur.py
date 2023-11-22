import re
import requests
import os.path

location_regex = r"^[A-Za-z]+"
temp_regex     = r"([+-]{0,1}\d+(?:\([+-]{0,1}\d+\)){0,1} °C)"

# Get wttr.in
wttr = requests.get("http://wttr.in/Reykjavik?0?q?T").content.decode("utf-8")

# Find strings
location = re.findall(location_regex, wttr)[0]
temp = re.findall(temp_regex, wttr)[0].replace(" ", "")

weather_info = f"{temp} ({location})"
file_locaton = os.path.expanduser("~/.dotfiles/vedur-nuna")

with open(file_locaton, "w+") as f:
    f.write(weather_info)
