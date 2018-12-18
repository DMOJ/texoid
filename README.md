# Texoid
Python server for LaTeX math rendering to SVG and PNG.
It is lightweight and perfect for embedding LaTeX documents into webpages, without the hassle of rendering the documents yourself.

## Installation
Texoid is super simple to set up and use.

```shell
$ pip install texoid
```

Texoid uses [`texbox`](https://github.com/DMOJ/texbox), a Docker image built for converting LaTeX documents to SVG and PNG securely, without exposing your system to malicious LaTeX code. To use Texoid with `texbox`, [install Docker](https://docs.docker.com/install/).

Alternatively, Texoid can directly use LaTeX to render documents to DVI format, `dvisvgm` to convert to SVGs, and ImageMagick to convert SVGs into PNGs. On a typical Debian or Ubuntu machine, you can the dependencies for this with:

```shell
$ apt-get install texlive-latex-base texlive-binaries imagemagick
```

## Running Texoid

### With Docker
To run Texoid with Docker, simply run the following command with a user in the `docker` group:

```shell
$ texoid --port=<port> --docker
```

This will automatically pull the latest `texbox` image and start using it.

### Without Docker
To start the Texoid without Docker, use:

```shell
$ LATEX_BIN=<path to latex> DVISVGM_BIN=<path to dvisvgm> CONVERT_BIN=<path to convert> texoid --port=<port>
```

The environment variables are not necessary if all three executables are present in `/usr/bin`. Here, `convert` refers to ImageMagick's `convert` tool.

## Using Texoid

Texoid expects POST body to contain the LaTeX document to render. You should send the request with an appropriate `Content-Type`, for example, `text/plain`, `application/x-tex`, or `text/x-tex`. Do not use `application/x-www-form-urlencoded`.

Texoid also has a legacy API. This API uses `application/x-www-form-urlencoded` as `Content-Type`, and sends the LaTeX code form-encoded in the `q` field.

### Response
The response will always contain a boolean field, `success`.

If `success` is `true`:

* `svg` will contain the SVG source of the rendered document
* `png` will contain a base64-encoded binary PNG file
* `meta` will be a dict containing two entries:
  * `width`, the width of the rendered document in pixels
  * `height`, the height of the rendered document, again in pixels
  * these arguments are what the SVG/PNGs generated should be sized by to display properly in webpages

If `success` is `false`, the response will contain an `error` field with the LaTeX error output.

### Examples
In these examples, a Texoid server is assumed to be running on `localhost`, port 8888. We will be rendering a simple LaTeX document:

```latex
\documentclass{standalone}
\begin{document}
$E=mc^2$
\end{document}
```

#### A successful render
```shell
$ curl -H 'Content-Type: text/plain' --data-raw '\documentclass{standalone}\begin{document}$E=mc^2$\end{document}' localhost:8888
{"success": true, "svg": "<?xml version='1.0'?><svg....</svg>", "png": "iVBORw0KGgoA....RK5CYII=", "meta": {"width": "48", "height": "10"}}
```

#### A malformed request
```shell
$ curl -H 'Content-Type: text/plain' --data 'malformed' localhost:8888
{"success": false, "error": "This is pdfTeX, Version 3.14159265-2.6-1.40.15...LaTeX Error: Missing \\begin{document}..."}
```

And that's it!
