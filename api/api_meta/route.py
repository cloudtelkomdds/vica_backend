from api.api_meta.category import Category
from api.api_meta.endpoint import Endpoint

class Route:
    SIGN_IN_WITH_GOOGLE = "/{0}/{1}".format(Category.AUTHENTICATION, Endpoint.SIGN_IN_WITH_GOOGLE)

    CREATE_PBX_REQUEST = "/{0}/{1}".format(Category.PBX_REQUEST, Endpoint.CREATE_PBX_REQUEST)
    GET_ALL_PBX_REQUESTS = "/{0}/{1}".format(Category.PBX_REQUEST, Endpoint.GET_ALL_PBX_REQUESTS)
    APPROVE_PBX_REQUEST = "/{0}/{1}".format(Category.PBX_REQUEST, Endpoint.APPROVE_PBX_REQUEST)
    DELETE_PBX_REQUEST = "/{0}/{1}".format(Category.PBX_REQUEST, Endpoint.DELETE_PBX_REQUEST)

    GET_ALL_PBXS = "/{0}/{1}".format(Category.PBX, Endpoint.GET_ALL_PBXS)
    DELETE_PBX = "/{0}/{1}".format(Category.PBX, Endpoint.DELETE_PBX)

    CREATE_EXTENSION = "/{0}/{1}".format(Category.EXTENSION, Endpoint.CREATE_EXTENSION)
    GET_ALL_EXTENSIONS = "/{0}/{1}".format(Category.EXTENSION, Endpoint.GET_ALL_EXTENSIONS)
    UPDATE_EXTENSION = "/{0}/{1}".format(Category.EXTENSION, Endpoint.UPDATE_EXTENSION)
    DELETE_EXTENSION = "/{0}/{1}".format(Category.EXTENSION, Endpoint.DELETE_EXTENSION)

    GET_LOCATIONS = "/{0}/{1}".format(Category.MISCELLANEOUS, Endpoint.GET_LOCATIONS)