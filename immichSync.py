from requests_toolbelt.multipart.encoder import MultipartEncoder
import httpx
from pprint import pprint
import time
from pathlib import Path
import os
import json
import requests
from PIL import Image
import io


def httpGetJson(url, key):
    
    print(url)
    code = 0
    http = httpx.Client()
    
    try:
        resp = http.get(
                    url,
                    headers = {'x-api-key': key}
                )
        code = 200
    except httpx.HTTPError as exc:
        print(f"HTTP Exception for {exc.request.url} - {exc}")

   
    # except httpx.ReadError.request as e:
    #     if not hasattr(e, "code"):
    #         print(e)
    #         code = -1
    #     else:
    #         code = e.coderint

    return resp.json()
    

def httpGetFile(url, key, path):
    
    print(url)
    code = 0
    http = httpx.Client()
    
    try:
        resp = http.get(
                    url,
                    headers = {'x-api-key': key}
                )
        code = 200
    except httpx.HTTPError as exc:
        print(f"HTTP Exception for {exc.request.url} - {exc}")

    
    # except httpx.ReadError.request as e:
    #     if not hasattr(e, "code"):
    #         print(e)
    #         code = -1
    #     else:
    #         code = e.coderint
    

    with open(path, 'wb') as f:
        f.write(resp.content)
    
def exists(path):
    
    print(path)
    if(os.path.exists(path)):
        return True
    return False

def getAllAlbums(serviceData):

    key = serviceData["immich"]["key"]
    baseUrl = f'{serviceData["immich"]["url"]}/albums'
    albums = httpGetJson(baseUrl, key)
    return albums

def getAlbumInfo(id, serviceData):

    key = serviceData["immich"]["key"]
    baseUrl = f'{serviceData["immich"]["url"]}/albums/{id}'

    albumInfo = httpGetJson(baseUrl, key)
    return albumInfo

# def downloadAssets(albumInfo, baseUrl, creds):
#     key = creds["immichKey"]
#     albumName = albumInfo["albumName"]
#     print(albumName)

#     for asset in albumInfo["assets"]:
#         id = asset["id"]
    
#         url = f'{baseUrl}/assets/{id}/original'

#         fileExtension = asset["originalFileName"].split(".")[-1]


#         path = f'photos/{albumName}'
#         Path(path).mkdir(parents=True, exist_ok=True)

#         path = f'photos/{albumName}/{id}.{fileExtension}'
#         if not exists(path):
#             httpGetFile(url, key, path)
#             print(f'downloaded {id}')  
#         else:
#             print("File alread exists")

    



#     # if httpGetFile(url, key, path) == 200:
#     #     return True
#     # else:
#     #     return False
    
def printAlbums(albums):
    print("index   Name")
    index = 0
    for album in albums:
        print(f'{index}\t{album["albumName"]}')
        index+=1

## create and empty file if it does not exist
def initState(file):
    if os.path.isfile(file):
        with open(file) as f:
            return json.load(f)
    else: ## create empty file
        open(file, 'a').close()
        return {}


def updateImmichState(state, albumInfo, serviceData):
    baseImmichUrl = serviceData["immich"]["url"]
    
    albumName = albumInfo["albumName"]


    if albumName not in state:
        print("album not found in state, initializing it...")
        state[albumName] = {}
    else:
        print("album found in state")

    for asset in albumInfo["assets"]:
        if asset["type"] == "IMAGE":
            if asset["id"] not in state[albumName]:
                print(f'asset {asset["id"]} not found in state, initializing it...')
                state[albumName][asset["id"]] = { "immich": {}}
                                                 
            state[albumName][asset["id"]]["immich"] = {
                        "id": asset["id"],
                        "type": asset["type"],
                        'exif': { 
                            'description': asset['exifInfo']["description"],
                            "lat": asset['exifInfo']["latitude"],
                            "lon": asset['exifInfo']["longitude"],
                            "dateTimeOriginal": asset['exifInfo']["dateTimeOriginal"] },
                        "resource": f"{baseImmichUrl}/assets/{asset['id']}/original",
                        # "resource": f"{baseImmichUrl}/assets/{asset['id']}/thumbnail",  ###  This is used to test with smaller files so that the download is not so slow.
                        "fileName": asset["originalFileName"]
                    }


    return state

