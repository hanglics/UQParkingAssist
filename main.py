from uq_feed_helper import *


def main():
    feedContent = getUQFeed()
    parseFeed(feedContent)


if __name__ == '__main__':
    main()
