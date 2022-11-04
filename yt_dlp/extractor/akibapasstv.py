from .common import InfoExtractor
from .vimeo import VHXEmbedIE
from ..utils import (
    ExtractorError,
    clean_html,
    get_element_by_class,
    get_element_by_id,
    get_elements_by_class,
    int_or_none,
    join_nonempty,
    unified_strdate,
    urlencode_postdata,
)


class AkibaPassTVIE(InfoExtractor):
    _LOGIN_URL = 'https://akibapasstv.vhx.tv/login'
    _NETRC_MACHINE = 'akibapasstv'

    _VALID_URL = r'https?://akibapasstv\.?vhx\.tv/(?:[^/]+/)*videos/(?P<id>[^/]+)/?$'
    _TESTS = [
        {
            'url': 'https://akibapasstv.vhx.tv/packages/shirobako-the-movie-omu/videos/shirobako-the-movie-omu',
            'note': 'Movie (no release date)',
            'md5': '',
            'info_dict': {
                'id': '2407779',
                'display_id': 'shirobako-the-movie-omu',
                'ext': 'mp4',
                'title': 'Shirobako - The Movie (OmU)',
                'description': 'md5:e4e8be4b547a057e61d39428053e5ef9',
                'thumbnail': 'https://vhx.imgix.net/akibapasstv/assets/1df8067e-d306-4ff7-8793-7c77f7c624a8.jpg',
                'duration': 7211,
                'uploader_id': 'peppermintanime',
                'uploader_url': 'https://vimeo.com/peppermintanime',
                'uploader': 'peppermint anime'
            },
            'expected_warnings': ['Ignoring subtitle tracks found in the HLS manifest']
        },
        {
            'url': 'https://akibapasstv.vhx.tv/packages/apan-03-11-2022/videos/akiba-raid-night-03-11-2022-catch-up',
            'note': 'Catch-Up Episode from live Event',
            'md5': '9d161927629295b7411a8ad07fb1c9f7',
            'info_dict': {
                'id': '2420668',
                'display_id': 'akiba-raid-night-03-11-2022-catch-up',
                'ext': 'mp4',
                'title': 'AKIBA RAID NIGHT - 03.11.2022 - Catch-up',
                'description': 'Erlebe brandneue Serien und beliebte Klassiker der Animewelt als linearen Event-Stream!',
                'thumbnail': 'https://vhx.imgix.net/akibapasstv/assets/b7882ba1-7731-4c41-8e13-b8d61b6d7d40.jpg',
                'duration': 20379,
                'uploader_id': 'peppermintanime',
                'uploader_url': 'https://vimeo.com/peppermintanime',
                'uploader': 'peppermint anime'
            },
            'expected_warnings': ['Ignoring subtitle tracks found in the HLS manifest']
        }
    ]

    def _get_authenticity_token(self, display_id):
        signin_page = self._download_webpage(
            self._LOGIN_URL, display_id, note='Getting authenticity token')
        return self._html_search_regex(
            r'name=["\']authenticity_token["\'] value=["\'](.+?)["\']',
            signin_page, 'authenticity_token')

    def _login(self, display_id):
        username, password = self._get_login_info()
        if not username:
            return True

        response = self._download_webpage(
            self._LOGIN_URL, display_id, note='Logging in', fatal=False,
            data=urlencode_postdata({
                'email': username,
                'password': password,
                'authenticity_token': self._get_authenticity_token(display_id),
                'utf8': True
            }))

        user_has_subscription = self._search_regex(
            r'user_has_subscription:\s*["\'](.+?)["\']', response, 'subscription status', default='none')
        if user_has_subscription.lower() == 'true':
            return
        elif user_has_subscription.lower() == 'false':
            return 'Account is not subscribed'
        else:
            return 'Incorrect username/password'

    def _real_extract(self, url):
        display_id = self._match_id(url)

        webpage = None
        if self._get_cookies('https://akibapasstv.vhx.tv').get('_session'):
            webpage = self._download_webpage(url, display_id)
        if not webpage or '<div id="watch-unauthorized"' in webpage:
            login_err = self._login(display_id)
            webpage = self._download_webpage(url, display_id)
            if login_err and '<div id="watch-unauthorized"' in webpage:
                if login_err is True:
                    self.raise_login_required(method='any')
                raise ExtractorError(login_err, expected=True)

        embed_url = self._search_regex(r'embed_url:\s*["\'](.+?)["\']', webpage, 'embed url')
        thumbnail = self._og_search_thumbnail(webpage)
        watch_info = get_element_by_id('watch-info', webpage) or ''

        title = clean_html(get_element_by_class('video-title', watch_info))
        season_episode = get_element_by_class(
            'site-font-secondary-color', get_element_by_class('text', watch_info))
        episode_number = int_or_none(self._search_regex(
            r'S[0-9]+E(\d+)', title or '', 'episode', default=None))

        return {
            '_type': 'url_transparent',
            'ie_key': VHXEmbedIE.ie_key(),
            'url': VHXEmbedIE._smuggle_referrer(embed_url, 'https://akibapasstv.vhx.tv'),
            'id': self._search_regex(r'embed\.vhx\.tv/videos/(.+?)\?', embed_url, 'id'),
            'display_id': display_id,
            'title': title,
            'description': self._html_search_meta('description', webpage, fatal=False),
            'thumbnail': thumbnail.split('?')[0] if thumbnail else None,  # Ignore crop/downscale
            'series': clean_html(get_element_by_class('series-title', watch_info)),
            'episode_number': episode_number,
            'episode': title if episode_number else None,
            'season_number': int_or_none(self._search_regex(
                r'Season (\d+),', season_episode or '', 'season', default=None)),
            'release_date': unified_strdate(self._search_regex(
                r'data-meta-field-name=["\']release_dates["\'] data-meta-field-value=["\'](.+?)["\']',
                watch_info, 'release date', default=None)),
        }


class AkibaPassTVSeasonIE(InfoExtractor):
    _VALID_URL = r'https?://akibapasstv\.?vhx\.tv/products/(?P<id>[^\/$&?#]+)(?:/?$|-season:[0-9]+/?$)'
    _TESTS = [
        {
            'url': 'https://akibapasstv.vhx.tv/products/the-testament-of-sister-new-devil-de-season-1',
            'note': 'Single-season series',
            'playlist_count': 12,
            'info_dict': {
                'id': 'the-testament-of-sister-new-devil-de-season-1',
                'title': 'The Testament of Sister New Devil (DE) - Season 1'
            }
        }
    ]

    def _real_extract(self, url):
        season_id = self._match_id(url)
        season_title = season_id.replace('-', ' ').title()
        webpage = self._download_webpage(url, season_id)

        entries = [
            self.url_result(
                url="https://akibapasstv.vhx.tv" + self._search_regex(r'<a href=["\'](.+?)["\'] class=["\']browse-item-link["\']',
                                       item, 'item_url'),
                ie=AkibaPassTVIE.ie_key()
            ) for item in get_elements_by_class('js-collection-item', webpage)
        ]

        seasons = (get_element_by_class('select-dropdown-wrapper', webpage) or '').strip().replace('\n', '')
        current_season = self._search_regex(r'<option[^>]+selected>([^<]+)</option>',
                                            seasons, 'current_season', default='').strip()

        return {
            '_type': 'playlist',
            'id': join_nonempty(season_id, current_season.lower().replace(' ', '-')),
            'title': join_nonempty(season_title, current_season, delim=' - '),
            'entries': entries
        }
