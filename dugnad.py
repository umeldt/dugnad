#!/usr/bin/python
# encoding: utf-8

from __future__ import unicode_literals
import os
import re
import glob
import json
import uuid
import yaml
import urllib
import logging
import hashlib
import datetime
import requests

from beaker.middleware import SessionMiddleware

import bottle
import bottle.ext.sqlite
from bottle import get, post, route, hook, request, response, redirect
from bottle import run, view
from bottle import static_file, template, SimpleTemplate, FormsDict
from bottle_utils.i18n import I18NPlugin, i18n_path, i18n_url, lazy_gettext as _

#import gi
#gi.require_version('Vips', '8.0')
#from gi.repository import Vips

config = yaml.load(open("config.yaml"))

bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024 * 16

SESSION = {
    'session.type': 'cookie',
    'session.cookie_expires': 60 * 60 * 24 * 365,
    'session.encrypt_key': "o(eaji3jgoijeh83",
    'session.validate_key': True,
}

app = bottle.default_app()
sqlite = bottle.ext.sqlite.Plugin(dbfile='dugnad.db')
app.install(sqlite)
app = I18NPlugin(app, config['languages'], config['languages'][0][0], "lang")
app = SessionMiddleware(app, SESSION)

logging.basicConfig(level=logging.INFO)

def deepzoom(url):
    url = urllib.unquote(url.strip())
    key = hashlib.sha256(url).hexdigest()
    name = "static/tmp/" + key
    if not os.path.exists(name + "_files"):
        urllib.urlretrieve(source, "%s.jpg" % name)
        image = Vips.Image.new_from_file("%s.jpg" % name)
        image.dzsave(name, layout="dz")
    return "%s.dzi" % key

class Form:
    @staticmethod
    def build(blueprint):
        if blueprint['type'] == "textfield":
            return [Form.Textfield(blueprint)]
        elif blueprint['type'] == "select":
            return [Form.Select(blueprint)]
        elif blueprint['type'] == "annotation":
            return [Form.Input({'type': 'text',
                                'name': 'marked-pages',
                                'disabled': True
                               }),
                    Form.Input({'type': 'hidden', 'name': blueprint['name']}),
                    Form.Button({'name': 'mark-page'}),
                    Form.Button({'name': 'removefabric'})
                   ]
        elif blueprint['type'] == "multi":
            return [Form.Row(blueprint, r) for r in range(blueprint["rows"])]
        else:
            return [Form.Input(blueprint)]


    class Button:
        def __init__(self, blueprint):
            self.name = blueprint['name']
            self.text = self.name
            self.type = "button"

        def tohtml(self):
            s = "<button id='%s' name='%s'>%s</button>" % (
                    self.name, self.name, _(self.text))
            return s

    class Select:
        def __init__(self, blueprint):
            self.type = blueprint['type']
            self.name = blueprint['name']
            self.text = self.name
            self.options = blueprint['pick']
            self.helptext = blueprint.get('help')

        def tohtml(self, label=True):
            s = ""
            if label:
                s += "<label>%s</label>\n" % _(self.text)
            s += "<select name='%s'>" % self.name
            for option in self.options:
                s += "<option>%s</option>" % option
            s += "</select>"
            if self.helptext:
              s += "<a class=help title='%s'>" % _(self.helptext)
              s += "<img src='/static/images/help.png'>"
              s += "</a>"
            return s

    class Input:
        def __init__(self, blueprint):
            self.type = blueprint['type']
            self.name = blueprint['name']
            self.text = self.name
            self.size = blueprint.get('size', "24")
            self.readonly = blueprint.get('disabled')
            self.checked = False
            self.url = blueprint.get('url')
            self.pick = blueprint.get('pick')
            self.path = blueprint.get('path')
            self.value = ""
            self.nolabel = False
            self.helptext = blueprint.get('help')

        def tohtml(self, label=True):
            s = ""
            if label and self.type != "hidden" and not self.nolabel:
                s += "<label>%s</label>\n" % _(self.text)
            s += "<input type=%s name='%s'" % (self.type, self.name)
            s += " size='%s'" % self.size
            s += " id='%s'" % self.name
            if self.nolabel:
                s += " placeholder='%s'" % _(self.text)
            if self.checked:
                s += " checked" 
            if self.value:
                s += " value='%s'" % self.value # .decode('utf-8')
            if self.url:
                s += " data-url='%s'" % self.url
            if self.path:
                s += " data-url='%s'" % path(self.path)
            if self.pick:
                s += " data-pick='%s'" % json.dumps(self.pick)
            if self.readonly:
                s += " readonly"
            # if self.helptext:
            #     s += " data-help='%s'" % json.dumps(unicode(translated))
            s += ">"
            if self.helptext:
              translated = _(self.helptext)
              s += "<a class=help title='%s'>" % _(self.helptext)
              s += "<img "
              s += " title='%s'" % unicode(translated)
              s += " src='/static/images/help.png'>"
              s += "</a>"
            return s

    class Textfield:
        def __init__(self, blueprint):
            self.name = blueprint['name']
            self.text = self.name
            self.type = "textfield"
            self.readonly = blueprint.get('disabled')
            self.value = ""

        def tohtml(self):
            s = ""
            s += "<label>%s</label>\n" % _(self.text)
            s += "<textarea name='%s'" % self.name
            if self.readonly:
                s += " readonly"
            s += ">%s</textarea>" % self.value or ""
            return s

    class Row:
        def __init__(self, recipe, row):
            self.name = None
            self.row = str(row)
            self.label = recipe.get("label", "")
            self.inputs = []
            for blueprint in recipe["columns"]:
                for element in Form.build(blueprint):
                    element.name = element.name + "_" + self.row
                    element.nolabel = True
                    element.size = 5
                    self.inputs.append(element)

        def tohtml(self):
            h = "<label>%s [%s]</label> " % (_(self.label), self.row)
            for element in self.inputs: h += element.tohtml()
            return h

    def __init__(self, slug, recipe):
        self.slug = slug
        self.inputs = []
        for blueprint in recipe:
            for element in Form.build(blueprint):
                self.inputs.append(element)

    def tohtml(self):
        h = ""
        for element in self.inputs: h += "<p>" + element.tohtml()
        return h

    def validate(self, request):
        for element in self.inputs:
            if element.name and element.name in request:
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

