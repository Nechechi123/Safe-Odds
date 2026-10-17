"""
Static file storage backends for the project.

Production uses WhiteNoise's compressed, hash-versioned static storage. The
hash manifest is produced by `collectstatic` during the build (see build.sh).

Django's stock storage raises ValueError when the manifest or a file is
missing, which breaks page rendering when tests run without a prior
`collectstatic`. This subclass falls back to the original file name in that
case, while keeping compression and cache-busting in production.
"""

from whitenoise.storage import CompressedManifestStaticFilesStorage as WhiteNoiseStorage


class CompressedManifestStaticFilesStorage(WhiteNoiseStorage):
    manifest_strict = False

    def stored_name(self, name):
        try:
            return super().stored_name(name)
        except ValueError:
            # Manifest or source file unavailable (e.g. running tests without
            # collectstatic). Fall back to the un-hashed name so pages render.
            return name
