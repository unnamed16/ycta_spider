__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/05/30'

import argparse
import os
from enum import Enum

from ycta_spider import adapter
from ycta_spider.api import build
from ycta_spider.api.shell import PlatformType

INFO = 'info'
CRAWL = 'crawl'
HIGHLIGHT = 'highlight'
RESPOND = 'respond'

PLATFORM = 'platform'

LIMIT = '--limit'
LIMIT_SHORT = '-l'

OUTPUT = '--output'
OUTPUT_SHORT = '-o'


class UriType(Enum):
    STDIO = 's'
    FILE = 'f'
    DIRECTORY = 'd'
    URL = 'u'


def get_uri_type(uri: str) -> UriType:
    if uri is None:
        return UriType.STDIO
    if os.path.isfile(uri):
        return UriType.FILE
    if os.path.isdir(uri):
        return UriType.DIRECTORY
    if os.path.islink(uri):
        return UriType.URL
    if uri.startswith('http') or uri.startswith('ssh'):
        return UriType.URL
    if os.path.splitext(uri)[1] == '':
        return UriType.DIRECTORY
    return UriType.FILE


def get_uri_message(uri: str) -> str:
    if uri is None:
        return "stdio"
    return "current work directory" if (uri == "" or uri == ".") else ("'" + uri + "'")


def cli() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", help="", required=True)

    info = subparsers.add_parser(
        INFO,
        help="download sources information from the specified platform")
    info.add_argument(
        PLATFORM,
        help="platform that has to be processed")
    info.add_argument(
        LIMIT_SHORT,
        LIMIT,
        type=int,
        help="limit of the records obtained per source, update infinitely on Enter key if not specified.")
    info.add_argument(
        OUTPUT_SHORT,
        OUTPUT,
        type=str,
        default=None,
        help="where to store the result (url - send, file - save, print if not specified)")

    crawl = subparsers.add_parser(
        CRAWL,
        help="download comments from the specified platform")
    crawl.add_argument(
        PLATFORM,
        help="platform that has to be processed")
    crawl.add_argument(
        LIMIT_SHORT,
        LIMIT,
        type=int,
        help="limit of the records obtained per source, update infinitely on Enter key if not specified.")
    crawl.add_argument(
        OUTPUT_SHORT,
        OUTPUT,
        type=str,
        default=None,
        help="where to store the result (url - send, file - save, print if not specified)")

    highlight = subparsers.add_parser(
        HIGHLIGHT,
        help="download highlighted comments from the specified platform")
    highlight.add_argument(
        PLATFORM,
        help="platform that has to be processed")
    highlight.add_argument(
        LIMIT_SHORT,
        LIMIT,
        type=int,
        help="limit of the records obtained per source, update infinitely on Enter key if not specified.")
    highlight.add_argument(
        OUTPUT_SHORT,
        OUTPUT,
        type=str,
        default=None,
        help="where to store the result (url - send, file - save, print if not specified)")

    respond = subparsers.add_parser(
        RESPOND,
        help="respond highlighted comments")
    respond.add_argument(
        LIMIT_SHORT,
        LIMIT,
        type=int,
        help="limit of the processed highlighted records per source, work infinitely if not specified.")
    respond.add_argument(
        OUTPUT_SHORT,
        OUTPUT,
        type=str,
        default=None,
        help="where to store the result (url - send, file - save, print if not specified)")

    args = parser.parse_args()
    if args.command == INFO:
        __try_info(args.platform, args.limit, args.output, args)
    elif args.command == CRAWL:
        __try_crawl(args.platform, args.limit, args.output, args)
    elif args.command == HIGHLIGHT:
        __try_highlight(args.platform, args.limit, args.output, args)
    elif args.command == RESPOND:
        __try_respond(args.platform, args.limit, args.output, args)


