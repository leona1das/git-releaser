#!/bin/env python
"""
Module for bumping release
"""
import re
import sys
import os
import git


class NewReleaseError(Exception):
    """
    Exception raised for NewRelease Class
    """
    pass


class NewRelease:
    """
    Class for bumping package version
    Releases should have the structure x.y.z
    x indicates major version,
    y indicates minor version,
    z indicates patch version
    """
    # pylint: disable=anomalous-backslash-in-string
    # This regex is correct, we need to escape . for it to work
    __VERSION_STRING = '[0-9]+\.[0-9]+\.[0-9]+'
    __BUMP_VERSIONS = ['major', 'minor', 'patch']
    __SETUP_FILE = 'setup.py'

    def __init__(self):
        self.current_version = self.extract_current_version()
        self.repo = git.Repo(os.getcwd())

    def get_version_from_line(self, line):
        """
        Find the current version number using regex
        :param line: Line to search for the version number
        :return: Version found
        """
        try:
            version = re.search(self.__VERSION_STRING, line).group(0)
        except (AttributeError, IndexError):
            version = None
        return version

    def extract_current_version(self):
        """
        Extract the version from __SETUP_FILE
        :return: Version if found
        """
        current_version = None
        with open(self.__SETUP_FILE) as in_file:
            for line in in_file:
                if 'version=' in line:
                    current_version = self.get_version_from_line(line)
                    break
        self.validate_release_number(current_version)
        return current_version

    def validate_release_number(self, version):
        """
        Check that the version is valid
        :param version: Version to check
        :raises: NewReleaseError if invalid version
        """
        regex = re.compile('^{}$'.format(self.__VERSION_STRING))
        if not regex.match(version):
            raise NewReleaseError('Invalid release version: {}'.format(version))

    def validate_release(self, release):
        """
        Check that the bump release is valid
        :param release: New release bump
        :raises: NewReleaseError if the release is invalid
        """
        if release not in self.__BUMP_VERSIONS:
            error = 'Not a valid release. Should be one of {}'\
                .format(self.__BUMP_VERSIONS)
            raise NewReleaseError(error)

    def next_version(self, release):
        """
        Find the next version by current version and bump (release)
        Bump will update either major, minor or patch number
        :param release:
        :return: Next version
        """
        version_split = self.current_version.split('.')
        major, minor, patch = version_split
        if release == 'major':
            major = int(major) + 1
            minor = 0
            patch = 0
        if release == 'minor':
            minor = int(minor) + 1
            patch = 0
        if release == 'patch':
            patch = int(patch) + 1
        next_version = '{}.{}.{}'.format(major, minor, patch)
        return next_version

    def update_git(self, new_version):
        """
        Updates git with new commit + tag for new version
        :param new_version: New version to be used
        """
        commit_message = 'New release: v{}'.format(new_version)
        self.repo.git.commit(m=commit_message)
        self.repo.create_tag('v{}'.format(new_version))

    def update_setup_file(self, next_version):
        """
        Updates __SETUP_FILE with the new version
        :param next_version: New version to be used
        """
        lines = []
        # This requires setup.py to have a line with: version='x.y.z',
        search_string = 'version=\'{}\','.format(self.current_version)
        with open(self.__SETUP_FILE) as infile:
            for line in infile:
                if line.strip() == search_string:
                    line = line.replace(self.current_version, next_version)
                lines.append(line)
        with open(self.__SETUP_FILE, 'w') as outfile:
            for line in lines:
                outfile.write(line)
        self.repo.git.add(self.__SETUP_FILE)

    def update_version(self, release):
        """
        Updates the version of the module
        :param release: Type of release (major/minor/patch)
        """
        self.validate_release(release)
        next_version = self.next_version(release)
        self.update_setup_file(next_version)
        self.update_git(next_version)
        print('Old version: {}, new version: {}'
              .format(self.current_version, next_version))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Specify release version or bump: major/minor/patch")
    else:
        NewRelease().update_version(sys.argv[1])
