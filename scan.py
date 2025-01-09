import glob
import json
from pathlib import Path
import re
import shutil
import zipfile
import configparser

def findEncoreRoot(listf):
    for path in listf:
        if 'info.json' in path:
            return (Path(path).parent, 0)
        elif 'song.ini' in path:
            return (Path(path).parent, 1)
        
db = {
    "encore": True,
    "RAW_path": "https://raw.githubusercontent.com/Encore-Developers/songs/main/",
    "songs": []
}

def saveScan(data, fpath = 'encore.json'):
    open(fpath, 'w').write(json.dumps(data, indent=4))

def scan():
    zips = glob.glob('Songs/*.zip')
    #print(zips)

    try:
        shutil.rmtree('covers/')
    except Exception as e:
        print('Covers folder does not exist!', e)

    for zipa in zips:

        with zipfile.ZipFile(zipa, "r") as zip_ref:
            file_list = zip_ref.namelist()
            encoreRoot, fileFormat = findEncoreRoot(file_list)
            encoreRt = str(encoreRoot)

            diffs = {}
            artist = None
            title = None
            album = None
            charters = []
            length = 0

            isRootFirstDir = encoreRt == '.'
            readableRoot = '' if isRootFirstDir else encoreRt + '/'
            cover = None

            if fileFormat == 1:
                with zip_ref.open(readableRoot + 'song.ini') as info:
                    infod = configparser.ConfigParser()
                    infotext = info.read().decode('utf-8')
                    infod.read_string(infotext)

                    artist = infod.get('song', 'artist')
                    title = infod.get('song', 'name')
                    diffs = {
                        "drums": infod.getint('song', 'diff_drums_pad', fallback=-1),
                        "bass": infod.getint('song', 'diff_bass_pad', fallback=-1),
                        "guitar": infod.getint('song', 'diff_guitar_pad', fallback=-1),
                        "vocals": infod.getint('song', 'diff_vocals_pad', fallback=-1),
                        "plastic_drums": infod.getint('song', 'diff_drums', fallback=-1),
                        "plastic_bass": infod.getint('song', 'diff_bass', fallback=-1),
                        "plastic_guitar": infod.getint('song', 'diff_guitar', fallback=-1),
                        "pitched_vocals": infod.getint('song', 'diff_vocals', fallback=-1),
                    }
                    charters = [infod.get('song', 'charter')]
                    length = int(infod.getint('song', 'song_length') / 1000)
                    album = infod.get('song', 'album')
                    
                    if 'album.png' in zip_ref.namelist():
                        albumfile = 'album.png'
                    else:
                        albumfile = 'album.jpg'

                    cover = albumfile
            else:
                with zip_ref.open(readableRoot + 'info.json') as info:
                    infod = json.load(info)

                    artist = infod['artist']
                    title = infod['title']
                    diffs = infod['diff']
                    charters = infod.get('charters', [])
                    length = infod.get('length', 0)
                    album = infod.get('album', None)
                    cover = infod['art']
                    #print(infod)
            

            songid = re.sub('-+', '-', re.sub('[^a-zA-Z0-9]', '-', f'{artist.replace(' ', '-')}-{title.replace(' ', '-')}'.lower())).rstrip('-')

            with zip_ref.open(readableRoot + cover) as coverart:
                Path('covers/').mkdir(exist_ok=True)
                Path('covers/'+songid + '/').mkdir(exist_ok=True)
                with open('covers/' + songid + '/' + cover, 'wb') as coverwrite:
                    coverwrite.write(coverart.read())

            #print(file_list)
            db['songs'].append(
                {
                    "zip": zipa.replace('Songs\\', '').replace('Songs/', ''),
                    "root": encoreRt,
                    "isRootFirstDir": isRootFirstDir,
                    "artist": artist,
                    "title": title,
                    "album": album,
                    "diffs": diffs,
                    "charters": charters,
                    "secs": length,
                    "id": songid,
                    "art": cover
                })
            
    saveScan(db)

if __name__ == "__main__":
    scan()