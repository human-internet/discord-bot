import os 
#from web.app.static
#import static
#import mvc_exceptions as mvc_exc
#import basic_backend

#seems unfinished
class Controller(object):
    def __init__(self, model, view, controller):
        self.controller = controller
        self.model = model
        self.view = view
class View(object):
    @staticmethod
    def show_page():
        print("Waiting for API")


class Model(object):
    def __init__(self, application_items):
        self._item_type = 'product'
        self.create_items(application_items)

    @property
    def item_type(self):
        return self._item_type


print("test")


