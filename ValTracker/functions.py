import logging
import traceback
from pathlib import Path

import aiohttp
import httpx as http
import requests
from PyQt5.QtGui import QImage

intervals = (
    ("Weeks", 604800),
    ("Days", 86400),
    ("Hours", 3600),
    ("Minutes", 60),
    ("Seconds", 1),
)

seasons = {
    # "V25A4": "e10a4",
    "V25A3": "e10a3",
    "V25A2": "e10a2",
    "V25A1": "e10a1",
    "E9A3": "e9a3",
    "E9A2": "e9a2",
    "E9A1": "e9a1",
    "E8A3": "e8a3",
    "E8A2": "e8a2",
    "E8A1": "e8a1",
    "E7A3": "e7a3",
    "E7A2": "e7a2",
    "E7A1": "e7a1",
    "E6A3": "e6a3",
    "E6A2": "e6a2",
    "E6A1": "e6a1",
    "E5A3": "e5a3",
    "E5A2": "e5a2",
    "E5A1": "e5a1",
    "E4A3": "e4a3",
    "E4A2": "e4a2",
    "E4A1": "e4a1",
    "E3A3": "e3a3",
    "E3A2": "e3a2",
    "E3A1": "e3a1",
    "E2A3": "e2a3",
    "E2A2": "e2a2",
    "E2A1": "e2a1",
}  # Problem: Hardcoded seasons, need to update manually, finding a way to get the current season automatically would be better

regions = ["EU", "NA", "KR", "AP", "LATAM", "BR"]


def get_ranks() -> dict:
    """
    Returns a dictionary of ranks with their corresponding tier numbers by api.
    """
    try:
        response = requests.get("https://valorant-api.com/v1/competitivetiers")
        response.raise_for_status()
        data = response.json()
        ranklist = {
            tier["tier"]: tier["tierName"] for tier in data["data"][0]["tiers"]
        }
        return ranklist
    except requests.RequestException as e:
        logging.error(f"Error fetching ranks: {e}")
        return None


def populate_combo_box(combo_box, items):
    """
    Populate a QComboBox with a list of items.
    """
    combo_box.clear()
    combo_box.addItems(items)


def get_image(url: str) -> QImage:
    """
    Fetch an image from a URL and return it as a QImage.
    """
    with http.Client() as client:
        r = client.get(url)
    img = QImage()
    img.loadFromData(r.content)
    return img


async def get_image_async(url: str) -> QImage:
    """
    Asynchronously fetch an image from a URL and return it as a QImage.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            img_data = await response.read()
            return QImage.fromData(img_data)


def display_time(seconds: int, granularity: int = 2) -> str:
    """
    Convert a number of seconds into a human-readable string.
    """
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip("s")
            result.append(f"{value} {name}")
    return " ".join(result[:granularity])


def clear_layout(layout) -> None:
    """
    Recursively clear all widgets from a layout.
    """
    if layout is not None:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                clear_layout(child.layout())


def humanize_agent_name(agent_name: str) -> str:
    """
    Humanize agent names by removing special characters and converting to lowercase.
    """
    return (
        agent_name.replace("/", "")
        .replace("\\", "")
        .replace(" ", "")
        .replace("'", "")
        .lower()
    )


def download_agent_images() -> None:
    """
    Download all agent images from valorant-api.com and save them in the Images/Agents folder.
    """
    try:
        agents_data = requests.get("https://valorant-api.com/v1/agents").json()
        agents = agents_data["data"]
        agents_folder = Path(__file__).parent.joinpath("Images/Agents")
        agents_folder.mkdir(parents=True, exist_ok=True)

        for agent in agents:
            agent_name = humanize_agent_name(agent["displayName"])
            agent_image_url = agent["displayIcon"]
            agent_image_path = agents_folder.joinpath(f"{agent_name}.png")

            if not agent_image_path.exists():
                response = requests.get(agent_image_url)
                with open(agent_image_path, "wb") as file:
                    file.write(response.content)
                logging.info(f"Downloaded image for agent: {agent_name}")

    except Exception as error:
        logging.error(
            f"Error downloading agent images: {traceback.format_exc()}"
        )
