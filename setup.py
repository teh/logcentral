from distutils.core import setup

setup(name='logcentral-logshipper',
      version='1.0',
      description='Ship systemd logs to logcentral',
      author='Tom Hunger',
      author_email='tehunger@gmail.com',
      url='https://github.com/teh/',
      packages=['logshipper'],
      scripts=[
          'logshipper/logshipper-daemon.py',
          'logshipper/logcentral-cli.py',
      ],
)
