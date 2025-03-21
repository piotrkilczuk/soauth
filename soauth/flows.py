from __future__ import annotations

import copy
from typing import Type, Any
from urllib.parse import urlencode
import uuid

import requests
from werkzeug import Response
from werkzeug.utils import redirect
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField
from wtforms.form import Form
from wtforms.validators import InputRequired, StopValidation


class BaseFlow:
    redirect_to_consent_screen_url: str
    acquire_tokens_url: str
    form: Type[Form]
    name: str
    state: dict[str, dict[str, Any]]

    port: int

    def __init__(self, port: int):
        self.port = port
        self.state = {}

    def collect_consent_screen_args(self, form: Form) -> dict:
        state_uuid = uuid.uuid4().hex
        form_data = form.data
        form_data.update({"redirect_uri": self.get_redirect_uri(), "state": state_uuid})
        self.state[state_uuid] = copy.copy(form_data)
        form_data.pop("client_secret")
        return form_data

    def get_redirect_uri(self) -> str:
        return f"http://localhost:{self.port}/{self.name}/callback"

    # def get_success_uri(self) -> str:
    #     return f"http://localhost:{self.port}/{self.name}/success"

    def redirect_to_consent_screen(self, consent_screen_args: dict) -> Response:
        url = self.redirect_to_consent_screen_url
        qs = urlencode(consent_screen_args)
        return redirect(f"{url}?{qs}")

    def acquire_tokens(self, code: str, state_uuid: str) -> dict:
        state = self.state[state_uuid]
        args = {
            "client_id": state["client_id"],
            "client_secret": state["client_secret"],
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.get_redirect_uri(),
        }
        response = requests.post(self.acquire_tokens_url, data=args)
        return response.json()


