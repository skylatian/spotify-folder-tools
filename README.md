# Spotify Folder Tools


> This project aims to use Spotify's Internal Api to automate organizing playlists into folders.


Folder IDs can be retrieved by dragging+dropping one into a plain text editor or terminal

![drag+drop](./images/terminal_drag_drop.gif)
These folder IDs are the same as the "group" IDs in the private API

enter venv: `source .venv/bin/activate`
exit evenv: `deactivate`


future plan:
- check for existed cached credentials - if they exist, use them
- attempt to make simple call with prior credentials. if call fails, get new credentials
- if call succeeds, move on.

> [!CAUTION]
> This project is not associated with Spotify in any manner, and may break at any time. Use at your own risk.