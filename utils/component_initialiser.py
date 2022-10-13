import importlib.util
import inspect
import logging
import os

from dash import html
from utils.app_context import AppContext

logger = logging.getLogger(__name__)

COMPONENTS = {}
CALLBACKS = {}
PAGES = {}
DATA_COMPONENTS = {}


class DefaultComponent:
    """ If a component fails to load, it gets replaced with this """

    def __int__(self):
        self.layout = html.Div()


def add_component(name, component, children, required_data):
    """
    Adds a component to the component dict
    """
    if name in COMPONENTS:
        raise f"Loaded duplicate components, name:{name}"
    COMPONENTS.update({name: (component, children, required_data)})


def add_data_component(name, data_component):
    """
    Adds a data component that can be accessed by using the required_data parameter
    """
    if name in DATA_COMPONENTS:
        raise f"Loaded duplicate components, name:{name}"
    DATA_COMPONENTS.update({name: data_component})


def add_page(path, name, page, reference_component):
    """
    Adds a page to the page dict
    If the component is a function, add it as is
    If the component is a class method, the reference component is the class its in
    """
    if page.__qualname__ != page.__name__:
        class_name, _ = page.__qualname__.split('.', maxsplit=1)
        PAGES.setdefault(class_name, {}).update({path: (name, page, class_name)})

    else:
        reference_component = reference_component if reference_component != "infer" else None
        PAGES.setdefault("", {}).update({path: (name, page, reference_component)})


def add_callback_decorator(callback, callback_args, callback_kwargs):
    """
    Adds a callback to the callback dict
    If the component is a function, add it as is
    If the component is a class method, the reference component is the class its in
    """
    if callback.__qualname__ != callback.__name__:
        class_name, _ = callback.__qualname__.split('.', maxsplit=1)
        CALLBACKS.setdefault(class_name, {}).update({callback: (callback_args, callback_kwargs)})

    else:
        CALLBACKS.setdefault("", {}).update({callback: (callback_args, callback_kwargs)})


def iterative_importer(path):
    """
    Imports every python script from a given path
    Ignores hidden files, files that begin with "." and "_" are considered hidden

    Path is relative to the working directory
    """
    # Returns True if the file is hidden

    check_hidden = lambda x: x.startswith('_') or x.startswith('.')
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if not check_hidden(d)]

        for script in files:
            if not check_hidden(script) and script.endswith('.py'):
                spec = importlib.util.spec_from_file_location(
                    script.rstrip('.py'), os.path.join(root, script)
                )
                spec.loader.exec_module(importlib.util.module_from_spec(spec))


def initialise_data_components(launch_config, app_context):
    """
    Initialise data components, data components are initialised with the launch config
    """
    initialised_components = {}
    for name, component in DATA_COMPONENTS.items():
        component_instance = component(launch_config)
        initialised_components[name] = component_instance

    initialised_components['app_context'] = app_context

    return initialised_components


def initialise_app_components(app, component_order, data_components):
    """
    Initialises all callback and page components in the context of the component they're attached to
    """
    app_context = data_components['app_context']

    for name in component_order:
        component, component_children, data_wishlist = COMPONENTS[name]
        try:
            component_wishlist = [app_context.components[c_name] for c_name in component_children]
            data_wishlist = [data_components[d_name] for d_name in data_wishlist]
            instance = component(*component_wishlist, *data_wishlist)

        except KeyError as e:
            # Something in the wishlist doesn't exist, we should do something about this later
            raise

        class_name = type(instance).__name__

        # Initialise callbacks as part of the component
        for method in CALLBACKS.get(class_name, {}):
            # Allow duplicate method names with the following if statement
            if method.__name__ in dir(instance) and method == getattr(type(instance), method.__name__):
                app.callback(
                    *CALLBACKS[class_name][method][0],
                    **CALLBACKS[class_name][method][1]
                )(getattr(instance, method.__name__))

        # Initialise pages as part of the component
        for endpoint, values in PAGES.get(class_name, {}).items():
            name, page, class_name = values
            if page.__name__ in dir(instance) and page == getattr(type(instance), page.__name__):
                app_context.add_page(page_name=name, page_url=endpoint, page_function=getattr(instance, page.__name__))

        app_context.add_component(name, instance)

    return app_context


def build_component_order(component_name, loaded_components=()):
    """
    Recursively look for components that need to be loaded for this component to work
    Returns a list that represents the order components should be loaded in
    """
    component, children, data_deps = COMPONENTS[component_name]
    for child_component in children:
        if child_component not in loaded_components:
            # prevent cyclic relations
            loaded_components = build_component_order(child_component, loaded_components)

    loaded_components = (*loaded_components, component_name)
    return loaded_components


def initialise(app, launch_config, base_path):
    """
    Run main initialisation steps, returns an app context
    """
    # import all components
    iterative_importer("components")
    iterative_importer("data")

    # initialise app context
    app_context = AppContext(base_path=base_path)
    components_list = ()

    # initialise pages that aren't part of components
    page_functions = PAGES.pop("", {})
    for path, page_items in page_functions.items():
        name, page, reference_component = page_items
        if reference_component:
            build_component_order(reference_component, loaded_components=components_list)
        app_context.add_page(page_name=name, page_url=path, page_function=page)

    # load components that are attached to pages
    for pages in PAGES.values():
        for path, page_items in pages.items():
            name, page, page_component = page_items

            # find the component that is the class of the page
            for component_name, component_items in COMPONENTS.items():
                component_class = component_items[0].__qualname__
                if component_class == page_component:
                    # Compare source files to prevent duplicates from different files from overwriting each other
                    if inspect.getsourcefile(component_items[0].__init__) == inspect.getsourcefile(page):
                        break
            else:
                raise f"Page {name} is part of a class that isn't a component"

            components_list = build_component_order(component_name, loaded_components=components_list)

    # add the navbar at the end so that the pages get loaded into it
    components_list = (*components_list, 'navigation_bar')

    data_components = initialise_data_components(launch_config, app_context)
    app_context = initialise_app_components(app, components_list, data_components)

    return app_context
