% crumb(config['title'], "/")
% crumb(_('login-or-register'))
% rebase('base.tpl', title='dugnad')

<section class=info>
  <section>
    <h1>{{_('login-or-register')}}</h1>

    % if fail:
    <p class=error>{{_('wrong-username-or-password')}}
    % end

    % if validated:
    <p class=ok>{{_('email-validated')}}
    % end

    <form method=post action={{path('/login')}} class=user id=login>
      <p class=info>{{_('login-explanation')}}
      <h2>{{_('login')}}</h2>
      <p>
        <label>{{_('username')}}</label>
        <input type=text name=name>
      <p>
        <label>{{_('password')}}</label>
        <input type=password name=password>
      <p>
        <input type=submit value='{{_('login')}}'>
    </form>

    <form method=post action={{path('/register')}} class=user id=register>
      <p class=info>{{_('register-explanation')}}
      <h2>{{_('register')}}</h2>
      <p>
        <label>{{_('username')}}</label>
        <input type=text name=name>
      <p>
        <label>{{_('email')}}</label>
        <input type=text name=email>
      <p>
        <label>{{_('password')}}</label>
        <input type=password name=password>
      <p>
        <input type=submit value='{{_('register')}}'>
    </form>
  </section>
</section>

