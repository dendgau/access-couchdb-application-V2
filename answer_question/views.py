# -*- coding: utf-8 -*-
import json
import logging
import forms
import datetime

from django import http
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import FormView
from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponse

from answer_question import couch_server as pycouchdb
from couch_server import MESSAGE


class JSONResponseMixin(object):

	def render_to_response(self, context):
		return self.get_json_response(self.convert_context_to_json(context))

	@staticmethod
	def get_json_response(content, **http_response_kwargs):
		return http.HttpResponse(
			content,
			content_type='application/json',
			**http_response_kwargs
		)

	@staticmethod
	def convert_context_to_json(context):
		return json.dumps(context)


class ListQA(ListView):
	paginate_by = 20
	template_name = "answer_question/list_answer_question.html"

	def get_queryset(self):
		queryset = []

		try:
			connection = pycouchdb.ConnectCouchdb()
			if self.request.GET.get("q", None):
				questions = connection.query_doc(pycouchdb.MAP_FUNCTION_MULTI_CONDITION %
					('doc.table == "question" && (doc.content).search("'+self.request.GET.get("q", None)+'") >= 0'))
			else:
				questions = connection.query_doc(pycouchdb.MAP_FUNCTION_COMMON % ("table", "question"))
			categories = connection.query_doc(pycouchdb.MAP_FUNCTION_COMMON % ("table", "category"))
			if questions:
				for q in questions:
					if q["value"]["category"]:
						for c in categories:
							if q["value"]["category"] == c["id"]:
								q["value"]["category"] = c["value"]["name"]
								break
			queryset = questions
		except Exception, e:
			logging.error(str(e))
			messages.add_message(self.request, messages.ERROR, MESSAGE['ERROR_CONNECT'])

		return queryset


class QADetail(TemplateView, JSONResponseMixin):
	template_name = "answer_question/edit_answer_question.html"

	def get_context_data(self, **kwargs):
		context = super(QADetail, self).get_context_data(**kwargs)
		try:
			question_id = self.kwargs.get("question_id", None)
			connection = pycouchdb.ConnectCouchdb()
			doc_question = connection.get_doc(question_id)
		except Exception, e:
			logging.error(str(e))
			messages.add_message(self.request, messages.ERROR, MESSAGE['ERROR_CONNECT'])
			return context

		context["question_id"] = question_id
		context["question"] = doc_question["content"]
		context["category"] = doc_question["category"]
		context["type"] = doc_question["type"]

		if doc_question["answer_id"]:
			condition_get_answer = 'doc.table == "answer" && ('
			for index, answer_id in enumerate(filter(None, doc_question["answer_id"])):
				if index == 0:
					condition_get_answer += ('doc._id == "%s"' % answer_id)
				else:
					condition_get_answer += (' || doc._id == "%s"' % answer_id)
			condition_get_answer += ")"

			answers = connection.query_doc(pycouchdb.MAP_FUNCTION_MULTI_CONDITION % condition_get_answer)
			context["answers"] = answers

		categories = connection.query_doc(pycouchdb.MAP_FUNCTION_COMMON % ("table", "category"))
		context["categories"] = categories
		return context

	def post(self, request, *args, **kwargs):
		if request.method == 'POST':
			try:
				question_id = kwargs.get("question_id", None)
				connection = pycouchdb.ConnectCouchdb()
				doc_question = connection.get_doc(question_id)
			except Exception, e:
				logging.error(str(e))
				messages.add_message(self.request, messages.ERROR, MESSAGE['ERROR_CONNECT'])
				return HttpResponse(status=500)

			_doc_question = {
				"content": request.POST.get("question", None),
				"type": request.POST.get("type-answers", None),
				"category": request.POST.get("categories", None)}
			doc_question.update(_doc_question)

			answers = filter(None, request.POST.getlist('answer'))
			if doc_question["type"] != "03" and answers:
				for answer in answers:
					_doc_answer = {
						"content": answer,
						"table": "answer",
						"question_id": doc_question.get("_id", None)
					}
					doc_answer = connection.save_doc(_doc_answer)
					doc_question["answer_id"].append(doc_answer["_id"])
			elif doc_question["type"] == "03":
				del (doc_question["answer_id"])[:]

			connection.save_doc(doc_question)
			messages.add_message(self.request, messages.SUCCESS, MESSAGE['EDIT_SUCCESS'])

		return HttpResponseRedirect('')


