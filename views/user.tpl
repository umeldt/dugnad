<p class=register-login>
% if user:
  {{_('signed-in-as')}} <b>{{request.login}}</b>
  ·
  <a href="{{path('/logout')}}">{{_('logout')}}</a>
% else:
  % if 'oauth' in config:
    <b>{{_('login-using')}}</b><br>
    % for key, service in config.get('oauth', {}).iteritems():
    <a href='{{service['url'] % service['id']}}'>{{service['name']}}</a>
    % end
  % end
% end
