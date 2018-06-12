% crumb(_(config['title']))
% rebase('base.tpl', title='dugnad')

<section class=info>
  <section>
    <h1>{{_('welcome')}}</h1>

<!--
    <aside>
      <h2>{{_('recent-changes')}}</h2>
      % for change in changelog.changes[:4]:
        <dt><time>{{change['date']}}</time></dt>
        <dd>{{change['text']}}</dd>
      % end
      <p><a href='changelog'>{{_('all-changes')}}</a>
    </aside>
-->
  
    <p>{{_('introduction')}}
  </section>
</section>

<section class=projects>
  % for proj in projects:
    % if not proj.hidden:
    <article>
      <a href='{{path("/project/" + proj.slug + "/overview")}}'>
        % if proj.image:
        <img src='{{config['static']}}/images/{{proj.image}}' alt>
        % end
        <h3>{{_(proj.title)}}</h3>
      </a>
    </article>
    % end
  % end
</section>