class QAAdd(TemplateView, JSONResponseMixin):
	template_name = "answer_question/add_answer_question.html"

	def get_context_data(self, **kwargs):
		context = super(QAAdd, self).get_context_data(**kwargs)
		try:
			connection = pycouchdb.ConnectCouchdb()
			categories = connection.query_doc(pycouchdb.MAP_FUNCTION_COMMON % ("table", "category"))
		except Exception, e:
			logging.error(str(e))
			messages.add_message(self.request, messages.ERROR, MESSAGE['ERROR_CONNECT'])
			return context

		context["categories"] = categories
		return context

	def post(self, request, *args, **kwargs):
		if request.method == 'POST':

			try:
				connection = pycouchdb.ConnectCouchdb()
			except Exception, e:
				logging.error(str(e))
				messages.add_message(self.request, messages.ERROR, MESSAGE['ERROR_CONNECT'])
				return HttpResponse(status=500)

			_doc_question = {
				"table": "question",
				"content": request.POST.get("question", None),
				"type": request.POST.get("type-answers", None),
				"category": request.POST.get("categories", None),
				"answer_id": []}
			doc_question = connection.save_doc(_doc_question)

			answers = filter(None, request.POST.getlist('answer'))
			if answers:
				for answer in answers:
					_doc_answer = {
						"content": str(answer),
						"table": "answer",
						"question_id": doc_question["_id"]
					}
					doc_answer = connection.save_doc(_doc_answer)
					doc_question["answer_id"].append(doc_answer["_id"])

			connection.save_doc(doc_question)
			messages.add_message(self.request, messages.SUCCESS, MESSAGE['ADD_SUCCESS'])

		return HttpResponseRedirect('/edit_answer_question/%s' % doc_question["_id"])


class ListCategory(ListView):
	paginate_by = 20
	template_name = "category/list_category.html"

	def get_queryset(self):
		queryset = []

		try:
			connection = pycouchdb.ConnectCouchdb()
			queryset = connection.query_doc(pycouchdb.MAP_FUNCTION_COMMON % ("table", "category"))
		except Exception, e:
			logging.error(str(e))
			messages.add_message(self.request, messages.ERROR, MESSAGE['ERROR_CONNECT'])

		return queryset


class CategoryAdd(FormView):
	form_class = forms.CategoryForm
	template_name = "category/add_category.html"
	success_url = ''

	def form_valid(self, form):
		try:
			connection = pycouchdb.ConnectCouchdb()
			doc_category = connection.save_doc({
				'table': 'category',
				'name': form.cleaned_data["category_name"]
			})
		except Exception, e:
			logging.error(str(e))
			messages.add_message(self.request, messages.ERROR, MESSAGE['ERROR_CONNECT'])
			return HttpResponse(status=500)

		self.success_url = "/edit_category/%s" % doc_category["_id"]
		messages.add_message(self.request, messages.SUCCESS, MESSAGE["ADD_SUCCESS"])
		return super(CategoryAdd, self).form_valid(form)

	def form_invalid(self, form):
		messages.add_message(self.request, messages.ERROR, MESSAGE["ERROR_CATEGORY_FORM"])
		return super(CategoryAdd, self).form_invalid(form)


