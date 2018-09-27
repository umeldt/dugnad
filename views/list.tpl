% crumb(config['title'], "/")
% crumb(project.title, "/project/" + project.slug + "/overview")
% crumb(_('log'))
% rebase('base.tpl', title='dugnad')

<script src='{{config['static']}}/tablesort.min.js'></script>

<section class=stats>
  <h1>{{_(project.title)}}</h1>
  <p>
    <a href='?view=map'>{{_('map')}}</a> ·
    <a href='?view=browse'>{{_('browse')}}</a> ·
    <a href='?skip={{int((request.query.skip or 0)) + 25}}'>{{_('older')}}</a>

  <table id=userlog class=list>
    <thead>
    <tr>
      <th>{{_('date')}}</th>
      <th>{{_('last-update')}}</th>
      % for term in project.sort:
      <th>{{_(term)}}</th>
      % end
      <th></th>
    </tr>
    </thead>
    % for post in posts:
    <tr>
      <td>{{post.date}}</td>
      <td>{{post.updated}}</td>
      % for term in project.sort:
      <td>{{post.get(term)}}</td>
      % end
      <td><a href='{{path("/project/" + project.slug + "/" + post.id)}}'>{{_('edit')}}</a>
    </tr>
    % end
  </table>
</section>

<script>
  new Tablesort(document.getElementById('userlog'));
</script>
