% crumb(config['title'], "/")
% crumb(_(project.title))
% rebase('base.tpl', title='dugnad')

<section class=info>
  <section>
    <h1>{{_(project.title)}}</h1>
    <p>{{!_(project.description)}}
  
    % if project.finished:
      <p><b>{{_('project-finished')}}</b>
    % else:
      <p id=start-transcribing>
        <a class=btn href='{{path("/project/" + project.slug)}}'>
          {{_('start-project')}}
        </a>
  </section>
</section>

