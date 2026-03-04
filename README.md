# DB manager
This is a small program I've written to manage json databases regarding anime, mangas and movies.

## How to make it work?
1. Extract the folder 
2. Update the MovieToken and FolderPath inside the config.json
3. Add the .exe to the system PATH (optional)

## Deleted my config file, now what?
Create a new one and copy the template below

```json
{
  "MovieTOKEN" : "YOUR_TMDB_MOVIE_TOKEN",
  "folderPath" :  "DESIRED PATH, MAKE SURE TO PUT THE FULL PATH"
}
```
## Wanna compile by myself!
Use [pyInstaller](https://pyinstaller.org/en/stable/usage.html).

## FAQ:
### Why python?
Easy to read and mantain.

### Why use this instead of Letterboxd or similar?
This approach lets you **own** your data. Therefore, if letterboxd goes down or another service becomes more popular it won't affect you.

### Will this pogram receive any major update?
Probably not.

### Roadmap
- [X] Code optimaztion (pandas, mainly)
- [X] Add editing mode 
- [ ] Add delete mode