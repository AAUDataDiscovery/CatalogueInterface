"""
Decorators for graphical components in the dash app
Wrapped functions are added to a list that's read into the app layout
"""

from utils.component_initialiser import add_component, add_data_component, add_page, add_callback_decorator


def component(name, children: list = None, required_data: list = None):
    """
    This decorator allows visual components to be defined in the app
    :param name:
    :param children:
    :param required_data:
    :return:
    """
    children = children or []
    required_data = required_data or []

    def app_component_decorator(given_component):
        add_component(name, given_component, children, required_data)

        return given_component

    return app_component_decorator


def callback(*callback_args, **callback_kwargs):
    """
    Adds a dash callback, which will function the same as using app.callback
    :param callback_args:
    :param callback_kwargs:
    :return:
    """

    def app_callback_decorator(callback_function):
        add_callback_decorator(callback_function, callback_args, callback_kwargs)
        return callback_function

    return app_callback_decorator


def page(path, name=None, reference_component="infer"):
    """
    Adds a navigable page to the app
    :param name:
    :param path:
    :param reference_component:
    """
    name = name or path

    def page_decorator(page_component):
        add_page(path, name, page_component, reference_component)
        return page_component

    return page_decorator


def data(name):
    """
    Adds a data component to be accessible by app components
    :param name:
    """

    def data_decorator(data_component):
        add_data_component(name, data_component)
        return data_component

    return data_decorator
