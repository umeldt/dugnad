#!/usr/bin/python
# encoding: utf-8

import os
import re
import glob
import json
import uuid
import yaml
import urllib
import logging
import datetime
import requests

from beaker.middleware import SessionMiddleware

import bottle
import bottle.ext.sqlite
from bottle import get, post, route, hook, request, redirect, run, view
from bottle import static_file, template, SimpleTemplate
from bottle_utils.i18n import I18NPlugin, i18n_path, i18n_url, lazy_gettext as _

bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024 * 16

SESSION = {
    'session.type': 'cookie',
    'session.cookie_expires': 60 * 60 * 24 * 365,
    'session.encrypt_key': "o(eaji3jgoijeh83",
    'session.validate_key': True,
}

app = bottle.default_app()
config = yaml.load(open("config.yaml"))
sqlite = bottle.ext.sqlite.Plugin(dbfile='dugnad.db')
app.install(sqlite)
app = I18NPlugin(app, config['languages'], config['languages'][0][0], "lang")
app = SessionMiddleware(app, SESSION)

logging.basicConfig(level=logging.INFO)

class Form:
    class Button:
        def __init__(self, blueprint):
            self.name = blueprint['name']
            self.type = "button"

        def tohtml(self):
            s = "<button id='%s' name='%s'>%s</button>" % (
                    self.name, self.name, _(self.name))
            return s

    class Input:
        def __init__(self, blueprint):
            self.type = blueprint['type']
            self.name = blueprint['name']
            self.size = blueprint.get('size', "24")
            self.readonly = blueprint.get('disabled')
            self.checked = False
            self.url = blueprint.get('url')
            self.pick = blueprint.get('pick')
            self.path = blueprint.get('path')
            self.value = ""

        def tohtml(self, label=True):
            s = ""
            if label and self.type != "hidden":
                s += "<label>%s</label>\n" % _(self.name)
            s += "<input type=%s name='%s'" % (self.type, self.name)
            s += " size='%s'" % self.size
            s += " id='%s'" % self.name
            if self.checked:
                s += " checked" 
            if self.value:
                s += " value='%s'" % self.value
            if self.url:
                s += " data-url='%s'" % self.url
            if self.path:
                s += " data-url='%s'" % path(self.path)
            if self.pick:
                s += " data-pick='%s'" % json.dumps(self.pick)
            if self.readonly:
                s += " readonly"
            s += ">"
            return s

    class Textfield:
        def __init__(self, blueprint):
            self.name = blueprint['name']
            self.type = "textfield"
            self.readonly = blueprint.get('disabled')
            self.value = ""

        def tohtml(self):
            s = ""
            s += "<label>%s</label>\n" % _(self.name)
            s += "<textarea name='%s'" % self.name
            if self.readonly:
                s += " readonly"
            s += ">%s</textarea>" % self.value or ""
            return s

    def __init__(self, slug, recipe):
        self.slug = slug
        self.inputs = []
        for blueprint in recipe:
            for element in self.build(blueprint):
                self.inputs.append(element)

    def build(self, blueprint):
        if blueprint['type'] == "textfield":
            return [self.Textfield(blueprint)]
        elif blueprint['type'] == "annotation":
            return [self.Input({'type': 'text',
                                'name': 'marked-pages',
                                'disabled': True
                               }),
                    self.Input({'type': 'hidden', 'name': blueprint['name']}),
                    self.Button({'name': 'mark-page'}),
                    self.Button({'name': 'removefabric'})
                   ]
        else:
            return [self.Input(blueprint)]

    def tohtml(self):
        h = ""
        for element in self.inputs: h += "<p>" + element.tohtml()
        return h

    def validate(self, request):
        for element in self.inputs:
            if element.name in request:
                if element.type == "checkbox":
                    if request[element.name]: element.checked = True
                else:
                    element.value = request[element.name]

class Changelog:
    fmt = r"(?P<date>.+):\s*(?P<text>.*)\s*\((?P<project>.*)\)"

    def __init__(self, path):
        self.changes = []
        with open(path, "r") as changefile:
            for line in list(changefile):
                match = re.match(self.fmt, line)
                if match: self.changes.append(match.groupdict())

