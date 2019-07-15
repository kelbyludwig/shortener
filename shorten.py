import hashlib
import random
from urllib.parse import urlparse
from flask import Flask, request, redirect

try:
    import config
except ImportError:
    print("error: config.py not found!")
    import sys
    sys.exit(1)

URLS = {}

app = Flask(__name__)

def render(string):
    s = """
    <html>
        <body>
            <style>
                body { margin: 1em; max-width: 50em; font-family: "Arial", sans-serif; font-size: 1.2em; line-height: 1.2; }
            </style>
            %s
        </body>
    </html>
    """
    return s % string

def path_hash(url):
    h = hashlib.md5()
    h.update(url.encode('utf-8'))
    r = random.Random(h.digest())
    choices = []
    for _ in range(config.PATH_SIZE):
        choices.append(r.choice(config.CHARSET))
    return ''.join(choices)

@app.route("/", methods=["GET"])
def shorten():
    url = request.args.get('u', None)
    if not url:
        return render('missing "u" parameter')

    # scheme-less urls will be treated as a redirect on the same domain, so add
    # a scheme.
    if not urlparse(url).scheme:
        url = 'https://' + url

    path = path_hash(url)
    app.logger.info('shortened url %s to path %s' % (url, path))
    URLS[path] = url
    return render(config.DOMAIN + '/%s' % path)

@app.route("/<path>", methods=["GET"])
def unshorten(path):
    url = URLS.get(path, None)
    if not url:
        return render('not found')
    return redirect(url)

if __name__ == "__main__":
    app.run()
