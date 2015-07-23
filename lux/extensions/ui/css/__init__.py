from . import main
from . import navbar
from . import forms
from . import features
from . import grid


def add_css(all):
    main.add_css(all)
    navbar.add_css(all)
    forms.add_css(all)
    features.add_css(all)
    grid.add_css(all)
