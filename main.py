# -*- coding: utf-8 -*-
import cgi
import os

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine._internal.django.conf import settings


class PostData(db.Model):
    filename = db.StringProperty(multiline=True)
    filedata = db.BlobProperty()
    filemimetype = db.StringProperty(multiline=False)


class Root(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'fileup.html')
        self.response.out.write(template.render(path, {}))


class Result(webapp.RequestHandler):
    def get(self):
        info = dict()
        query_str = "SELECT * FROM PostData"
        datum = db.GqlQuery(query_str)
        items = []
        for data in datum:
            iteminfo = {}
            iteminfo['id'] = data.key()
            iteminfo['filename'] = self.esc(data.filename)
            iteminfo['filedata'] = self.esc(data.filedata)
            iteminfo['filemimetype'] = self.esc(data.filemimetype)

            items.append(iteminfo)
        info['items'] = items

        path = os.path.join(os.path.dirname(__file__), 'fileall.html')
        self.response.out.write(template.render(path, info))

    def esc(self, data):
        return cgi.escape(data) if data else ""


class Upload(webapp.RequestHandler):
    def post(self):
        postdata = PostData()

        f = self.request.POST['file']
        try:
            postdata.filename = f.filename
            postdata.filedata = db.Blob(f.file.read())
            postdata.filemimetype = f.type
        except:
            pass
        postdata.put()

        self.redirect('/')


class Download(webapp.RequestHandler):
    def get(self):
        postdata = db.get(self.request.get("id"))
        data = postdata.filedata
        mime = str(postdata.filemimetype)

        self.response.headers['Content-Type'] = mime
        self.response.out.write(data)


class Delete(webapp.RequestHandler):
    def get(self):
        postdata = db.get(self.request.get("id"))
        postdata.delete()
        self.redirect('/get')


app = webapp.WSGIApplication([
                                 ('/', Root),
                                 ('/get', Result),
                                 ('/upload', Upload),
                                 ('/download', Download),
                                 ('/delete', Delete),
                             ], debug=True)


def main():
    settings.configure(TEMPLATE_DEBUG=True)
    run_wsgi_app(app)


if __name__ == '__main__':
    main()
