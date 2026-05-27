moduledir = get_option('prefix') / get_option('datadir') / meson.project_name() / 'popcorn' / 'integrations'

widgets = [
  '__init__.py',
  'secret.py',
  'models.py',
  'jellyfin.py',
]

install_data(widgets, install_dir: moduledir)
