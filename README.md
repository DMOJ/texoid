# Texoid
Python server for LaTeX math rendering to SVG and PNG.
It is lightweight and perfect for embedding LaTeX documents into webpages, without the hassle of rendering the documents yourself.

## Installation
Texoid is super simple to set up and use.

```shell
$ git clone https://github.com/DMOJ/texoid.git
$ cd texoid
$ python setup.py develop
```

Texoid relies on LaTeX to render documents to DVI format, dvisvgm to convert to SVGs, and ImageMagick to convert SVGs into PNGs. On a typical Debian or Ubuntu machine, you can fetch everything you need with:

```shell
$ apt-get install texlive-latex-base texlive-binaries imagemagick
```

## Running Texoid
To start the Texoid server, simply run:
```shell
$ LATEX_BIN=<path to latex> DVISVGM_BIN=<path to dvisvgm> CONVERT_BIN=<path to convert> texoid --port=<port>
```

The environment variables are not necessary if all three executables are present in `/usr/bin`. Here, `convert` refers to ImageMagick's `convert` tool.

## Using Texoid
Texoid expects POST data containing one argument, `q`: the LaTeX document to render.

### Response
The response will always contain a boolean field, `success`.

If `success` is `true`:

* `svg` will contain the SVG source of the rendered document
* `png` will contain a Base64-encoded binary PNG file
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

#### With cURL

##### A successful render
```shell
$ curl --data 'q=%5Cdocumentclass%7Bstandalone%7D%0A%5Cbegin%7Bdocument%7D%0A%24E%3Dmc%5E2%24%0A%5Cend%7Bdocument%7D' localhost:8888
{"success": true, "svg": "<?xml version='1.0'?><svg....</svg>", "png": "iVBORw0KGgoA....kSuQmCC\n", "meta": {"width": "48", "height": "10"}}
```

##### A malformed request
```shell
$ curl --data 'q=malformed' localhost:8888
{"success": false, "error": "This is pdfTeX, Version 3.14159265-2.6-1.40.15...LaTeX Error: Missing \\begin{document}..."}
```

And that's it!
