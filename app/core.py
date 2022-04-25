'''
Core class for APP

'''

class Route:
    ''' A ordinary router '''
    def __init__(self, url, view):
        self.url = url
        self.view = view