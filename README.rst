Python RedTube API Client
=========================

Here we go! I'd like to present simple module to access `RedTube API <http://api.redtube.com/>`_. That API has a few
methods to access their video library with external clients (such as this small piece of code). Only read access is
provided at this moment.

So, I'll show you one small example, how to use this cool library::

    from redtube import RedClient

    red = RedClient()
    # Getting top of the top... I think so :)
    collection = red.search()
    # Search method provides list like object of type RedCollection with video entries of type RedVideo.
    print type(collection)
    # You can show you total videos for current search and current page
    print collection.total, collection.page

    # Let's search banana, it's good choice for this search engine
    collection = red.search(query='banana', page=2)
    # As you can see, we can access next page by page parameter
    # Also you can access next page by calling next method from RedCollection instance
    collection = red.next()

    # You can access video entries by their internal ID
    first = red.by_id('1')
    # Or by some syntax sugar:
    first = red[1]
    print first # <RedVideo[1] "Heather taking it deep again">

    # RedVideo entries has many useful information about video, ie:
    print first.title, first.duration, first.url, first.player_url, first.embed
    # As you can see, we can access video streaming url for this client or generate video embed code

    # Also you can retrieve tag, category or star lists provided by RedTube
    categories, tags, stars = red.categories, red.tags, red.stars
    # This methods has internal cache, so you will do only one HTTP request for multi calls.

That's all, guys! Have a nice day!
