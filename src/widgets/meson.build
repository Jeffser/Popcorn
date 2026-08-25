moduledir = get_option('prefix') / get_option('datadir') / meson.project_name() / 'popcorn' / 'widgets'

widgets = [
  '__init__.py',
]

install_data(widgets, install_dir: moduledir)

subdir('pages')
subdir('misc')
subdir('series')
subdir('containers')
subdir('episode')
subdir('movie')