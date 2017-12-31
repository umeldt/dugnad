<p class=register-login>
% if user:
  {{_('signed-in-as')}} {{request.user.username}}
  ·
  <a href="{{path('/logout')}}">{{_('logout')}}</a>
% else:
  <a href='{{path('/login')}}'>{{_('login-or-register')}}</a>
% end