def writeState(state, stateFile):
    with open(stateFile, 'w') as f:
        json.dump(state, f)

def resizeImage(data, maxSize=2500):
    image = Image.open(io.BytesIO(data))
    image.thumbnail((maxSize,maxSize), Image.ANTIALIAS)

    return image


def downloadAssetFromImmich(resourceUrl, fileName, serviceData):
    # upload to WP
    metadata = {}
    key = serviceData["immich"]["key"]

    # def wp_upload_image(domain, user, app_pass, imgPath):
    # filename = imgPath.split('/')[-1] if len(imgPath.split('/')[-1])>1 else imgPath.split('\\')[-1]
    extension = fileName[fileName.rfind('.')+1 : len(fileName)]
    print(f'DOWNLOADING - {resourceUrl}')
    
    immHttp = httpx.Client()
    try:
        immResp = immHttp.get(
                    resourceUrl,
                    headers = {'x-api-key': key}
                )
        code = 200
    except httpx.HTTPError as exc:
        print(f"HTTP Exception for {exc.request.url} - {exc}")

    # except httpx.ReadError.request as e:
    #     if not hasattr(e, "code"):
    #         print(e)
    #         code = -1
    #     else:
    #         code = e.coderint
        return None
    
    print("complete")

   


    with open("tempDownload.jpg", 'wb') as f:
        f.write(immResp.content)

    return immResp.content


def uploadToWordPress(image, assetData, serviceData):

    mem_file = io.BytesIO()
    image.save(mem_file, "jpeg", quality=90)
    mem_file.seek(0)

    fileName = assetData["immich"]["fileName"]
    auth = (serviceData["wordpress"]["user"], serviceData["wordpress"]["pass"])
    url = f'{serviceData["wordpress"]["url"]}/media'
    multipart_data = MultipartEncoder(
    fields={
        'file': (fileName, mem_file, 'image/jpg'),
        'caption': assetData["immich"]["exif"]["description"],
        #   'alt_text': 'a bunch of hermit crabs eating a coconut on the beach',
        #   'description': 'i dont have a description.'
      }
    )

    response = requests.post(url, data=multipart_data,
                         headers={'Content-Type': multipart_data.content_type},
                         auth=auth)

    if response.status_code in [200, 201]:
        return response.json()

    return None

def updateWordpressAssetMeta(assetData, serviceData):
    return None

## this will either upload the file with metadata, or update the metadata.
## it will not re-upload files, based on the state.json file.
def syncToWordPress(state, serviceData):

    for albumName in state:
        album = state[albumName]
        for assetId in album:
            if "wordpress" not in album[assetId]:

                # never uploaded, we need to upload it and save meta to state.
                image = downloadAssetFromImmich(album[assetId]["immich"]["resource"], 
                                  album[assetId]["immich"]["fileName"], 
                                  serviceData)
                image = resizeImage(image)
                wpAssetData = uploadToWordPress(image, album[assetId], serviceData)

                if wpAssetData is not None:
                    print("updating state")

                    if "wordpress" not in state[albumName][assetId]:
                        state[albumName][assetId]["wordpress"] = {}

                    state[albumName][assetId]["wordpress"]["id"] = int(wpAssetData["id"], )  ## Force to int as it is returning a weird type <class int>
                    state[albumName][assetId]["wordpress"]["caption"] = wpAssetData["caption"]["raw"]

                    writeState(state, serviceData["stateFile"])


                ## Todo - update metadata.  I am not sure whether this will reflect in images already in a gallery in a post.
                # else:
                #     updateWordpressAssetMeta(album[assetId], serviceData):
            else: 
                print(f'{albumName} - ...{assetId[-5:]} has already been uploaded, Syncing Metadata only. (Just kidding, this isn\'t implemented yet!)')




if __name__ == "__main__":


    with open(".env") as f:
        serviceData = json.load(f)

    state = initState(serviceData["stateFile"])

    albums = getAllAlbums(serviceData)

    printAlbums(albums)

    albumIndex = int(input("Which album would you like to download?  Select the index number: "))

    ## Todo: validate entry

    albumInfo = getAlbumInfo(albums[albumIndex]["id"], serviceData)

    state = updateImmichState(state, albumInfo, serviceData)
    writeState(state, serviceData["stateFile"])

    syncToWordPress(state, serviceData)

    


    