class CategoryEdit(FormView):
	form_class = forms.CategoryForm
	template_name = "category/edit_category.html"
	success_url = '/'

	def get_context_data(self, **kwargs):
		context = super(CategoryEdit, self).get_context_data(**kwargs)
		context["category_id"] = self.kwargs.get("category_id", None)
		return context

	def get_initial(self):
		initial = super(CategoryEdit, self).get_initial()
		try:
			category_id = self.kwargs.get("category_id", None)
			connection = pycouchdb.ConnectCouchdb()
			category_doc = connection.get_doc(category_id)
		except Exception, e:
			logging.error(str(e))
			messages.add_message(self.request, messages.ERROR, MESSAGE['ERROR_CONNECT'])
			return HttpResponse(status=500)

		initial["category_name"] = category_doc["name"]
		return initial

	def form_valid(self, form):
		try:
			category_id = self.kwargs.get("category_id", None)
			connection = pycouchdb.ConnectCouchdb()
			doc_category = connection.get_doc(category_id)
			doc_category["name"] = form.cleaned_data["category_name"]
			connection.save_doc(doc_category)
		except Exception, e:
			logging.error(str(e))
			messages.add_message(self.request, messages.ERROR, MESSAGE['ERROR_CONNECT'])
			return HttpResponse(status=500)

		self.success_url = "/edit_category/%s" % doc_category["_id"]
		messages.add_message(self.request, messages.SUCCESS, MESSAGE["EDIT_SUCCESS"])
		return super(CategoryEdit, self).form_valid(form)

	def form_invalid(self, form):
		messages.add_message(self.request, messages.ERROR, MESSAGE["ERROR_CATEGORY_FORM"])
		return super(CategoryEdit, self).form_invalid(form)


@csrf_exempt
def remove_category(request):
	if request.method == 'POST':
		try:
			category_id = request.POST.get("categoryId", None)
			connection = pycouchdb.ConnectCouchdb()
			connection.delete_doc(category_id)

			questions = connection.query_doc(pycouchdb.MAP_FUNCTION_COMMON % ("category", str(category_id)))
			if questions:
				for q in questions:
					question_doc = connection.get_doc(q["id"])
					question_doc["category"] = None
					connection.save_doc(question_doc)
		except Exception, e:
			logging.error(str(e))
			# messages.add_message(request, messages.ERROR, MESSAGE['ERROR_CONNECT'])
			return HttpResponse(status=500)
		return HttpResponse(status=200)

@csrf_exempt
def remove_answer(request):
	if request.method == 'POST':
		try:
			answer_id = request.POST.get("answerId", None)
			question_id = request.POST.get("questionId", None)

			connection = pycouchdb.ConnectCouchdb()
			connection.delete_doc(answer_id)

			doc_question = connection.get_doc(question_id)
			doc_question["answer_id"].remove(answer_id)

			connection.save_doc(doc_question)
		except Exception, e:
			logging.error(str(e))
			# messages.add_message(request, messages.ERROR, MESSAGE['ERROR_CONNECT'])
			return HttpResponse(status=500)
		return HttpResponse(status=200)

@csrf_exempt
def remove_answer_question(request):
	if request.method == 'POST':
		try:
			question_id = request.POST.get("questionId", None)
			connection = pycouchdb.ConnectCouchdb()
			doc_question = connection.get_doc(question_id)
		except Exception, e:
			logging.error(str(e))
			return HttpResponse(status=500)

		if doc_question:
			doc_answers = doc_question["answer_id"]
			connection.delete_doc(question_id)

			if doc_answers:
				for answer in doc_answers:
					connection.delete_doc(answer)

		# messages.add_message(request, messages.SUCCESS, MESSAGE['DELETE_SUCCESS'])
		return HttpResponse(status=200)


class ListCode(ListView):
	paginate_by = 20
	template_name = "code/list_code.html"

	def get_queryset(self):
		queryset = []

		try:
			connection = pycouchdb.ConnectCouchdb()
			codes = connection.query_doc(pycouchdb.MAP_FUNCTION_COMMON % ("table", "code"))
			for c in codes:
				username = connection.get_doc(c["value"]["user_id"])
				c["value"].update({"username": username["name"]})
			queryset = codes
		except Exception, e:
			logging.error(str(e))
			messages.add_message(self.request, messages.ERROR, MESSAGE['ERROR_CONNECT'])

		return queryset


