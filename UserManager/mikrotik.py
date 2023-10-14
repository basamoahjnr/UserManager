import os

import routeros_api
from dotenv import load_dotenv

load_dotenv()


def create_hotspot_user(username, password):
    try:
        connection = routeros_api.RouterOsApiPool(
            os.environ.get('R_IP'),
            username=os.environ.get('R_USERNAME'),
            password=os.environ.get('R_PASSWORD'),
            port=8291,
            use_ssl=False,
            ssl_verify=True,
            ssl_verify_hostname=True,
            ssl_context=None,
        )
        api = connection.get_api()
        api('/ip/hotspot/user/add', {'name': username, 'password': password})
        return True
    except Exception as e:
        print(f"Error creating hotspot user: {e}")
        return False


def get_hotspot_profiles(router_ip, router_username, router_password):
    try:

        connection = routeros_api.RouterOsApiPool(
            router_ip,
            router_username,
            router_password,
            port=8728,
            use_ssl=False,
            plaintext_login=True
        )
        api = connection.get_api()
        response = api.get_binary_resource('/').call('ip/hotspot/user/profile/print')
        profiles = [item.decode('utf-8') if isinstance(item, bytes) else item for item in
                    [profile['name'] for profile in response]]
        connection.disconnect()
        # Convert the profiles string from byte to string type
        return profiles
    except Exception as e:
        print(f"Error fetching hotspot profiles: {e}")
        return []


hotspot_profiles = get_hotspot_profiles(os.getenv('M_IP'), os.getenv('M_USERNAME'), os.getenv('M_PASSWORD'))
