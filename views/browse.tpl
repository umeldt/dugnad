% crumb(config['title'], "/")
% crumb(project.title, "/project/" + project.slug + "/overview")
% crumb('log', "/project/" + project.slug + "/userlog")
% crumb(_('browse'))
% rebase('base.tpl', title='dugnad', pager=True)

<script src='{{config['static']}}/openseadragon.js'></script>
<script src='{{config['static']}}/openseadragon-fabric.js'></script>
<script src='{{config['static']}}/fabric.js'></script>
<script src='{{config['static']}}/dugnad.js'></script>

<section id=dz>
  <div id=dzi>
  </div>
</section>

% include("viewer.tpl", project=project, browse=request.uid)

<style>
html, body { height: 100%; width: 100%; margin: 0; position: relative; }

main { height: 100%; }
#dz { background: #777; }
#dz, #dzi { height: 100%; width: 100%; }

</style>