class Source:
    @classmethod
    def random(cls, db, project):
        query = "SELECT * FROM sources WHERE project = ?"
        row = db.execute(query, [project.slug]).fetchone()
        if row: return cls(dict(row))
        return None

    def weighted(cls, db, project):
        query = """SELECT * FROM sources WHERE project = ?
                   ORDER BY priority LIMIT 100"""
        rows = db.execute(query, [project.slug]).fetchall()
        if rows: return cls(dict(random.choice(rows)))
        return None

    def __init__(self, attrs):
        self.raw = attrs
        for k in attrs: setattr(self, k, attrs[k])
        self.data = json.loads(self.data)

class Entry:
    @classmethod
    def find(cls, db, uuid):
        query = "SELECT * FROM entries WHERE id = ?"
        row = db.execute(query, [uuid]).fetchone()
        return cls(dict(row))

    def excluded(self):
        return False

    def __init__(self, attrs, proj=None):
        self.raw = attrs
        for k in attrs: setattr(self, k, attrs[k])
        if proj:
            self.project = proj
        else:
            self.project = Project.find(self.project)
        self.data = json.loads(self.data)

    def get(self, k):
        if hasattr(self, k): return getattr(self, k)
        if k in self.data: return self.data[k]

    def path(self):
        return path("/projects/%s/%s" % (self.project.slug, self.id))

    def update(self, db, uid, entry):
        # finished = not data.get('later')
        query = "DELETE FROM markings WHERE post = ?"
        db.execute(query, [self.id])
        if 'data' in entry:
            pages = json.loads(entry['data'])
            for page, marks in pages.iteritems():
                self.project.addmarkings(db, self.id, uid, page, marks)
        now = str(datetime.datetime.now())
        query = "UPDATE entries SET data = ?, updated = ? WHERE id = ?"
        db.execute(query, [json.dumps(dict(entry)), now, self.id])

    def wkt(self):
        if self.data.get('footprintWKT'):
            return json.dumps(self.data['footprintWKT'])

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
        for k in attrs: setattr(self, k, attrs[k])

    def json(self, db):
        query = "SELECT * FROM entries WHERE project = ? ORDER BY updated DESC"
        rows = db.execute(query, [self.slug]).fetchall()
        entries = []
        for row in rows:
            entry = dict(row)
            if 'user' in entry and entry['user'] != "anonymous":
                entry['user'] = hashlib.sha512(entry['user']).hexdigest()
            if 'data' in entry:
                entry['data'] = json.loads(entry['data'])
                if 'annotation' in entry['data']:
                  del entry['data']['annotation']
            entries.append(entry)
        return json.dumps(entries)

    def userlog(self, db, uid, skip):
        query = """SELECT * FROM entries WHERE project = ? AND user = ?
                   ORDER BY updated DESC LIMIT 50 OFFSET ?"""
        rows = db.execute(query, [self.slug, uid, skip]).fetchall()
        entries = []
        sort = {}
        for term in self.sort:
            sort[term] = []
        for row in rows:
            entry = Entry(dict(row))
            for term in self.sort:
                value = entry.get(term)
                if value and value not in sort[term]:
                    sort[term].append(value)
            if not entry.excluded():
                entries.append(entry)
        for term in self.sort:
            sort[term].sort()
        return entries, sort

    def contribute(self, db, uid, entry):
        finished = not entry.get('later')
        entry = str(uuid.uuid4())
        if 'data' in entry and entry['data']:
            pages = json.loads(entry['data'])
            for page, marks in pages.iteritems():
                self.addmarkings(db, entry, uid, page, marks)
        now = str(datetime.datetime.now())
        query = """INSERT INTO
                   entries(id, user, project, date, data, finished, updated)
                   VALUES(?, ?, ?, ?, ?, ?, ?)"""
        db.execute(query, [entry, uid, self.slug, now,
                json.dumps(dict(entry)), finished, now])

    def addmarkings(self, db, entry, uid, page, data):
        now = str(datetime.datetime.now())
        query = """INSERT INTO
                   markings(id, user, project, date, entry, page, markings)
                   VALUES(?, ?, ?, ?, ?, ?, ?)"""
        db.execute(query, [str(uuid.uuid4()), uid, self.slug, date, entry,
                   page, json.dumps(data), now])

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
    projects = []
    for f in glob.glob("projects/*.yaml"):
        try:
            project = Project(f)
            projects.append(project)
        except:
            None
    return { 'projects': projects }

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
    query = "SELECT * FROM markings WHERE project = ? AND page = ?"
    rows = db.execute(query, [slug, page])
    results = [dict(r) for r in rows]
    return json.dumps(results)