def __try_info(platform_name: str, limit: int, output: str, args: argparse.Namespace) -> None:
    if not __check_platform(platform_name):
        return
    output_message = get_uri_message(output)
    uri_type = get_uri_type(output)
    if uri_type == UriType.STDIO:
        print(f'Print source info from {platform_name}')
        adapter.print_info(
            build.shell(PlatformType[platform_name]).get_sources_info(limit=limit),
            manual_control=limit is None
        )
    elif uri_type == UriType.FILE:
        print(f'Save source info from {platform_name} to {output_message}')
        adapter.save_info(
            build.shell(PlatformType[platform_name]).get_sources_info(limit=limit),
            output
        )
    elif uri_type == UriType.DIRECTORY:
        print(f'Unsupportable option: save info to the folder {output_message}')
    elif uri_type == UriType.URL:
        print(f'Send source info from {platform_name} to {output_message}')
        print("Arguments combination is not yet supported: " + str(args))


def __try_crawl(platform_name: str, limit: int, output: str, args: argparse.Namespace) -> None:
    if not __check_platform(platform_name):
        return
    output_message = get_uri_message(output)
    limit_message = "all" if limit is None else limit
    uri_type = get_uri_type(output)
    if uri_type == UriType.STDIO:
        print(f'Print {limit_message} comments per source from {platform_name}')
        adapter.print_comments(
            build.shell(PlatformType[platform_name]).get_comments_from_several_sources(limit=limit),
            manual_control=limit is None
        )
    elif uri_type == UriType.FILE:
        print(f'Save {limit_message} comments per source from {platform_name} to {output_message}')
        adapter.save_comments(
            build.shell(PlatformType[platform_name]).get_comments_from_several_sources(limit=limit),
            output
        )
    elif uri_type == UriType.DIRECTORY:
        print(f'Unsupportable option: save comments to the folder {output_message}')
    elif uri_type == UriType.URL:
        print(f'Send {limit_message} comments per source from {platform_name} to {output_message}')
        print("Arguments combination is not yet supported: " + str(args))


def __try_highlight(platform_name: str, limit: int, output: str, args: argparse.Namespace) -> None:
    if not __check_platform(platform_name):
        return
    output_message = get_uri_message(output)
    limit_message = "all" if limit is None else limit
    uri_type = get_uri_type(output)
    if uri_type == UriType.STDIO:
        print(f'Print {limit_message} highlighted comments per source from {platform_name}')
        print("Arguments combination is not yet supported: " + str(args))
    elif uri_type == UriType.FILE:
        print(f'Save {limit_message} highlighted comments per source from {platform_name} to {output_message}')
        print("Arguments combination is not yet supported: " + str(args))
    elif uri_type == UriType.DIRECTORY:
        print(f'Unsupportable option: save highlighted comments to the folder {output_message}')
    elif uri_type == UriType.URL:
        print(f'Send {limit_message} highlighted comments per source from {platform_name} to {output_message}')
        print("Arguments combination is not yet supported: " + str(args))


def __try_respond(platform_name: str, limit: int, output: str, args: argparse.Namespace) -> None:
    if not __check_platform(platform_name):
        return
    output_message = get_uri_message(output)
    limit_message = "all" if limit is None else limit
    uri_type = get_uri_type(output)
    if uri_type == UriType.STDIO:
        print(f'Print {limit_message} responded comments per source from {platform_name}')
        print("Arguments combination is not yet supported: " + str(args))
    elif uri_type == UriType.FILE:
        print(f'Save {limit_message} responded comments per source from {platform_name} to {output_message}')
        print("Arguments combination is not yet supported: " + str(args))
    elif uri_type == UriType.DIRECTORY:
        print(f'Unsupportable option: save responded comments to the folder {output_message}')
    elif uri_type == UriType.URL:
        print(f'Send {limit_message} responded comments per source from {platform_name} to {output_message}')
        print("Arguments combination is not yet supported: " + str(args))


def __check_platform(platform_name: str) -> bool:
    if getattr(PlatformType, platform_name, None) is None:
        print("Unsupported platform '" + platform_name + "'")
        print("Available values: " + str([s.value for s in PlatformType]))
        return False
    return True


if __name__ == "__main__":
    cli()
