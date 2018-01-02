% crumb(config['title'], "/")
% crumb(project.title, "/project/" + project.slug + "/overview")
% crumb(_('log'))
% rebase('base.tpl', title='dugnad')

<section class=stats>
  <h1>{{_(project.title)}}</h1>
  <p>
    <a href='?view=map'>{{_('map')}}</a> ·
    <a href='?view=browse'>{{_('browse')}}</a>

  <table class=list>
    <tr>
      <th>{{_('id')}}</th>
      <th>{{_('date')}}</th>
      <th>{{_('last-update')}}</th>
      <th></th>
    </tr>
    % for post in posts:
    <tr>
      <td>{{post.id}}</td>
      <td>{{post.date}}</td>
      <td>{{post.updated}}</td>
      <td><a href='{{path("/project/" + project.slug + "/" + post.id)}}'>{{_('edit')}}</a>
    </tr>
    % end
  </table>
</section>

