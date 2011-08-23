# -*- coding: utf-8 -*-
import crypt
from django.http import HttpResponse
from django.core.paginator import Paginator, InvalidPage
from django.shortcuts import render_to_response,get_object_or_404,get_list_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse,HttpResponseRedirect
from django.template.context import RequestContext

from django.contrib.auth.models import User as user

from subprocess import Popen,PIPE
from django.views.decorators.csrf import csrf_exempt

from wsgiadmin.settings import ROOT
from wsgiadmin.ftps.models import *

from wsgiadmin.ftps.tools import *

@login_required
def show(request,p=1):
	u = request.session.get('switched_user', request.user)
	superuser = request.user
	p = int(p)
	
	paginator = Paginator(list(u.ftp_set.all()), 10)
	
	if paginator.count == 0:
		page = None
	else:
		page = paginator.page(p)	
		
	return render_to_response('ftps.html',
							{
								"ftps":page,
								"paginator":paginator,
								"num_page":p,
								"u":u,
								"superuser":superuser,
							    "menu_active": "ftps",
							}, context_instance=RequestContext(request))

@login_required
def add(request):
	u = request.session.get('switched_user', request.user)
	superuser = request.user

	choices = [(d,d) for d in user_directories(u)]

	if request.method == 'POST':
		form = form_ftp(request.POST)
		form.u = u
		form.fields["dir"].choices = choices

		if form.is_valid():
			iftp = ftp()
			iftp.username	= u.username+"_"+form.cleaned_data["name"]
			iftp.dir		= form.cleaned_data["dir"]
			iftp.password	= crypt.crypt(form.cleaned_data["password1"],form.cleaned_data["name"])
			iftp.uid		= u.parms.uid
			iftp.gid		= u.parms.gid
			iftp.owner		= u
			iftp.save()
			
			return HttpResponseRedirect(reverse("ftps.views.show"))
	else:
		form = form_ftp()
		form.u = u
		form.fields["dir"].choices = choices

	return render_to_response('universal.html',
								{
									"form":form,
									"title":"Přidání FTP účtu",
									"submit":"Přidat FTP účet",
									"note":["* Před uživatelské jméno bude automaticky přidáno %s_"%u.username],
									"action":reverse("ftps.views.add"),
									"u":u,
									"superuser":superuser,
								    "menu_active": "ftps",
								},
	                            context_instance=RequestContext(request)
							)

@login_required
def update(request,fid):
	fid = int(fid)
	iftp = get_object_or_404(ftp,id=fid)
	u = request.session.get('switched_user', request.user)
	superuser = request.user

	choices = [(d,d) for d in user_directories(u)]

	if request.method == 'POST':
		form = form_ftp_update(request.POST)
		form.u = u
		form.edit_name = iftp.username
		form.fields["dir"].choices = choices

		if form.is_valid():
			if iftp.owner == u:
				iftp.username	= u.username+"_"+form.cleaned_data["name"]
				iftp.dir		= form.cleaned_data["dir"]
				#iftp.password	= form.cleaned_data["password1"]
				iftp.save()
				return HttpResponseRedirect(reverse("ftps.views.show"))
			else:
				return HttpResponseRedirect(reverse("useradmin.views.error"))
	else:
		form = form_ftp_update()
		form.u = u
		form.fields["dir"].choices = choices
		form.initial = {"name":iftp.username[len(u.username+"_"):],"dir":iftp.dir}

	return render_to_response('universal.html',
								{
									"form":form,
									"title":"Úprava FTP účtu",
									"submit":"Upravit FTP účet",
									"note":["* Před uživatelské jméno bude automaticky přidáno %s_"%u.username],
									"action":reverse("ftps.views.update",args=[fid]),
									"u":u,
									"superuser":superuser,
								    "menu_active": "ftps",
								},
	                            context_instance=RequestContext(request)
							)

@login_required
def passwd(request,fid):
	fid = int(fid)
	iftp = get_object_or_404(ftp,id=fid)
	u = request.session.get('switched_user', request.user)
	superuser = request.user

	choices = [(d,d) for d in user_directories(u)]

	if request.method == 'POST':
		form = form_ftp_passwd(request.POST)

		if form.is_valid():
			if iftp.owner == u:
				iftp.password	= crypt.crypt(form.cleaned_data["password1"],iftp.owner.username)
				iftp.save()
				return HttpResponseRedirect(reverse("ftps.views.show"))
			else:
				return HttpResponseRedirect(reverse("useradmin.views.error"))
	else:
		form = form_ftp_passwd()

	return render_to_response('universal.html',
								{
									"form":form,
									"title":"Úprava FTP účtu",
									"submit":"Upravit FTP účet",
									"action":reverse("ftps.views.passwd",args=[fid]),
									"u":u,
									"superuser":superuser,
								    "menu_active": "ftps",
								},
	                            context_instance=RequestContext(request)
							)

@login_required
@csrf_exempt
def rm(request,fid):
	fid = int(fid)
	iftp = get_object_or_404(ftp,id=fid)
	u = request.session.get('switched_user', request.user)
	superuser = request.user
	
	if iftp.owner == u:
		iftp.delete()
		return HttpResponse("FTP účet vymazán")
	else:
		return HttpResponse("Chyba oprávnění")