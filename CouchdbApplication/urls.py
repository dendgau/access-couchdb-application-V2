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
		views.QAAdd.as_view(),
		name="add_answer_question"
	),
	url(
		r'^edit_answer_question/(?P<question_id>.*)',
		views.QADetail.as_view(),
		name='edit_answer_question'),

	# MANGE CATEGORY
	url(
		r"^list_category",
		views.ListCategory.as_view(),
		name="list_category"
	),
	url(
		r'^add_category',
		views.CategoryAdd.as_view(),
		name='add_category'),
	url(
		r'^edit_category/(?P<category_id>.*)',
		views.CategoryEdit.as_view(),
		name='edit_category'),

	# MANGE CODE
	url(
		r"^list_code",
		views.ListCode.as_view(),
		name="list_code"
	),
	url(
		r'^add_code',
		views.QACodeAdd.as_view(),
		name='add_code'),
	url(
		r'^edit_code/(?P<code_id>.*)',
		views.QACodeDetail.as_view(),
		name='edit_code'),

	# AJAX CONNECT TO SERVER
	url(
		r"^remove_answer_question",
		views.remove_answer_question,
		name="remove_answer_question"
	),
	url(
		r"^remove_answer",
		views.remove_answer,
		name="remove_answer"
	),
	url(
		r"^remove_category",
		views.remove_category,
		name="remove_category"
	),
	url(
		r"^remove_code",
		views.remove_code,
		name="remove_code"
	)
)