class QACodeAdd(TemplateView, JSONResponseMixin):
	template_name = "code/add_code.html"

	def get_context_data(self, **kwargs):
		context = super(QACodeAdd, self).get_context_data(**kwargs)
		try:
			connection = pycouchdb.ConnectCouchdb()
			members = connection.query_doc(pycouchdb.MAP_FUNCTION_COMMON % ("table", "member"))
			questions = connection.query_doc(pycouchdb.MAP_FUNCTION_COMMON % ("table", "question"))
		except Exception, e:
			logging.error(str(e))
			messages.add_message(self.request, messages.ERROR, MESSAGE['ERROR_CONNECT'])
			return context

		context["members"] = members
		context["questions"] = questions
		return context

	def post(self, request, *args, **kwargs):
		if request.method == 'POST':
			try:
				connection = pycouchdb.ConnectCouchdb()
			except Exception, e:
				logging.error(str(e))
				messages.add_message(self.request, messages.ERROR, MESSAGE['ERROR_CONNECT'])
				return HttpResponse(status=500)

			_doc_code = {
				"table": "code",
				"name": request.POST.get("code_name", None),
				"point": int(request.POST.get("point", None)),
				"time": int(request.POST.get("duration", None)),
				"user_id": request.POST.get("member_id", None),
				"question_id": filter(None, request.POST.getlist('question_select')),
				"date": (datetime.datetime.now()).strftime("%d-%m-%Y"),
				"status": "0"}
			doc_code = connection.save_doc(_doc_code)

		return HttpResponseRedirect('/edit_code/%s' % doc_code["_id"])


class QACodeDetail(TemplateView, JSONResponseMixin):
	template_name = "code/edit_code.html"

	def get_context_data(self, **kwargs):
		context = super(QACodeDetail, self).get_context_data(**kwargs)
		try:
			connection = pycouchdb.ConnectCouchdb()
			doc_code = connection.get_doc(kwargs.get("code_id", None))
			doc_code.update({"id": kwargs.get("code_id", None)})
			doc_member = connection.get_doc(doc_code["user_id"])
			questions = connection.query_doc(pycouchdb.MAP_FUNCTION_COMMON % ("table", "question"))
		except Exception, e:
			logging.error(str(e))
			messages.add_message(self.request, messages.ERROR, MESSAGE['ERROR_CONNECT'])
			return context

		context["doc_code"] = doc_code
		context["doc_member"] = doc_member
		context["questions"] = questions
		return context

	def post(self, request, *args, **kwargs):
		if request.method == 'POST':
			try:
				connection = pycouchdb.ConnectCouchdb()
				doc_code = connection.get_doc(kwargs.get("code_id", None))
			except Exception, e:
				logging.error(str(e))
				messages.add_message(self.request, messages.ERROR, MESSAGE['ERROR_CONNECT'])
				return HttpResponse(status=500)

			doc_code.update({
				"table": "code",
				"name": request.POST.get("code_name", None),
				"time": int(request.POST.get("duration", None)),
				"point": int(request.POST.get("point", None)),
				"question_id": filter(None, request.POST.getlist('question_select')),
				"date": (datetime.datetime.now()).strftime("%d-%m-%Y")})
			doc_code = connection.save_doc(doc_code)

		return HttpResponseRedirect('/edit_code/%s' % doc_code["_id"])

@csrf_exempt
def remove_code(request):
	if request.method == 'POST':
		try:
			code_id = request.POST.get("codeId", None)
			connection = pycouchdb.ConnectCouchdb()
			connection.delete_doc(code_id)
		except Exception, e:
			logging.error(str(e))
			# messages.add_message(request, messages.ERROR, MESSAGE['ERROR_CONNECT'])
			return HttpResponse(status=500)
		return HttpResponse(status=200)