class GoogleAPIScopeValidator:
    """
    The scopes are here: https://developers.google.com/identity/protocols/oauth2/scopes?hl=en
    """

    valid_scopes: set[str] = {
        "https://mail.google.com/",
        "https://www.google.com/calendar/feeds",
        "https://www.google.com/m8/feeds",
        "https://www.googleapis.com/auth/adexchange.buyer",
        "https://www.googleapis.com/auth/admin.chrome.printers",
        "https://www.googleapis.com/auth/admin.chrome.printers.readonly",
        "https://www.googleapis.com/auth/admin.datatransfer",
        "https://www.googleapis.com/auth/admin.datatransfer.readonly",
        "https://www.googleapis.com/auth/admin.directory.customer",
        "https://www.googleapis.com/auth/admin.directory.customer.readonly",
        "https://www.googleapis.com/auth/admin.directory.device.chromeos",
        "https://www.googleapis.com/auth/admin.directory.device.chromeos.readonly",
        "https://www.googleapis.com/auth/admin.directory.device.mobile",
        "https://www.googleapis.com/auth/admin.directory.device.mobile.action",
        "https://www.googleapis.com/auth/admin.directory.device.mobile.readonly",
        "https://www.googleapis.com/auth/admin.directory.domain",
        "https://www.googleapis.com/auth/admin.directory.domain.readonly",
        "https://www.googleapis.com/auth/admin.directory.group",
        "https://www.googleapis.com/auth/admin.directory.group.member",
        "https://www.googleapis.com/auth/admin.directory.group.member.readonly",
        "https://www.googleapis.com/auth/admin.directory.group.readonly",
        "https://www.googleapis.com/auth/admin.directory.orgunit",
        "https://www.googleapis.com/auth/admin.directory.orgunit.readonly",
        "https://www.googleapis.com/auth/admin.directory.resource.calendar",
        "https://www.googleapis.com/auth/admin.directory.resource.calendar.readonly",
        "https://www.googleapis.com/auth/admin.directory.rolemanagement",
        "https://www.googleapis.com/auth/admin.directory.rolemanagement.readonly",
        "https://www.googleapis.com/auth/admin.directory.user",
        "https://www.googleapis.com/auth/admin.directory.user.alias",
        "https://www.googleapis.com/auth/admin.directory.user.alias.readonly",
        "https://www.googleapis.com/auth/admin.directory.user.readonly",
        "https://www.googleapis.com/auth/admin.directory.user.security",
        "https://www.googleapis.com/auth/admin.directory.userschema",
        "https://www.googleapis.com/auth/admin.directory.userschema.readonly",
        "https://www.googleapis.com/auth/admin.reports.audit.readonly",
        "https://www.googleapis.com/auth/admin.reports.usage.readonly",
        "https://www.googleapis.com/auth/admob.readonly",
        "https://www.googleapis.com/auth/admob.report",
        "https://www.googleapis.com/auth/adsensehost",
        "https://www.googleapis.com/auth/analytics",
        "https://www.googleapis.com/auth/analytics.edit",
        "https://www.googleapis.com/auth/analytics.manage.users",
        "https://www.googleapis.com/auth/analytics.manage.users.readonly",
        "https://www.googleapis.com/auth/analytics.provision",
        "https://www.googleapis.com/auth/analytics.readonly",
        "https://www.googleapis.com/auth/analytics.user.deletion",
        "https://www.googleapis.com/auth/androidenterprise",
        "https://www.googleapis.com/auth/androidmanagement",
        "https://www.googleapis.com/auth/androidpublisher",
        "https://www.googleapis.com/auth/appengine.admin",
        "https://www.googleapis.com/auth/apps.alerts",
        "https://www.googleapis.com/auth/apps.groups.migration",
        "https://www.googleapis.com/auth/apps.groups.settings",
        "https://www.googleapis.com/auth/apps.licensing",
        "https://www.googleapis.com/auth/apps.order",
        "https://www.googleapis.com/auth/apps.order.readonly",
        "https://www.googleapis.com/auth/bigquery",
        "https://www.googleapis.com/auth/bigquery.insertdata",
        "https://www.googleapis.com/auth/bigtable.admin",
        "https://www.googleapis.com/auth/bigtable.admin.cluster",
        "https://www.googleapis.com/auth/bigtable.admin.instance",
        "https://www.googleapis.com/auth/bigtable.admin.table",
        "https://www.googleapis.com/auth/blogger",
        "https://www.googleapis.com/auth/blogger.readonly",
        "https://www.googleapis.com/auth/books",
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/calendar.events",
        "https://www.googleapis.com/auth/calendar.events.readonly",
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/calendar.settings.readonly",
        "https://www.googleapis.com/auth/chat.admin.delete",
        "https://www.googleapis.com/auth/chat.admin.memberships",
        "https://www.googleapis.com/auth/chat.admin.memberships.readonly",
        "https://www.googleapis.com/auth/chat.admin.spaces",
        "https://www.googleapis.com/auth/chat.admin.spaces.readonly",
        "https://www.googleapis.com/auth/chat.app.delete",
        "https://www.googleapis.com/auth/chat.app.memberships",
        "https://www.googleapis.com/auth/chat.app.spaces",
        "https://www.googleapis.com/auth/chat.app.spaces.create",
        "https://www.googleapis.com/auth/chat.delete",
        "https://www.googleapis.com/auth/chat.import",
        "https://www.googleapis.com/auth/chat.memberships",
        "https://www.googleapis.com/auth/chat.memberships.app",
        "https://www.googleapis.com/auth/chat.memberships.readonly",
        "https://www.googleapis.com/auth/chat.messages",
        "https://www.googleapis.com/auth/chat.messages.create",
        "https://www.googleapis.com/auth/chat.messages.reactions",
        "https://www.googleapis.com/auth/chat.messages.reactions.create",
        "https://www.googleapis.com/auth/chat.messages.reactions.readonly",
        "https://www.googleapis.com/auth/chat.messages.readonly",
        "https://www.googleapis.com/auth/chat.spaces",
        "https://www.googleapis.com/auth/chat.spaces.create",
        "https://www.googleapis.com/auth/chat.spaces.readonly",
        "https://www.googleapis.com/auth/chat.users.readstate",
        "https://www.googleapis.com/auth/chat.users.readstate.readonly",
        "https://www.googleapis.com/auth/classroom.announcements",
        "https://www.googleapis.com/auth/classroom.announcements.readonly",
        "https://www.googleapis.com/auth/classroom.courses",
        "https://www.googleapis.com/auth/classroom.courses.readonly",
        "https://www.googleapis.com/auth/classroom.coursework.me",
        "https://www.googleapis.com/auth/classroom.coursework.me.readonly",
        "https://www.googleapis.com/auth/classroom.coursework.students",
        "https://www.googleapis.com/auth/classroom.coursework.students.readonly",
        "https://www.googleapis.com/auth/classroom.courseworkmaterials",
        "https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly",
        "https://www.googleapis.com/auth/classroom.guardianlinks.me.readonly",
        "https://www.googleapis.com/auth/classroom.guardianlinks.students",
        "https://www.googleapis.com/auth/classroom.guardianlinks.students.readonly",
        "https://www.googleapis.com/auth/classroom.profile.emails",
        "https://www.googleapis.com/auth/classroom.profile.photos",
        "https://www.googleapis.com/auth/classroom.push-notifications",
        "https://www.googleapis.com/auth/classroom.rosters",
        "https://www.googleapis.com/auth/classroom.rosters.readonly",
        "https://www.googleapis.com/auth/classroom.student-submissions.me.readonly",
        "https://www.googleapis.com/auth/classroom.student-submissions.students.readonly",
        "https://www.googleapis.com/auth/classroom.topics",
        "https://www.googleapis.com/auth/classroom.topics.readonly",
        "https://www.googleapis.com/auth/cloud-bigtable.admin",
        "https://www.googleapis.com/auth/cloud-bigtable.admin.cluster",
        "https://www.googleapis.com/auth/cloud-bigtable.admin.table",
        "https://www.googleapis.com/auth/cloud-billing",
        "https://www.googleapis.com/auth/cloud-billing.readonly",
        "https://www.googleapis.com/auth/cloud-identity.devices.lookup",
        "https://www.googleapis.com/auth/cloud-identity.groups",
        "https://www.googleapis.com/auth/cloud-identity.groups.readonly",
        "https://www.googleapis.com/auth/cloud-language",
        "https://www.googleapis.com/auth/cloud-platform",
        "https://www.googleapis.com/auth/cloud-platform.read-only",
        "https://www.googleapis.com/auth/cloud-translation",
        "https://www.googleapis.com/auth/cloud-vision",
        "https://www.googleapis.com/auth/cloud_debugger",
        "https://www.googleapis.com/auth/cloud_search",
        "https://www.googleapis.com/auth/cloud_search.debug",
        "https://www.googleapis.com/auth/cloud_search.indexing",
        "https://www.googleapis.com/auth/cloud_search.query",
        "https://www.googleapis.com/auth/cloud_search.settings",
        "https://www.googleapis.com/auth/cloud_search.settings.indexing",
        "https://www.googleapis.com/auth/cloud_search.settings.query",
        "https://www.googleapis.com/auth/cloud_search.stats",
        "https://www.googleapis.com/auth/cloud_search.stats.indexing",
        "https://www.googleapis.com/auth/cloudkms",
        "https://www.googleapis.com/auth/cloudruntimeconfig",
        "https://www.googleapis.com/auth/compute",
        "https://www.googleapis.com/auth/compute.readonly",
        "https://www.googleapis.com/auth/contacts",
        "https://www.googleapis.com/auth/contacts.other.readonly",
        "https://www.googleapis.com/auth/contacts.readonly",
        "https://www.googleapis.com/auth/content",
        "https://www.googleapis.com/auth/dataportability.alerts.subscriptions",
        "https://www.googleapis.com/auth/dataportability.businessmessaging.conversations",
        "https://www.googleapis.com/auth/dataportability.chrome.autofill",
        "https://www.googleapis.com/auth/dataportability.chrome.bookmarks",
        "https://www.googleapis.com/auth/dataportability.chrome.dictionary",
        "https://www.googleapis.com/auth/dataportability.chrome.extensions",
        "https://www.googleapis.com/auth/dataportability.chrome.history",
        "https://www.googleapis.com/auth/dataportability.chrome.reading_list",
        "https://www.googleapis.com/auth/dataportability.chrome.settings",
        "https://www.googleapis.com/auth/dataportability.discover.follows",
        "https://www.googleapis.com/auth/dataportability.discover.likes",
        "https://www.googleapis.com/auth/dataportability.discover.not_interested",
        "https://www.googleapis.com/auth/dataportability.maps.aliased_places",
        "https://www.googleapis.com/auth/dataportability.maps.commute_routes",
        "https://www.googleapis.com/auth/dataportability.maps.commute_settings",
        "https://www.googleapis.com/auth/dataportability.maps.ev_profile",
        "https://www.googleapis.com/auth/dataportability.maps.factual_contributions",
        "https://www.googleapis.com/auth/dataportability.maps.offering_contributions",
        "https://www.googleapis.com/auth/dataportability.maps.photos_videos",
        "https://www.googleapis.com/auth/dataportability.maps.questions_answers",
        "https://www.googleapis.com/auth/dataportability.maps.reviews",
        "https://www.googleapis.com/auth/dataportability.maps.starred_places",
        "https://www.googleapis.com/auth/dataportability.myactivity.maps",
        "https://www.googleapis.com/auth/dataportability.myactivity.myadcenter",
        "https://www.googleapis.com/auth/dataportability.myactivity.play",
        "https://www.googleapis.com/auth/dataportability.myactivity.search",
        "https://www.googleapis.com/auth/dataportability.myactivity.shopping",
        "https://www.googleapis.com/auth/dataportability.myactivity.youtube",
        "https://www.googleapis.com/auth/dataportability.mymaps.maps",
        "https://www.googleapis.com/auth/dataportability.order_reserve.purchases_reservations",
        "https://www.googleapis.com/auth/dataportability.play.devices",
        "https://www.googleapis.com/auth/dataportability.play.grouping",
        "https://www.googleapis.com/auth/dataportability.play.installs",
        "https://www.googleapis.com/auth/dataportability.play.library",
        "https://www.googleapis.com/auth/dataportability.play.playpoints",
        "https://www.googleapis.com/auth/dataportability.play.promotions",
        "https://www.googleapis.com/auth/dataportability.play.purchases",
        "https://www.googleapis.com/auth/dataportability.play.redemptions",
        "https://www.googleapis.com/auth/dataportability.play.subscriptions",
        "https://www.googleapis.com/auth/dataportability.play.usersettings",
        "https://www.googleapis.com/auth/dataportability.saved.collections",
        "https://www.googleapis.com/auth/dataportability.search_ugc.comments",
        "https://www.googleapis.com/auth/dataportability.search_ugc.media.reviews_and_stars",
        "https://www.googleapis.com/auth/dataportability.search_ugc.media.streaming_video_providers",
        "https://www.googleapis.com/auth/dataportability.search_ugc.media.thumbs",
        "https://www.googleapis.com/auth/dataportability.search_ugc.media.watched",
        "https://www.googleapis.com/auth/dataportability.searchnotifications.settings",
        "https://www.googleapis.com/auth/dataportability.searchnotifications.subscriptions",
        "https://www.googleapis.com/auth/dataportability.shopping.addresses",
        "https://www.googleapis.com/auth/dataportability.shopping.reviews",
        "https://www.googleapis.com/auth/dataportability.streetview.imagery",
        "https://www.googleapis.com/auth/dataportability.youtube.channel",
        "https://www.googleapis.com/auth/dataportability.youtube.clips",
        "https://www.googleapis.com/auth/dataportability.youtube.comments",
        "https://www.googleapis.com/auth/dataportability.youtube.live_chat",
        "https://www.googleapis.com/auth/dataportability.youtube.music",
        "https://www.googleapis.com/auth/dataportability.youtube.playable",
        "https://www.googleapis.com/auth/dataportability.youtube.posts",
        "https://www.googleapis.com/auth/dataportability.youtube.private_playlists",
        "https://www.googleapis.com/auth/dataportability.youtube.private_videos",
        "https://www.googleapis.com/auth/dataportability.youtube.public_playlists",
        "https://www.googleapis.com/auth/dataportability.youtube.public_videos",
        "https://www.googleapis.com/auth/dataportability.youtube.shopping",
        "https://www.googleapis.com/auth/dataportability.youtube.subscriptions",
        "https://www.googleapis.com/auth/dataportability.youtube.unlisted_playlists",
        "https://www.googleapis.com/auth/dataportability.youtube.unlisted_videos",
        "https://www.googleapis.com/auth/datastore",
        "https://www.googleapis.com/auth/ddmconversions",
        "https://www.googleapis.com/auth/devstorage.full_control",
        "https://www.googleapis.com/auth/devstorage.read_only",
        "https://www.googleapis.com/auth/devstorage.read_write",
        "https://www.googleapis.com/auth/dfareporting",
        "https://www.googleapis.com/auth/dfatrafficking",
        "https://www.googleapis.com/auth/directory.readonly",
        "https://www.googleapis.com/auth/documents",
        "https://www.googleapis.com/auth/documents.readonly",
        "https://www.googleapis.com/auth/doubleclicksearch",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/drive.activity",
        "https://www.googleapis.com/auth/drive.activity.readonly",
        "https://www.googleapis.com/auth/drive.admin.labels",
        "https://www.googleapis.com/auth/drive.admin.labels.readonly",
        "https://www.googleapis.com/auth/drive.appdata",
        "https://www.googleapis.com/auth/drive.apps.readonly",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive.labels",
        "https://www.googleapis.com/auth/drive.labels.readonly",
        "https://www.googleapis.com/auth/drive.meet.readonly",
        "https://www.googleapis.com/auth/drive.metadata",
        "https://www.googleapis.com/auth/drive.metadata.readonly",
        "https://www.googleapis.com/auth/drive.photos.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
        "https://www.googleapis.com/auth/drive.scripts",
        "https://www.googleapis.com/auth/ediscovery",
        "https://www.googleapis.com/auth/ediscovery.readonly",
        "https://www.googleapis.com/auth/factchecktools",
        "https://www.googleapis.com/auth/firebase",
        "https://www.googleapis.com/auth/firebase.messaging",
        "https://www.googleapis.com/auth/firebase.readonly",
        "https://www.googleapis.com/auth/fitness.activity.read",
        "https://www.googleapis.com/auth/fitness.activity.write",
        "https://www.googleapis.com/auth/fitness.blood_glucose.read",
        "https://www.googleapis.com/auth/fitness.blood_glucose.write",
        "https://www.googleapis.com/auth/fitness.blood_pressure.read",
        "https://www.googleapis.com/auth/fitness.blood_pressure.write",
        "https://www.googleapis.com/auth/fitness.body.read",
        "https://www.googleapis.com/auth/fitness.body.write",
        "https://www.googleapis.com/auth/fitness.body_temperature.read",
        "https://www.googleapis.com/auth/fitness.body_temperature.write",
        "https://www.googleapis.com/auth/fitness.heart_rate.read",
        "https://www.googleapis.com/auth/fitness.heart_rate.write",
        "https://www.googleapis.com/auth/fitness.location.read",
        "https://www.googleapis.com/auth/fitness.location.write",
        "https://www.googleapis.com/auth/fitness.nutrition.read",
        "https://www.googleapis.com/auth/fitness.nutrition.write",
        "https://www.googleapis.com/auth/fitness.oxygen_saturation.read",
        "https://www.googleapis.com/auth/fitness.oxygen_saturation.write",
        "https://www.googleapis.com/auth/fitness.reproductive_health.read",
        "https://www.googleapis.com/auth/fitness.reproductive_health.write",
        "https://www.googleapis.com/auth/fitness.sleep.read",
        "https://www.googleapis.com/auth/fitness.sleep.write",
        "https://www.googleapis.com/auth/forms",
        "https://www.googleapis.com/auth/forms.body",
        "https://www.googleapis.com/auth/forms.body.readonly",
        "https://www.googleapis.com/auth/forms.currentonly",
        "https://www.googleapis.com/auth/forms.responses.readonly",
        "https://www.googleapis.com/auth/games",
        "https://www.googleapis.com/auth/genomics",
        "https://www.googleapis.com/auth/gmail.addons.current.action.compose",
        "https://www.googleapis.com/auth/gmail.addons.current.message.action",
        "https://www.googleapis.com/auth/gmail.addons.current.message.metadata",
        "https://www.googleapis.com/auth/gmail.addons.current.message.readonly",
        "https://www.googleapis.com/auth/gmail.compose",
        "https://www.googleapis.com/auth/gmail.insert",
        "https://www.googleapis.com/auth/gmail.labels",
        "https://www.googleapis.com/auth/gmail.metadata",
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.settings.basic",
        "https://www.googleapis.com/auth/gmail.settings.sharing",
        "https://www.googleapis.com/auth/groups",
        "https://www.googleapis.com/auth/indexing",
        "https://www.googleapis.com/auth/keep",
        "https://www.googleapis.com/auth/keep.readonly",
        "https://www.googleapis.com/auth/logging.admin",
        "https://www.googleapis.com/auth/logging.read",
        "https://www.googleapis.com/auth/logging.write",
        "https://www.googleapis.com/auth/manufacturercenter",
        "https://www.googleapis.com/auth/meetings.space.created",
        "https://www.googleapis.com/auth/meetings.space.readonly",
        "https://www.googleapis.com/auth/monitoring",
        "https://www.googleapis.com/auth/monitoring.read",
        "https://www.googleapis.com/auth/monitoring.write",
        "https://www.googleapis.com/auth/ndev.clouddns.readonly",
        "https://www.googleapis.com/auth/ndev.clouddns.readwrite",
        "https://www.googleapis.com/auth/ndev.cloudman",
        "https://www.googleapis.com/auth/ndev.cloudman.readonly",
        "https://www.googleapis.com/auth/photoslibrary",
        "https://www.googleapis.com/auth/photoslibrary.appendonly",
        "https://www.googleapis.com/auth/photoslibrary.edit.appcreateddata",
        "https://www.googleapis.com/auth/photoslibrary.readonly",
        "https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata",
        "https://www.googleapis.com/auth/photoslibrary.sharing",
        "https://www.googleapis.com/auth/postmaster.readonly",
        "https://www.googleapis.com/auth/presentations",
        "https://www.googleapis.com/auth/presentations.readonly",
        "https://www.googleapis.com/auth/pubsub",
        "https://www.googleapis.com/auth/sasportal",
        "https://www.googleapis.com/auth/script.deployments",
        "https://www.googleapis.com/auth/script.deployments.readonly",
        "https://www.googleapis.com/auth/script.metrics",
        "https://www.googleapis.com/auth/script.processes",
        "https://www.googleapis.com/auth/script.projects",
        "https://www.googleapis.com/auth/script.projects.readonly",
        "https://www.googleapis.com/auth/service.management",
        "https://www.googleapis.com/auth/service.management.readonly",
        "https://www.googleapis.com/auth/siteverification",
        "https://www.googleapis.com/auth/siteverification.verify_only",
        "https://www.googleapis.com/auth/source.full_control",
        "https://www.googleapis.com/auth/source.read_only",
        "https://www.googleapis.com/auth/source.read_write",
        "https://www.googleapis.com/auth/spanner.admin",
        "https://www.googleapis.com/auth/spanner.data",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/sqlservice.admin",
        "https://www.googleapis.com/auth/streetviewpublish",
        "https://www.googleapis.com/auth/tagmanager.delete.containers",
        "https://www.googleapis.com/auth/tagmanager.edit.containers",
        "https://www.googleapis.com/auth/tagmanager.edit.containerversions",
        "https://www.googleapis.com/auth/tagmanager.manage.accounts",
        "https://www.googleapis.com/auth/tagmanager.manage.users",
        "https://www.googleapis.com/auth/tagmanager.publish",
        "https://www.googleapis.com/auth/tagmanager.readonly",
        "https://www.googleapis.com/auth/tasks",
        "https://www.googleapis.com/auth/tasks.readonly",
        "https://www.googleapis.com/auth/trace.append",
        "https://www.googleapis.com/auth/user.addresses.read",
        "https://www.googleapis.com/auth/user.birthday.read",
        "https://www.googleapis.com/auth/user.emails.read",
        "https://www.googleapis.com/auth/user.gender.read",
        "https://www.googleapis.com/auth/user.organization.read",
        "https://www.googleapis.com/auth/user.phonenumbers.read",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/webmasters",
        "https://www.googleapis.com/auth/webmasters.readonly",
        "https://www.googleapis.com/auth/youtube",
        "https://www.googleapis.com/auth/youtube.channel-memberships.creator",
        "https://www.googleapis.com/auth/youtube.force-ssl",
        "https://www.googleapis.com/auth/youtube.readonly",
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtubepartner",
        "https://www.googleapis.com/auth/youtubepartner-channel-audit",
        "https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
        "https://www.googleapis.com/auth/yt-analytics.readonly",
    }

    def __call__(self, form: GoogleAPIForm, field: StringField):
        scopes = field.data.strip().split(" ")
        if not scopes:
            raise StopValidation("No scopes provided")
        for scope in scopes:
            if scope not in self.valid_scopes:
                raise StopValidation(f"Invalid scope: {scope}")


class GoogleAPIForm(Form):
    client_id = StringField(
        "client_id", description="Your app identifier", validators=[InputRequired()]
    )
    client_secret = StringField(
        "client_secret", description="Your app secret", validators=[InputRequired()]
    )
    scope = StringField(
        "scopes",
        description='Enter the scopes separated by a space. Example: "email profile"',
        validators=[InputRequired(), GoogleAPIScopeValidator()],
    )
    access_type = SelectField(
        "access_type", choices=[("offline", "offline"), ("online", "online")]
    )


class GoogleAPI(BaseFlow):
    redirect_to_consent_screen_url = "https://accounts.google.com/o/oauth2/v2/auth"
    acquire_tokens_url = "https://oauth2.googleapis.com/token"
    form = GoogleAPIForm
    name = "google"

    def collect_consent_screen_args(self, form: GoogleAPIForm) -> dict:
        base_data = super().collect_consent_screen_args(form)
        base_data["response_type"] = "code"
        return base_data
