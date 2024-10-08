import glob
import json
from pathlib import Path
import re
import shutil
import zipfile

def findEncoreRoot(listf):
    for path in listf:
        if 'info.json' in path:
            return Path(path).parent
        
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
            encoreRoot = str(findEncoreRoot(file_list))

            diffs = {}
            artist = None
            title = None
            album = None
            charters = []
            length = 0

            isRootFirstDir = encoreRoot == '.'
            readableRoot = '' if isRootFirstDir else encoreRoot + '/'
            cover = None

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
                    "root": encoreRoot,
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
