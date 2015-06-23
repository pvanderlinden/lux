from lux.extensions.ui.lib import *     # noqa


def add_css(all):
    '''Css rules for sidebar
    '''
    css = all.css
    media = all.media
    vars = all.variables
    cfg = all.app.config

    # Sidebar variables container
    navbar = vars.navbar
    sidebar = vars.sidebar
    sidebar.width = px(250)
    sidebar.toggle.margin = px(15)
    sidebar.toggle.size = px(22)
    sidebar.toggle.padding = 0.5*(navbar.height-sidebar.toggle.size)

    collapse_width = px(cfg['NAVBAR_COLLAPSE_WIDTH'])

    media(min_width=collapse_width).css(
        '.sidebar',
        width=sidebar.width)

    media(min_width=collapse_width).css(
        '.navbar.navbar-static-top .navbar-nav',
        css('> li > a.sidebar-toggle',
            font_size=sidebar.toggle.size,
            line_height=sidebar.toggle.size,
            padding_top=sidebar.toggle.padding,
            paddint_bottom=sidebar.toggle.padding))

    css('.overlay',
        position='absolute',
        background_color='transparent',
        display='none',
        width='100%',
        bottom=px(0),
        left=px(0),
        top=px(0),
        z_index=800)

    css('.content-wrapper',
        z_index=800)

    css('a',
        color=color('#3c8dbc'))

    css('a:hover, a:active, a:focus',
        outline='none',
        color=color('#72afd2'),
        text_decoration='none')

    css('.main-sidebar',
        position='absolute',
        overflow_y='auto',
        overflow_x='hidden',
        top=px(0),
        min_height='100%',
        width=sidebar.width,
        z_index=810)

    css('.right-sidebar',
        css(' .content-wrapper, .navbar-static-top',
            transform='translate(0px, 0px)',
            transition='transform 0.15s cubic-bezier(0.2, 0.3, 0.25, 0.9) 0s'),
        css(' .main-sidebar',
            transform='translate(250px, 0px)',
            transition='transform 0.15s cubic-bezier(0.2, 0.3, 0.25, 0.9) 0s',
            right=0),
        css(' .navbar-static-top',
            css(' .navbar-main',
                css(' > li',
                    float='right'),
                float='right'),
            css(' .navbar-side',
                float='left'),
            css(' .sidebar-toggle',
                margin_left=sidebar.toggle.margin,
                border_left='1px solid #ddd')),
        )

    css('.left-sidebar',
        css(' .content-wrapper, .navbar-static-top',
            transform='translate(0px, 0px)',
            transition='transform 0.15s cubic-bezier(0.2, 0.3, 0.25, 0.9) 0s'),
        css(' .main-sidebar',
            transform='translate(-250px, 0px)',
            transition='transform 0.15s cubic-bezier(0.2, 0.3, 0.25, 0.9) 0s',
            left=0),
        css(' .navbar-static-top',
            css(' .navbar-main',
                css(' > li',
                    float='left'),
                float='left'),
            css(' .navbar-side',
                float='right'),
            css(' .sidebar-toggle',
                margin_right=sidebar.toggle.margin,
                border_right='1px solid #ddd')),
        )

    css('.sidebar-open-left',
        css(' .overlay',
            display='block',
            background_color='rgba(0, 0, 0, 0.1)'),
        css(' .navbar-side',
            display='none'),
        css(' .content-wrapper, .navbar-static-top',
            transform='translate(250px, 0px)',
            transition='transform 0.15s cubic-bezier(0.2, 0.3, 0.25, 0.9) 0s'),
        css(' .main-sidebar',
            Transform(x=px(0), y=px(0))),
        )

    css('.sidebar-open-right',
        css(' .overlay',
            display='block',
            background_color='rgba(0, 0, 0, 0.1)'),
        css(' .navbar-side',
            display='none'),
        css(' .content-wrapper, .navbar-static-top',
            transform='translate(-250px, 0px)',
            transition='transform 0.15s cubic-bezier(0.2, 0.3, 0.25, 0.9) 0s'),
        css(' .main-sidebar',
            Transform(x=px(0), y=px(0)))
        )

    css('.sidebar-fixed',
        position='fixed'),

    css('.sidebar',
        css(' .nav-panel',
            css(':before, :after',
                content='\"\"',
                display='table'),
            css(':after',
                clear='both'),
            css(' .image > img',
                width=px(35),
                height=px(35),
                margin_top=px(8),
                margin_left=px(8)),
            css(' .info',
                css(' > p',
                    margin_bottom=px(4),
                    margin_top=px(5),
                    color=color('#ccc'),
                    font_size=px(11)),
                css(' > a',
                    css(' .fa',
                        margin_right=px(3)),
                    color=color('#fff'),
                    text_decoration='none',
                    padding_right=px(5),
                    font_weight=600,
                    font_size=px(15)),
                padding=spacing(5, 5, 5, 15),
                line_height=1),
            padding=spacing(3, 10),
            height=navbar.height,
            background=color('#425466')),
        css(' .sidebar-menu',
            css(' .treeview-menu',
                css('.active',
                    opacity=1,
                    height='100%'),
                css(' .treeview-menu',
                    padding_left=px(20)),
                css(' > li',
                    css(' > a',
                        css(' > .fa',
                            width=px(20)),
                        css(' > .fa-angle-left, > .fa-angle-down',
                            width='auto'),
                        padding=spacing(5, 5, 5, 18),
                        display='block',
                        font_size=px(14)),
                    margin=px(0)),
                list_style='none',
                padding=px(0),
                margin=px(0),
                padding_left=px(5),
                opacity=0,
                height=px(0),
                _webkit_transition='0.2s linear',
                _moz_transition='0.2s linear',
                _ms_transition='0.2s linear',
                _o_transition='0.2s linear',
                transition='0.2s linear'),
            css(' li',
                css('.active',
                    css(' > a > .fa-angle-left',
                        _webkit_transform='rotate(-90deg)',
                        _ms_transform='rotate(-90deg)',
                        _o_transform='rotate(-90deg)',
                        transform='rotate(-90deg)')),
                css('.header',
                    padding=spacing(5, 25, 5, 15),
                    font_size=px(12)),
                css(' .label',
                    margin_top=px(3),
                    margin_right=px(5)),
                css(' > a',
                    css(' > .fa-angle-left',
                        width='auto',
                        height='auto',
                        padding=px(0),
                        margin_right=px(10),
                        margin_top=px(3)),
                    css(' > .fa',
                        width=px(20)),
                    padding=spacing(8, 5, 8, 15),
                    display='block'),
                position='relative',
                margin=px(0),
                padding=px(0),
                width=sidebar.width),
            list_style='none',
            margin=px(0),
            padding=px(0)),
        margin_top=px(0),
        padding_bottom=px(10))

    media(max_width=collapse_width).css(
        '.right-sidebar',
        css(' .navbar-static-top',
            css(' .navbar-main',
                float='right',
                margin_right=px(1)))).css(
        '.left-sidebar',
        css(' .navbar-static-top',
            css(' .navbar-main',
                float='left',
                margin_left=px(1))))

    sidebar_skin(all)