class Post:
    @classmethod
    def find(cls, db, uuid):
        query = "select * from transcriptions where id = ?"
        row = db.execute(query, [uuid]).fetchone()
        return cls(dict(row))

    def excluded(self):
        return False

    def __init__(self, attrs, proj=None):
        for k in attrs:
            setattr(self, k, attrs[k])
        if proj:
            self.project = proj
        else:
            self.project = Project.find(self.project)
        self.annotation = json.loads(self.annotation)

    def get(self, k):
        if hasattr(self, k): return getattr(self, k)
        if k in self.annotation: return self.annotation[k]

    def path(self):
        return path("/projects/%s/%s" % (self.project.slug, self.id))

    def update(self, db, uid, data):
        # finished = not data.get('later')
        query = "delete from markings where post = ?"
        db.execute(query, [self.id])
        if 'annotation' in data:
            pages = json.loads(data['annotation'])
            for page, marks in pages.iteritems():
                self.project.addmarkings(db, self.id, uid, page, marks)
        now = str(datetime.datetime.now())
        query = "update transcriptions set annotation = ?, updated = ? where id = ?"
        db.execute(query, [json.dumps(dict(data)), now, self.id])

    def wkt(self):
        if self.annotation.get('footprintWKT'):
            return json.dumps(self.annotation['footprintWKT'])

class Project:
    @classmethod
    def find(cls, slug):
        path = "projects/%s.yaml" % slug
        return cls(path)

    def __init__(self, path):
        self.slug = os.path.splitext(os.path.basename(path))[0]
        self.hidden = False
        self.finished = False
        attrs = yaml.load(open(path, 'r'))
        for k in attrs:
            setattr(self, k, attrs[k])

    def userlog(self, db, uid):
        query = "select * from transcriptions where project = ? and user = ? order by updated desc"
        rows = db.execute(query, [self.slug, uid]).fetchall()
        posts = []
        sort = {}
        for term in self.sort:
            sort[term] = []
        for row in rows:
            post = Post(dict(row))
            for term in self.sort:
                value = post.get(term)
                if value and value not in sort[term]:
                    sort[term].append(value)
            if not post.excluded():
                posts.append(post)
        for term in self.sort:
            sort[term].sort()
        return posts, sort

    def contribute(self, db, uid, data):
        finished = not data.get('later')
        postid = str(uuid.uuid4())
        if 'annotation' in data and data['annotation']:
            pages = json.loads(data['annotation'])
            for page, marks in pages.iteritems():
                self.addmarkings(db, postid, uid, page, marks)
        now = str(datetime.datetime.now())
        query = "insert into transcriptions values(?, ?, ?, ?, ?, ?, ?, ?)"
        # id, key, user, project, date, annotation, finished, updated
        db.execute(query, [postid, "", uid, self.slug, now,
                json.dumps(dict(data)), finished, now])

    def addmarkings(self, db, postid, uid, page, data):
        # id, post, project, page, markings, user, date
        now = str(datetime.datetime.now())
        query = "insert into markings values(?, ?, ?, ?, ?, ?, ?)"
        db.execute(query, [str(uuid.uuid4()), postid, self.slug, page,
                   json.dumps(data), uid, now])

def dropcrumb(text, url=None):
    request.crumbs.append((url, text))

def path(raw):
    return i18n_path(raw)

def url(*args, **kw):
    return i18n_url(*args, **kw)

def query(raw, limitto=None):
    if limitto:
        params = {}
        for k, v in raw.iteritems():
            if k in limitto: params[k] = v
    else:
        params = raw
    return "?" + urllib.urlencode(params)

def dump(raw, exclude=['page', 'text']):
    data = dict(raw)
    for k in exclude: data.pop(k, None)
    if not data: return ""
    return json.dumps(data)

SimpleTemplate.defaults["request"] = request
SimpleTemplate.defaults["config"] = config
SimpleTemplate.defaults["crumb"] = dropcrumb
SimpleTemplate.defaults["path"] = path
SimpleTemplate.defaults["url"] = url
SimpleTemplate.defaults["dump"] = dump

@hook('before_request')
def before_request():
    request.session = bottle.request.environ.get('beaker.session')
    request.crumbs = []
    if request.session.get('oauth_service'):
        request.user = request.session['oauth_user']
        request.login = "%s (%s)" % (request.session['oauth_user'],
                                     request.session['oauth_service'])
        request.uid = "%s:%s" % (request.session['oauth_service'],
                                 request.session['oauth_id'])
    else:
        request.user = None
        request.uid = "anonymous"

@get('/')
@view('index')
def index():
    changelog = Changelog('CHANGELOG')
    projects = []
    projects = [Project(f) for f in glob.glob("projects/*.yaml")]
    return { 'changelog': changelog, 'projects': projects }

