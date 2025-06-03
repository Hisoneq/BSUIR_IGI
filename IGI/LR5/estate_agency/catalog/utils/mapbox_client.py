import requests
import logging
from django.conf import settings
from urllib.parse import quote

logger = logging.getLogger(__name__)

class MapboxClient(object):
    @staticmethod
    def get_map_image_url(address):
        geocoding_url = settings.MAPBOX_GEOCODING_API.format(
            quote(address)
        )
        params = {
            'access_token': settings.MAPBOX_ACCESS_TOKEN,
            'types': 'address',
            'language': settings.MAPBOX_LANGUAGE,
            'limit': 1
        }

        try:
            response = requests.get(geocoding_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            if not data.get('features'):
                logger.warning(f"Address not found: {address}")
                return settings.MAPBOX_DEFAULT_IMAGE

            lng, lat = data['features'][0]['geometry']['coordinates']
            logger.debug(f"lng={lng}, lat={lat}")

            map_url = settings.MAPBOX_STATIC_MAP_API.format(
                lng=lng,
                lat=lat,
                token=settings.MAPBOX_ACCESS_TOKEN
            )
            logger.info(f"Generate map URL for {address}: {map_url}")
            return map_url

        except requests.RequestException as e:
            logger.error(f"Error while requesting Mapbox API for address {address}: {str(e)}")
            return settings.MAPBOX_DEFAULT_IMAGE
        except (KeyError, IndexError) as e:
            logger.error(f"Error processing Mapbox API response for address {address}: {str(e)}")
            return settings.MAPBOX_DEFAULT_IMAGE
