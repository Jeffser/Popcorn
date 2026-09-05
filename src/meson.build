pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'popcorn'
gnome = import('gnome')

blueprints = files(
  'ui/window.blp',
  'ui/preferences.blp',
  'ui/shortcuts-dialog.blp',

  'ui/pages/login.blp',
  'ui/pages/home.blp',
  'ui/pages/search.blp',
  'ui/pages/wrapbox_page.blp',
  'ui/pages/welcome.blp',
  'ui/pages/main.blp',
  'ui/pages/libraries.blp',

  'ui/misc/user_view_button.blp',
  'ui/misc/overview_carousel.blp',

  'ui/series/overview.blp',
  'ui/series/button.blp',
  'ui/series/page.blp',

  'ui/episode/button.blp',
  'ui/episode/page.blp',

  'ui/movie/button.blp',
  'ui/movie/page.blp',

  'ui/season/button.blp',
  'ui/season/page.blp',

  'ui/player/page.blp',
  'ui/player/window.blp',
  'ui/player/next_up_button.blp',

  'ui/containers/carousel.blp',
  'ui/containers/wrapbox.blp',
)

blueprints = custom_target('blueprints',
  input: blueprints,
  output: '.',
  command: [
    find_program('blueprint-compiler', version: '>= 0.18.0'),
    'batch-compile',
    '@OUTPUT@',
    '@CURRENT_SOURCE_DIR@',
    '@INPUT@'
  ],
)

gnome.compile_resources('popcorn',
  'popcorn.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
  dependencies: blueprints,
  source_dir: meson.current_source_dir(),
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'popcorn.in',
  output: 'popcorn',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x'
)

configure_file(
  input: 'popcorn_search_provider.py.in',
  output: 'popcorn_search_provider',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x'
)

popcorn_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'constants.py',
  'actions.py',
  'preferences.py',
]

install_data(popcorn_sources, install_dir: moduledir)

subdir('widgets')
subdir('integrations')
