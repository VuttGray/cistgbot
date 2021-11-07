from os.path import join, dirname

from setuptools import setup, find_packages

import cistgbot


def get_requirements():
    """Collect the requirements list for the package"""
    requirements = []
    with open('requirements.txt') as f:
        for requirement in f:
            requirements.append(requirement.strip())
    return requirements


def main():
    requirements = get_requirements()
    packet_name = cistgbot.__name__
    setup(
        name=packet_name,
        version=cistgbot.__version__,
        author='Denis Stepanov',
        author_email='denis.stepanov@psi-cro.com',
        packages=find_packages(),
        long_description=open(join(dirname(__file__), 'README.md')).read(),
        install_requires=requirements,
        entry_points={
            'console_scripts':
                [f'configure = {packet_name}:configure',
                 f'send_message = {packet_name}:send_message',
                 f'run = {packet_name}.bot:run']
        }
    )


if __name__ == "__main__":
    main()
