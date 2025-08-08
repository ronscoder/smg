from django.shortcuts import render, HttpResponse
from .models import Site, Project, WorkProgress, MaterialBOQ, WorkItem
from django.db.models import OuterRef, Subquery, Max
import pandas as pd


# Create your views here.
def get_projects_status():
  items = WorkItem.objects.filter(index=True)
  #fill dict for all marked items, fill 0s.
  # merge with actual work progress
  wps = WorkProgress.objects.filter(work_item__in=items, id=Subquery(WorkProgress.objects.filter(site=OuterRef("site"), work_item=OuterRef('work_item')).order_by("-date").values("id")[:1]))
  data = []
  for wp in wps:
    obj = {}
    item = wp.work_item
    boq = MaterialBOQ.objects.get(material=item.ref_material, site=wp.site)
    obj['item'] = f"{item.name} ({item.ref_material.unit.short})"
    obj["site"] = wp.site.name
    obj["date"] = wp.date
    obj["quantity_target"] = boq.quantity
    obj["quantity_completed"] = wp.quantity
    obj["item_status"] = wp.status or "NOT STARTED"
    obj["site_status"] = wp.site.status
    data.append(obj)
  df = pd.DataFrame(data)
  pv = pd.pivot_table(df,index=["site",
		  "site_status",
			#"date",
			"item",
			"item_status",
			],
		values=["quantity_target", "quantity_completed"], 
		#columns = ['item_status']
		)
  #pv = pv.sort_index(level='item_status', ascending=False)
  return pv


def projects_status(request):
	pv = get_projects_status()
	pv_html = pv.to_html()
	return render(request, "projects/projects_status.html", {"pv_html": pv_html})


def download_projects_progress(request):
	pv = get_projects_status()
	response = HttpResponse(
		content_type="    application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
	)
	response["Content-Disposition"] = f'attachment; filename="projects_progress.xlsx"'
	pv.to_excel(response, index=True)
	return response
