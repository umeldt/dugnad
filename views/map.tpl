% crumb(config['title'], "/")
% crumb(project.title, "/project/" + project.slug + "/overview")
% crumb('log', "/project/" + project.slug + "/userlog")
% crumb(_('map'))
% rebase('base.tpl', title='dugnad')

<link rel='stylesheet' href='{{config['static']}}/leaflet.css'>
<link rel='stylesheet' href='{{config['static']}}/leaflet.draw.css'>
<link rel='stylesheet' href='{{config['static']}}/leaflet.measure.css'>

<script src='{{config['static']}}/leaflet.js'></script>
<script src='{{config['static']}}/leaflet.draw.js'></script>
<script src='{{config['static']}}/leaflet.measure.js'></script>
<script src='{{config['static']}}/wicket.js'></script>
<script src='{{config['static']}}/wicket-leaflet.js'></script>
<script src='{{config['static']}}/dugnad.js'></script>

<section class=stats>
  % if sort:
  <form method=get>
    <input type=hidden name=view value=map>
    % for term, values in sort.iteritems():
    % if values:
    <select name="{{term}}">
      <option value="">-- {{_(term)}} --</option>
      % for value in values:
      <option>{{value}}</option>
      % end
    </select>
    % end
    % end
    <input value="{{_('filter')}}" type=submit>
  </form>
  % end

  <div id=map>
  </div>
</section>

<script>
var data = [
  % for entry in entries:
  % if entry.wkt():
  { id: "{{!entry.id}}", path: "{{!entry.path()}}", wkt: {{!entry.wkt()}} },
  % end
  % end
];

T.populateMap = function() {
  for(var i = 0; i < data.length; i++) {
    var wkt = new Wkt.Wkt();
    wkt.read(data[i].wkt);
    var obj = wkt.toObject(T.map.defaults)
    obj.path = data[i].id;
    obj.on("click", function(e) {
      document.location = e.target.path;
    });
    obj.addTo(T.map);
  }
}
</script>

