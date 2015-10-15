from django.conf.urls import patterns, url, include
from answer_question import views
import allauth.account.views as account


urlpatterns = patterns(
	"",
	url(r'^login', account.LoginView.as_view(), name="account_login"),
	url(r'^logout', account.LogoutView.as_view(), name="account_logout"),
	# MANGE ANSWER QUESTION
	url(
		r"^$",
		views.list_answer_question,
		name="home"
	),
	url(
		r"^add_answer_question",
		views.add_answer_question,
		name="add_answer_question"
	),
	url(
		r'^edit_answer_question/(?P<question_id>.*)',
		views.edit_answer_question,
		name='edit_answer_question'),

	# MANGE CATEGORY
	url(
		r"^list_category",
		views.list_category,
		name="list_category"
	),
	url(
		r'^add_category',
		views.add_category,
		name='add_category'),
	url(
		r'^edit_category/(?P<category_id>.*)',
		views.edit_category,
		name='edit_category'),

	# MANGE CODE
	url(
		r"^list_code",
		views.list_code,
		name="list_code"
	),
	url(
		r'^add_code',
		views.add_code,
		name='add_code'),
	url(
		r'^edit_code/(?P<code_id>.*)',
		views.edit_code,
		name='edit_code'),

	# AJAX CONNECT TO SERVER
	url(
		r"^remove_answer_question",
		views._remove_answer_question,
		name="remove_answer_question"
	),
	url(
		r"^remove_answer",
		views._remove_answer,
		name="remove_answer"
	),
	url(
		r"^remove_category",
		views._remove_category,
		name="remove_category"
	),
	url(
		r"^remove_code",
		views._remove_code,
		name="remove_code"
	)
)

