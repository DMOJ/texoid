# Texoid
Python server for LaTeX math rendering to SVG and PNG.

Texoid is super simple to set up and use.

## Installation
```shell
$ git clone https://github.com/DMOJ/texoid.git
$ cd texoid
$ python setup.py develop
```

## Running Texoid
To start the Texoid server, simply run:
```shell
$ LATEX_BIN=<path to latex> DVISVGM_BIN=<path to dvisvgm> CONVERT_BIN=<path to convert> texoid --port=<port> 
```

The environment variables are not necessary if all three executables are present in `/usr/bin`. Here, `convert` refers to ImageMagick's `convert` tool, with `rsvg` enabled.

## Using Texoid
Texoid expects POST data containing one argument, `q`: the LaTeX document to render.

It returns `success`: `true` if LaTeX rendering was successful, as well as two nodes `svg` and `png`. `svg` contains the SVG source, while `png` contains a Base64-encoded binary PNG file. If `success` is `false`, the response will contain an `error` field with the LaTeX error output.

In these examples, a Texoid server is assumed to be running on `localhost`, port 8888. We will be rendering a simple LaTeX document:

```latex
\documentclass{standalone}
\begin{document}
$E=mc^2$
\end{document}
```

### With cURL

#### A successful render
```shell
$ curl --data 'q=%5Cdocumentclass%7Bstandalone%7D%0A%5Cbegin%7Bdocument%7D%0A%24E%3Dmc%5E2%24%0A%5Cend%7Bdocument%7D' localhost:8888
{"svg": "<?xml version='1.0'?><svg....</svg>", "png": "iVBORw0KGgoA....kSuQmCC\n", "success": true}
```

#### A malformed request
```shell
$ curl --data 'q=malformed' localhost:8888
{"success": false, "error": "This is pdfTeX, Version 3.14159265-2.6-1.40.15...LaTeX Error: Missing \\begin{document}..."}
```

And that's it!
