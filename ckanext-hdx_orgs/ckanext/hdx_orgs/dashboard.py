import ckan.controllers.user as uc
import logging
from urllib import quote
from urlparse import urlparse

from pylons import config

import ckan.lib.base as base
import ckan.model as model
import ckan.lib.helpers as h
import ckan.new_authz as new_authz
import ckan.logic as logic
import ckan.logic.schema as schema
import ckan.lib.captcha as captcha
import ckan.lib.mailer as mailer
import ckan.lib.navl.dictization_functions as dictization_functions
import ckan.plugins as p

from ckan.common import _, c, g, request

log = logging.getLogger(__name__)


abort = base.abort
render = base.render
validate = base.validate

check_access = logic.check_access
get_action = logic.get_action
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError

DataError = dictization_functions.DataError
unflatten = dictization_functions.unflatten


class DashboardController(uc.UserController):
	def _get_dashboard_context(self, filter_type=None, filter_id=None, q=None):
		'''Return a dict needed by the dashboard view to determine context.'''

		def display_name(followee):
			'''Return a display name for a user, group or dataset dict.'''
			display_name = followee.get('display_name')
			fullname = followee.get('fullname')
			title = followee.get('title')
			name = followee.get('name')
			return display_name or fullname or title or name

		if (filter_type and filter_id):
			context = {
				'model': model, 'session': model.Session,
				'user': c.user or c.author, 'auth_user_obj': c.userobj,
				'for_view': True
			}
			try:
				c.group_dict = logic.get_action('organization_show')(context, {'id': filter_id})#patch for db entries
				if c.group_dict['is_organization']:
					filter_type = 'organization'
			except:
				filter_type = filter_type
			data_dict = {'id': filter_id}
			followee = None

			action_functions = {
				'dataset': 'package_show',
				'user': 'user_show',
				'group': 'group_show',
				'organization' : 'organization_show' #ADD BY HDX
			}
			action_function = logic.get_action(
				action_functions.get(filter_type))
			# Is this a valid type?
			if action_function is None:
				abort(404, _('Follow item not found'))
			try:
				followee = action_function(context, data_dict)
			except NotFound:
				abort(404, _('{0} not found').format(filter_type))
			except NotAuthorized:
				abort(401, _('Unauthorized to read {0} {1}').format(
					filter_type, id))
			if followee is not None:
				return {
					'filter_type': filter_type,
					'q': q,
					'context': display_name(followee),
					'selected_id': followee.get('id'),
					'dict': followee,
				}

		return {
			'filter_type': filter_type,
			'q': q,
			'context': _('Everything'),
			'selected_id': False,
			'dict': None,
		}

	def dashboard_activity_stream(self, user_id, filter_type=None, filter_id=None,
							  offset=0):
		'''Return the dashboard activity stream of the current user.

		:param user_id: the id of the user
		:type user_id: string

		:param filter_type: the type of thing to filter by
		:type filter_type: string

		:param filter_id: the id of item to filter by
		:type filter_id: string

		:returns: an activity stream as an HTML snippet
		:rtype: string

		'''
		context = {'model': model, 'session': model.Session, 'user': c.user}

		if filter_type:
			action_functions = {
				'dataset': 'package_activity_list_html',
				'user': 'user_activity_list_html',
				'group': 'group_activity_list_html',
				'organization': 'organization_activity_list_html' #ADDED BY HDX
			}
			action_function = logic.get_action(action_functions.get(filter_type))
			return action_function(context, {'id': filter_id, 'offset': offset})
		else:
			return logic.get_action('dashboard_activity_list_html')(
				context, {'offset': offset})


	def dashboard(self, id=None, offset=0):
		context = {'model': model, 'session': model.Session,
				   'user': c.user or c.author, 'auth_user_obj': c.userobj,
				   'for_view': True}
		data_dict = {'id': id, 'user_obj': c.userobj, 'offset': offset}
		self._setup_template_variables(context, data_dict)

		q = request.params.get('q', u'')
		filter_type = request.params.get('type', u'')
		filter_id = request.params.get('name', u'')

		c.followee_list = get_action('followee_list')(
			context, {'id': c.userobj.id, 'q': q})
		c.dashboard_activity_stream_context = self._get_dashboard_context(
			filter_type, filter_id, q)
		c.dashboard_activity_stream = self.dashboard_activity_stream(c.userobj.id, filter_type, filter_id, offset)

		# Mark the user's new activities as old whenever they view their
		# dashboard page.
		get_action('dashboard_mark_activities_old')(context, {})

		return render('user/dashboard.html')