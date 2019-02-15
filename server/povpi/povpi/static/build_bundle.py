"""
    povpi/static/build_bundle.py
    Uploads bundle to AWS S3 Resource
"""

from pathlib import Path

import boto3


def main():
    """upload bundled js to s3 resource bucket"""
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('povpi-resources')
    bundle = Path().cwd() / 'dist' / 'bundle.js'
    if not bundle.exists():
        raise AttributeError('bundle.js does not exist!')
    key = 'js/bundle.js'
    print('Uploading bundle.js to povpi-resources s3 Bucket...')
    bucket.upload_file(str(bundle.resolve()), key,
                       ExtraArgs={'ACL': 'public-read'})

    print('Complete!')


if __name__ == "__main__":
    main()
