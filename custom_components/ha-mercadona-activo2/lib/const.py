# Define los parámetros necesarios
# PRE: https://sts.premercadona.es/adfs/oauth2/token/
# PRO: https://sts.mercadona.es/adfs/oauth2/token/
OAUTH2_TOKEN_URL = "https://sts.mercadona.es/adfs/oauth2/token/"
# PRE: 8e6dc338-dcf3-44f6-a443-8f32897641aa
# PRO: 06b18d7d-23da-4e41-8654-8ec8704e297e
OAUTH2_CLIENT_ID = "06b18d7d-23da-4e41-8654-8ec8704e297e"
OAUTH2_SCOPE = "openid"
OAUTH2_RESPONSE_TYPE = "id_token code"
OAUTH2_GRANT_TYPE = "password"

# PRE: https://back.activo2.pre.mercadona.com/mot/v2/schedule?lang=es
# PRO: https://back.activo2.mercadona.com/mot/v2/schedule?lang=es
API_URL_SCHEDULE = "https://back.activo2.mercadona.com/mot/v2/schedule?lang=es"
# PRE: https://back.activo2.pre.mercadona.com/user/info
# PRO: https://back.activo2.mercadona.com/user/info
API_URL_USERINFO = "https://back.activo2.mercadona.com/user/info"

# PRE: preproduccion.net\\
# PRO: ofidona.net\\
USERNAME_PREFIX = "ofidona.net\\"
