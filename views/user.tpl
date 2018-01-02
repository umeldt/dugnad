<p class=register-login>
% if user:
  {{_('signed-in-as')}} {{request.login}}
  ·
  <a href="{{path('/logout')}}">{{_('logout')}}</a>
% else:
  % for key, service in config.get('oauth', {}).iteritems():
  <a href='{{service['url'] % service['id']}}'>{{_(service['text'])}}</a>
  % end
% end
