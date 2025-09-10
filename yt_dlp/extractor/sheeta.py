import functools
import json
import re
import urllib.parse

from ..networking.exceptions import HTTPError
from ..utils import (
    ExtractorError,
    OnDemandPagedList,
    filter_dict,
    int_or_none,
    parse_qs,
    unified_timestamp,
    url_or_none,
)
from ..utils.traversal import traverse_obj
from .common import InfoExtractor

class SheetaEmbedIE(InfoExtractor):
    IE_NAME = 'sheeta'
    IE_DESC = 'fan club system developed by DWANGO (ドワンゴ)'
    _VALID_URL = False
    _WEBPAGE_TESTS = [{
        'url': 'https://nicochannel.jp/kaorin/video/sm89Hd4SEduy8WTsb4KxAhBL',
        'info_dict': {
            'id': 'sm89Hd4SEduy8WTsb4KxAhBL',
            'title': '前田佳織里の世界攻略計画 #2',
            'ext': 'mp4',
            'channel': '前田佳織里の世界攻略計画',
            'channel_id': 'nicochannel.jp/kaorin',
            'channel_url': 'https://nicochannel.jp/kaorin',
            'age_limit': 0,
            'live_status': 'not_live',
            'thumbnail': str,
            'description': 'md5:02573495c8be849c0cb88df6f1b85f8b',
            'timestamp': 1644546015,
            'duration': 4093,
            'comment_count': int,
            'view_count': int,
            'tags': ['前田攻略', '前田佳織里', '前田佳織里の世界攻略計画'],
            'upload_date': '20220211',
        },
        'params': {
            'skip_download': True,
        },
    }, {
        # age limited video; test purpose channel.
        'url': 'https://nicochannel.jp/testman/video/smJPZg3nwAxP8UECPsHDiCGM',
        'info_dict': {
            'id': 'smJPZg3nwAxP8UECPsHDiCGM',
            'title': 'DW_itaba_LSM検証_1080p60fps_9000Kbpsで打ち上げたときの挙動確認（パススルーあり）',
            'ext': 'mp4',
            'channel': '本番チャンネルプラステストマン',
            'channel_id': 'nicochannel.jp/testman',
            'channel_url': 'https://nicochannel.jp/testman',
            'age_limit': 18,
            'live_status': 'was_live',
            'thumbnail': str,
            'description': 'TEST',
            'timestamp': 1701329428,
            'duration': 229,
            'comment_count': int,
            'view_count': int,
            'tags': ['検証用'],
            'upload_date': '20231130',
            'release_timestamp': 1701328800,
            'release_date': '20231130',
        },
        'params': {
            'skip_download': True,
        },
    }, {
        # query: None
        'url': 'https://nicochannel.jp/testman/videos',
        'info_dict': {
            'id': 'nicochannel.jp/testman/videos',
            'title': '本番チャンネルプラステストマン-videos',
            'age_limit': 0,
            'timestamp': 1737957232,
            'upload_date': '20250127',
        },
        'playlist_mincount': 18,
    }, {
        # query: None
        'url': 'https://nicochannel.jp/testtarou/videos',
        'info_dict': {
            'id': 'nicochannel.jp/testtarou/videos',
            'title': 'チャンネルプラステスト太郎-videos',
            'age_limit': 0,
            'timestamp': 1737957232,
            'upload_date': '20250127',
        },
        'playlist_mincount': 2,
    }, {
        # query: None
        'url': 'https://nicochannel.jp/testjirou/videos',
        'info_dict': {
            'id': 'nicochannel.jp/testjirou/videos',
            'title': 'チャンネルプラステスト"二郎21-videos',
            'age_limit': 0,
            'timestamp': 1737957232,
            'upload_date': '20250127',
        },
        'playlist_mincount': 12,
    }, {
        # query: tag
        'url': 'https://nicochannel.jp/testman/videos?tag=%E6%A4%9C%E8%A8%BC%E7%94%A8',
        'info_dict': {
            'id': 'nicochannel.jp/testman/videos',
            'title': '本番チャンネルプラステストマン-videos',
            'age_limit': 0,
            'timestamp': 1737957232,
            'upload_date': '20250127',
        },
        'playlist_mincount': 6,
    }, {
        # query: vodType
        'url': 'https://nicochannel.jp/testman/videos?vodType=1',
        'info_dict': {
            'id': 'nicochannel.jp/testman/videos',
            'title': '本番チャンネルプラステストマン-videos',
            'age_limit': 0,
            'timestamp': 1737957232,
            'upload_date': '20250127',
        },
        'playlist_mincount': 18,
    }, {
        # query: sort
        'url': 'https://nicochannel.jp/testman/videos?sort=-released_at',
        'info_dict': {
            'id': 'nicochannel.jp/testman/videos',
            'title': '本番チャンネルプラステストマン-videos',
            'age_limit': 0,
            'timestamp': 1737957232,
            'upload_date': '20250127',
        },
        'playlist_mincount': 18,
    }, {
        # query: tag, vodType
        'url': 'https://nicochannel.jp/testman/videos?tag=%E6%A4%9C%E8%A8%BC%E7%94%A8&vodType=1',
        'info_dict': {
            'id': 'nicochannel.jp/testman/videos',
            'title': '本番チャンネルプラステストマン-videos',
            'age_limit': 0,
            'timestamp': 1737957232,
            'upload_date': '20250127',
        },
        'playlist_mincount': 6,
    }, {
        # query: tag, sort
        'url': 'https://nicochannel.jp/testman/videos?tag=%E6%A4%9C%E8%A8%BC%E7%94%A8&sort=-released_at',
        'info_dict': {
            'id': 'nicochannel.jp/testman/videos',
            'title': '本番チャンネルプラステストマン-videos',
            'age_limit': 0,
            'timestamp': 1737957232,
            'upload_date': '20250127',
        },
        'playlist_mincount': 6,
    }, {
        # query: vodType, sort
        'url': 'https://nicochannel.jp/testman/videos?vodType=1&sort=-released_at',
        'info_dict': {
            'id': 'nicochannel.jp/testman/videos',
            'title': '本番チャンネルプラステストマン-videos',
            'age_limit': 0,
            'timestamp': 1737957232,
            'upload_date': '20250127',
        },
        'playlist_mincount': 18,
    }, {
        # query: tag, vodType, sort
        'url': 'https://nicochannel.jp/testman/videos?tag=%E6%A4%9C%E8%A8%BC%E7%94%A8&vodType=1&sort=-released_at',
        'info_dict': {
            'id': 'nicochannel.jp/testman/videos',
            'title': '本番チャンネルプラステストマン-videos',
            'age_limit': 0,
            'timestamp': 1737957232,
            'upload_date': '20250127',
        },
        'playlist_mincount': 6,
    }, {
        'url': 'https://nicochannel.jp/testman/lives',
        'info_dict': {
            'id': 'nicochannel.jp/testman/lives',
            'title': '本番チャンネルプラステストマン-lives',
            'age_limit': 0,
            'timestamp': 1737957232,
            'upload_date': '20250127',
        },
        'playlist_mincount': 18,
    }, {
        'url': 'https://nicochannel.jp/testtarou/lives',
        'info_dict': {
            'id': 'nicochannel.jp/testtarou/lives',
            'title': 'チャンネルプラステスト太郎-lives',
            'age_limit': 0,
            'timestamp': 1737957232,
            'upload_date': '20250127',
        },
        'playlist_mincount': 2,
    }, {
        'url': 'https://nicochannel.jp/testjirou/lives',
        'info_dict': {
            'id': 'nicochannel.jp/testjirou/lives',
            'title': 'チャンネルプラステスト"二郎21-lives',
            'age_limit': 0,
            'timestamp': 1737957232,
            'upload_date': '20250127',
        },
        'playlist_mincount': 6,
    }, {
        'url': 'https://qlover.jp/doku/video/smy4caVHR6trSddiG9uCDiy4',
        'info_dict': {
            'id': 'smy4caVHR6trSddiG9uCDiy4',
            'title': '名取さなの毒にも薬にもならないラジオ#39',
            'ext': 'mp4',
            'channel': '名取さなの毒にも薬にもならないラジオ',
            'channel_id': 'qlover.jp/doku',
            'channel_url': 'https://qlover.jp/doku',
            'age_limit': 0,
            'live_status': 'not_live',
            'thumbnail': str,
            'description': 'md5:75c2143a59b4b70141b77ddb485991fd',
            'timestamp': 1711933200,
            'duration': 1872,
            'comment_count': int,
            'view_count': int,
            'tags': ['名取さな', 'どくラジ', '文化放送', 'ラジオ'],
            'upload_date': '20240401',
        },
        'params': {
            'skip_download': True,
        },
    }, {
        'url': 'https://itomiku-fc.jp/live/sm4P8x6oVPFBx59bNBGSgKoE',
        'info_dict': {
            'id': 'sm4P8x6oVPFBx59bNBGSgKoE',
            'title': '【3/9(土)14:00～】「all yours」美来の日SP♪',
            'ext': 'mp4',
            'channel': '伊藤美来 Official Fanclub 「all yours」',
            'channel_id': 'itomiku-fc.jp',
            'channel_url': 'https://itomiku-fc.jp',
            'age_limit': 0,
            'live_status': 'was_live',
            'thumbnail': str,
            'description': 'md5:80a6a14db30d8506f70bec6a28a6c4ad',
            'timestamp': 1709964399,
            'duration': 4542,
            'comment_count': int,
            'view_count': int,
            'tags': ['生放送', '生放送アーカイブ'],
            'upload_date': '20240309',
            'release_timestamp': 1709959800,
            'release_date': '20240309',
        },
        'params': {'skip_download': True},
    }, {
        'url': 'https://canan8181.com/video/smxar9atjfNBn27bHhcTFLyg',
        'info_dict': {
            'id': 'smxar9atjfNBn27bHhcTFLyg',
            'title': '💛【7月】ドネートお礼しながら感想＆どきどきトーク【感想会】',
            'ext': 'mp4',
            'channel': 'Canan official fanclub',
            'channel_id': 'canan8181.com',
            'channel_url': 'https://canan8181.com',
            'age_limit': 15,
            'live_status': 'was_live',
            'thumbnail': str,
            'description': 'md5:0cd80e51da82dbb89deae5ea14aad24d',
            'timestamp': 1659182206,
            'duration': 6997,
            'comment_count': int,
            'view_count': int,
            'tags': ['安眠など♡アーカイブ＆動画（わらのおうちプラン以上）'],
            'upload_date': '20220730',
            'release_timestamp': 1659175200,
            'release_date': '20220730',
        },
        'params': {'skip_download': True},
    }, {
        'url': 'https://audee-membership.jp/aisaka-yuuka/audio/smx3ebEZFRnHeaGzUzgi5A98',
        'info_dict': {
            'id': 'smx3ebEZFRnHeaGzUzgi5A98',
            'title': '#相坂湯 第38回 ロコムジカちゃんの歌唱についてモノ申す！？ ある意味レアな？鼻声坂くん！',
            'ext': 'm4a',
            'channel': '相坂優歌 湯上がり何飲む？',
            'channel_id': 'audee-membership.jp/aisaka-yuuka',
            'channel_url': 'https://audee-membership.jp/aisaka-yuuka',
            'age_limit': 0,
            'live_status': 'not_live',
            'thumbnail': str,
            'description': 'md5:fdf881191f8057aa6af6042fc17fb94c',
            'timestamp': 1710860400,
            'duration': 631,
            'comment_count': int,
            'view_count': int,
            'tags': ['RADIO'],
            'upload_date': '20240319',
        },
        'params': {'skip_download': True},
    }, {
        'url': 'https://hololive-fc.com/videos',
        'info_dict': {
            'id': 'hololive-fc.com/videos',
            'title': '旧ホロライブ公式ファンクラブ-videos',
            'age_limit': 0,
            'timestamp': 1737957238,
            'upload_date': '20250127',
        },
        'playlist_mincount': 12,
    }, {
        'url': 'https://tokinosora-fc.com/videos?vodType=1',
        'info_dict': {
            'id': 'tokinosora-fc.com/videos',
            'title': 'ときのそらオフィシャルファンクラブ-videos',
            'age_limit': 0,
            'timestamp': 1737957234,
            'upload_date': '20250127',
        },
        'playlist_mincount': 18,
    }, {
        'url': 'https://audee-membership.jp/okuma-wakana/videos?tag=RADIO&vodType=1&sort=display_date',
        'info_dict': {
            'id': 'audee-membership.jp/okuma-wakana/videos',
            'title': '大熊和奏 朝のささやき-videos',
            'age_limit': 0,
            'timestamp': 1737957233,
            'upload_date': '20250127',
        },
        'playlist_mincount': 6,
    }, {
        'url': 'https://qlover.jp/bokuao/lives',
        'info_dict': {
            'id': 'qlover.jp/bokuao/lives',
            'title': '僕が見たかった青空の 「青天のヘキレキ！」-lives',
            'age_limit': 0,
            'timestamp': 1737957231,
            'upload_date': '20250127',
        },
        'playlist_mincount': 1,
    }, {
        'url': 'https://audee-membership.jp/tanaka-chiemi/lives',
        'info_dict': {
            'id': 'audee-membership.jp/tanaka-chiemi/lives',
            'title': '田中ちえ美のたなかのカナタ！-lives',
            'age_limit': 0,
            'timestamp': 1737957233,
            'upload_date': '20250127',
        },
        'playlist_mincount': 5,
    }]

    _DOMAIN = None
    _API_BASE_URL = None
    _FANCLUB_GROUP_ID = None
    _FANCLUB_SITE_ID_AUTH = None
    _FANCLUB_SITE_ID_INFO = None

    _LIST_PAGE_SIZE = 12
    _LOGIN_METHOD = 'password'

    def _extract_from_url(self, url):
        parsed_url = urllib.parse.urlparse(url)
        if '/videos' in parsed_url.path:
            return self._extract_video_list_page(url)
        elif '/lives' in parsed_url.path:
            return self._extract_live_list_page(url)
        else:
            return self._extract_player_page(url)

    def _extract_from_webpage(self, url, webpage):
        if 'GTM-KXT7G5G' in webpage or 'NicoGoogleTagManagerDataLayer' in webpage:
            yield self._extract_from_url(url)
            raise self.StopExtraction

    def _call_api(self, path, item_id, *args, **kwargs):
        return self._download_json(f'{self._API_BASE_URL}/{path}', item_id, *args, **kwargs)

    def _call_api_authed(self, path, item_id, **kwargs):
        expected_code_msg = {
            401: 'Invalid token',
            403: 'Login required',
            404: 'Members-only content',
            408: 'Outdated token',
        }
        headers = filter_dict({
            'Content-Type': 'application/json',
            'fc_use_device': 'null',
            'origin': f'https://{self._DOMAIN}',
        })

        try:
            return self._call_api(path, item_id, headers=headers, **kwargs)
        except ExtractorError as e:
            if not isinstance(e.cause, HTTPError) or e.cause.status not in expected_code_msg:
                raise e
            self.raise_login_required('%s (%d)' % (
                expected_code_msg[e.cause.status], e.cause.status), metadata_available=True, method=self._LOGIN_METHOD)
            return None

    def _find_fanclub_site_id(self, channel_id):
        fanclub_list_json = self._call_api(
            'content_providers/channel_domain', f'channels/{channel_id}',
            query={'current_site_domain': urllib.parse.quote(f'https://{self._DOMAIN}/{channel_id}')},
            note='Fetching channel list', errnote='Unable to fetch channel list',
        )
        if fanclub_id := traverse_obj(
                fanclub_list_json, ('data', 'content_providers', 'id', {int_or_none}), get_all=False):
            return fanclub_id
        raise ExtractorError(f'Channel {channel_id} does not exist', expected=True)

    def _extract_base_info(self, channel_id):
        site_settings = self._download_json(
            f'https://{self._DOMAIN}/site/settings.json', None,
            note='Fetching site settings', errnote='Unable to fetch site settings')
        self.write_debug(f'site_settings = {site_settings!r}')

        self._API_BASE_URL = site_settings['api_base_url']
        self._FANCLUB_GROUP_ID = site_settings['fanclub_group_id']
        self._FANCLUB_SITE_ID_AUTH = site_settings['fanclub_site_id']

        if channel_id:
            self._FANCLUB_SITE_ID_INFO = self._find_fanclub_site_id(channel_id)
        else:
            self._FANCLUB_SITE_ID_INFO = self._FANCLUB_SITE_ID_AUTH

    @property
    def _channel_base_info(self):
        return traverse_obj(self._call_api(
            f'fanclub_sites/{self._FANCLUB_SITE_ID_INFO}/page_base_info', f'fanclub_sites/{self._FANCLUB_SITE_ID_INFO}',
            note='Fetching channel base info', errnote='Unable to fetch channel base info', fatal=False,
        ), ('data', 'fanclub_site', {dict})) or {}

    @property
    def _channel_user_info(self):
        return traverse_obj(self._call_api(
            f'fanclub_sites/{self._FANCLUB_SITE_ID_INFO}/user_info', f'fanclub_sites/{self._FANCLUB_SITE_ID_INFO}',
            note='Fetching channel user info', errnote='Unable to fetch channel user info', fatal=False,
            data=json.dumps('null').encode(),
        ), ('data', 'fanclub_site', {dict})) or {}

    def _extract_channel_info(self, channel_id):
        if channel_id:
            full_channel_id = f'{self._DOMAIN}/{channel_id}'
            channel_url = f'https://{self._DOMAIN}/{channel_id}'
        else:
            full_channel_id = self._DOMAIN
            channel_url = f'https://{self._DOMAIN}'

        return {
            'channel': self._channel_base_info.get('fanclub_site_name'),
            'channel_id': full_channel_id,
            'channel_url': channel_url,
            'age_limit': traverse_obj(self._channel_user_info, (
                'content_provider', 'age_limit', {int_or_none})),
        }

    def _extract_player_page(self, url):
        self._DOMAIN, channel_id, content_code = re.match(
            r'https?://(?P<domain>[\w.-]+)(/(?P<channel>[\w.-]+))?/(?:live|video|audio)/(?P<code>sm\w+)', url,
        ).group('domain', 'channel', 'code')
        self._extract_base_info(channel_id)

        data_json = self._call_api(
            f'video_pages/{content_code}', content_code, headers={'fc_site_id': self._FANCLUB_SITE_ID_INFO, 'fc_use_device': 'null'},
            note='Fetching video page info', errnote='Unable to fetch video page info',
        )['data']['video_page']

        live_status = self._get_live_status(data_json, content_code)
        release_timestamp_str = data_json.get('live_scheduled_start_at')

        if live_status == 'is_upcoming':
            if release_timestamp_str:
                msg = f'This live event will begin at {release_timestamp_str} UTC'
            else:
                msg = 'This event has not started yet'
            self.raise_no_formats(msg, expected=True, video_id=content_code)

        return {
            'id': content_code,
            'formats': list(self._yield_formats(data_json, live_status, content_code)),
            'live_status': live_status,
            'release_timestamp': unified_timestamp(release_timestamp_str),
            **self._extract_channel_info(channel_id),
            **traverse_obj(data_json, {
                'title': ('title', {str}),
                'thumbnail': ('thumbnail_url', {url_or_none}),
                'description': ('description', {str}),
                'timestamp': ('display_date', {unified_timestamp}),
                'duration': ('active_video_filename', 'length', {int_or_none}),
                'comment_count': ('video_aggregate_info', 'number_of_comments', {int_or_none}),
                'view_count': ('video_aggregate_info', 'total_views', {int_or_none}),
                'tags': ('video_tags', ..., 'tag', {str}),
            }),
            '__post_extractor': self.extract_comments(
                content_code=content_code,
                comment_group_id=traverse_obj(data_json, ('video_comment_setting', 'comment_group_id'))),
        }

    def _get_comments(self, content_code, comment_group_id):
        item_id = f'{content_code}/comments'

        if not comment_group_id:
            return None

        comment_access_token = self._call_api(
            f'video_pages/{content_code}/comments_user_token', item_id,
            note='Getting comment token', errnote='Unable to get comment token',
        )['data']['access_token']

        comment_list, urlh = self._download_json_handle(
            'https://comm-api.sheeta.com/messages.history', video_id=item_id,
            note='Fetching comments', errnote='Unable to fetch comments',
            headers={'Content-Type': 'application/json'}, expected_status=404,
            query={
                'sort_direction': 'asc',
                'limit': int_or_none(self._configuration_arg('max_comments', [''])[0]) or 120,
            },
            data=json.dumps({
                'token': comment_access_token,
                'group_id': comment_group_id,
            }).encode())
        if urlh.status == 404:
            self.report_warning('Unable to fetch comments due to rate limit', content_code)
            return

        for comment in traverse_obj(comment_list, ...):
            yield traverse_obj(comment, {
                'author': ('nickname', {str}),
                'author_id': ('sender_id', {str}),
                'id': ('id', {str}, {lambda x: x or None}),
                'text': ('message', {str}),
                'timestamp': (('updated_at', 'sent_at', 'created_at'), {unified_timestamp}),
                'author_is_uploader': ('sender_id', {lambda x: x == '-1'}),
            }, get_all=False)

    def _get_live_status(self, data_json, content_code):
        video_type = data_json.get('type')
        live_finished_at = data_json.get('live_finished_at')

        if video_type == 'vod':
            if live_finished_at:
                live_status = 'was_live'
            else:
                live_status = 'not_live'
        elif video_type == 'live':
            if not data_json.get('live_started_at'):
                return 'is_upcoming'

            if not live_finished_at:
                live_status = 'is_live'
            else:
                live_status = 'was_live'

                video_allow_dvr_flg = traverse_obj(data_json, ('video', 'allow_dvr_flg'))
                video_convert_to_vod_flg = traverse_obj(data_json, ('video', 'convert_to_vod_flg'))

                self.write_debug(
                    f'{content_code}: allow_dvr_flg = {video_allow_dvr_flg}, convert_to_vod_flg = {video_convert_to_vod_flg}.')

                if not (video_allow_dvr_flg and video_convert_to_vod_flg):
                    raise ExtractorError(
                        'Live was ended, there is no video for download', video_id=content_code, expected=True)
        else:
            raise ExtractorError(f'Unknown type: {video_type!r}', video_id=content_code)

        self.write_debug(f'{content_code}: video_type={video_type}, live_status={live_status}')
        return live_status

    def _yield_formats(self, data_json, live_status, content_code):
        if data_json.get('video'):
            payload = {}
            if data_json.get('type') == 'live' and live_status == 'was_live':
                payload = {'broadcast_type': 'dvr'}

            session_id = traverse_obj(self._call_api_authed(
                f'video_pages/{content_code}/session_ids', f'{content_code}/session',
                data=json.dumps(payload).encode(), note='Getting session id', errnote='Unable to get session id'),
                ('data', 'session_id', {str}))

            if session_id:
                m3u8_url = data_json['video_stream']['authenticated_url'].format(session_id=session_id)
                yield from self._extract_m3u8_formats(m3u8_url, content_code)

        if data_json.get('audio'):
            m3u8_url = traverse_obj(self._call_api_authed(
                f'video_pages/{content_code}/content_access', f'{content_code}/content_access',
                note='Getting content resource', errnote='Unable to get content resource'),
                ('data', 'resource', {url_or_none}))

            if m3u8_url:
                audio_type = traverse_obj(data_json, (
                    'audio_filename_transcoded_list', lambda _, v: v['url'] == m3u8_url,
                    'video_filename_type', 'value', {str}), get_all=False)
                if audio_type == 'audio_free':
                    # fully free audios are always of "audio_paid"
                    msg = 'You have no right to access the paid content. '
                    if traverse_obj(data_json, 'video_free_periods'):
                        msg += 'There may be some silent parts in this audio'
                    else:
                        msg += 'This audio may be completely blank'
                    self.raise_login_required(
                        msg, metadata_available=True, method=self._LOGIN_METHOD)

                yield {
                    'url': m3u8_url,
                    'format_id': audio_type,
                    'protocol': 'm3u8_native',
                    'ext': 'm4a',
                    'vcodec': 'none',
                    'acodec': 'aac',
                }

    def _fetch_paged_channel_video_list(self, path, query, channel, item_id, page):
        response = self._call_api(
            path, item_id, query={
                **query,
                'page': (page + 1),
                'per_page': self._LIST_PAGE_SIZE,
            },
            headers={'fc_use_device': 'null'},
            note=f'Fetching channel info (page {page + 1})',
            errnote=f'Unable to fetch channel info (page {page + 1})')

        for content_code in traverse_obj(
                response, ('data', 'video_pages', 'list', ..., 'content_code', {str})):
            yield self.url_result('/'.join(filter(
                None, [f'https://{self._DOMAIN}', channel, 'video', content_code])))

    def _extract_video_list_page(self, url):
        """
        API parameters:
            sort:
                -display_date         公開日が新しい順 (newest to oldest)
                 display_date         公開日が古い順 (oldest to newest)
                -number_of_vod_views 再生数が多い順 (most play count)
                 number_of_vod_views コメントが多い順 (most comments)
            vod_type (is "vodType" in "url"):
                0 すべて (all)
                1 会員限定 (members only)
                2 一部無料 (partially free)
                3 レンタル (rental)
                4 生放送アーカイブ (live archives)
                5 アップロード動画 (uploaded videos)
                7 無料 (free)
        """

        self._DOMAIN, channel_id = re.match(
            r'https?://(?P<domain>[\w.-]+)(/(?P<channel>[\w.-]+))?/videos', url,
        ).group('domain', 'channel')
        self._extract_base_info(channel_id)

        channel_info = self._extract_channel_info(channel_id)
        full_channel_id = channel_info['channel_id']
        channel_name = channel_info['channel']
        qs = parse_qs(url)

        return self.playlist_result(
            OnDemandPagedList(
                functools.partial(
                    self._fetch_paged_channel_video_list, f'fanclub_sites/{self._FANCLUB_SITE_ID_INFO}/video_pages',
                    filter_dict({
                        'tag': traverse_obj(qs, ('tag', 0)),
                        'sort': traverse_obj(qs, ('sort', 0), default='-display_date'),
                        'vod_type': traverse_obj(qs, ('vodType', 0), default='0'),
                    }),
                    channel_id, f'{full_channel_id}/videos'),
                self._LIST_PAGE_SIZE),
            playlist_id=f'{full_channel_id}/videos', playlist_title=f'{channel_name}-videos')

    def _extract_live_list_page(self, url):
        """
        API parameters:
            live_type:
                1 放送中 (on air)
                2 放送予定 (scheduled live streams, oldest to newest)
                3 過去の放送 - すべて (all ended live streams, newest to oldest)
                4 過去の放送 - 生放送アーカイブ (all archives for live streams, oldest to newest)
            We use "4" instead of "3" because some recently ended live streams could not be downloaded.
        """

        self._DOMAIN, channel_id = re.match(
            r'https?://(?P<domain>[\w.-]+)(/(?P<channel>[\w.-]+))?/lives', url,
        ).group('domain', 'channel')
        self._extract_base_info(channel_id)

        channel_info = self._extract_channel_info(channel_id)
        full_channel_id = channel_info['channel_id']
        channel_name = channel_info['channel']

        return self.playlist_result(
            OnDemandPagedList(
                functools.partial(
                    self._fetch_paged_channel_video_list, f'fanclub_sites/{self._FANCLUB_SITE_ID_INFO}/live_pages',
                    {'live_type': 4}, channel_id, f'{full_channel_id}/lives'),
                self._LIST_PAGE_SIZE),
            playlist_id=f'{full_channel_id}/lives', playlist_title=f'{channel_name}-lives')