@get('/project/<slug>/<uuid>/markings/<page>')
def markings_entries(slug, page, db):
    query = "SELECT * FROM markings WHERE id = ? AND page = ?"
    rows = db.execute(query, [slug, page])
    results = [dict(r) for r in rows]
    return json.dumps(results)

@get('/project/<slug>')
def project(slug, db):
    def document(db, project):
        forms = [Form(form, project.forms[form]) for form in project.order]
        [form.validate(FormsDict.decode(request.query)) for form in forms]
        return template("document", { 'project': project, 'forms': forms })

    def random(db, project):
        forms = [Form(form, project.forms[form]) for form in project.order]
        source = Source.random(db, project)
        return template("image", {
            'project': project, 'forms': forms, 'source': source
        })

    def weighted(db, project):
        forms = [Form(form, project.forms[form]) for form in project.order]
        source = Source.weighted(db, project)
        return template("image", {
            'project': project, 'forms': forms, 'source': source
        })

    project = Project.find(slug)
    dispatch = {
        'document': document,
        'random': random,
        'weighted': weighted
    }
    return dispatch[project.type](db, project)

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
    entries, sort = project.userlog(db, request.uid, request.query.skip or 0)
    params = { 'project': project, 'entries': entries, 'sort': sort }
    if request.query.view == "map":
        return template('map', params)
    elif request.query.view == "browse":
        return template('browse', params)
    return template("list", params)

@get('/project/<slug>/export.json')
def jsonexport(slug, db):
    project = Project.find(slug)
    response.content_type = "application/json; charset=utf-8"
    return project.json(db)

@get('/project/<slug>/<uuid>')
def review(slug, uuid, db):
    project = Project.find(slug)
    entry = Entry.find(db, uuid)
    if entry.user != request.uid:
        redirect(path('/project/%s/userlog' % slug))
    forms = [Form(form, project.forms[form]) for form in project.order]
    [form.validate(entry.data) for form in forms]
    return template("document",{'id': uuid, 'project': project, 'forms': forms})

@post('/project/<slug>/<uuid>')
def revise(slug, uuid, db):
    entry = Entry.find(db, uuid)
    if entry.user == request.uid:
        entry.update(db, request.uid, request.forms)
    redirect(path('/project/%s/userlog' % slug))

@get('/lookup/<key>')
def lookup(key, db):
    q = request.query.q
    if key in config['lookup'] and q:
        src = config['lookup'][key]
        query = "SELECT * FROM %s WHERE %s LIKE ? LIMIT 25" % (
                src['table'], src['key'])
        rows = db.execute(query, [q + "%"]).fetchall()
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

