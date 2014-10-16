'''Extension for creating style sheets using python.

To use this extension, add the ``lux.extensions.ui`` entry into the
:setting:`EXTENSIONS` list in your config file.
To add additional ``css`` rules, a user extension module must provide the
``add_css`` function which accept one parameter only, the ``css`` container.
The ``add_css`` function is called when building the css file via the ``style``
command.


.. _python-css-tools:

Variables and Symbols
=========================

.. automodule:: lux.extensions.ui.lib.base
   :members:
   :member-order: bysource

Colours
===========

.. automodule:: lux.extensions.ui.lib.colorvar
   :members:
   :member-order: bysource

Mixins
=========================

.. automodule:: lux.extensions.ui.lib.mixins
   :members:
   :member-order: bysource

'''
import lux
from lux import Parameter

from .lib import *


class Extension(lux.Extension):

    _config = [
        Parameter('FONTAWESOME',
            '//netdna.bootstrapcdn.com/font-awesome/4.2.0/css/font-awesome',
            'FONTAWESOME url. Set to none to not use it.'),
        Parameter('BOOTSTRAP',
            '//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap',
            'Twitter bootstrap url. Set to none to not use it.'),
        Parameter('EXCLUDE_EXTENSIONS_CSS', None,
                  'Optional list of extensions to exclude form the css')]

    def on_html_document(self, app, request, doc):
        for name in ('BOOTSTRAP', 'FONTAWESOME'):
            doc.head.links.append(app.config[name])


def add_css(all):
    css = all.css
    vars = all.variables

    colors(all)

    vars.font_family = '"Helvetica Neue",Helvetica,Arial,sans-serif'
    vars.font_size = px(14)
    vars.line_height = 1.42857
    vars.font_style = 'normal'
    vars.color = color('#333')
    vars.background = color('#fff')
    # Helper classes
    vars.push_bottom = '20px !important'

    css('.push-bottom',
        margin_bottom=vars.push_bottom)

    # SKINS
    skins = all.variables.skins
    default = skins.default
    default.background = color('#f7f7f9')

    inverse = skins.inverse
    inverse.background = color('#3d3d3d')

    css('body',
        font_family=vars.font_family,
        font_size=vars.font_size,
        line_height=vars.line_height,
        font_style=vars.font_style,
        background=vars.background,
        color=vars.color)

    css('.form-group .help-block',
        display='none')

    css('.form-group.has-error .help-block.active',
        display='block')

    css('.nav-second-level li a',
        padding_left=px(37))

    # a class for setting the aspect ratio of a container
    # put class <div style="padding-top:75%"></div>
    # follow by <div class="absolute-full"></div>
    # to get a 4:3 aspect ratio
    css('.absolute-full',
        position='absolute',
        top=0, bottom=0)


def colors(all):
    vars = all.variables
    black = color('#000')

    vars.colors.gray_darker = lighten(black, 13.5)
    vars.colors.gray_dark = lighten(black, 20)
    vars.colors.gray = lighten(black, 50)
    vars.colors.gray_light = lighten(black, 70)
    vars.colors.gray_lighter = lighten(black, 93.5)
