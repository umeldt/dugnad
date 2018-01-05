% if user:
  <p>
    % if get('project'):
      <a href="{{path('/project/' + project.slug + '/userlog')}}">{{_('my-transcriptions')}}</a>
    % end
% else:
  <p>-
% end
