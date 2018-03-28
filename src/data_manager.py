import json
import pymongo
from pymongo import MongoClient


class AlbumDataManagerError(LookupError):
    pass

class AlbumDataManager:

    def __init__(self, args_db_name, args_host, args_port, args_user, args_password):
        self.nb_created_albums = 0
        self.nb_updated_albums = 0
        self.nb_created_tracks = 0
        self.nb_updated_tracks = 0
        user_password = ''
        if args_user and args_password:
            user_password = args_user + ":" + args_password + "@"
        try:
            client = MongoClient(
                'mongodb://{}{}:{}/'.format(user_password, args_host, args_port))
            self.db = client[args_db_name]
            client.server_info() # raises exception is connection doesnt't work
        except pymongo.errors.PyMongoError as e: # catches all pymongo errors
            raise AlbumDataManagerError(e)


    def upsert(self, Album):
        self.upsert_tracks(Album.tracks, Album.cat_no)
        Album.tracks = None
        self.upsert_album(Album)

    def upsert_album(self, album_json):
        album_json = json.loads(album_json.toJSON())
        del album_json['tracks']
        album_json["_id"] = album_json['cat_no']
        try:
            res = self.db.albums.find({"_id": album_json["_id"]})
            if res.count == 0:
                self.db.albums.insert(album_json)
                self.nb_created_albums += 1
            else:
                self.db.albums.update({"_id": album_json["_id"]}, album_json, True)
                self.nb_updated_albums += 1
        except pymongo.errors.PyMongoError as e:   # catch all pymongo errors
            raise AlbumDataManagerError(e)


    def upsert_tracks(self, tracks_json, album_reference):
        for track in tracks_json:
            track = json.loads(track.toJSON())
            track['_id'] = album_reference + "-" + track['no']
            try:
                res = self.db.albums.find({"_id": track['_id']})
                if res.count == 0:
                    self.db.tracks.insert(track)
                    self.nb_created_tracks += 1
                else:
                    self.db.tracks.update({"_id": track['_id']}, track, True)
                    self.nb_updated_tracks += 1
            except pymongo.errors.PyMongoError as e:   # catch all pymongo errors
                raise AlbumDataManagerError(e)
