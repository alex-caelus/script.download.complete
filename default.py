import xbmc, xbmcgui, xbmcplugin
import os
import shutil


whitelistfilename = os.path.dirname(__file__) + "/resources/whitelist.txt"
sourcefolder = xbmcplugin.getSetting(int(sys.argv[1]), "sourcefolder")

class Item:
    """
    Encapsules a item that should be handled
    """
    def __init__(self, name):
        self.name = name
        self.fullpath = sourcefolder  + name

def GetWhitelist():
    try:
        return [i.strip() for i in open(whitelistfilename).readlines()]
    except IOError:
        print("Could not read whitelist: " + whitelistfilename)
        #the whitelist file has not yet been created
        return []
        
def GetUnhandledItems():
    whitelist = GetWhitelist()
    return [Item(i) for i in os.listdir(sourcefolder) if i not in whitelist]
    
def UpdateMediaLibrary():
    update = xbmcplugin.getSetting(int(sys.argv[1]), "update") == "true"
    if update:
        xbmc.executebuiltin('UpdateLibrary(video)')
    
def moveorcopy(item, destination):
    copy = xbmcplugin.getSetting(int(sys.argv[1]), "copy") == "true"
    p = xbmcgui.DialogProgress()
    
    try:
        if copy:
            p.create("Copying file/directory!")
            p.update(0, "working...")
            if os.path.isdir(item.fullpath):
                shutil.copytree(item.fullpath, destination+item.name)
            else:
                shutil.copy2(item.fullpath, destination)
            #we should ignore this in the future
            ActionIgnore(item)
        else:
            p.create("Moving file/directory!")
            p.update(0, "working...")
            shutil.move(item.fullpath, destination)
    except (IOError, OSError) as e:
        print("Exception while transfering files")
        xbmcgui.Dialog().ok("Error occured", "The transfer could not be completed!\nError was:\n" + str(e))
        raise e
    p.close()
    
    UpdateMediaLibrary()
    
def ActionPostpone(item):
    pass
    
def ActionIgnore(item):
    try:
        with open(whitelistfilename, "a") as myfile:
            myfile.write(item.name+"\n")
    except IOError as e:
        xbmcgui.Dialog().ok("Error occured", "The ignore operation failed!\nError was:\n" + str(e))
        raise e
        
    
def ActionMovie(item):
    destinationfolder = xbmcplugin.getSetting(int(sys.argv[1]), "moviefolder")
    moveorcopy(item, destinationfolder)
    
def ActionTvSeries(item):
    destinationfolder = xbmcplugin.getSetting(int(sys.argv[1]), "tvfolder")
    currentdir = ""
    
    choices = ["# Go up", "# Put file/directory here"]
    
    choice = -1
    while True:
        if len(currentdir) == 0:
            choices[0] = "# Abort"
        else:
            choices[0] = "# Go up"
        series = [i for i in os.listdir(destinationfolder+currentdir)]
        choice = xbmcgui.Dialog().select('Put "' + item.name + '" in TV-Series/'+currentdir, choices+series)
        if choice is 0:
            if len(currentdir) == 0:
                return
            else:
                currentdir = ""
        elif choice is 1:
            moveorcopy(item, destinationfolder+currentdir)
            return
        else:
            currentdir += series[choice-2] + "/"
            
    print(path)
    
def HandleItem(item):
    actions = [ActionPostpone, ActionIgnore, ActionMovie, ActionTvSeries]
    descriptions = ["Ask me again later (postpone choice)", "Ignore (leave it in downloads folder)", "Move to Movie library", "Move to TV-Series library"]
    
    #Get choice form user
    ret = xbmcgui.Dialog().select(item.name, descriptions)
    
    #do the action
    actions[ret](item)
        
    
def HandleAllRemaining():
    items = GetUnhandledItems()
    
    if items is None:
        return
        
    if len(items) == 0:
        xbmcgui.Dialog().ok("Nothing to do", "No recently downloaded files found!")
        return
    
    for item in items:
        HandleItem(item)
    
    
#start
HandleAllRemaining()