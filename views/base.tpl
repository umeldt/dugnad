<!doctype html>
<meta charset=utf-8>
<meta name=viewport content='width=device-width, initial-scale=1'>
<title>{{title}}</title>
<base href=''>
<link rel=stylesheet href='{{config['static']}}/dugnad.css?1'>

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

    % if get('pager'):
    <form method=get>
      <p>
        <b>{{_('select-page')}}</b>
        <select id=select-page name=page>
        % for n in range(1, project.source['pages']):
          <option>{{n}}</option>
        % end
        </select>
    </form>
    % end
    
    % include('access.tpl', user=request.user)
  </nav>
</header>

<main>
{{!base}}
</main>

<footer>
  <p>
    % for link in config['links']:
    <a href='{{link['url']}}'>
      <img src='{{link['image']}}'>
    </a>
    % end
</footer>

