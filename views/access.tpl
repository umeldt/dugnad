% if user:
  <p>
    % if get('project'):
      <a href="{{path('/project/' + project.slug + '/userlog')}}">{{_('my-transcriptions')}}</a>
      % if user.role == "bakromtilgang":
      ·
      % end
    % end
% end
