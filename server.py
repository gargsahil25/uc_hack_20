#!/usr/bin/env python3
 
import os
import posixpath
import http.server
import urllib.request, urllib.parse, urllib.error
import cgi
import shutil
import mimetypes
import re
import img_proc
from io import BytesIO

class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
 
    """Simple HTTP request handler with GET/HEAD/POST commands.

    This serves files from the current directory and any of its
    subdirectories.  The MIME type for files is determined by
    calling the .guess_type() method. And can reveive file uploaded
    by client.

    The GET/HEAD/POST requests are identical except that the HEAD
    request omits the actual contents of the file.

    """
 
    def do_GET(self):
        """Serve a GET request."""
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
            f.close()
 
    def do_HEAD(self):
        """Serve a HEAD request."""
        f = self.send_head()
        if f:
            f.close()
 
   
    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """

        if self.path.__eq__('/') or self.path.startswith('/?'):
            img = 'img2.jpg'
            if self.path.startswith('/?'):
                param_map_arr = self.path.replace('/?','')
                param_map = param_map_arr.split('&')
                dict = {}
                for elem in param_map:
                    item = elem.split('=')
                    dict[item[0]] = item[1]
                if dict.get('img') != None:
                    img = dict['img']
                if 'color' in dict:
                    img_proc.changeColor(img, (300,100), dict['color'].split(','), None)
                elif 'pattern'in dict:
                    img_proc.changeColor(img, (300,100), None, dict['pattern'])
            self.path = './public/images/' + self.path
            path = self.translate_path(self.path)
            return self.list_directory(path, img)
        
        self.path = './public/' + self.path
        path = self.translate_path(self.path)

        f = None
        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f
 
    def list_directory(self, path, img):
        """Helper to produce a directory listing (absent index.html).

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        f = BytesIO()
        displaypath = cgi.escape(urllib.parse.unquote(self.path))
        f.write(b'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write(("<html>\n<title>LN2</title><link rel='stylesheet' href='/css/index.css'/><script src='https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js'></script><script type='text/javascript' src='/js/index.js'></script>\n<body>\n").encode())
        f.write(b"<h1>LN2 - What's cooler than Liquid Nitrogen</h1><hr>")
        
        f.write(b"<div class='inline'>\n")
        f.write(b"<h3> Sample Images </h3>")

        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            f.write(('<span><img class="sample" src="/images/%s"/ data-name="%s" data-key="img"></span>'
                    % (urllib.parse.quote(linkname), linkname)).encode())
        f.write(b"</div>")
        f.write(b"<div class='inline'>")
        f.write(b"<h3> Choose colors </h3>")
        f.write(b"<span class='sample c1' data-name='220,180,170' data-key='color'></span>")
        f.write(b"<span class='sample c2' data-name='220,99,78' data-key='color'></span>")
        f.write(b"<span class='sample c3' data-name='135,168,161' data-key='color'></span>")
        f.write(b"<span class='sample c4' data-name='220,180,170' data-key='color'></span>")
        f.write(b"<span class='sample c5' data-name='107,148,109' data-key='color'></span>")
        f.write(b"</div>")
        f.write(b"<div class='inline'>")
        f.write(b"<h3> Choose patterns </h3>")
        f.write(b"<span><img class='sample' src='/patterns/pattern1.jpg' data-name='pattern1.jpg' data-key='pattern'/></span>")
        f.write(b"<span><img class='sample' src='/patterns/pattern2.jpg' data-name='pattern2.jpg' data-key='pattern'/></span>")
        f.write(b"<span><img class='sample' src='/patterns/pattern3.jpg' data-name='pattern3.jpg' data-key='pattern'/></span>")
        f.write(b"<span><img class='sample' src='/patterns/pattern4.jpg' data-name='pattern4.jpg' data-key='pattern'/></span>")
        f.write(b"</div>")
        f.write(("<div><img class='main' src='/images/%s'/><img class='main' src='/edited/%s'/></div>" % (img, img)).encode())
        f.write(b"</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f
 
    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = [_f for _f in words if _f]
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path
 
    def copyfile(self, source, outputfile):
        """Copy all data between two file objects.

        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).

        The only reason for overriding this would be to change
        the block size or perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data as well.

        """
        shutil.copyfileobj(source, outputfile)
 
    def guess_type(self, path):
        """Guess the type of a file.

        Argument is a PATH (a filename).

        Return value is a string of the form type/subtype,
        usable for a MIME Content-type header.

        The default implementation looks the file's extension
        up in the table self.extensions_map, using application/octet-stream
        as a default; however it would be permissible (if
        slow) to look inside the data to make a better guess.

        """
 
        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']
 
    if not mimetypes.inited:
        mimetypes.init() # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream', # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
        })
 
 
def test(HandlerClass = SimpleHTTPRequestHandler,
         ServerClass = http.server.HTTPServer):
    http.server.test(HandlerClass, ServerClass)
 
if __name__ == '__main__':
    test()