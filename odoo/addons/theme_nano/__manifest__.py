{
    'name': 'Nano Theme',
    'description': 'Nano Theme - Responsive Bootstrap Theme for Odoo CMS',
    'category': 'Theme/Lifestyle',
    'summary': 'Maker, Agencies, Creative, Design, IT, Services, Fancy',
    'sequence': 270,
    'version': '2.0.0',
    'author': 'Odoo S.A.',
    'depends': ['theme_common'],
    'data': [
        'data/ir_asset.xml',
        'views/images_library.xml',

        'views/snippets/s_banner.xml',
        'views/snippets/s_carousel.xml',
        'views/snippets/s_cover.xml',
        'views/snippets/s_features.xml',
        'views/snippets/s_image_text.xml',
        'views/snippets/s_images_wall.xml',
        'views/snippets/s_parallax.xml',
        'views/snippets/s_references.xml',
        'views/snippets/s_text_block.xml',
        'views/snippets/s_text_image.xml',
        'views/snippets/s_three_columns.xml',
    ],
    'images': [
        'static/description/nano_cover.gif',
        'static/description/nano_screenshot.jpg',
    ],
    'images_preview_theme': {
        'website.s_cover_default_image': '/theme_nano/static/src/img/snippets/s_cover.jpg',
        'website.library_image_10': '/theme_nano/static/src/img/snippets/s_images_wall_01.jpg',
        'website.library_image_05': '/theme_nano/static/src/img/snippets/s_images_wall_02.jpg',
        'website.library_image_08': '/theme_nano/static/src/img/snippets/s_images_wall_03.jpg',
        'website.library_image_13': '/theme_nano/static/src/img/snippets/s_images_wall_04.jpg',
        'website.library_image_03': '/theme_nano/static/src/img/snippets/s_images_wall_05.jpg',
        'website.library_image_02': '/theme_nano/static/src/img/snippets/s_images_wall_06.jpg',
        'website.s_parallax_default_image': '/theme_nano/static/src/img/snippets/s_parallax.jpg',
        'website.s_reference_demo_image_1': '/theme_nano/static/src/img/snippets/s_reference_01.png',
        'website.s_reference_demo_image_2': '/theme_nano/static/src/img/snippets/s_reference_02.png',
        'website.s_reference_demo_image_3': '/theme_nano/static/src/img/snippets/s_reference_03.png',
        'website.s_reference_demo_image_4': '/theme_nano/static/src/img/snippets/s_reference_04.png',
        'website.s_reference_demo_image_5': '/theme_nano/static/src/img/snippets/s_reference_05.png',
        'website.s_reference_default_image_6': '/theme_nano/static/src/img/snippets/s_reference_06.png',
    },
    'snippet_lists': {
        'homepage': ['s_cover', 's_features', 's_text_block', 's_images_wall', 's_parallax', 's_references'],
    },
    'license': 'LGPL-3',
    'live_test_url': 'https://theme-nano.odoo.com',
    'assets': {
        'website.assets_editor': [
            'theme_nano/static/src/js/tour.js',
        ],
    }
}
