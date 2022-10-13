class AppContext:
    """
    Holds app metadata which can be accessed by app components
    """

    def __init__(self, **custom_context_args):
        """
        Initialise all custom arguments as attributes of the context
        """
        self.components = {}
        self.page_data = {}
        for var_name, var in custom_context_args.items():
            setattr(self, var_name, var)

    def add_page(self, page_name, page_url, page_function):
        """
        Adds a page that can be navigated to
        """
        self.page_data[page_url] = (page_name, page_function)

    def add_component(self, name, component):
        """
        Adds a component that can be accessed
        """
        self.components[name] = component
