# encoding: utf-8

import sys
from workflow import Workflow, ICON_WEB, web


reload(sys)
sys.setdefaultencoding('utf8')


def get_recent_sites():
    """Retrieve recent sites from daohang

    Returns a list of sites dictionaries.

    """

    url = "http://127.0.0.1:8008/datas/"

    r = web.get(url)

    # throw an error if request failed
    # Workflow will catch this and show it to the user
    r.raise_for_status()

    # Parse the JSON returned by daohang
    sites = {}
    sites['items'] = []
    for site in r.json():
        if site['list']:
            for dh in site['list']:
                sites['items'].append(
                    {'full-title': "%s - %s" % (site['title'], dh['title']),
                     'title': dh['title'],
                     'desc': dh['desc'],
                     'href': dh['href'],
                     'keywords': " ".join([site['title'], dh['title'], dh['desc'], dh['href']])})
    return sites


def search_key_for_site(keyword):
    """Generate a string search key for a site"""
    elements = {}
    elements['items'] = []

    sites = get_recent_sites()

    for site in sites['items']:
        if keyword in site['keywords'].lower() or keyword in site['keywords']:
            elements['items'].append(site)
        else:
            pass

    return elements


def main(wf):

    # Get query from Alfred
    if len(wf.args):
        query = wf.args[0]
    else:
        query = None

    # Retrieve sites from cache if available and no more than 600
    # seconds old
    sites = wf.cached_data('sites', get_recent_sites, max_age=600)

    # If script was passed a query, use it to filter sites
    if query:
        sites = search_key_for_site(query)

    # Loop through the returned sites and add an item for each to if sites  null
    if not sites['items']:
        wf.add_item(title='无匹配项',
                    subtitle='',
                    valid=True
                    )

    # Loop through the returned sites and add an item for each to if sites not null
    # the list of results for Alfred
    for site in sites['items']:
        wf.add_item(title=site['full-title'],
                    subtitle="%s - %s" % (site['desc'], site['href']),
                    arg=query,
                    valid=True)

    # Send the results to Alfred as XML
    wf.send_feedback()


if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))
