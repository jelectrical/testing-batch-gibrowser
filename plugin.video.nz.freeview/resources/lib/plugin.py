from matthuisman import plugin, settings, inputstream
from matthuisman.session import Session
from matthuisman.language import _

from .constants import M3U8_URL

@plugin.route('')
def home(**kwargs):
    folder = plugin.Folder()

    channels = get_channels()
    for slug in sorted(channels, key=lambda k: channels[k].get('channel', channels[k]['name'])):
        channel = channels[slug]

        folder.add_item(
            label    = channel['name'],
            path     = plugin.url_for(play, slug=slug, _is_live=True),
            info     = {'plot': channel.get('description')},
            video    = channel.get('video', {}),
            audio    = channel.get('audio', {}),
            art      = {'thumb': channel.get('logo')},
            playable = True,
        )

    folder.add_item(label=_.SETTINGS,  path=plugin.url_for(plugin.ROUTE_SETTINGS))

    return folder

@plugin.route()
def play(slug, **kwargs):
    channel = get_channels()[slug]

    item = plugin.Item(
        path     = channel['master_url'],
        headers  = channel['headers'],
        info     = {'plot': channel.get('description')},
        video    = channel.get('video', {}),
        audio    = channel.get('audio', {}),
        art      = {'thumb': channel.get('logo')},
    )
    
    if channel.get('hls', False) and settings.getBool('use_ia_hls', False):
        item.inputstream = inputstream.HLS()

    return item

def get_channels():
    return Session().get(M3U8_URL).json()

@plugin.route()
@plugin.merge()
def playlist(output, **kwargs):
    channels = get_channels()

    with open(output, 'wb') as f:
        f.write('#EXTM3U\n')

        for slug in sorted(channels, key=lambda k: channels[k].get('channel', channels[k]['name'])):
            channel = channels[slug]

            f.write('#EXTINF:-1 tvg-id="{id}" tvg-chno="{chno}" tvg-logo="{logo}",{name}\n{path}\n'.format(
                id=slug, logo=channel.get('logo', '').encode('utf8'), name=channel['name'].encode('utf8'), chno=channel.get('channel', ''), 
                    path=plugin.url_for(play, slug=slug, _is_live=True)))