@get('/changelog')
@view('changelog')
def changelog():
    changelog = Changelog('CHANGELOG')
    return { 'changelog': changelog }

@get('/project/<slug>/overview')
@view('overview')
def overview(slug):
    project = Project.find(slug)
    return { 'project': project }

@get('/project/<slug>/markings/<page>')
def markings(slug, page, db):
    query = "select * from markings where project = ? and page = ?"
    rows = db.execute(query, [slug, page])
    results = [dict(r) for r in rows]
    return json.dumps(results)

@get('/project/<slug>/<uuid>/markings/<page>')
def markings_post(slug, page, db):
    query = "select * from markings where id = ? and page = ?"
    rows = db.execute(query, [slug, page])
    results = [dict(r) for r in rows]
    return json.dumps(results)

@get('/project/<slug>')
def project(slug):
    def document(project):
        forms = [Form(form, project.forms[form]) for form in project.order]
        [form.validate(request.query) for form in forms]
        return template("document", { 'project': project, 'forms': forms })
    
    def transcribe(project):
        pass

    project = Project.find(slug)
    dispatch = {
        'document': document,
        'transcription': transcribe
    }
    return dispatch[project.type](project)

@post('/project/<slug>')
def transcribe(slug, db):
    project = Project.find(slug)
    base = request.headers['referer'].split("?")[0]
    if 'skip' in request.forms: redirect(base)
    project.contribute(db, request.uid, request.forms)
    redirect(base + query(request.forms, project.sticky))

@get('/project/<slug>/userlog')
def userlog(slug, db):
    project = Project.find(slug)
    posts, sort = project.userlog(db, request.uid)
    if request.query.view == "map":
        return template("map", { 'project': project, 'posts': posts, 'sort': sort })
    elif request.query.view == "browse":
        return template("browse", { 'project': project, 'posts': posts })
    return template("list", { 'project': project, 'posts': posts })

@get('/project/<slug>/<uuid>')
def review(slug, uuid, db):
    project = Project.find(slug)
    post = Post.find(db, uuid)
    if post.user != request.uid:
        redirect(path('/project/%s/userlog' % slug))
    forms = [Form(form, project.forms[form]) for form in project.order]
    [form.validate(post.annotation) for form in forms]
    return template("document",{'id': uuid, 'project': project, 'forms': forms})

@post('/project/<slug>/<uuid>')
def revise(slug, uuid, db):
    post = Post.find(db, uuid)
    if post.user == request.uid:
        post.update(db, request.uid, request.forms)
    redirect(path('/project/%s/userlog' % slug))

@get('/lookup/<key>')
def lookup(key, db):
    q = request.query.q
    if key in config['lookup'] and q:
        src = config['lookup'][key]
        query = "select * from %s where %s like ? limit 25" % (
                src['table'], src['key'])
        rows = db.execute(query, ["%" + q + "%"]).fetchall()
        results = [dict(r) for r in rows]
        return json.dumps(results)

@get('/static/<path:path>')
def static(path):
    return static_file(path, root='static')

@route('/logout')
def logout():
    request.session.delete()
    redirect(path("/"))

# handle oauth logins
@get("/oauth/<key>")
def oauthcallback(key):
    service = config['oauth'][key]
    raw = requests.post(service['tokenurl'], data={
        'client_id': service['id'],
        'client_secret': service['secret'],
        'code': request.query['code']
    }, headers={
        'Accept': 'application/json'
    })
    reply = raw.json()
    request.session['oauth'] = reply['access_token']
    if 'url' in service['authenticate']:
        request.session.save()
        return redirect(path("/oauthenticate/" + key))
    request.session['oauth_service'] = key
    request.session['oauth_id'] = reply[service['authenticate']['id']]
    request.session['oauth_user'] = reply[service['authenticate']['handle']]
    request.session.save()
    redirect(path("/"))

@get("/oauthenticate/<key>")
def oauthorize(key):
    service = config['oauth'][key]
    raw = requests.get(service['authenticate']["url"], params={
        'access_token': request.session['oauth'],
    }, headers={
        'Accept': 'application/json'
    })
    result = raw.json()
    request.session['oauth_service'] = key
    request.session['oauth_id'] = result[service['authenticate']['id']]
    request.session['oauth_user'] = result[service['authenticate']['handle']]
    request.session.save()
    redirect(path("/"))

if __name__ == "__main__":
    run(app, server="gunicorn", host="0.0.0.0", port=8080)