def sidebar_skin(all):
    '''Sidebar default skin styles
    '''
    css = all.css
    sidebar = all.variables.sidebar

    # Dark skin
    default = sidebar.skins.default
    default.border_color = '#eee'
    default.border_size = 1
    default.color = '#eee'
    default.background = '#2D3C4B'

    default.header.background = '#fff'
    default.header.color = '#eee'

    default.menu.link.color = '#fff'
    default.menu.link.background = '#263647'
    default.menu.link.border_color = '#fff'
    default.menu.section.color = '#fff'
    default.menu.section.background = '#243241'

    default.toggle.link.color = '#333'
    default.toggle.link.color_hover = '#999'
    default.toggle.link.background_hover = '#fff'

    default.treeview.background = '#3E5165'
    default.treeview.link.color = '#ccc'
    default.treeview.link.color_active = '#fff'

    if not sidebar.skin or sidebar.skin == 'default':
        skin = default
    else:
        skin = sidebar.skins[sidebar.skin]

    css('.skin',
        css(' .main-sidebar',
            background=skin.background),
        css(' .sidebar',
            css(' a',
                css(':hover',
                    text_decoration='none'),
                color=skin.color),
            css(' > .sidebar-menu',
                css(' > li',
                    css(' > .treeview-menu',
                        background=skin.treeview.background),
                    css('.active > a',
                        color=skin.menu.link.color,
                        background=skin.menu.link.background,
                        border_left_color=skin.menu.link.border_color),
                    css(' > a',
                        css(':hover',
                            color=skin.menu.link.color,
                            background=skin.menu.link.background,
                            border_left_color=skin.menu.link.border_color),
                        margin_right=px(1),
                        border_left='3px solid transparent',
                        font_size=px(15)),
                    css('.header',
                        background=skin.menu.section.background,
                        color=skin.menu.section.color),
                    ))),
        css(' .treeview-menu',
            css(' > li',
                css('.active > a',
                    color=skin.treeview.link.color_active),
                css(' > a',
                    css(':hover',
                        color=skin.treeview.link.color_active),
                    color=skin.treeview.link.color),
                ))
        )