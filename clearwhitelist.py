import os
import xbmcgui

whitelistfilename = os.path.dirname(__file__) + "/resources/whitelist.txt"

os.remove(whitelistfilename)

xbmcgui.Dialog().ok("Done", "Successfully cleared the whitelist!")