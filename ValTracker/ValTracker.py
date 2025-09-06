# -----------------------------------------------------------
# ValTracker by NavisGames
# -----------------------------------------------------------
# This application provides player statistics, match history,
# and leaderboard information for Valorant using the valo_api.
# Selling this application is not allowed.
# Read the LICENSE file for more information.
# If you want to fork this program, share what you changed ^^
# -----------------------------------------------------------


import asyncio
import concurrent.futures
import logging
import os
import sys
import time
import traceback
from pathlib import Path

import valo_api
from dotenv import load_dotenv

load_dotenv()

valo_api.set_api_key(os.getenv("VALO_API_KEY"))  # Safety

from functions import (
    clear_layout,
    display_time,
    download_agent_images,
    fetch_url,
    get_image,
    get_image_async,
    get_ranks,
    populate_combo_box,
    regions,
    seasons,
)
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFontDatabase, QImage, QPalette, QPixmap
from PyQt5.QtWidgets import QApplication

logging.basicConfig(level=logging.INFO)


class Ui_ValorantTrackerByNavisGames(object):
    async def setupUi(
        self,
        valtracker: QtWidgets.QMainWindow,
    ) -> None:
        """
        Set up the UI for the Valorant Tracker application.
        """
        try:
            # ---------------------------------------------------------
            # MainWindow Setup
            # ---------------------------------------------------------
            self.dark_mode = False
            valtracker.setObjectName("valtracker")
            valtracker.setEnabled(True)
            valtracker.resize(1049, 890)
            valtracker.setMaximumSize(QtCore.QSize(16777215, 16777215))

            # ---------------------------------------------------------
            # Global Font Setup
            # ---------------------------------------------------------
            QFontDatabase.addApplicationFont("Images\\Tungsten-Bold.ttf")
            font = QtGui.QFont()
            font.setFamily("Tungsten Bold")
            font.setPointSize(20)
            font.setWeight(50)
            font.setKerning(True)

            # Window Settings
            valtracker.setFont(font)
            valtracker.setMouseTracking(False)
            valtracker.setWindowTitle("ValTracker - NavisGames")

            # Window Icon
            icon = QtGui.QIcon()
            iconImage = Path(__file__).parent.joinpath("Images\\icon.png")
            icon.addPixmap(
                QtGui.QPixmap(str(iconImage)), QtGui.QIcon.Normal, QtGui.QIcon.Off
            )
            valtracker.setWindowIcon(icon)
            valtracker.setDockOptions(
                QtWidgets.QMainWindow.AllowTabbedDocks
                | QtWidgets.QMainWindow.AnimatedDocks
            )

            # ---------------------------------------------------------
            # Central Widget & Main Layout
            # ---------------------------------------------------------
            self.centralwidget = QtWidgets.QWidget(valtracker)
            self.centralwidget.setObjectName("centralwidget")

            self.horizontalLayout_main = QtWidgets.QHBoxLayout(self.centralwidget)
            self.horizontalLayout_main.setContentsMargins(10, 10, 10, 10)
            self.horizontalLayout_main.setSpacing(10)
            self.horizontalLayout_main.setObjectName("horizontalLayout_main")

            # ---------------------------------------------------------
            # Left Tabs (Home, Leaderboard, Match, ...)
            # ---------------------------------------------------------
            self.tabs_left = QtWidgets.QTabWidget(self.centralwidget)
            self.tabs_left.setEnabled(True)
            self.tabs_left.setFocusPolicy(QtCore.Qt.NoFocus)
            self.tabs_left.setLayoutDirection(QtCore.Qt.LeftToRight)
            self.tabs_left.setTabPosition(QtWidgets.QTabWidget.North)
            self.tabs_left.setTabShape(QtWidgets.QTabWidget.Rounded)
            self.tabs_left.setUsesScrollButtons(False)
            self.tabs_left.setTabsClosable(False)
            self.tabs_left.setMovable(False)
            self.tabs_left.setObjectName("TabsLeft")

            # ---------------------------------------------------------
            # HOME TAB
            # ---------------------------------------------------------
            self.home = QtWidgets.QWidget()
            self.home.setObjectName("Home")
            self.verticalLayout = QtWidgets.QVBoxLayout(self.home)
            self.verticalLayout.setObjectName("verticalLayout")

            # ---------------------------------------------------------
            # Player Input Section
            # ---------------------------------------------------------
            self.player_input = QtWidgets.QFrame(self.home)
            self.player_input.setObjectName("player_input")
            self.horizontalLayout = QtWidgets.QHBoxLayout(self.player_input)
            self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
            self.horizontalLayout.setSpacing(5)
            self.horizontalLayout.setObjectName("horizontalLayout")

            # Light / Dark Mode Switcher
            self.mode_switcher = QtWidgets.QPushButton(self.player_input)
            self.mode_switcher.setToolTip("Switch between light and dark mode")
            icon1 = QtGui.QIcon()
            LightMode = Path(__file__).parent.joinpath("Images\\LightMode.webp")
            icon1.addPixmap(
                QtGui.QPixmap(str(LightMode)), QtGui.QIcon.Normal, QtGui.QIcon.Off
            )
            self.mode_switcher.setIcon(icon1)
            self.mode_switcher.setIconSize(QtCore.QSize(32, 32))
            self.mode_switcher.setObjectName("mode_switcher")
            self.horizontalLayout.addWidget(self.mode_switcher)

            # Player Name Input
            self.player_name = QtWidgets.QLineEdit(self.player_input)
            self.player_name.setToolTip("Enter your player name (max 16 characters)")
            self.player_name.setMaxLength(16)
            self.player_name.setAlignment(QtCore.Qt.AlignCenter)
            self.player_name.setPlaceholderText("PLAYER NAME (16 characters)")
            self.player_name.setObjectName("player_name")
            self.horizontalLayout.addWidget(self.player_name)

            # Player Tag Input
            self.player_tag = QtWidgets.QLineEdit(self.player_input)
            self.player_tag.setToolTip("Enter your player tag (max 5 characters)")
            self.player_tag.setMaxLength(5)
            self.player_tag.setAlignment(QtCore.Qt.AlignCenter)
            self.player_tag.setPlaceholderText("PLAYER TAG (5 characters)")
            self.player_tag.setObjectName("player_tag")
            self.horizontalLayout.addWidget(self.player_tag)

            # Player Region Dropdown
            self.player_region = QtWidgets.QComboBox(self.player_input)
            self.player_region.setToolTip("Select your region")
            self.player_region.setCurrentText("EU")
            self.player_region.setMaxVisibleItems(6)
            self.player_region.setDuplicatesEnabled(False)
            self.player_region.setObjectName("player_region")
            self.player_region.addItems(["EU", "NA", "KR", "AP", "LATAM", "BR"])
            self.player_region.setEditable(True)
            self.PlayerRegionEdit = self.player_region.lineEdit()
            self.PlayerRegionEdit.setAlignment(Qt.AlignCenter)
            self.PlayerRegionEdit.setReadOnly(True)
            self.horizontalLayout.addWidget(self.player_region)

            # Player Gamemode Dropdown
            self.player_gamemode = QtWidgets.QComboBox(self.player_input)
            self.player_gamemode.setToolTip("Select the game mode")
            self.player_gamemode.setCurrentText("ALL")
            self.player_gamemode.setMaxVisibleItems(6)
            self.player_gamemode.setDuplicatesEnabled(False)
            self.player_gamemode.setObjectName("player_gamemode")
            self.player_gamemode.addItems(
                [
                    "ALL",
                    "COMPETITIVE",
                    "UNRATED",
                    "SPIKERUSH",
                    "SWIFTPLAY",
                    "DEATHMATCH",
                ]
            )
            self.player_gamemode.setEditable(True)
            self.player_gamemode_edit = self.player_gamemode.lineEdit()
            self.player_gamemode_edit.setAlignment(Qt.AlignCenter)
            self.player_gamemode_edit.setReadOnly(True)
            self.horizontalLayout.addWidget(self.player_gamemode)

            # Apply & Reset Buttons
            self.dialog_button = QtWidgets.QDialogButtonBox(self.player_input)
            self.dialog_button.setOrientation(QtCore.Qt.Horizontal)
            self.get_button = QtWidgets.QPushButton("EXECUTE")
            self.get_button.setToolTip("Fetch player information")
            self.reset_button = QtWidgets.QPushButton("RESET")
            self.reset_button.setToolTip("Reset all inputs")
            self.dialog_button.addButton(
                self.get_button, QtWidgets.QDialogButtonBox.ActionRole
            )
            self.dialog_button.addButton(
                self.reset_button, QtWidgets.QDialogButtonBox.ActionRole
            )
            self.horizontalLayout.addWidget(self.dialog_button)

            # Stretch Settings for Inputs
            self.horizontalLayout.setStretch(1, 4)
            self.horizontalLayout.setStretch(2, 3)
            self.verticalLayout.addWidget(self.player_input)

            # ---------------------------------------------------------
            # Player Information Section
            # ---------------------------------------------------------
            self.player_information = QtWidgets.QFrame(self.home)
            self.player_information.setObjectName("player_information")
            self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.player_information)
            self.horizontalLayout_2.setContentsMargins(5, 5, 5, 5)
            self.horizontalLayout_2.setSpacing(15)

            # Player Banner
            example_banner = Path(__file__).parent.joinpath(
                "Images\\Example\\ExampleWideBanner.png"
            )
            self.player_banner = QtWidgets.QLabel(self.player_information)
            self.player_banner.setPixmap(QtGui.QPixmap(str(example_banner)))
            self.player_banner.setScaledContents(True)
            self.player_banner.setAlignment(QtCore.Qt.AlignCenter)
            self.player_banner.setFrameShape(QtWidgets.QFrame.Box)
            self.player_banner.setLineWidth(0)
            self.player_banner.setObjectName("player_banner")
            self.horizontalLayout_2.addWidget(self.player_banner)

            # Player Data Frame
            self.player_datas = QtWidgets.QFrame(self.player_information)
            self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.player_datas)

            # Player puu-id + Region
            self.player_ids = QtWidgets.QLabel(self.player_datas)
            font = QtGui.QFont()
            font.setPointSize(15)
            self.player_ids.setFont(font)
            self.player_ids.setText("puu-ID | EU")
            self.player_ids.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            self.verticalLayout_5.addWidget(self.player_ids)

            # Player Name + Rank
            tier_icon = Path(__file__).parent.joinpath(
                "Images\\Example\\ExampleRank.png"
            )
            self.player = QtWidgets.QLabel(self.player_datas)
            font = QtGui.QFont()
            font.setPointSize(35)
            self.player.setFont(font)
            self.player.setText(
                f"<html><head/><body>"
                f'<p><span style=" font-size:29pt;">player#Tag</span></p>'
                f"<p>Account Level 0 | Iron 3 "
                f'<img src="{tier_icon}" width="32" height="32"/> '
                f'<span style=" font-size:20pt;"> 0rr</span></p>'
                f"</body></html>"
            )
            self.player.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            self.verticalLayout_5.addWidget(self.player)

            self.horizontalLayout_2.addWidget(self.player_datas)
            self.verticalLayout.addWidget(self.player_information)

            # ---------------------------------------------------------
            # General Stats Section
            # ---------------------------------------------------------
            self.general_stats = QtWidgets.QFrame(self.home)
            self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.general_stats)

            # Stats Frame
            self.StatsFrame = QtWidgets.QFrame(self.general_stats)
            self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.StatsFrame)

            # Title
            self.stats_title = QtWidgets.QLabel(self.StatsFrame)
            self.stats_title.setText(
                "<html><head/><body>"
                '<p><span style=" font-size:22pt;">GENERAL STATS</span>'
                '<span style=" font-size:18pt; color:#6a6a6a;"> (Last 10 Matches)</span></p>'
                "</body></html>"
            )
            self.stats_title.setAlignment(QtCore.Qt.AlignCenter)
            self.verticalLayout_6.addWidget(self.stats_title)

            # Stats Box (Accuracy & KD etc.)
            self.g_stats = QtWidgets.QFrame(self.StatsFrame)
            self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.g_stats)

            # Accuracy Icon
            Basic = Path(__file__).parent.joinpath("Images\\Dummy\\Basic.png")
            self.accuracy_logo = QtWidgets.QLabel(self.g_stats)
            self.accuracy_logo.setPixmap(QtGui.QPixmap(str(Basic)))
            self.accuracy_logo.setAlignment(QtCore.Qt.AlignCenter)
            self.horizontalLayout_9.addWidget(self.accuracy_logo)

            # Accuracy Text
            self.accuarcy_text = QtWidgets.QLabel(self.g_stats)
            self.accuarcy_text.setText("Headshots: 0%\nBodyshots: 0%\nLegshots: 0%")
            self.accuarcy_text.setAlignment(QtCore.Qt.AlignCenter)
            self.horizontalLayout_9.addWidget(self.accuarcy_text)

            # Stats Text
            self.stats_text = QtWidgets.QLabel(self.g_stats)
            self.stats_text.setText(
                "K/D: 0.00\n"
                "Average Combat Score: 0\n"
                "Average Damage per Round: 0\n"
                "Winrate: 0%"
            )
            self.stats_text.setAlignment(QtCore.Qt.AlignCenter)
            self.horizontalLayout_9.addWidget(self.stats_text)

            self.verticalLayout_6.addWidget(self.g_stats)
            self.horizontalLayout_8.addWidget(self.StatsFrame)
            self.verticalLayout.addWidget(self.general_stats)

            # ---------------------------------------------------------
            # Competitive & Match History Section
            # ---------------------------------------------------------
            self.stats = QtWidgets.QFrame(self.home)
            self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.stats)

            # Competitive Stats
            self.comp_information = QtWidgets.QFrame(self.stats)
            self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.comp_information)

            self.comp_title = QtWidgets.QLabel(self.comp_information)
            self.comp_title.setText("COMPETITIVE STATS")
            self.comp_title.setAlignment(QtCore.Qt.AlignCenter)
            self.verticalLayout_2.addWidget(self.comp_title)

            self.comp_scroll_area = QtWidgets.QScrollArea(self.comp_information)
            self.comp_scroll_area.setVerticalScrollBarPolicy(
                QtCore.Qt.ScrollBarAsNeeded
            )
            self.comp_scroll_area.setHorizontalScrollBarPolicy(
                QtCore.Qt.ScrollBarAlwaysOff
            )
            self.comp_scroll_area.setWidgetResizable(True)

            self.CompScrollLayout = QtWidgets.QWidget()
            self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.CompScrollLayout)

            self.comp_history = QtWidgets.QLabel(self.CompScrollLayout)
            font = QtGui.QFont()
            font.setPointSize(14)
            self.comp_history.setFont(font)
            self.comp_history.setText(
                "Matchmaking Ratio\n"
                "Competitive Wins\n"
                "Competitive Games Played\n"
                "Previous Ranks\n"
                "Rank History"
            )
            self.comp_history.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
            self.horizontalLayout_3.addWidget(self.comp_history)

            self.comp_scroll_area.setWidget(self.CompScrollLayout)
            self.verticalLayout_2.addWidget(self.comp_scroll_area)
            self.horizontalLayout_6.addWidget(self.comp_information)

            # Match History
            self.match_history = QtWidgets.QFrame(self.stats)
            self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.match_history)

            self.history_title = QtWidgets.QLabel(self.match_history)
            self.history_title.setText("MATCH HISTORY")
            self.history_title.setAlignment(QtCore.Qt.AlignCenter)
            self.verticalLayout_4.addWidget(self.history_title)

            self.history_scroll_area = QtWidgets.QScrollArea(self.match_history)
            self.history_scroll_area.setHorizontalScrollBarPolicy(
                QtCore.Qt.ScrollBarAlwaysOff
            )
            self.history_scroll_area.setWidgetResizable(True)

            self.history_scroll_layout = QtWidgets.QWidget()
            self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.history_scroll_layout)

            self.history = QtWidgets.QLabel(self.history_scroll_layout)
            font = QtGui.QFont()
            font.setPointSize(14)
            self.history.setFont(font)
            self.history.setText(
                "<html><head/><body>"
                "Day, Date, Time<br>"
                "Match ID<br>"
                "Region - Cluster<br>"
                f"Map | Mode | Agent: <img src='{Path(__file__).parent.joinpath('Images/Agents/Jett.png')}' width='23' height='23'/> Jett<br>"
                "0-0 WON<br>"
                "Kills Assists Deaths | 0.00 K/D<br>"
                "HS%: 0% | ACS: 0 | ADR: 0 | Total Score: 0<br>"
                "</body></html>"
            )
            self.history.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
            self.horizontalLayout_4.addWidget(self.history)

            self.history_scroll_area.setWidget(self.history_scroll_layout)
            self.verticalLayout_4.addWidget(self.history_scroll_area)
            self.horizontalLayout_6.addWidget(self.match_history)

            # Add Competitive + Match History to Home
            self.verticalLayout.addWidget(self.stats)

            # Error Label (Home Tab)
            self.home_error = QtWidgets.QLabel(self.home)
            font = QtGui.QFont()
            font.setPointSize(12)
            self.home_error.setFont(font)
            self.home_error.setText("")
            self.home_error.setWordWrap(True)
            self.verticalLayout.addWidget(self.home_error)

            # Add HOME Tab to Tabs
            self.tabs_left.addTab(self.home, "HOME")

            # ---------------------------------------------------------
            # Leaderboard TAB
            # ---------------------------------------------------------
            self.leaderboard = QtWidgets.QWidget()
            self.leaderboard.setObjectName("leaderboard")
            layout_leaderboard = QtWidgets.QVBoxLayout(self.leaderboard)
            layout_leaderboard.setContentsMargins(10, 10, 10, 10)
            layout_leaderboard.setSpacing(10)

            # Leaderboard Input Card
            self.LeaderBoardInput = QtWidgets.QFrame(self.leaderboard)
            self.LeaderBoardInput.setObjectName("LeaderBoardInput")
            input_layout = QtWidgets.QHBoxLayout(self.LeaderBoardInput)
            input_layout.setContentsMargins(10, 10, 10, 10)
            input_layout.setSpacing(10)

            # Act ComboBox
            self.act = QtWidgets.QComboBox(self.LeaderBoardInput)
            populate_combo_box(self.act, list(seasons.keys()))
            self.act.setCurrentText(list(seasons.keys())[0])
            self.act.setEditable(True)
            self.act_edit = self.act.lineEdit()
            self.act_edit.setAlignment(Qt.AlignCenter)
            self.act_edit.setReadOnly(True)
            input_layout.addWidget(self.act)

            # Region ComboBox
            self.leaderboard_region = QtWidgets.QComboBox(self.LeaderBoardInput)
            populate_combo_box(self.leaderboard_region, regions)
            self.leaderboard_region.setCurrentText("EU")
            self.leaderboard_region.setEditable(True)
            self.leaderboard_edit = self.leaderboard_region.lineEdit()
            self.leaderboard_edit.setAlignment(Qt.AlignCenter)
            self.leaderboard_edit.setReadOnly(True)
            input_layout.addWidget(self.leaderboard_region)

            # Player Count SpinBox
            self.player_count = QtWidgets.QSpinBox(self.LeaderBoardInput)
            self.player_count.setAlignment(Qt.AlignCenter)
            self.player_count.setButtonSymbols(QtWidgets.QAbstractSpinBox.UpDownArrows)
            self.player_count.setPrefix("Players: ")
            self.player_count.setRange(1, 15000)
            input_layout.addWidget(self.player_count)

            # Reload Button
            self.reload_button = QtWidgets.QPushButton("Reload", self.LeaderBoardInput)
            self.reload_button.setToolTip("Reload the leaderboard")
            input_layout.addWidget(self.reload_button)

            layout_leaderboard.addWidget(self.LeaderBoardInput)

            # Players ScrollArea
            self.player_scroll_area = QtWidgets.QScrollArea(self.leaderboard)
            self.player_scroll_area.setWidgetResizable(True)
            self.player_scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
            self.player_scroll_area_layout = QtWidgets.QWidget()
            self.player_scroll_area_layout.setObjectName("player_scroll_area_layout")
            self.verticalLayout_8 = QtWidgets.QVBoxLayout(
                self.player_scroll_area_layout
            )
            self.verticalLayout_8.setSpacing(5)
            self.verticalLayout_8.setContentsMargins(5, 5, 5, 5)
            self.player_scroll_area.setWidget(self.player_scroll_area_layout)

            layout_leaderboard.addWidget(self.player_scroll_area)
            self.tabs_left.addTab(self.leaderboard, "LEADERBOARD")

            # --- MATCH TRACKER TAB ---
            self.match_tracker = QtWidgets.QWidget()
            self.match_tracker.setObjectName("match_tracker")
            layout_match = QtWidgets.QVBoxLayout(self.match_tracker)
            layout_match.setContentsMargins(10, 10, 10, 10)
            layout_match.setSpacing(10)

            # Input Card
            match_input_frame = QtWidgets.QFrame(self.match_tracker)

            match_input_layout = QtWidgets.QHBoxLayout(match_input_frame)
            match_input_layout.setContentsMargins(10, 10, 10, 10)
            match_input_layout.setSpacing(10)

            # MatchID Input
            self.match_id_input = QtWidgets.QLineEdit(match_input_frame)
            self.match_id_input.setMaxLength(36)
            self.match_id_input.setAlignment(QtCore.Qt.AlignCenter)
            self.match_id_input.setPlaceholderText("ENTER MATCH ID (36 characters)")
            match_input_layout.addWidget(self.match_id_input)

            # Execute Button
            self.execute_button = QtWidgets.QPushButton("EXECUTE", match_input_frame)
            self.execute_button.setToolTip("Fetch match information")
            match_input_layout.addWidget(self.execute_button)

            layout_match.addWidget(match_input_frame)

            # Title Label
            self.MatchInformations = QtWidgets.QLabel(self.match_tracker)
            title_font = QtGui.QFont()
            title_font.setPointSize(18)
            title_font.setBold(True)
            self.MatchInformations.setFont(title_font)
            self.MatchInformations.setText("MATCH INFORMATION")
            self.MatchInformations.setAlignment(QtCore.Qt.AlignCenter)
            layout_match.addWidget(self.MatchInformations)

            # Spacer
            layout_match.addItem(
                QtWidgets.QSpacerItem(
                    20,
                    40,
                    QtWidgets.QSizePolicy.Minimum,
                    QtWidgets.QSizePolicy.Expanding,
                )
            )

            # Error Label
            self.match_error = QtWidgets.QLabel(self.match_tracker)
            error_font = QtGui.QFont()
            error_font.setPointSize(12)
            self.match_error.setFont(error_font)
            self.match_error.setStyleSheet("color: red;")
            self.match_error.setAlignment(QtCore.Qt.AlignCenter)
            self.match_error.setWordWrap(True)
            layout_match.addWidget(self.match_error)

            self.tabs_left.addTab(self.match_tracker, "MATCH")

            # --- RIGHT SIDE TABS ---
            self.tabs_right = QtWidgets.QTabWidget(self.centralwidget)
            self.tabs_right.setTabPosition(QtWidgets.QTabWidget.North)
            self.tabs_right.setTabShape(QtWidgets.QTabWidget.Rounded)
            self.tabs_right.setMovable(False)
            self.tabs_right.setObjectName("TabsRight")

            self.horizontalLayout_main.addWidget(self.tabs_left)
            self.horizontalLayout_main.addWidget(self.tabs_right)

            # Create Dicts with Bundles and use Valorant API to get all current bundles
            try:
                current_Bundle = valo_api.get_store_featured_v2()
            except Exception as e:
                self.home_error.setText(
                    f"<span style='color:red;'>Error fetching bundles: {e}</span>"
                )
                current_Bundle = []
            self.bundle = dict()

            for i, bundles in enumerate(current_Bundle):
                bundleUuid = bundles.bundle_uuid

                # Get bundle JSON and banner
                bundleJson = fetch_url(
                    f"https://valorant-api.com/v1/bundles/{bundleUuid}"
                ).json()
                img = await get_image_async(bundleJson["data"]["displayIcon2"])

                # Resize the banner image
                max_width = 400
                max_height = 200
                img = img.scaled(
                    max_width,
                    max_height,
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation,
                )

                # ---------------------------------------------------------
                # Bundle TAB
                # ---------------------------------------------------------
                self.bundle[i] = QtWidgets.QWidget()
                self.bundle[i].setObjectName("Bundle")
                layout_bundle = QtWidgets.QVBoxLayout(self.bundle[i])
                layout_bundle.setContentsMargins(10, 10, 10, 10)
                layout_bundle.setSpacing(0)

                # Main Frame as Card
                self.bundle_main = QtWidgets.QFrame(self.bundle[i])
                self.bundle_main.setObjectName("BundleMain")
                layout_main = QtWidgets.QVBoxLayout(self.bundle_main)
                layout_main.setContentsMargins(10, 10, 10, 10)
                layout_main.setSpacing(10)

                # Banner
                self.bundle_banner = QtWidgets.QLabel(self.bundle_main)
                self.bundle_banner.setPixmap(QtGui.QPixmap(img))
                self.bundle_banner.setAlignment(QtCore.Qt.AlignCenter)
                self.bundle_banner.setSizePolicy(
                    QtWidgets.QSizePolicy.Expanding,
                    QtWidgets.QSizePolicy.Fixed,
                )
                self.bundle_banner.setStyleSheet("border-radius: 8px;")
                layout_main.addWidget(self.bundle_banner)

                # Separator
                line = QtWidgets.QFrame()
                line.setFrameShape(QtWidgets.QFrame.HLine)
                line.setFrameShadow(QtWidgets.QFrame.Sunken)
                layout_main.addWidget(line)

                # Prices
                self.bundle_prices = QtWidgets.QLabel(self.bundle_main)
                self.bundle_prices.setAlignment(QtCore.Qt.AlignCenter)
                self.bundle_prices.setWordWrap(True)
                layout_main.addWidget(self.bundle_prices)

                # Spacer
                layout_main.addItem(
                    QtWidgets.QSpacerItem(
                        20,
                        40,
                        QtWidgets.QSizePolicy.Minimum,
                        QtWidgets.QSizePolicy.Expanding,
                    )
                )

                # Footer: Remaining Time
                self.bundle_last = QtWidgets.QLabel(self.bundle_main)
                font = QtGui.QFont()
                font.setPointSize(15)
                font.setBold(True)
                self.bundle_last.setFont(font)
                self.bundle_last.setAlignment(QtCore.Qt.AlignCenter)
                self.bundle_last.setStyleSheet("color: red;")
                layout_main.addWidget(self.bundle_last)

                # Add main frame into bundle widget
                layout_bundle.addWidget(self.bundle_main)

                # Collect item prices
                prices = [f"Bundle Price - {bundles.bundle_price} Valorant Points<br>"]
                for item in bundles.items:
                    if item.amount > 1:
                        if item.discounted_price == 0:
                            prices.append(
                                f"{item.amount}x {item.name} - {item.base_price} VP "
                                f"<span style='font-size:small;'>(Free if bought as a whole Bundle)</span><br>"
                            )
                        else:
                            prices.append(
                                f"{item.amount}x {item.name} - {item.base_price} VP "
                                f"<span style='font-size:small;'>({item.discounted_price} VP if bought as whole Bundle)</span><br>"
                            )
                    else:
                        if item.discounted_price == 0:
                            prices.append(
                                f"{item.name} - {item.base_price} VP "
                                f"<span style='font-size:small;'>(Free if bought as a whole Bundle)</span><br>"
                            )
                        else:
                            prices.append(
                                f"{item.name} - {item.base_price} VP "
                                f"<span style='font-size:small;'>({item.discounted_price} VP if bought as whole Bundle)</span><br>"
                            )
                prices = "".join(prices)

                # Set texts
                self.bundle_prices.setText(prices)
                self.bundle_last.setText(
                    f"Bundle remaining in Shop: {display_time(bundles.seconds_remaining, 3)}"
                )

                # Add as Tab
                self.tabs_right.addTab(
                    self.bundle[i],
                    f"{bundleJson['data']['displayName'].upper()}",
                )

            self.horizontalLayout_main.addWidget(self.tabs_right)

            # Create Loading Bar
            self.loading_bar = QtWidgets.QProgressBar(self.centralwidget)
            self.loading_bar.setGeometry(QtCore.QRect(10, 860, 1029, 23))
            self.loading_bar.setProperty("value", 0)
            self.loading_bar.setTextVisible(True)
            self.loading_bar.setObjectName("loading_bar")
            self.loading_bar.setVisible(False)
            self.verticalLayout.addWidget(self.loading_bar)

            valtracker.setCentralWidget(self.centralwidget)
            self.tabs_left.setCurrentIndex(0)
            self.player_region.setCurrentIndex(0)
            self.leaderboard_region.setCurrentIndex(0)

            # Functions
            self.get_button.clicked.connect(self.get_information)
            self.execute_button.clicked.connect(self.get_match_information)
            self.reset_button.clicked.connect(self.reset_information)
            self.reload_button.clicked.connect(self.get_leaderboard)
            self.mode_switcher.clicked.connect(self.modeSwitch)
            QtCore.QMetaObject.connectSlotsByName(valtracker)

        except Exception as error:
            logging.error(f"Error setting up UI: {traceback.format_exc()}")
            self.home_error.setText(f"Error: {error}")

    def update_loading_bar(self, value: int) -> None:
        """
        Update the loading bar with the given value.
        """
        self.loading_bar.setValue(value)
        if value >= 100:
            self.loading_bar.setVisible(False)
        else:
            self.loading_bar.setVisible(True)

    def clear_errors(self) -> None:
        """
        Clear error messages from the UI.
        """
        self.home_error.setText("")
        self.match_error.setText("")

    def get_information(self) -> None:
        """
        Fetch and display player information.
        """
        self.clear_errors()
        self.update_loading_bar(10)
        try:
            # API functions
            Details = valo_api.get_account_details_by_name(
                version="v2",
                name=self.player_name.text(),
                tag=self.player_tag.text(),
            )

            # Get rank, rr and mmr
            RankDetails = valo_api.get_mmr_details_by_name_v2(
                region=self.player_region.currentText(),
                name=self.player_name.text(),
                tag=self.player_tag.text(),
            )

            # Get Match history
            if self.player_gamemode.currentText() != "ALL":
                HistoryDetails = valo_api.get_match_history_by_name(
                    version="v3",
                    region=self.player_region.currentText(),
                    name=self.player_name.text(),
                    tag=self.player_tag.text(),
                    size=10,
                    game_mode=self.player_gamemode.currentText().lower(),
                )
            else:
                HistoryDetails = valo_api.get_match_history_by_name(
                    version="v3",
                    region=self.player_region.currentText(),
                    name=self.player_name.text(),
                    tag=self.player_tag.text(),
                    size=10,
                )

            # Get Recent rank Changes
            MMRDetails = valo_api.get_mmr_history_by_name(
                version="v1",
                region=self.player_region.currentText(),
                name=self.player_name.text(),
                tag=self.player_tag.text(),
            )

            self.update_loading_bar(50)

            # DETAILS ~ puuid, region, Account Level and the PlayerCard
            # RANK DETAILS ~ rank, rr, mmr
            puuid = Details.puuid
            region = Details.region
            account_level = Details.account_level
            card_id = Details.card
            card_data = fetch_url(
                f"https://valorant-api.com/v1/playercards/{card_id}"
            ).json()
            card = card_data["data"]["wideArt"]
            rank = RankDetails.current_data.currenttierpatched
            peak_rank = RankDetails.highest_rank.patched_tier
            rr = RankDetails.current_data.ranking_in_tier
            mmr = RankDetails.current_data.elo

            # Sets PUU-ID and region
            self.player_ids.setText(f"{puuid} | {region}")

            # Creates List with mmr, Comp Wins, Comp Games
            rank_icon = Path(__file__).parent.joinpath(f"Images/Ranks/{rank}.png")
            peak_rank_icon = Path(__file__).parent.joinpath(
                f"Images/Ranks/{peak_rank}.png"
            )
            previous_ranks = [
                f"Rank: {rank} <img src='{rank_icon}' width='23' height='23'/> {rr}rr<br>"
                f"Peak Rank: {peak_rank} <img src='{peak_rank_icon}' width='23' height='23'/><br>"
                f"Matchmaking Ratio: {mmr}<br><br>"
            ]

            # Gets Last rank Adds last Ranks with mmr, Wins, Games to the List | if player didn't play in this act or an
            # API Problem is there, then continue
            act_ranks = RankDetails.by_season
            last_rank = dict(reversed(act_ranks.items()))
            for x in last_rank:
                try:
                    if (
                        last_rank[x].final_rank_patched
                        not in (
                            None,
                            "Unrated",
                        )
                        and x != "v25a1".lower()
                    ):
                        rank_icon = Path(__file__).parent.joinpath(
                            f"Images/Ranks/{last_rank[x].final_rank_patched}.png"
                        )
                        previous_ranks.append(
                            f"{x.upper()}: {last_rank[x].final_rank_patched} <img src='{rank_icon}' width='23' height='23'/> | {last_rank[x].wins} Wins - {last_rank[x].number_of_games} Game(s) played<br>"
                        )
                    else:
                        continue
                except Exception as error:
                    print(traceback.format_exc())
                    self.home_error.setText(f"{format(error)}")

            # If there is a rank, add a rank history
            # For every last match in the detail get +rr or -rr and rank / rr
            if rank is not None:
                previous_ranks.append("<br>")
                for x in MMRDetails:
                    rank_icon = Path(__file__).parent.joinpath(
                        f"Images/Ranks/{x.currenttierpatched}.png"
                    )
                    if x.mmr_change_to_last_game >= 0:
                        previous_ranks.append(
                            f"{x.date} | {x.currenttierpatched} <img src='{rank_icon}' width='23' height='23'/> {x.ranking_in_tier}rr (+{x.mmr_change_to_last_game})<br>"
                        )
                    else:
                        previous_ranks.append(
                            f"{x.date} | {x.currenttierpatched} <img src='{rank_icon}' width='23' height='23'/> {x.ranking_in_tier}rr ({x.mmr_change_to_last_game})<br>"
                        )

            # Makes Ranks to str and makes it to Text
            previous_ranks = "".join(previous_ranks)
            self.comp_history.setText(previous_ranks)

            # getting an QImage for the player card.
            with concurrent.futures.ThreadPoolExecutor() as executor:
                img = executor.submit(
                    get_image,
                    card,
                )
                img = img.result()
            self.player_banner.setPixmap(QPixmap(img))

            # Get Match history as a List, and gets every current matches
            match_history = ["<html><head/><body>"]

            # Some Variables
            headshots = 0
            bodyshots = 0
            legshots = 0
            total_damage = 0
            total_rounds = 0
            total_combat_score = 0
            total_kills = 0
            total_deaths = 0
            total_wins = 0
            total_matches = 0

            for x in HistoryDetails:
                # Match, Team, Players and Rounds played
                match = x.metadata
                teams = x.teams
                players = x.players
                rounds_played = match.rounds_played

                # Get Stats of player with get_stats function
                get_stats = {
                    player.name: player.stats for player in players.all_players
                }.get(Details.name)

                # Get Agent of player
                get_agent = {
                    player.name: player.character for player in players.all_players
                }.get(Details.name)

                # Get Agent image from local file
                agent_image = Path(__file__).parent.joinpath(
                    f"Images/Agents/{get_agent.lower()}.png"
                )

                # Some Variables
                kills = (
                    get_stats.kills
                    if hasattr(
                        get_stats,
                        "kills",
                    )
                    else 0
                )
                deaths = (
                    get_stats.deaths
                    if hasattr(
                        get_stats,
                        "deaths",
                    )
                    else 0
                )
                assists = (
                    get_stats.assists
                    if hasattr(
                        get_stats,
                        "assists",
                    )
                    else 0
                )
                total_score = (
                    get_stats.score
                    if hasattr(
                        get_stats,
                        "score",
                    )
                    else 0
                )
                combat_score = total_score / rounds_played
                damage = 0

                for rounds in x.rounds:
                    player = {
                        p.player_display_name: p for p in rounds.player_stats
                    }.get(f"{Details.name}#{Details.tag}")
                    damage += (
                        player.damage
                        if hasattr(
                            player,
                            "damage",
                        )
                        else 0
                    )
                    total_rounds += 1

                # Add Aim rates
                headshots += (
                    get_stats.headshots
                    if hasattr(
                        get_stats,
                        "headshots",
                    )
                    else 0
                )
                bodyshots += (
                    get_stats.bodyshots
                    if hasattr(
                        get_stats,
                        "bodyshots",
                    )
                    else 0
                )
                legshots += (
                    get_stats.legshots
                    if hasattr(
                        get_stats,
                        "legshots",
                    )
                    else 0
                )

                # Some Variables
                total_kills += kills
                total_deaths += deaths
                total_combat_score += combat_score
                total_damage += damage

                # Calculate HS% in the Match
                try:
                    headshot_rate = round(
                        get_stats.headshots
                        / (
                            get_stats.headshots
                            + get_stats.bodyshots
                            + get_stats.legshots
                        )
                        * 100
                    )
                except ZeroDivisionError:
                    headshot_rate = 0

                # Rounds to 0.00 <- 2 Decimals
                try:
                    kd = format(
                        kills / deaths,
                        ".2f",
                    )
                except ZeroDivisionError:
                    kd = format(
                        kills,
                        ".2f",
                    )

                # Get Team and Team information of player with get_team function
                get_team = {p.name: p.team for p in players.all_players}.get(
                    Details.name
                )
                if get_team == "Blue":
                    get_team = teams.blue
                else:
                    get_team = teams.red

                # Set when Won, Rounds Won, Lost.
                won = get_team.has_won
                rounds_won = get_team.rounds_won
                rounds_lost = get_team.rounds_lost
                total_matches += 1

                # If match lost, make text lost
                if won:
                    total_wins += 1
                    won = '<span style="color:green;">WON</span>'
                else:
                    won = '<span style="color:red;">LOST</span>'

                # Get Match ID, Map, region, Cluster and Mode with Match Metadata
                match_id = match.matchid
                match_map = match.map
                region = match.region.upper()
                cluster = match.cluster
                mode = match.mode

                # If Deathmatch, remove Rounds, Won/Lost and Combat Score
                if mode == "Deathmatch":
                    match_history.append(
                        f"{match.game_start_patched}<br>"
                        f"{match_id}<br>"
                        f"<span style='color:purple;'>{region} - {cluster}</span><br>"
                        f"{match_map} | {mode} | Agent: <img src='{agent_image}' width='23' height='23'/> {get_agent}<br>"
                        f"<span style='color:green;'>{kills} Kills</span> <span style='color:blue;'>{assists} Assists</span> <span style='color:red;'>{deaths} Deaths</span> | {kd} K/D<br>"
                        f"Total Score: {total_score}<br><br>"
                    )
                else:
                    match_history.append(
                        f"{match.game_start_patched}<br>"
                        f"{match_id}<br>"
                        f"<span style='color:purple;'>{region} - {cluster}</span><br>"
                        f"{match_map} | {mode} | Agent: <img src='{agent_image}' width='23' height='23'/> {get_agent}<br>"
                        f"{rounds_won}-{rounds_lost} {won}<br>"
                        f"<span style='color:green;'>{kills} Kills</span> <span style='color:blue;'>{assists} Assists</span> <span style='color:red;'>{deaths} Deaths</span> | {kd} K/D<br>"
                        f"HS%: {headshot_rate}% | CS: {round(combat_score)} | ADR: {round(damage / rounds_played)} | Total Score: {total_score}<br><br>"
                    )

            # Set Match to Text
            match_history.append("</body></html>")
            match_history = "".join(match_history)

            # Dummys
            headshot_dummy = Path(__file__).parent.joinpath(
                "Images\\Dummy\\Headshot.png"
            )
            bodyshot_dummy = Path(__file__).parent.joinpath(
                "Images\\Dummy\\Bodyshot.png"
            )
            legshot_dummy = Path(__file__).parent.joinpath("Images\\Dummy\\Legshot.png")
            basic_dummy = Path(__file__).parent.joinpath("Images\\Dummy\\Basic.png")

            # Set Rates with Math
            if self.player_gamemode.currentText() != "DEATHMATCH":
                try:
                    headshot_rate = round(
                        headshots / (headshots + bodyshots + legshots) * 100
                    )
                    bodyshot_rate = round(
                        bodyshots / (headshots + bodyshots + legshots) * 100
                    )
                    legshot_rate = round(
                        legshots / (headshots + bodyshots + legshots) * 100
                    )
                except ZeroDivisionError:
                    headshot_rate = 0
                    bodyshot_rate = 0
                    legshot_rate = 0

                # Set Dummy Prior

                if headshot_rate > bodyshot_rate and headshot_rate > legshot_rate:
                    self.accuracy_logo.setPixmap(QtGui.QPixmap(str(headshot_dummy)))
                elif bodyshot_rate > headshot_rate and bodyshot_rate > legshot_rate:
                    self.accuracy_logo.setPixmap(QtGui.QPixmap(str(bodyshot_dummy)))
                elif legshot_rate > headshot_rate and legshot_rate > bodyshot_rate:
                    self.accuracy_logo.setPixmap(QtGui.QPixmap(str(legshot_dummy)))
                else:
                    self.accuracy_logo.setPixmap(QtGui.QPixmap(str(basic_dummy)))
            else:
                headshot_rate = "-"
                bodyshot_rate = "-"
                legshot_rate = "-"
                self.accuracy_logo.setPixmap(QtGui.QPixmap(str(basic_dummy)))

            # Gets the current rank AS TIER INDEX (int) and compares it with the index data, to get the RANK IMAGE
            tier_index = RankDetails.current_data.currenttier
            data = fetch_url("https://valorant-api.com/v1/competitivetiers").json()
            tiers = data["data"][-1]["tiers"]
            tier = None

            # If it has any rank, get it ELSE say Unranked
            if rank is not None:
                for tier in tiers:
                    if tier["tier"] == tier_index:
                        tier = tier["tierName"]
                        break
            else:
                tier = "UNRANKED"

            # Gets the PNG for the HTML Rich Text
            tier_icon = Path(__file__).parent.joinpath(f"Images/Ranks/{tier}.png")

            # Add Texts
            self.history.setText(match_history)  # <- List which got made to a string
            self.accuarcy_text.setText(
                f"Headshots: {headshot_rate}%<br>"
                f"Bodyshots: {bodyshot_rate}%<br>"
                f"Legshots: {legshot_rate}%"
            )
            try:
                self.stats_text.setText(
                    f"K/D: {format(total_kills / total_deaths, '.2f')}<br>"
                    f"Average Combat Score: {round(total_combat_score / total_matches)}<br>"
                    f"Average Damage per Round: {round(total_damage / total_rounds)}<br>"
                    f"Winrate: {round(total_wins / total_matches * 100)}%"
                )
            except ZeroDivisionError:
                self.stats_text.setText("")
            self.player.setText(
                f'<html><head/><body><p><span style=" font-size:29pt; font-weight:bold;">{Details.name}#{Details.tag}<p'
                f'>Account Level <span style="color:blue;">{account_level}</span> | <span style="color:orange;">{rank}</span> </span><img src="{tier_icon}"width="32 '
                f'"height="32"/><span style=" font-size:20pt;"> {rr}rr</span></p></body></html>'
            )
            self.home_error.setText(f"")
            self.update_loading_bar(100)  # Update loading bar to 100%
        except Exception as error:
            logging.error(
                f"Error fetching player information: {traceback.format_exc()}"
            )
            self.home_error.setText(f"Error: {error}")
            self.update_loading_bar(0)  # Reset loading bar on error

    def get_leaderboard(self) -> None:
        """
        Fetch and display leaderboard information.
        """
        # Clear previous leaderboard data
        self.leaderboard_player = {}
        self.leaderboard_player_layout = {}
        self.leaderboard_player_banner = {}
        self.leaderboard_player_information = {}
        self.leaderboard_player_spacer = {}

        self.clear_errors()
        self.update_loading_bar(10)  # Update loading bar to 10%
        start_time = time.time()
        try:
            # Get Values
            season = self.act.currentText()
            region = self.leaderboard_region.currentText()
            player_limit = int(self.player_count.value())
            player_cards = {}

            try:
                clear_layout(self.verticalLayout_8)
            except AttributeError:
                pass

            # Get API
            leaderboard = valo_api.get_leaderboard(
                version="v2",
                region=region,
                season=seasons[season],
            )

            self.update_loading_bar(50)  # Update loading bar to 50%

            # Set all new leaderboard stuff
            for (
                i,
                x,
            ) in enumerate(leaderboard.players):
                if i < player_limit:
                    try:
                        # Setting player
                        self.leaderboard_player[i] = QtWidgets.QFrame(
                            self.player_scroll_area_layout
                        )
                        self.leaderboard_player[i].setEnabled(True)
                        self.leaderboard_player[i].setObjectName("PlayerTemplate")
                        self.leaderboard_player_layout[i] = QtWidgets.QHBoxLayout(
                            self.leaderboard_player[i]
                        )
                        self.leaderboard_player_layout[i].setContentsMargins(
                            0,
                            0,
                            0,
                            0,
                        )
                        self.leaderboard_player_layout[i].setObjectName(
                            "PlayerLayoutTemplate"
                        )

                        # Setting Banner
                        example_banner = Path(__file__).parent.joinpath(
                            "Images\\Example\\Example_banner.png"
                        )
                        self.leaderboard_player_banner[i] = QtWidgets.QLabel(
                            self.leaderboard_player[i]
                        )
                        self.leaderboard_player_banner[i].setText("")
                        self.leaderboard_player_banner[i].setPixmap(
                            QtGui.QPixmap(str(example_banner))
                        )
                        self.leaderboard_player_banner[i].setScaledContents(False)
                        self.leaderboard_player_banner[i].setObjectName(
                            "leaderboard_player_banner"
                        )
                        self.leaderboard_player_layout[i].addWidget(
                            self.leaderboard_player_banner[i]
                        )
                        self.leaderboard_player_information[i] = QtWidgets.QLabel(
                            self.leaderboard_player[i]
                        )

                        # Get LeaderboardPlayers rank, watching out if Episode is under 5
                        tier = x.competitiveTier
                        ranklist = get_ranks()
                        rank = ranklist.get(
                            tier,
                            "Unknown Rank",
                        )

                        # If anonymous else stuff
                        if x.IsAnonymized:
                            self.leaderboard_player_information[i].setText(
                                f"#{x.leaderboardRank} | Anonymous player | {rank} {x.rankedRating}rr | {x.numberOfWins} Wins"
                            )
                        else:
                            self.leaderboard_player_information[i].setText(
                                f"#{x.leaderboardRank} | {x.gameName}#{x.tagLine} | {rank} {x.rankedRating}rr | {x.numberOfWins} Wins | {x.puuid}"
                            )

                        # Layouts
                        self.leaderboard_player_information[i].setAlignment(
                            QtCore.Qt.AlignCenter
                        )
                        self.leaderboard_player_information[i].setObjectName(
                            "leaderboard_player_information"
                        )
                        self.leaderboard_player_layout[i].addWidget(
                            self.leaderboard_player_information[i]
                        )

                        self.leaderboard_player_spacer[i] = QtWidgets.QSpacerItem(
                            40,
                            20,
                            QtWidgets.QSizePolicy.Expanding,
                            QtWidgets.QSizePolicy.Minimum,
                        )
                        self.leaderboard_player_layout[i].addItem(
                            self.leaderboard_player_spacer[i]
                        )
                        self.verticalLayout_8.addWidget(self.leaderboard_player[i])

                        # Getting players banner and add it to player_cards
                        player_card = f"https://media.valorant-api.com/playercards/{x.PlayerCardID}/smallart.png"
                        player_cards[i] = player_card

                    except AttributeError:
                        continue
                else:
                    break

            self.leaderboard_spacer = QtWidgets.QSpacerItem(
                20,
                40,
                QtWidgets.QSizePolicy.Minimum,
                QtWidgets.QSizePolicy.Expanding,
            )
            self.verticalLayout_8.addItem(self.leaderboard_spacer)

            # Get & Set Banner
            items = list(player_cards.items())  # [(idx, url), ...]
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
                responses = list(ex.map(lambda pair: fetch_url(pair[1]), items))

            for (idx, _url), resp in zip(items, responses):
                if not resp or not resp.ok:
                    logging.warning(
                        f"Image fetch failed for idx={idx} url={_url} status={getattr(resp, 'status_code', 'n/a')}"
                    )
                    continue
                img = QImage()
                img.loadFromData(resp.content)
                self.leaderboard_player_banner[idx].setPixmap(QPixmap(img))

            logging.info(f"LEADERBOARD took --- {time.time() - start_time} seconds ---")
            self.update_loading_bar(100)  # Update loading bar to 100%

        except Exception as error:
            logging.error(f"Error fetching leaderboard: {traceback.format_exc()}")
            self.home_error.setText(f"Error: {error}")
            self.update_loading_bar(0)  # Reset loading bar on error

    def get_match_information(self) -> None:
        """
        Fetch and display match information.
        """
        self.clear_errors()
        self.update_loading_bar(10)  # Update loading bar to 10%
        try:
            # Get Match Details
            Match = valo_api.get_match_details_v2(match_id=self.match_id_input.text())

            # Variables
            match_id = Match.metadata.matchid
            game_date = Match.metadata.game_start_patched
            game_last = Match.metadata.game_length
            region = Match.metadata.region.upper()
            cluster = Match.metadata.cluster
            gamemode = Match.metadata.mode
            game_map = Match.metadata.map

            # Get Team Scores
            team_a_score = Match.teams.blue.rounds_won
            team_b_score = Match.teams.red.rounds_won

            self.update_loading_bar(50)  # Update loading bar to 50%

            # Get Player Statistics
            def generate_player_stats(players):
                sorted_players = sorted(
                    players, key=lambda p: p.stats.score, reverse=True
                )
                player_stats = ""
                for player in sorted_players:
                    agent_image = Path(__file__).parent.joinpath(
                        f"Images/Agents/{player.character.lower()}.png"
                    )
                    rank_icon = Path(__file__).parent.joinpath(
                        f"Images/Ranks/{player.currenttier_patched}.png"
                    )
                    headshot_rate = (
                        round(
                            (
                                player.stats.headshots
                                / (
                                    player.stats.headshots
                                    + player.stats.bodyshots
                                    + player.stats.legshots
                                )
                            )
                            * 100
                        )
                        if (
                            player.stats.headshots
                            + player.stats.bodyshots
                            + player.stats.legshots
                        )
                        > 0
                        else 0
                    )
                    kd = (
                        format(player.stats.kills / player.stats.deaths, ".2f")
                        if player.stats.deaths > 0
                        else format(player.stats.kills, ".2f")
                    )
                    player_stats += (
                        "<tr>"
                        f"<td>{player.name}</td>"
                        f"<td><img src='{agent_image}' width='32' height='32'/></td>"
                        f"<td><img src='{rank_icon}' width='32' height='32'/></td>"
                        f"<td>{player.stats.kills}</td>"
                        f"<td>{player.stats.deaths}</td>"
                        f"<td>{player.stats.assists}</td>"
                        f"<td>{headshot_rate}%</td>"
                        f"<td>{kd}</td>"
                        f"<td>{player.damage_made}</td>"
                        f"<td>{player.stats.score}</td>"
                        "</tr>"
                    )
                return player_stats

            team_a_stats = generate_player_stats(Match.players.blue)
            team_b_stats = generate_player_stats(Match.players.red)

            player_stats = (
                "<table border='1' style='font-size:12pt; width:100%; text-align:center; border-collapse:collapse;'>"
                "<thead style='background-color:#f2f2f2;'>"
                "<tr>"
                "<th>Player</th>"
                "<th>Agent</th>"
                "<th>Rank</th>"
                "<th>Kills</th>"
                "<th>Deaths</th>"
                "<th>Assists</th>"
                "<th>HS Rate</th>"
                "<th>K/D</th>"
                "<th>Damage</th>"
                "<th>Score</th>"
                "</tr>"
                "</thead>"
                "<tbody>"
                "<tr><td colspan='10' style='background-color:#e0e0e0;'>Team A</td></tr>"
                f"{team_a_stats}"
                "<tr><td colspan='10' style='background-color:#e0e0e0;'>Team B</td></tr>"
                f"{team_b_stats}"
                "</tbody></table>"
            )

            match_info_html = (
                "<html><head/><style>p { margin: 2px 0; }</style></head><body>"
                "<p><span style=' font-size:22pt;'>MATCH INFORMATION</span></p>"
                f"<p style='font-size:14pt;'>{match_id}</p>"
                f"<p style='font-size:14pt;'>{game_date} - {game_last}</p>"
                f"<p style='font-size:14pt;'>{region} - {cluster}</p>"
                f"<p style='font-size:14pt;'>{gamemode} - {game_map}</p>"
                f"<p style='font-size:14pt;'>Score: <span style='color:green;'>Team A {team_a_score}</span> : <span style='color:red;'>{team_b_score} Team B</span></p>"
                f"<p style='font-size:14pt;'>Total Kills: {sum(p.stats.kills for p in Match.players.all_players)}</p>"
                f"<p style='font-size:14pt;'>Total Assists: {sum(p.stats.assists for p in Match.players.all_players)}</p>"
                f"{player_stats}"
                "</body></html>"
            )

            self.MatchInformations.setTextFormat(QtCore.Qt.RichText)
            self.MatchInformations.setText(match_info_html)
            self.update_loading_bar(100)  # Update loading bar to 100%

        except Exception as error:
            logging.error(f"Error fetching match information: {traceback.format_exc()}")
            self.match_error.setText(f"Error: {error}")
            self.update_loading_bar(0)  # Reset loading bar on error

    def reset_information(self) -> None:
        """
        Reset the displayed information to default values.
        """
        self.clear_errors()
        self.update_loading_bar(10)  # Update loading bar to 10%
        try:
            tier_icon = Path(__file__).parent.joinpath(
                "Images\\Example\\ExampleRank.png"
            )
            example_banner = Path(__file__).parent.joinpath(
                "Images\\Example\\ExampleWideBanner.png"
            )
            basic_dummy = Path(__file__).parent.joinpath("Images\\Dummy\\Basic.png")
            self.player_name.setText("")
            self.player_name.setPlaceholderText("PLAYER NAME (16 characters)")
            self.player_tag.setText("")
            self.player_tag.setPlaceholderText("PLAYER TAG (5 characters)")
            self.player_banner.setPixmap(QtGui.QPixmap(str(example_banner)))
            self.player_ids.setText("puu-ID | EU")
            self.player.setText(
                f'<html><head/><body><p><span style=" font-size:29pt;">player#Tag<p'
                f'>Account Level 0 | Iron 3 </span><img src="{tier_icon}"width="32 '
                f'"height="32"/><span style=" font-size:20pt;"> 0rr</span></p></body></html>'
            )
            self.MatchInformations.setText(
                "Match ID<br>"
                "Date - Match Duration<br>"
                "region - Cluster<br>"
                "Gamemode - Map"
            )
            self.accuarcy_text.setText(
                "Headshots: 0%<br>" "Bodyshots: 0%<br>" "Legshots: 0%"
            )
            self.accuracy_logo.setPixmap(QtGui.QPixmap(str(basic_dummy)))
            self.stats_text.setText(
                "K/D: 0.00<br>"
                "Average Combat Score: 0<br>"
                "Average Damage per Round: 0<br>"
                "Winrate: 0%"
            )
            self.home_error.setText(f"")
            self.match_error.setText(f"")
            self.comp_history.setText(
                "Matchmaking Ratio <br>"
                "Competitive Wins <br>"
                "Competitive Games played <br>"
                "Previous Ranks <br>"
                "rank history<br>"
                ""
            )
            self.history.setText(
                "<html><head/><body>"
                "Day, Date, Time<br>"
                "Match ID<br>"
                "region - Cluster<br>"
                f"Map | Mode | Agent: <img src='{Path(__file__).parent.joinpath(f"Images/Agents/Jett.png")}' width='23' height='23'/> Jett<br>"
                "0-0 WON<br>"
                "Kills Assists Deaths | 0.00 K/D<br>"
                "HS%: 0% | ACS: 0 | ADR: 0 | Total Score: 0<br>"
                "</body></html>"
            )
            self.update_loading_bar(100)  # Update loading bar to 100%

        except Exception as error:
            logging.error(f"Error resetting information: {traceback.format_exc()}")
            self.update_loading_bar(0)  # Reset loading bar on error

    def modeSwitch(self) -> None:
        """
        Switch between light and dark mode.
        """
        LightMode = Path(__file__).parent.joinpath("Images\\LightMode.webp")
        DarkMode = Path(__file__).parent.joinpath("Images\\DarkMode.webp")
        if self.dark_mode:
            self.dark_mode = False
            self.mode_switcher.setIcon(QtGui.QIcon(str(LightMode)))
            QApplication.setPalette(QApplication.style().standardPalette())
        else:
            self.dark_mode = True
            self.mode_switcher.setIcon(QtGui.QIcon(str(DarkMode)))
            dark_palette = QPalette()
            dark_palette.setColor(
                QPalette.Window,
                QColor("#111823"),
            )
            dark_palette.setColor(
                QPalette.WindowText,
                Qt.white,
            )
            dark_palette.setColor(
                QPalette.Base,
                QColor("#111823"),
            )
            dark_palette.setColor(
                QPalette.AlternateBase,
                QColor("#111823"),
            )
            dark_palette.setColor(
                QPalette.ToolTipBase,
                QColor("#111823"),
            )
            dark_palette.setColor(
                QPalette.ToolTipText,
                Qt.white,
            )
            dark_palette.setColor(
                QPalette.Text,
                Qt.white,
            )
            dark_palette.setColor(
                QPalette.Button,
                QColor("#111823"),
            )
            dark_palette.setColor(
                QPalette.ButtonText,
                Qt.white,
            )
            dark_palette.setColor(
                QPalette.BrightText,
                Qt.red,
            )
            dark_palette.setColor(
                QPalette.Link,
                QColor("#111823"),
            )
            dark_palette.setColor(
                QPalette.Highlight,
                QColor("#111823"),
            )
            dark_palette.setColor(
                QPalette.HighlightedText,
                QColor("#616161"),
            )
            dark_palette.setColor(
                QPalette.Active,
                QPalette.Button,
                QColor("#111823"),
            )
            dark_palette.setColor(
                QPalette.Disabled,
                QPalette.ButtonText,
                Qt.darkGray,
            )
            dark_palette.setColor(
                QPalette.Disabled,
                QPalette.WindowText,
                Qt.darkGray,
            )
            dark_palette.setColor(
                QPalette.Disabled,
                QPalette.Text,
                Qt.darkGray,
            )
            dark_palette.setColor(
                QPalette.Disabled,
                QPalette.Light,
                QColor("#111823"),
            )
            QApplication.setPalette(dark_palette)


async def main() -> None:
    """
    Main function to run the application.
    """
    download_agent_images()  # Download agent images once at the start
    app = QtWidgets.QApplication(sys.argv)
    valtracker = QtWidgets.QMainWindow()
    ui = Ui_ValorantTrackerByNavisGames()

    try:
        await ui.setupUi(valtracker)
    except Exception as e:
        logging.error(f"Error setting up UI: {e}")
        return

    QApplication.setStyle("Fusion")
    valtracker.show()

    try:
        sys.exit(app.exec_())
    except Exception as e:
        logging.error(f"Error running application: {e}")


if __name__ == "__main__":
    asyncio.run(main())
    asyncio.run(main())
