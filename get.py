"""
This code is for retrieving different things

author: Teddy Tortorici
"""

import sys
import os
import getpass


def google_drive() -> str:
    """locates the remote google drive folder on your machine"""
    user = getpass.getuser()
    if sys.platform == "darwin":    # for mac users
        path = f"/Volumes/GoogleDrive"
    elif sys.platform == "linux":
        path = f"/home/{user}/Documents/Google\\ Drive"
    else:   # if it's not linux or mac it's probably windows
        if os.name == 'nt':     # just double checking that it's windows
            if user == 'etcto':
                path = f"D:\\Google Drive\\My Drive"
            else:
                path = "G:\\My Drive"
        else:
            path = ""
    return path


gpib_address = {"LS": 13,
                "SCOPE": 10,
                "VS": 4}

port = 62538
