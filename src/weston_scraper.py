import argparse
import sys
import datetime
from data_manager import AlbumDataManager
from data_manager import AlbumDataManagerError
from parser import AlbumParser
from parser import AlbumParserError


CODE_OK = 0
CODE_ERROR_DAO = 3
CODE_ERROR_PARSER = 4


def get_args():
    parser = argparse.ArgumentParser(description='Scraps album and track' \
        + 'data from WestOneMusic.com and stores it in a MongoDB')
    required = parser.add_argument_group('required arguments')
    required.add_argument("-db_name", help="Name of the Mongo database", required=True)
    parser.add_argument("-host", default="localhost", \
        help="Host to be used for the Mongo Connection, default: localhost")
    parser.add_argument("-port", default="27017", \
        help="Port to be used for the Mongo Connection, default: 27017")
    parser.add_argument("-user", default="", \
        help="User to be used for the Mongo Connection, default: '' ")
    parser.add_argument("-password", default="", \
        help="Password to be used for the Mongo Connection, default: '' ")
    args = parser.parse_args()
    return args


def print_stats(data_manager, parser, total_time):
    print str(data_manager.nb_created_albums) + " created albums"
    print str(data_manager.nb_updated_albums) + " updated albums"
    print str(data_manager.nb_created_tracks) + " created tracks"
    print str(data_manager.nb_updated_tracks) + " updated tracks"
    print str(parser.NB_HTTP_REQUEST) + " HTTP REQUESTS"
    print total_time, " total time"


def main():
    start_time = datetime.datetime.now().replace(microsecond=0)
    args = get_args()
    try:
        data_manager = AlbumDataManager(
            args.db_name, args.host, args.port,
            args.user, args.password)
        parser = AlbumParser()
        for album in parser.parse():
            data_manager.upsert(album)
        end_time = datetime.datetime.now().replace(microsecond=0)
        print_stats(data_manager, parser, end_time - start_time)
    except AlbumDataManagerError as e:
        # logger.error("Error when accessing data: {0}".format(e))
        return CODE_ERROR_DAO
    except AlbumParserError as e:
        # logger.error("Error when parsing: {0}".format(e))
        return CODE_ERROR_PARSER
    return CODE_OK


if __name__ == "__main__":
    sys.exit(main())
