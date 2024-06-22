import aiohttp
import httpx as http
from PyQt5.QtGui import QImage

intervals = (
    ("Weeks", 604800),  # 60 * 60 * 24 * 7
    ("Days", 86400),  # 60 * 60 * 24
    ("Hours", 3600),  # 60 * 60
    ("Minutes", 60),
    ("Seconds", 1),
)

seasons = [
    "E8A3",
    "E8A2",
    "E8A1",
    "E7A3",
    "E7A2",
    "E7A1",
    "E6A3",
    "E6A2",
    "E6A1",
    "E5A3",
    "E5A2",
    "E5A1",
    "E4A3",
    "E4A2",
    "E4A1",
    "E3A3",
    "E3A2",
    "E3A1",
    "E2A3",
    "E2A2",
    "E2A1",
]

ranklist = {
    0: "Unranked",
    1: "Unused 1",
    2: "Unused 2",
    3: "Iron 1",
    4: "Iron 2",
    5: "Iron 3",
    6: "Bronze 1",
    7: "Bronze 2",
    8: "Bronze 3",
    9: "Silver 1",
    10: "Silver 2",
    11: "Silver 3",
    12: "Gold 1",
    13: "Gold 2",
    14: "Gold 3",
    15: "Platinum 1",
    16: "Platinum 2",
    17: "Platinum 3",
    18: "Diamond 1",
    19: "Diamond 2",
    20: "Diamond 3",
    21: "Ascendant 1",
    22: "Ascendant 2",
    23: "Ascendant 3",
    24: "Immortal 1",
    25: "Immortal 2",
    26: "Immortal 3",
    27: "Radiant",
}


def get_image(url: str):
    with http.Client() as client:
        r = client.get(url)
    img = QImage()
    img.loadFromData(r.content)
    return img


async def get_image_async(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            img_data = await response.read()
            return QImage.fromData(img_data)


def display_time(seconds: int, granularity=2):
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip("s")
            result.append("{} {}".format(value, name))
    return " ".join(result[:granularity])


def clear_layout(layout):
    if layout is not None:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                clear_layout(child.layout())
