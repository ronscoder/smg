from django.urls import path

from . import views

urlpatterns = [
        path("", views.index, name="index"),
        #path("unrecharged_reports/", views.unrecharged_reports, name="unrecharged_reports"),
        path("raidgroups/", views.raidgroups, name="raidgroups"),
        path("consumergroups/", views.consumergroups, name="consumergroups"),
        path("raidgroupings/<int:rgid>/", views.raidgroupings, name="raidgroupings"),
        path("raid/<int:rid>/", views.raid, name="raid"),
        
        path("download_raidgroup/<int:rgid>/", views.download_raidgroup, name="download_raidgroup"),
        path("consumergroup/<int:cgid>/", views.consumergroup, name="consumergroup"),
        path("download_consumergroup/<int:cgid>/", views.download_consumergroup, name="download_consumergroup"),
        path("duplicacy_report/", views.duplicacy_report, name="duplicacy_report"),
        
        path("download_duplicates/", views.download_duplicates, name="download_duplicates"),
        path("uploads/", views.uploads, name="uploads"),
        path("uploaded/", views.uploaded, name="uploaded"),
      
        path("<int:consumer_id>/", views.consumer_details, name="consumer_details"),
        path("test_api/", views.test_api),
        path("fix_db_changes", views.fix_db_changes, name='fix_db_changes'),
        path("update_consumer_master", views.update_consumer_master, name='update_consumer_master'),
        path("messages", views.messages, name='messages'),
        path("search_consumers", views.search_consumers, name='search_consumers'),
        path("fetch_cdetails/<int:consumer_id>/", views.fetch_cdetails, name='fetch_cdetails'),
        ]