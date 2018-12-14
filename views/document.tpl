% crumb(config['title'], "/")
% crumb(project.title, "/project/" + project.slug + "/overview")
% crumb(_('transcribe'))
<!doctype html>
<meta charset=utf-8>
<title>dugnad · {{project.slug}}</title>
<link rel='stylesheet' href='{{config['static']}}/transcribe.css'>
<link rel='stylesheet' href='{{config['static']}}/leaflet.css'>
<link rel='stylesheet' href='{{config['static']}}/leaflet.draw.css'>
<link rel='stylesheet' href='{{config['static']}}/leaflet.measure.css'>
<link rel='stylesheet' href='{{config['static']}}/auto-complete.css'>
<link rel='stylesheet' href='{{config['static']}}/tippy.css'>

<script src='{{config['static']}}/openseadragon.js'></script>
<script src='{{config['static']}}/openseadragon-fabric.js'></script>
<script src='{{config['static']}}/fabric.js'></script>
<script src='{{config['static']}}/leaflet.js'></script>
<script src='{{config['static']}}/leaflet.draw.js'></script>
<script src='{{config['static']}}/leaflet.measure.js'></script>
<script src='{{config['static']}}/wicket.js'></script>
<script src='{{config['static']}}/wicket-leaflet.js'></script>
<script src='{{config['static']}}/auto-complete.js'></script>
<script src='{{config['static']}}/tippy.all.min.js'></script>
<script src='{{config['static']}}/dugnad.js'></script>

<header>
  <nav>
    <a href='{{path('/')}}'>
      <h1><b>{{_(config['title'])}}</b> {{config['subheading']}}</h1>
    </a>

    % include('user.tpl', user=request.user)
  </nav>

  <nav class=crumbs>
    <p>
    % for crumb in request.crumbs:
      % if crumb[0]:
      <a href='{{path(crumb[0])}}'>{{_(crumb[1])}}</a> ·
      % else:
      <a class=now>{{crumb[1]}}</a>
      % end
    % end

    <form method=get>
      <p>
        <b>{{_('select-page')}}</b>:
        <select id=select-page name=page>
        % for n in range(1, project.source['pages']):
          <option value={{n}}>{{n + project.source.get('shift', 1)}}</option>
        % end
        </select>

        <select id=document-index name=page>
        % for item in project.source.get('index', []):
          <option value={{item['page'] + project.source.get('indexshift', 1)}} data-auto="{{dump(item)}}">{{item['page'] }}: {{item['text']}}</option>
        % end
        </select>
    </form>

    % include('access.tpl', user=request.user)
  </nav>
</header>

<main>
  <aside id=map-overlay class=overlay>
    <div id=map></div>
    <a id=ring></a>
  </aside>

  <section id=dz>
    <p class=modes>
      <a id=show-map data-replace="{{_('link-document')}}" href='#'>
        {{_('link-map')}}
      </a>
    <section id=dzi></section>
  </section>

  <section id=tr>
    % if get('id'):
      <form id=transcription method=post action="{{path("/project/" + project.slug)}}/{{id}}">
    % else:
      <form id=transcription method=post action="{{path("/project/" + project.slug)}}">
    % end
      % for form in forms:
      <fieldset>
        <legend>{{_(form.slug)}}</legend>
        {{!form.tohtml()}}
      </fieldset>
      % end
      <p>
        <input name=save type=submit value="{{_('submit')}}">

      <div id=help>
        <h3>{{_('help')}}</h3>
        <p id=helptext>{{_(project.help['introduction'])}}
      </div>
    </form>
  </section>
</main>

% include("viewer.tpl", project=project)

