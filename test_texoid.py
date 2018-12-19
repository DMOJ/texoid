import argparse
import glob
import os
from base64 import b64decode

import requests

SAMPLE_LATEX_DIR = os.path.join(os.path.dirname(__file__), 'tests')


def main():
    parser = argparse.ArgumentParser(description='Texoid testing program.')
    parser.add_argument('url', help='the URL on which Texoid runs')
    args = parser.parse_args()

    for file in glob.iglob(os.path.join(SAMPLE_LATEX_DIR, '*.tex')):
        print('Testing Texoid rendering:', file)
        with open(file, 'rb') as f:
            body = f.read()

        resp = requests.post(args.url, data=body, headers={
            'Content-Type': 'text/plain'
        })
        resp.raise_for_status()
        data = resp.json()

        assert data['success']
        assert 'png' in data
        assert b64decode(data['png'].encode('ascii')).startswith(b'\x89PNG')
        assert 'svg' in data
        assert '<svg' in data['svg']
        assert 'meta' in data
        assert 'width' in data['meta']
        assert 'height' in data['meta']
        assert isinstance(data['meta']['width'], int)
        assert isinstance(data['meta']['height'], int)


if __name__ == '__main__':
    main()
