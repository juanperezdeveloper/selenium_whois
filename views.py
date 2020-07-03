
from django.shortcuts import render, redirect
from django.views.generic import ListView,CreateView,UpdateView,DeleteView,TemplateView
from .models import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from .forms import CajeroForm,PuntoVentaForm,TerminalForm,UsuarioForm,GrupoForm,JackpotKenoForm,JackpotBingoForm
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.db.models import Count
from django.db.models.functions import Coalesce
from django.db.models import Q
from django.template.response import TemplateResponse
from django.db.models import Sum
import datetime
from django.contrib.auth.models import Group
from django.contrib.sessions.models import Session
from django.contrib.auth import authenticate, login, logout


# Create your views here.
# class Home(LoginRequiredMixin,TemplateView):
	
# 	template_name=	'dashboard.html'
# 	login_url='/login'
# 	context_object_name='obj'

def Login(request):
	next = request.GET.get('next', '/home/')
	if request.method == "POST":
		username == request.POST['username']
		password == request.POST['password']
		user = authenticate(username=username, password=password)

		if user is not None:
			if user.is_active:
				login(request, user)
				return (HttpResponseRedirect(next))
			else:
				HttpResponse("Inactive user.")
		else:
			return HttpResponseRedirect(settings.Login_URL)

	return render(request,"login/login-page.html",{redirect_to:next})

@login_required
def Home(request):
	
	template_name=	'dashboard.html'
	login_url='/login'
	# context_object_name='obj'
	username = request.user.username
	queryset = []
	today = datetime.datetime.today().strftime('%Y/%m/%d')
	inicial_date = '0000/00/00'

	current_user = request.user

	if current_user.is_staff and current_user.is_superuser == False:

		inicial_date = today

		# get datas of puntoventa related on the logged user. (superuser + related users)
		puntoventa_filter = PuntoVenta.objects.all()

		# allset from CartonKeno
		filterd_set_keno = CartonKeno.objects.all().filter(fecha_keno=today)
		# allset from CartonCartas
		filterd_set_cartas = CartonCartas.objects.all().filter(fecha_cartas=today)

		filterd_set_keno_aggregate = filterd_set_keno.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_k'), ventas=Sum('valor_apuesta_k'))
		
		filterd_set_cartas_aggregate = filterd_set_cartas.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__user_id__username').annotate(tickets=Count('id_c_c'), ventas=Sum('valor_apuesta_c'))
		
		# calculate the premois
		# filterd_set_ganadoreskeno = GanadoresKeno.objects.all().filter(fecha_ganadores_k=today)
		# filterd_set_ganadorescartas = GanadoresCartas.objects.all().filter(fecha_ganadores_c=today)
	
	# logged user is a superuser but not staff
	elif current_user.is_superuser and current_user.is_staff == False:

		users = User.objects.filter(groups__id=current_user.id)
		user_ids = users.values('id')

		# get datas of puntoventa related on the logged user. (superuser + related users)
		puntoventa_filter = PuntoVenta.objects.filter(Q(user_id__in=user_ids) | Q(user_id=current_user.id))

		# allset from CartonKeno
		filterd_set_keno = CartonKeno.objects.all().filter(fecha_keno__lte=today)
		# allset from CartonCartas
		filterd_set_cartas = CartonCartas.objects.all().filter(fecha_cartas__lte=today)

		filterd_set_keno = filterd_set_keno.filter(Q(id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_cajero__id_pos_pc__id_pv__user_id=current_user.id))
		filterd_set_cartas = filterd_set_cartas.filter(Q(id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_cajero__id_pos_pc__id_pv__user_id=current_user.id))

		filterd_set_keno_aggregate = filterd_set_keno.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_k'), ventas=Sum('valor_apuesta_k'))
		
		filterd_set_cartas_aggregate = filterd_set_cartas.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__user_id__username').annotate(tickets=Count('id_c_c'), ventas=Sum('valor_apuesta_c'))
	
	# if the logged user is not a superuser and staff 
	elif current_user.is_superuser == False and current_user.is_staff == False:
		# get datas of puntoventa related on the logged user. (only logged user)
		puntoventa_filter = PuntoVenta.objects.filter(user_id=current_user.id)

		# allset from CartonKeno
		filterd_set_keno = CartonKeno.objects.all().filter(fecha_keno__lte=today)
		# allset from CartonCartas
		filterd_set_cartas = CartonCartas.objects.all().filter(fecha_cartas__lte=today)

		# if user_id != "0":
		filterd_set_keno = filterd_set_keno.filter( id_cajero__id_pos_pc__id_pv__user_id=current_user.id )
		filterd_set_cartas = filterd_set_cartas.filter( id_cajero__id_pos_pc__id_pv__user_id=current_user.id )
		# else:

		filterd_set_keno_aggregate = filterd_set_keno.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_k'), ventas=Sum('valor_apuesta_k'))
		
		filterd_set_cartas_aggregate = filterd_set_cartas.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__user_id__username').annotate(tickets=Count('id_c_c'), ventas=Sum('valor_apuesta_c'))
		
		
		# calculate the premois
		
		# filterd_set_ganadoreskeno = GanadoresKeno.objects.all().filter(fecha_ganadores_k__lte=today)
		# filterd_set_ganadorescartas = GanadoresCartas.objects.all().filter(fecha_ganadores_c__lte=today)

		
	# add ventas from two queryset list (CartonKeno + CartonCartas)
	table_data = set_table_data(filterd_set_keno_aggregate, filterd_set_cartas_aggregate, current_user.is_staff, '0', inicial_date, today)
		
	# # append filtered set for datatable
	# queryset.append(table_data) # obj.0

	# get pdvs
	pdvs = len(table_data)

	tickets = 0
	ventas = 0
	premios = 0
	saldo = 0
	for item in table_data:
		tickets += item['tickets']
		ventas += item['ventas']
		premios += item['premios']
		saldo += item['saldo']


	# return Response
	# tickets : tickets
	# ventas : ventas
	# premios : premios
	# saldo : saldo	
	# pdvs : pdvs
	# username : username
	return TemplateResponse(request, template_name, {'tickets':tickets, 'ventas':'${:0,.2f}'.format(ventas), 'premios':'${:0,.2f}'.format(premios), 'saldo':'${:0,.2f}'.format(saldo), 'pdvs':pdvs, 'username':username})
	

def set_table_data(allset_carton_keno_aggregate, allset_carton_cartas_aggregate, is_staff=False, user_id = '0', inicial = '', final=''):
	

	table_data = []

	for i in range(len(allset_carton_keno_aggregate)):

		line_cartas = {}
		line_cartas['tickets'] = 0
		line_cartas['ventas'] = 0

		line_keno = allset_carton_keno_aggregate[i]

		charts_len = len(allset_carton_cartas_aggregate)
		
		if  charts_len != 0 and charts_len >= i:

			for j in range(len(allset_carton_cartas_aggregate)):
				
				carton_cartas_aggregate = allset_carton_cartas_aggregate[j]
				
				cartas_username = carton_cartas_aggregate['id_cajero__id_pos_pc__id_pv__user_id__username']
				cartas_localidad = carton_cartas_aggregate['id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad']
				cartas_pdv = carton_cartas_aggregate['id_cajero__id_pos_pc__id_pv__nombre_pv']

				keno_username = line_keno['id_cajero__id_pos_pc__id_pv__user_id__username']
				keno_localidad = line_keno['id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad']
				keno_pdv = line_keno['id_cajero__id_pos_pc__id_pv__nombre_pv']


				if cartas_username == keno_username and cartas_localidad == keno_localidad and cartas_pdv == keno_pdv: 
					
					line_cartas['tickets'] += carton_cartas_aggregate['tickets']
					line_cartas['ventas'] += carton_cartas_aggregate['ventas']
					
			
		sum_keno_cartas = line_keno

		# add tickets from two tables (keno + cartas)
		sum_keno_cartas['tickets'] = line_cartas['tickets'] + line_keno['tickets']

		# add ventas from two tables (keno + cartas)
		sum_keno_cartas['ventas'] = line_cartas['ventas'] + line_keno['ventas']

		# calculate premios
		if user_id != '0':
			filterd_set_ganadoreskeno = GanadoresKeno.objects.all().filter( id_c_k__id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=line_keno['id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad'] ).filter( id_c_k__id_cajero__id_pos_pc__id_pv__nombre_pv=line_keno['id_cajero__id_pos_pc__id_pv__nombre_pv'] ).filter( id_c_k__id_cajero__id_pos_pc__id_pv__user_id = user_id )
			filterd_set_ganadorescartas = GanadoresCartas.objects.all().filter( id_c_c__id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=line_keno['id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad'] ).filter( id_c_c__id_cajero__id_pos_pc__id_pv__nombre_pv=line_keno['id_cajero__id_pos_pc__id_pv__nombre_pv'] ).filter( id_c_c__id_cajero__id_pos_pc__id_pv__user_id = user_id )
		else:
			filterd_set_ganadoreskeno = GanadoresKeno.objects.all().filter( id_c_k__id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=line_keno['id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad'] ).filter( id_c_k__id_cajero__id_pos_pc__id_pv__nombre_pv=line_keno['id_cajero__id_pos_pc__id_pv__nombre_pv'] )
			filterd_set_ganadorescartas = GanadoresCartas.objects.all().filter( id_c_c__id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=line_keno['id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad'] ).filter( id_c_c__id_cajero__id_pos_pc__id_pv__nombre_pv=line_keno['id_cajero__id_pos_pc__id_pv__nombre_pv'] )
			
		if inicial != '' and final != '':
			filterd_set_ganadoreskeno = filterd_set_ganadoreskeno.filter(fecha_ganadores_k__gte=inicial, fecha_ganadores_k__lte=final)
			filterd_set_ganadorescartas = filterd_set_ganadorescartas.filter(fecha_ganadores_c__gte=inicial, fecha_ganadores_c__lte=final)

		premios_ganadoreskeno = filterd_set_ganadoreskeno.aggregate(valor_ganado_k__sum=Coalesce(Sum('valor_ganado_k'),0))['valor_ganado_k__sum']
		premios_ganadorescartas = filterd_set_ganadorescartas.aggregate(valor_ganado_c__sum=Coalesce(Sum('valor_ganado_c'),0))['valor_ganado_c__sum']

		if premios_ganadorescartas is not None:
			# line_cartas['premios'] = premios_ganadoreskeno + premios_ganadorescartas
			sum_keno_cartas['premios'] = premios_ganadoreskeno + premios_ganadorescartas
		else:
			sum_keno_cartas['premios'] = premios_ganadoreskeno

		# calculate saldo
		sum_keno_cartas['saldo'] = sum_keno_cartas['ventas'] - sum_keno_cartas['premios']

		# calculate percentage
		if sum_keno_cartas['ventas'] != 0:
			sum_keno_cartas['percentage'] = round(sum_keno_cartas['premios'] * 100 / sum_keno_cartas['ventas'], 2)
		else:
			sum_keno_cartas['percentage'] = 0

		sum_keno_cartas['percentage'] = '%{:0,.2f}'.format(sum_keno_cartas['percentage'])

		table_data.append(sum_keno_cartas)

		
	return table_data


# class Reportes(LoginRequiredMixin,ListView):
# class Reportes(ListView):
@login_required
def reportes(request, general_report=None):
	
	# model:CartonKeno
	template_name=	'reportes.html'
	context_object_name='obj'
	queryset = []

	current_user = request.user

	if current_user.is_staff:
		allset_carton_keno = CartonKeno.objects.all()
		allset_carton_cartas = CartonCartas.objects.all()

		#get data for all puntoventa
		puntoventa_filter = PuntoVenta.objects.all()

		# auth_user table (only logged user)
		filterset_user = User.objects.all().values('id', 'username').annotate(dcount=Count('id'))


	elif current_user.is_superuser and current_user.is_staff == False:
		users = User.objects.filter(groups__id=current_user.id)
		user_ids = users.values('id')

		allset_carton_keno = CartonKeno.objects.all()
		allset_carton_cartas = CartonCartas.objects.all()

		# for user_id in user_ids: (superuser + related users)
		allset_carton_keno = allset_carton_keno.filter(Q(id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_cajero__id_pos_pc__id_pv__user_id=current_user.id))
		allset_carton_cartas = allset_carton_cartas.filter(Q(id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_cajero__id_pos_pc__id_pv__user_id=current_user.id))

		# get datas of puntoventa related on the logged user. (superuser + related users)
		puntoventa_filter = PuntoVenta.objects.filter(Q(user_id__in=user_ids) | Q(user_id=current_user.id))

		# auth_user table (superuser + related users)
		filterset_user = User.objects.filter(Q(groups__id=current_user.id) | Q(id=current_user.id)).values('id', 'username').annotate(dcount=Count('id'))
		
	elif current_user.is_superuser == False and current_user.is_staff == False:
		# (only logged user)
		allset_carton_keno = CartonKeno.objects.filter(id_cajero__id_pos_pc__id_pv__user_id=current_user.id)
		allset_carton_cartas = CartonCartas.objects.filter(id_cajero__id_pos_pc__id_pv__user_id=current_user.id)

		# get datas of puntoventa related on the logged user. (only logged user)
		puntoventa_filter = PuntoVenta.objects.filter(user_id=current_user.id)

		# auth_user table (only logged user)
		filterset_user = User.objects.filter(id=current_user.id).values('id', 'username').annotate(dcount=Count('id'))
		

	allset_carton_keno_aggregate = allset_carton_keno.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_k'), ventas=Sum('valor_apuesta_k'))
	allset_carton_charts_aggregate = allset_carton_cartas.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_c'), ventas=Sum('valor_apuesta_c'))
	
	
	# add ventas from two queryset list
	table_data = set_table_data(allset_carton_keno_aggregate, allset_carton_charts_aggregate, current_user.is_staff)

	queryset.append(table_data) # obj.0


	# model:Localidad
	# filterset_localidad = Localidad.objects.values('nombre_localidad').annotate(dcount=Count('nombre_localidad'))
	localidads = puntoventa_filter.values('id_localidad')
	filterset_localidad = Localidad.objects.filter(id_localidad__in=localidads).values('nombre_localidad').annotate(dcount=Count('nombre_localidad'))	
	queryset.append(filterset_localidad) # obj.1

	# model:PuntoVenta
	# filterset_pdv = PuntoVenta.objects.values('nombre_pv').annotate(dcount=Count('nombre_pv'))
	filterset_pdv = puntoventa_filter.values('nombre_pv').annotate(dcount=Count('nombre_pv'))	
	queryset.append(filterset_pdv) # obj.2


	pdvs = len(table_data)
	tickets = 0
	ventas = 0
	premios = 0
	saldo = 0
	for item in table_data:
		tickets += item['tickets']
		ventas += item['ventas']
		premios += item['premios']
		saldo += item['saldo']

	
	queryset.append(filterset_user) # obj.3

	header_colors = []
	if ventas < 0:
		header_colors.append(0)
	else:
		header_colors.append(1)

	if premios < 0:
		header_colors.append(0)
	else:
		header_colors.append(1)

	if saldo < 0:
		header_colors.append(0)
	else:
		header_colors.append(1)
	
	total_panel = {'pdvs':pdvs, 'tickets':tickets, 'ventas':'${:0,.2f}'.format(ventas), 'premios':'${:0,.2f}'.format(premios), 'saldo':'${:0,.2f}'.format(saldo)}
	queryset.append(total_panel) # obj.4, 'header_colors':header_colors

	result_dict = {'obj':queryset, 'header_colors':header_colors}
	if not general_report:
		return TemplateResponse(request, 'reportes.html', result_dict)
	else:
		return queryset

@login_required
def ajax_reportes(request, general_report=None):
	# get post data
	localidad = request.POST.get('localidad') # localidad
	nombre_pv = request.POST.get('nombre_pv') # nombre_pv
	user_id = request.POST.get('user_id')
	selecclonar = request.POST.get('selecclonar') # selecclonar (hoy, selecclone de)
	inicial = request.POST.get('inicial') # inicial date
	final = request.POST.get('final') # final date
	
	# response queryset as a list
	queryset = []

	# count and sum
	pdvs = 0
	tickets = 0
	ventas = 0 # sum of ventas from two tables (carton_keno & carton_cartas)
	ventas_list = [] # each ventas from two tables (carton_keno & carton_cartas)
	premios = 0 # sum of premios from two tables (carton_keno & carton_cartas)
	premios_list = [] # each premios from two tables (carton_keno & carton_cartas)
	saldo = 0
	percentage = 0

	current_user = request.user

	if current_user.is_staff and current_user.is_superuser == False:

		# get datas of puntoventa for all users.
		puntoventa_filter = PuntoVenta.objects.all()

		if localidad == "" and nombre_pv == "":
			# get all QuerySet

			# allset from CartonKeno
			filterd_set_keno = CartonKeno.objects.all().filter(fecha_keno__gte=inicial, fecha_keno__lte=final)
			# allset from CartonCartas
			filterd_set_cartas = CartonCartas.objects.all().filter(fecha_cartas__gte=inicial, fecha_cartas__lte=final)

			if user_id != "0":
				filterd_set_keno = filterd_set_keno.filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
				filterd_set_cartas = filterd_set_cartas.filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			# else:
			# 	filterd_set_keno = filterd_set_keno.filter(id_cajero__id_pos_pc__id_pv__user_id=current_user.id)
			# 	filterd_set_cartas = filterd_set_cartas.filter(id_cajero__id_pos_pc__id_pv__user_id=current_user.id)

			filterd_set_keno_aggregate = filterd_set_keno.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_k'), ventas=Sum('valor_apuesta_k'))
			
			filterd_set_cartas_aggregate = filterd_set_cartas.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__user_id__username').annotate(tickets=Count('id_c_c'), ventas=Sum('valor_apuesta_c'))
			
		else:   	 
			# filtered QuerySet
			# filterd_set from CartonKeno and CartonCartas
			filterd_set_keno = CartonKeno.objects.all().filter(fecha_keno__gte=inicial, fecha_keno__lte=final)
			filterd_set_cartas = CartonCartas.objects.all().filter(fecha_cartas__gte=inicial, fecha_cartas__lte=final)

			if user_id != "0":
				filterd_set_keno = filterd_set_keno.filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
				filterd_set_cartas = filterd_set_cartas.filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			# else:
			# 	filterd_set_keno = CartonKeno.objects.all().filter(fecha_keno__gte=inicial, fecha_keno__lte=final).filter(Q(id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_cajero__id_pos_pc__id_pv__user_id=current_user.id))
			# 	filterd_set_cartas = CartonCartas.objects.all().filter(fecha_cartas__gte=inicial, fecha_cartas__lte=final).filter(Q(id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_cajero__id_pos_pc__id_pv__user_id=current_user.id))

			if nombre_pv != "":	
				filterd_set_keno = filterd_set_keno.filter( id_cajero__id_pos_pc__id_pv__nombre_pv=nombre_pv )
				filterd_set_keno_aggregate = filterd_set_keno.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_k'), ventas=Sum('valor_apuesta_k'))
				
				filterd_set_cartas = filterd_set_cartas.filter( id_cajero__id_pos_pc__id_pv__nombre_pv=nombre_pv )
				filterd_set_cartas_aggregate = filterd_set_cartas.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_c'), ventas=Sum('valor_apuesta_c'))

			if localidad != "":
				filterd_set_keno = filterd_set_keno.filter( id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=localidad )
				filterd_set_keno_aggregate = filterd_set_keno.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_k'), ventas=Sum('valor_apuesta_k'))
				
				filterd_set_cartas = filterd_set_cartas.filter( id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=localidad )
				filterd_set_cartas_aggregate = filterd_set_cartas.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_c'), ventas=Sum('valor_apuesta_c'))
		
		# calculate the premois
		filterd_set_ganadoreskeno = GanadoresKeno.objects.all().filter(fecha_ganadores_k__gte=inicial, fecha_ganadores_k__lte=final)#.filter(Q(id_c_k__id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_c_k__id_cajero__id_pos_pc__id_pv__user_id=current_user.id))
		filterd_set_ganadorescartas = GanadoresCartas.objects.all().filter(fecha_ganadores_c__gte=inicial, fecha_ganadores_c__lte=final)#.filter(Q(id_c_c__id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_c_c__id_cajero__id_pos_pc__id_pv__user_id=current_user.id))

		if user_id != '0':
			
			# check if user_id is superuser
			user_info = User.objects.filter(id=user_id).values('is_staff')

			# if selected user is superuser
			if user_info[0]['is_staff'] == False:
				# get datas of puntoventa related on the logged user. (selected user)
				puntoventa_filter = PuntoVenta.objects.filter(user_id=user_id)
		
				# calculate the premios
				filterd_set_ganadoreskeno = GanadoresKeno.objects.all().filter(fecha_ganadores_k__gte=inicial, fecha_ganadores_k__lte=final).filter( id_c_k__id_cajero__id_pos_pc__id_pv__user_id=user_id )
				filterd_set_ganadorescartas = GanadoresCartas.objects.all().filter(fecha_ganadores_c__gte=inicial, fecha_ganadores_c__lte=final).filter( id_c_c__id_cajero__id_pos_pc__id_pv__user_id=user_id )
		
		# auth_user table (superuser + related users)
		#filterset_user = User.objects.filter(Q(groups__id=current_user.id) | Q(id=current_user.id)).values('id', 'username').annotate(dcount=Count('id'))
		filterset_user = User.objects.all().values('id', 'username').annotate(dcount=Count('id'))
	
	# logged user is a superuser but not staff
	elif current_user.is_superuser and current_user.is_staff == False:

		users = User.objects.filter(groups__id=current_user.id)
		user_ids = users.values('id')

		# get datas of puntoventa related on the logged user. (superuser + related users)
		puntoventa_filter = PuntoVenta.objects.filter(Q(user_id__in=user_ids) | Q(user_id=current_user.id))

		if localidad == "" and nombre_pv == "":
			# get all QuerySet

			# allset from CartonKeno
			filterd_set_keno = CartonKeno.objects.all().filter(fecha_keno__gte=inicial, fecha_keno__lte=final)
			# allset from CartonCartas
			filterd_set_cartas = CartonCartas.objects.all().filter(fecha_cartas__gte=inicial, fecha_cartas__lte=final)

			if user_id != "0":
				filterd_set_keno = filterd_set_keno.filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
				filterd_set_cartas = filterd_set_cartas.filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			else:
				filterd_set_keno = filterd_set_keno.filter(Q(id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_cajero__id_pos_pc__id_pv__user_id=current_user.id))
				filterd_set_cartas = filterd_set_cartas.filter(Q(id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_cajero__id_pos_pc__id_pv__user_id=current_user.id))

			filterd_set_keno_aggregate = filterd_set_keno.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_k'), ventas=Sum('valor_apuesta_k'))
			
			filterd_set_cartas_aggregate = filterd_set_cartas.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__user_id__username').annotate(tickets=Count('id_c_c'), ventas=Sum('valor_apuesta_c'))
			
		else:   	 
			# filtered QuerySet
			# filterd_set from CartonKeno
			if user_id != "0":
				filterd_set_keno = CartonKeno.objects.all().filter(fecha_keno__gte=inicial, fecha_keno__lte=final).filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
				filterd_set_cartas = CartonCartas.objects.all().filter(fecha_cartas__gte=inicial, fecha_cartas__lte=final).filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			else:
				filterd_set_keno = CartonKeno.objects.all().filter(fecha_keno__gte=inicial, fecha_keno__lte=final).filter(Q(id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_cajero__id_pos_pc__id_pv__user_id=current_user.id))
				filterd_set_cartas = CartonCartas.objects.all().filter(fecha_cartas__gte=inicial, fecha_cartas__lte=final).filter(Q(id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_cajero__id_pos_pc__id_pv__user_id=current_user.id))

			if nombre_pv != "":	
				filterd_set_keno = filterd_set_keno.filter( id_cajero__id_pos_pc__id_pv__nombre_pv=nombre_pv )
				filterd_set_keno_aggregate = filterd_set_keno.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_k'), ventas=Sum('valor_apuesta_k'))
				
				filterd_set_cartas = filterd_set_cartas.filter( id_cajero__id_pos_pc__id_pv__nombre_pv=nombre_pv )
				filterd_set_cartas_aggregate = filterd_set_cartas.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_c'), ventas=Sum('valor_apuesta_c'))

			if localidad != "":
				filterd_set_keno = filterd_set_keno.filter( id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=localidad )
				filterd_set_keno_aggregate = filterd_set_keno.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_k'), ventas=Sum('valor_apuesta_k'))
				
				filterd_set_cartas = filterd_set_cartas.filter( id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=localidad )
				filterd_set_cartas_aggregate = filterd_set_cartas.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_c'), ventas=Sum('valor_apuesta_c'))
		
		# calculate the premois
		filterd_set_ganadoreskeno = GanadoresKeno.objects.all().filter(fecha_ganadores_k__gte=inicial, fecha_ganadores_k__lte=final).filter(Q(id_c_k__id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_c_k__id_cajero__id_pos_pc__id_pv__user_id=current_user.id))
		filterd_set_ganadorescartas = GanadoresCartas.objects.all().filter(fecha_ganadores_c__gte=inicial, fecha_ganadores_c__lte=final).filter(Q(id_c_c__id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_c_c__id_cajero__id_pos_pc__id_pv__user_id=current_user.id))

		if user_id != '0':
			
			# check if user_id is superuser
			user_info = User.objects.filter(id=user_id).values('is_superuser')

			# if selected user is superuser
			if user_info[0]['is_superuser'] == False:
				# get datas of puntoventa related on the logged user. (selected user)
				puntoventa_filter = PuntoVenta.objects.filter(user_id=user_id)
		
				# calculate the premios
				filterd_set_ganadoreskeno = GanadoresKeno.objects.all().filter(fecha_ganadores_k__gte=inicial, fecha_ganadores_k__lte=final).filter( id_c_k__id_cajero__id_pos_pc__id_pv__user_id=user_id )
				filterd_set_ganadorescartas = GanadoresCartas.objects.all().filter(fecha_ganadores_c__gte=inicial, fecha_ganadores_c__lte=final).filter( id_c_c__id_cajero__id_pos_pc__id_pv__user_id=user_id )
		
		# auth_user table (superuser + related users)
		filterset_user = User.objects.filter(Q(groups__id=current_user.id) | Q(id=current_user.id)).values('id', 'username').annotate(dcount=Count('id'))

	# if the logged user is not a superuser and staff 
	elif current_user.is_superuser == False and current_user.is_staff == False:
		# get datas of puntoventa related on the logged user. (only logged user)
		puntoventa_filter = PuntoVenta.objects.filter(user_id=user_id)

		# auth_user table (only logged user)
		filterset_user = User.objects.filter(id=user_id).values('id', 'username').annotate(dcount=Count('id'))
	
		if localidad == "" and nombre_pv == "":
			# get all QuerySet

			# allset from CartonKeno
			filterd_set_keno = CartonKeno.objects.all().filter(fecha_keno__gte=inicial, fecha_keno__lte=final)
			# allset from CartonCartas
			filterd_set_cartas = CartonCartas.objects.all().filter(fecha_cartas__gte=inicial, fecha_cartas__lte=final)

			# if user_id != "0":
			filterd_set_keno = filterd_set_keno.filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			filterd_set_cartas = filterd_set_cartas.filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			# else:

			filterd_set_keno_aggregate = filterd_set_keno.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_k'), ventas=Sum('valor_apuesta_k'))
			
			filterd_set_cartas_aggregate = filterd_set_cartas.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__user_id__username').annotate(tickets=Count('id_c_c'), ventas=Sum('valor_apuesta_c'))
			
		else:   	 
			# filtered QuerySet
			# filterd_set from CartonKeno
			# if user_id != "0":
			filterd_set_keno = CartonKeno.objects.all().filter(fecha_keno__gte=inicial, fecha_keno__lte=final).filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			filterd_set_cartas = CartonCartas.objects.all().filter(fecha_cartas__gte=inicial, fecha_cartas__lte=final).filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			# else:
			# 	filterd_set_keno = CartonKeno.objects.all().filter(fecha_keno__gte=inicial, fecha_keno__lte=final)
			# 	filterd_set_cartas = CartonCartas.objects.all().filter(fecha_cartas__gte=inicial, fecha_cartas__lte=final)

			if nombre_pv != "":	
				filterd_set_keno = filterd_set_keno.filter( id_cajero__id_pos_pc__id_pv__nombre_pv=nombre_pv )
				filterd_set_keno_aggregate = filterd_set_keno.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_k'), ventas=Sum('valor_apuesta_k'))
				
				filterd_set_cartas = filterd_set_cartas.filter( id_cajero__id_pos_pc__id_pv__nombre_pv=nombre_pv )
				filterd_set_cartas_aggregate = filterd_set_cartas.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_c'), ventas=Sum('valor_apuesta_c'))

			if localidad != "":
				filterd_set_keno = filterd_set_keno.filter( id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=localidad )
				filterd_set_keno_aggregate = filterd_set_keno.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_k'), ventas=Sum('valor_apuesta_k'))
				
				filterd_set_cartas = filterd_set_cartas.filter( id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=localidad )
				filterd_set_cartas_aggregate = filterd_set_cartas.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_c'), ventas=Sum('valor_apuesta_c'))
		
		# calculate the premois
		if user_id != "0":
			filterd_set_ganadoreskeno = GanadoresKeno.objects.all().filter(fecha_ganadores_k__gte=inicial, fecha_ganadores_k__lte=final).filter( id_c_k__id_cajero__id_pos_pc__id_pv__user_id=user_id )
			filterd_set_ganadorescartas = GanadoresCartas.objects.all().filter(fecha_ganadores_c__gte=inicial, fecha_ganadores_c__lte=final).filter( id_c_c__id_cajero__id_pos_pc__id_pv__user_id=user_id )
		else:
			filterd_set_ganadoreskeno = GanadoresKeno.objects.all().filter(fecha_ganadores_k__gte=inicial, fecha_ganadores_k__lte=final)
			filterd_set_ganadorescartas = GanadoresCartas.objects.all().filter(fecha_ganadores_c__gte=inicial, fecha_ganadores_c__lte=final)

		
	# add ventas from two queryset list (CartonKeno + CartonCartas)
	table_data = set_table_data(filterd_set_keno_aggregate, filterd_set_cartas_aggregate, current_user.is_staff, user_id, inicial, final)
		
	# append filtered set for datatable
	queryset.append(table_data) # obj.0

	# get pdvs
	pdvs = len(table_data)

	# calculate tickets
	# Count( CartonKeno.id_c_k) + Count( CartonCartas.id_c_c)
	tickets = filterd_set_keno.count() + filterd_set_cartas.count()

	# calculate the ventas
	# SUM( CartonKeno.valor_apuesta_k + CartonCartas.valor_apuesta_c )
	vantas_cartonkeno = filterd_set_keno.aggregate(Sum('valor_apuesta_k'))['valor_apuesta_k__sum']
	
	vantas_cartoncarts = filterd_set_cartas.aggregate(Sum('valor_apuesta_c'))['valor_apuesta_c__sum']
	
	
	if vantas_cartonkeno is not None: 
		ventas += vantas_cartonkeno
	
	if vantas_cartoncarts is not None: 
		ventas += vantas_cartoncarts

	if nombre_pv != "":
		filterd_set_ganadoreskeno = filterd_set_ganadoreskeno.filter( id_c_k__id_cajero__id_pos_pc__id_pv__nombre_pv=nombre_pv )
		filterd_set_ganadorescartas = filterd_set_ganadorescartas.filter( id_c_c__id_cajero__id_pos_pc__id_pv__nombre_pv=nombre_pv )
	if localidad != "":
		filterd_set_ganadoreskeno = filterd_set_ganadoreskeno.filter( id_c_k__id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=localidad )
		filterd_set_ganadorescartas = filterd_set_ganadorescartas.filter( id_c_c__id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=localidad )
		

	premios_ganadoreskeno = filterd_set_ganadoreskeno.aggregate(Sum('valor_ganado_k'))['valor_ganado_k__sum']


	if premios_ganadoreskeno is not None: 
		premios += premios_ganadoreskeno
	
	premios_ganadorescartas = filterd_set_ganadorescartas.aggregate(Sum('valor_ganado_c'))['valor_ganado_c__sum']
	
	if premios_ganadorescartas is not None: 
		premios += premios_ganadorescartas

	# calculate the saldo
	# SUM( GanadoresKeno.valor_ganado_k + GanadoresCartas.valor_ganado_c ) - SUM( CartonKeno.valor_apuesta_k + CartonCartas.valor_apuesta_c )
	saldo = ventas - premios

	# calculate the percentage
	# SUM( GanadoresKeno.valor_ganado_k + GanadoresCartas.valor_ganado_c ) * 100 / SUM( CartonKeno.valor_apuesta_k + CartonCartas.valor_apuesta_c )
	if ventas != 0:
		percentage = premios * 100 / ventas 

	
	# model:Localidad
	# filterset_localidad = Localidad.objects.values('nombre_localidad').annotate(dcount=Count('nombre_localidad'))
	localidads = puntoventa_filter.values('id_localidad')
	filterset_localidad = Localidad.objects.filter(id_localidad__in=localidads).values('nombre_localidad').annotate(dcount=Count('nombre_localidad'))	
	queryset.append(filterset_localidad) # obj.1

	# model:PuntoVenta
	# filterset_pdv = PuntoVenta.objects.values('nombre_pv').annotate(dcount=Count('nombre_pv'))
	filterset_pdv = puntoventa_filter.values('nombre_pv').annotate(dcount=Count('nombre_pv'))	
	queryset.append(filterset_pdv) # obj.2

	queryset.append(filterset_user) #obj.3

	header_colors = []
	if ventas < 0:
		header_colors.append(0)
	else:
		header_colors.append(1)

	if premios < 0:
		header_colors.append(0)
	else:
		header_colors.append(1)

	if saldo < 0:
		header_colors.append(0)
	else:
		header_colors.append(1)
	# return Response
	# obj : queryset
	# localidad : localidad
	# nombre_pv : nombre_pv
	# selecclonar : selecclonar
	# inicial : inicial
	# final : final
	# tickets : tickets
	# ventas : ventas
	# premios : premios
	# saldo : saldo
	# percentage : percentage		
	# pdvs : pdvs
	# user_id : user_id
	# header_colors: header_colors
	result_dict = {'obj':queryset, 'localidad':localidad, 'nombre_pv':nombre_pv, 'selecclonar':selecclonar, 'inicial':inicial, 'final':final, 'tickets':tickets, 'ventas':'${:0,.2f}'.format(ventas), 'premios':'${:0,.2f}'.format(premios), 'saldo':'${:0,.2f}'.format(saldo), 'percentage':'%{:0,.2f}'.format(percentage), 'pdvs':pdvs, 'user_id':int(user_id), 'header_colors':header_colors}
	if not general_report:
		return TemplateResponse(request, 'reportes.html', result_dict)
	else:
		return result_dict

def set_table_bingo(allset_apuesta_bingo_aggregate, is_staff=False, user_id = '0', inicial = '', final=''):
	

	table_data_bingo = []

	for i in range(len(allset_apuesta_bingo_aggregate)):

		line_bingo = allset_apuesta_bingo_aggregate[i]

		bingo_username = line_bingo['id_cajero__id_pos_pc__id_pv__user_id__username']
		bingo_localidad = line_bingo['id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad']
		bingo_pdv = line_bingo['id_cajero__id_pos_pc__id_pv__nombre_pv']


		# calculate premios
		if user_id != '0':
			filterd_set_ganadoresbingo = GanadoresBingo.objects.all().filter( id_apuesta_b__id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=line_bingo['id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad'] ).filter( id_apuesta_b__id_cajero__id_pos_pc__id_pv__nombre_pv=line_bingo['id_cajero__id_pos_pc__id_pv__nombre_pv'] ).filter( id_apuesta_b__id_cajero__id_pos_pc__id_pv__user_id = user_id )
		else:
			filterd_set_ganadoresbingo = GanadoresBingo.objects.all().filter( id_apuesta_b__id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=line_bingo['id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad'] ).filter( id_apuesta_b__id_cajero__id_pos_pc__id_pv__nombre_pv=line_bingo['id_cajero__id_pos_pc__id_pv__nombre_pv'] )
			
		if inicial != '' and final != '':
			filterd_set_ganadoresbingo = filterd_set_ganadoresbingo.filter(fecha_ganadores_b__gte=inicial, fecha_ganadores_b__lte=final)
			
		premios_ganadoresbingo = filterd_set_ganadoresbingo.aggregate(valor_ganado_b__sum=Coalesce(Sum('valor_ganado_b'),0))['valor_ganado_b__sum']
		
		sum_bingo = line_bingo
		
		sum_bingo['premios'] = premios_ganadoresbingo

		# calculate saldo
		sum_bingo['saldo'] = sum_bingo['ventas'] - sum_bingo['premios']

		# calculate percentage
		if sum_bingo['ventas'] != 0:
			sum_bingo['percentage'] = round(sum_bingo['premios'] * 100 / sum_bingo['ventas'], 2)
		else:
			sum_bingo['percentage'] = 0

		sum_bingo['percentage'] = '%{:0,.2f}'.format(sum_bingo['percentage'])

		table_data_bingo.append(sum_bingo)

		
	return table_data_bingo


@login_required
def reportes_bingo(request, general_report=None):
	
	# model:ApuestaBingo
	template_name=	'reportes_bingo.html'
	context_object_name='obj'
	queryset = []

	current_user = request.user

	if current_user.is_staff:
		allset_apuesta_bingo = ApuestaBingo.objects.all()
		
		#get data for all puntoventa
		puntoventa_filter = PuntoVenta.objects.all()

		# auth_user table (only logged user)
		filterset_user = User.objects.all().values('id', 'username').annotate(dcount=Count('id'))


	elif current_user.is_superuser and current_user.is_staff == False:
		users = User.objects.filter(groups__id=current_user.id)
		user_ids = users.values('id')

		allset_apuesta_bingo = ApuestaBingo.objects.all()
		
		# for user_id in user_ids: (superuser + related users)
		allset_apuesta_bingo = allset_apuesta_bingo.filter(Q(id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_cajero__id_pos_pc__id_pv__user_id=current_user.id))

		# get datas of puntoventa related on the logged user. (superuser + related users)
		puntoventa_filter = PuntoVenta.objects.filter(Q(user_id__in=user_ids) | Q(user_id=current_user.id))

		# auth_user table (superuser + related users)
		filterset_user = User.objects.filter(Q(groups__id=current_user.id) | Q(id=current_user.id)).values('id', 'username').annotate(dcount=Count('id'))
		
	elif current_user.is_superuser == False and current_user.is_staff == False:
		# (only logged user)
		allset_apuesta_bingo = ApuestaBingo.objects.filter(id_cajero__id_pos_pc__id_pv__user_id=current_user.id)

		# get datas of puntoventa related on the logged user. (only logged user)
		puntoventa_filter = PuntoVenta.objects.filter(user_id=current_user.id)

		# auth_user table (only logged user)
		filterset_user = User.objects.filter(id=current_user.id).values('id', 'username').annotate(dcount=Count('id'))
		

	allset_apuesta_bingo_aggregate = allset_apuesta_bingo.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_b'), ventas=Sum('valor_apuesta_b'))
	
	
	# add ventas from queryset list
	table_data_bingo = set_table_bingo(allset_apuesta_bingo_aggregate, current_user.is_staff)

	queryset.append(table_data_bingo) # obj.0


	localidads = puntoventa_filter.values('id_localidad')
	filterset_localidad = Localidad.objects.filter(id_localidad__in=localidads).values('nombre_localidad').annotate(dcount=Count('nombre_localidad'))	
	queryset.append(filterset_localidad) # obj.1

	filterset_pdv = puntoventa_filter.values('nombre_pv').annotate(dcount=Count('nombre_pv'))	
	queryset.append(filterset_pdv) # obj.2


	pdvs = len(table_data_bingo)
	tickets = 0
	ventas = 0
	premios = 0
	saldo = 0
	for item in table_data_bingo:
		tickets += item['tickets']
		ventas += item['ventas']
		premios += item['premios']
		saldo += item['saldo']

	
	queryset.append(filterset_user) # obj.3

	header_colors = []
	if ventas < 0:
		header_colors.append(0)
	else:
		header_colors.append(1)

	if premios < 0:
		header_colors.append(0)
	else:
		header_colors.append(1)

	if saldo < 0:
		header_colors.append(0)
	else:
		header_colors.append(1)
	
	total_panel = {'pdvs':pdvs, 'tickets':tickets, 'ventas':'${:0,.2f}'.format(ventas), 'premios':'${:0,.2f}'.format(premios), 'saldo':'${:0,.2f}'.format(saldo)}
	queryset.append(total_panel) # obj.4, 'header_colors':header_colors

	result_dict = {'obj':queryset, 'header_colors':header_colors}
	if not general_report:
		return TemplateResponse(request, 'reportes_bingo.html', result_dict)
	else:
		return queryset

@login_required
def ajax_reportes_bingo(request, general_report=None):
	# get post data
	localidad = request.POST.get('localidad') # localidad
	nombre_pv = request.POST.get('nombre_pv') # nombre_pv
	user_id = request.POST.get('user_id')
	selecclonar = request.POST.get('selecclonar') # selecclonar (hoy, selecclone de)
	inicial = request.POST.get('inicial') # inicial date
	final = request.POST.get('final') # final date
	
	# response queryset as a list
	queryset = []

	# count and sum
	pdvs = 0
	tickets = 0
	ventas = 0 # sum of ventas from two tables (carton_keno & carton_cartas)
	ventas_list = [] # each ventas from two tables (carton_keno & carton_cartas)
	premios = 0 # sum of premios from two tables (carton_keno & carton_cartas)
	premios_list = [] # each premios from two tables (carton_keno & carton_cartas)
	saldo = 0
	percentage = 0

	current_user = request.user

	if current_user.is_staff and current_user.is_superuser == False:

		# get datas of puntoventa for all users.
		puntoventa_filter = PuntoVenta.objects.all()

		if localidad == "" and nombre_pv == "":
			# get all QuerySet

			# allset from CartonBingo
			filterd_set_bingo = ApuestaBingo.objects.all().filter(fecha_apuesta_b__gte=inicial, fecha_apuesta_b__lte=final)
			
			if user_id != "0":
				filterd_set_bingo = filterd_set_bingo.filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
				
			
			filterd_set_bingo_aggregate = filterd_set_bingo.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_b'), ventas=Sum('valor_apuesta_b'))
			
			
		else:   	 
			# filtered QuerySet
			filterd_set_bingo = ApuestaBingo.objects.all().filter(fecha_apuesta_b__gte=inicial, fecha_apuesta_b__lte=final)
			
			if user_id != "0":
				filterd_set_bingo = filterd_set_bingo.filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			
			if nombre_pv != "":	
				filterd_set_bingo = filterd_set_bingo.filter( id_cajero__id_pos_pc__id_pv__nombre_pv=nombre_pv )
				filterd_set_bingo_aggregate = filterd_set_bingo.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_b'), ventas=Sum('valor_apuesta_b'))
				
			if localidad != "":
				filterd_set_bingo = filterd_set_bingo.filter( id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=localidad )
				filterd_set_bingo_aggregate = filterd_set_bingo.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_b'), ventas=Sum('valor_apuesta_b'))
				
				
		# calculate the premois
		filterd_set_ganadoresbingo = GanadoresBingo.objects.all().filter(fecha_ganadores_b__gte=inicial, fecha_ganadores_b__lte=final)#.filter(Q(id_apuesta_b__id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_apuesta_b__id_cajero__id_pos_pc__id_pv__user_id=current_user.id))
		
		if user_id != '0':
			
			# check if user_id is superuser
			user_info = User.objects.filter(id=user_id).values('is_staff')

			# if selected user is superuser
			if user_info[0]['is_staff'] == False:
				# get datas of puntoventa related on the logged user. (selected user)
				puntoventa_filter = PuntoVenta.objects.filter(user_id=user_id)
		
				# calculate the premios
				filterd_set_ganadoresbingo = GanadoresBingo.objects.all().filter(fecha_ganadores_b__gte=inicial, fecha_ganadores_b__lte=final).filter( id_apuesta_b__id_cajero__id_pos_pc__id_pv__user_id=user_id )
				
		# auth_user table (superuser + related users)
		filterset_user = User.objects.all().values('id', 'username').annotate(dcount=Count('id'))
	
	# logged user is a superuser but not staff
	elif current_user.is_superuser and current_user.is_staff == False:

		users = User.objects.filter(groups__id=current_user.id)
		user_ids = users.values('id')

		# get datas of puntoventa related on the logged user. (superuser + related users)
		puntoventa_filter = PuntoVenta.objects.filter(Q(user_id__in=user_ids) | Q(user_id=current_user.id))

		if localidad == "" and nombre_pv == "":
			# get all QuerySet

			# allset from ApuestaBingo
			filterd_set_bingo = ApuestaBingo.objects.all().filter(fecha_apuesta_b__gte=inicial, fecha_apuesta_b__lte=final)
			
			if user_id != "0":
				filterd_set_bingo = filterd_set_bingo.filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			else:
				filterd_set_bingo = filterd_set_bingo.filter(Q(id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_cajero__id_pos_pc__id_pv__user_id=current_user.id))
			
			filterd_set_bingo_aggregate = filterd_set_bingo.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_b'), ventas=Sum('valor_apuesta_b'))
			
		else:   	 
			# filtered QuerySet
			# filterd_set from ApuestaBingo
			if user_id != "0":
				filterd_set_bingo = ApuestaBingo.objects.all().filter(fecha_apuesta_b__gte=inicial, fecha_apuesta_b__lte=final).filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			else:
				filterd_set_bingo = ApuestaBingo.objects.all().filter(fecha_apuesta_b__gte=inicial, fecha_apuesta_b__lte=final).filter(Q(id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_cajero__id_pos_pc__id_pv__user_id=current_user.id))
				
			if nombre_pv != "":	
				filterd_set_bingo = filterd_set_bingo.filter( id_cajero__id_pos_pc__id_pv__nombre_pv=nombre_pv )
				filterd_set_bingo_aggregate = filterd_set_bingo.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_b'), ventas=Sum('valor_apuesta_b'))
				
				
			if localidad != "":
				filterd_set_bingo = filterd_set_bingo.filter( id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=localidad )
				filterd_set_bingo_aggregate = filterd_set_bingo.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_b'), ventas=Sum('valor_apuesta_b'))
				
				
		# calculate the premois
		filterd_set_ganadoresbingo = GanadoresBingo.objects.all().filter(fecha_ganadores_b__gte=inicial, fecha_ganadores_b__lte=final).filter(Q(id_apuesta_b__id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_apuesta_b__id_cajero__id_pos_pc__id_pv__user_id=current_user.id))
		
		if user_id != '0':
			
			# check if user_id is superuser
			user_info = User.objects.filter(id=user_id).values('is_superuser')

			# if selected user is superuser
			if user_info[0]['is_superuser'] == False:
				# get datas of puntoventa related on the logged user. (selected user)
				puntoventa_filter = PuntoVenta.objects.filter(user_id=user_id)
		
				# calculate the premios
				filterd_set_ganadoresbingo = GanadoresBingo.objects.all().filter(fecha_ganadores_b__gte=inicial, fecha_ganadores_b__lte=final).filter( id_apuesta_b__id_cajero__id_pos_pc__id_pv__user_id=user_id )
				
		# auth_user table (superuser + related users)
		filterset_user = User.objects.filter(Q(groups__id=current_user.id) | Q(id=current_user.id)).values('id', 'username').annotate(dcount=Count('id'))

	# if the logged user is not a superuser and staff 
	elif current_user.is_superuser == False and current_user.is_staff == False:
		# get datas of puntoventa related on the logged user. (only logged user)
		puntoventa_filter = PuntoVenta.objects.filter(user_id=user_id)

		# auth_user table (only logged user)
		filterset_user = User.objects.filter(id=user_id).values('id', 'username').annotate(dcount=Count('id'))
	
		if localidad == "" and nombre_pv == "":
			# get all QuerySet

			# allset from ApuestaBingo
			filterd_set_bingo = ApuestaBingo.objects.all().filter(fecha_apuesta_b__gte=inicial, fecha_apuesta_b__lte=final)
			
			# if user_id != "0":
			filterd_set_bingo = filterd_set_bingo.filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			
			filterd_set_bingo_aggregate = filterd_set_bingo.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_b'), ventas=Sum('valor_apuesta_b'))
			
			
		else:   	 
			# filtered QuerySet
			# filterd_set from ApuestaBingo
			# if user_id != "0":
			filterd_set_bingo = ApuestaBingo.objects.all().filter(fecha_apuesta_b__gte=inicial, fecha_apuesta_b__lte=final).filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			
			if nombre_pv != "":	
				filterd_set_bingo = filterd_set_bingo.filter( id_cajero__id_pos_pc__id_pv__nombre_pv=nombre_pv )
				filterd_set_bingo_aggregate = filterd_set_bingo.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_b'), ventas=Sum('valor_apuesta_b'))
				
			
			if localidad != "":
				filterd_set_bingo = filterd_set_bingo.filter( id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=localidad )
				filterd_set_bingo_aggregate = filterd_set_bingo.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_b'), ventas=Sum('valor_apuesta_b'))
				
			
		# calculate the premois
		if user_id != "0":
			filterd_set_ganadoresbingo = GanadoresBingo.objects.all().filter(fecha_ganadores_b__gte=inicial, fecha_ganadores_b__lte=final).filter( id_apuesta_b__id_cajero__id_pos_pc__id_pv__user_id=user_id )
			
		else:
			filterd_set_ganadoresbingo = GanadoresBingo.objects.all().filter(fecha_ganadores_b__gte=inicial, fecha_ganadores_b__lte=final)
		
		
	# add ventas from queryset list (ApuestaBingo)
	table_data_bingo = set_table_bingo(filterd_set_bingo_aggregate, current_user.is_staff, user_id, inicial, final)
		
	# append filtered set for datatable
	queryset.append(table_data_bingo) # obj.0

	# get pdvs
	pdvs = len(table_data_bingo)

	# calculate tickets
	# Count( ApuestaBingo.id_apuesta_b)
	tickets = filterd_set_bingo.count()

	# calculate the ventas
	# SUM( ApuestaBingo.valor_apuesta_b )
	vantas_ApuestaBingo = filterd_set_bingo.aggregate(Sum('valor_apuesta_b'))['valor_apuesta_b__sum']
	
	if vantas_ApuestaBingo is not None: 
		ventas += vantas_ApuestaBingo
	

	if nombre_pv != "":
		filterd_set_ganadoresbingo = filterd_set_ganadoresbingo.filter( id_apuesta_b__id_cajero__id_pos_pc__id_pv__nombre_pv=nombre_pv )
		
	if localidad != "":
		filterd_set_ganadoresbingo = filterd_set_ganadoresbingo.filter( id_apuesta_b__id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=localidad )
				
	premios_ganadoresbingo = filterd_set_ganadoresbingo.aggregate(Sum('valor_ganado_b'))['valor_ganado_b__sum']


	if premios_ganadoresbingo is not None: 
		premios += premios_ganadoresbingo
	
	
	# calculate the saldo
	# SUM( GanadoresBingo.valor_ganado_b ) - SUM( ApuestaBingo.valor_apuesta_b )
	saldo = ventas - premios

	# calculate the percentage
	# SUM( GanadoresBingo.valor_ganado_b ) * 100 / SUM( ApuestaBingo.valor_apuesta_b )
	if ventas != 0:
		percentage = premios * 100 / ventas 

	
	# model:Localidad
	localidads = puntoventa_filter.values('id_localidad')
	filterset_localidad = Localidad.objects.filter(id_localidad__in=localidads).values('nombre_localidad').annotate(dcount=Count('nombre_localidad'))	
	queryset.append(filterset_localidad) # obj.1

	# model:PuntoVenta
	filterset_pdv = puntoventa_filter.values('nombre_pv').annotate(dcount=Count('nombre_pv'))	
	queryset.append(filterset_pdv) # obj.2

	queryset.append(filterset_user) #obj.3

	header_colors = []
	if ventas < 0:
		header_colors.append(0)
	else:
		header_colors.append(1)

	if premios < 0:
		header_colors.append(0)
	else:
		header_colors.append(1)

	if saldo < 0:
		header_colors.append(0)
	else:
		header_colors.append(1)
	# return Response
	# obj : queryset
	# localidad : localidad
	# nombre_pv : nombre_pv
	# selecclonar : selecclonar
	# inicial : inicial
	# final : final
	# tickets : tickets
	# ventas : ventas
	# premios : premios
	# saldo : saldo
	# percentage : percentage		
	# pdvs : pdvs
	# user_id : user_id
	# header_colors: header_colors
	result_dict = {'obj':queryset, 'localidad':localidad, 'nombre_pv':nombre_pv, 'selecclonar':selecclonar, 'inicial':inicial, 'final':final, 'tickets':tickets, 'ventas':'${:0,.2f}'.format(ventas), 'premios':'${:0,.2f}'.format(premios), 'saldo':'${:0,.2f}'.format(saldo), 'percentage':'%{:0,.2f}'.format(percentage), 'pdvs':pdvs, 'user_id':int(user_id), 'header_colors':header_colors}
	if not general_report:
		return TemplateResponse(request, 'reportes_general.html', result_dict)
	else:
		return result_dict


def set_table_caballos(allset_apuesta_caballos_aggregate, is_staff=False, user_id = '0', inicial = '', final=''):
	

	table_data_caballos = []

	for i in range(len(allset_apuesta_caballos_aggregate)):

		line_caballos = allset_apuesta_caballos_aggregate[i]

		caballos_username = line_caballos['id_cajero__id_pos_pc__id_pv__user_id__username']
		caballos_localidad = line_caballos['id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad']
		caballos_pdv = line_caballos['id_cajero__id_pos_pc__id_pv__nombre_pv']


		# calculate premios
		if user_id != '0':
			filterd_set_ganadorescab = GanadoresCaballos.objects.all().filter( id_apuesta_cab__id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=line_caballos['id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad'] ).filter( id_apuesta_cab__id_cajero__id_pos_pc__id_pv__nombre_pv=line_caballos['id_cajero__id_pos_pc__id_pv__nombre_pv'] ).filter( id_apuesta_cab__id_cajero__id_pos_pc__id_pv__user_id = user_id )
		else:
			filterd_set_ganadorescab = GanadoresCaballos.objects.all().filter( id_apuesta_cab__id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=line_caballos['id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad'] ).filter( id_apuesta_cab__id_cajero__id_pos_pc__id_pv__nombre_pv=line_caballos['id_cajero__id_pos_pc__id_pv__nombre_pv'] )
			
		if inicial != '' and final != '':
			filterd_set_ganadorescab = filterd_set_ganadorescab.filter(fecha_ganado_cab__gte=inicial, fecha_ganado_cab__lte=final)
			
		premios_ganadorescab = filterd_set_ganadorescab.aggregate(valor_ganado_cab__sum=Coalesce(Sum('valor_ganado_cab'),0))['valor_ganado_cab__sum']
		
		sum_caballos = line_caballos
		
		sum_caballos['premios'] = premios_ganadorescab

		# calculate saldo
		sum_caballos['saldo'] = sum_caballos['ventas'] - sum_caballos['premios']

		# calculate percentage
		if sum_caballos['ventas'] != 0:
			sum_caballos['percentage'] = round(sum_caballos['premios'] * 100 / sum_caballos['ventas'], 2)
		else:
			sum_caballos['percentage'] = 0

		sum_caballos['percentage'] = '%{:0,.2f}'.format(sum_caballos['percentage'])

		table_data_caballos.append(sum_caballos)

		
	return table_data_caballos


@login_required
def reportes_caballos(request, general_report=None):
	
	# model:ApuestaCaballos
	template_name=	'reportes_caballos.html'
	context_object_name='obj'
	queryset = []

	current_user = request.user

	if current_user.is_staff:
		allset_apuesta_cab = ApuestaCaballos.objects.all()
		
		#get data for all puntoventa
		puntoventa_filter = PuntoVenta.objects.all()

		# auth_user table (only logged user)
		filterset_user = User.objects.all().values('id', 'username').annotate(dcount=Count('id'))


	elif current_user.is_superuser and current_user.is_staff == False:
		users = User.objects.filter(groups__id=current_user.id)
		user_ids = users.values('id')

		allset_apuesta_cab = ApuestaCaballos.objects.all()
		
		# for user_id in user_ids: (superuser + related users)
		allset_apuesta_cab = allset_apuesta_cab.filter(Q(id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_cajero__id_pos_pc__id_pv__user_id=current_user.id))

		# get datas of puntoventa related on the logged user. (superuser + related users)
		puntoventa_filter = PuntoVenta.objects.filter(Q(user_id__in=user_ids) | Q(user_id=current_user.id))

		# auth_user table (superuser + related users)
		filterset_user = User.objects.filter(Q(groups__id=current_user.id) | Q(id=current_user.id)).values('id', 'username').annotate(dcount=Count('id'))
		
	elif current_user.is_superuser == False and current_user.is_staff == False:
		# (only logged user)
		allset_apuesta_cab = ApuestaCaballos.objects.filter(id_cajero__id_pos_pc__id_pv__user_id=current_user.id)

		# get datas of puntoventa related on the logged user. (only logged user)
		puntoventa_filter = PuntoVenta.objects.filter(user_id=current_user.id)

		# auth_user table (only logged user)
		filterset_user = User.objects.filter(id=current_user.id).values('id', 'username').annotate(dcount=Count('id'))
		

	allset_apuesta_caballos_aggregate = allset_apuesta_cab.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_cab'), ventas=Sum('valor_apuesta_cab'))
	
	
	# add ventas from queryset list
	table_data_caballos = set_table_caballos(allset_apuesta_caballos_aggregate, current_user.is_staff)

	queryset.append(table_data_caballos) # obj.0


	localidads = puntoventa_filter.values('id_localidad')
	filterset_localidad = Localidad.objects.filter(id_localidad__in=localidads).values('nombre_localidad').annotate(dcount=Count('nombre_localidad'))	
	queryset.append(filterset_localidad) # obj.1

	filterset_pdv = puntoventa_filter.values('nombre_pv').annotate(dcount=Count('nombre_pv'))	
	queryset.append(filterset_pdv) # obj.2


	pdvs = len(table_data_caballos)
	tickets = 0
	ventas = 0
	premios = 0
	saldo = 0
	for item in table_data_caballos:
		tickets += item['tickets']
		ventas += item['ventas']
		premios += item['premios']
		saldo += item['saldo']

	
	queryset.append(filterset_user) # obj.3

	header_colors = []
	if ventas < 0:
		header_colors.append(0)
	else:
		header_colors.append(1)

	if premios < 0:
		header_colors.append(0)
	else:
		header_colors.append(1)

	if saldo < 0:
		header_colors.append(0)
	else:
		header_colors.append(1)
	
	total_panel = {'pdvs':pdvs, 'tickets':tickets, 'ventas':'${:0,.2f}'.format(ventas), 'premios':'${:0,.2f}'.format(premios), 'saldo':'${:0,.2f}'.format(saldo)}
	queryset.append(total_panel) # obj.4, 'header_colors':header_colors

	result_dict = {'obj':queryset, 'header_colors':header_colors}
	if not general_report:
		return TemplateResponse(request, 'reportes_caballos.html', result_dict)
	else:
		return queryset

@login_required
def ajax_reportes_caballos(request, general_report=None):
	# get post data
	localidad = request.POST.get('localidad') # localidad
	nombre_pv = request.POST.get('nombre_pv') # nombre_pv
	user_id = request.POST.get('user_id')
	selecclonar = request.POST.get('selecclonar') # selecclonar (hoy, selecclone de)
	inicial = request.POST.get('inicial') # inicial date
	final = request.POST.get('final') # final date
	
	# response queryset as a list
	queryset = []

	# count and sum
	pdvs = 0
	tickets = 0
	ventas = 0 # sum of ventas from two tables (carton_keno & carton_cartas)
	ventas_list = [] # each ventas from two tables (carton_keno & carton_cartas)
	premios = 0 # sum of premios from two tables (carton_keno & carton_cartas)
	premios_list = [] # each premios from two tables (carton_keno & carton_cartas)
	saldo = 0
	percentage = 0

	current_user = request.user

	if current_user.is_staff and current_user.is_superuser == False:

		# get datas of puntoventa for all users.
		puntoventa_filter = PuntoVenta.objects.all()

		if localidad == "" and nombre_pv == "":
			# get all QuerySet

			# allset from CartonBingo
			filterd_set_cab = ApuestaCaballos.objects.all().filter(fecha_apuesta_cab__gte=inicial, fecha_apuesta_cab__lte=final)
			
			if user_id != "0":
				filterd_set_cab = filterd_set_cab.filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
				
			
			filterd_set_cab_aggregate = filterd_set_cab.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_cab'), ventas=Sum('valor_apuesta_cab'))
			
			
		else:   	 
			# filtered QuerySet
			filterd_set_cab = ApuestaCaballos.objects.all().filter(fecha_apuesta_cab__gte=inicial, fecha_apuesta_cab__lte=final)
			
			if user_id != "0":
				filterd_set_cab = filterd_set_cab.filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			
			if nombre_pv != "":	
				filterd_set_cab = filterd_set_cab.filter( id_cajero__id_pos_pc__id_pv__nombre_pv=nombre_pv )
				filterd_set_cab_aggregate = filterd_set_cab.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_cab'), ventas=Sum('valor_apuesta_cab'))
				
			if localidad != "":
				filterd_set_cab = filterd_set_cab.filter( id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=localidad )
				filterd_set_cab_aggregate = filterd_set_cab.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_cab'), ventas=Sum('valor_apuesta_cab'))
				
				
		# calculate the premois
		filterd_set_ganadorescab = GanadoresCaballos.objects.all().filter(fecha_ganado_cab__gte=inicial, fecha_ganado_cab__lte=final)#.filter(Q(id_apuesta_cab__id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_apuesta_cab__id_cajero__id_pos_pc__id_pv__user_id=current_user.id))
		
		if user_id != '0':
			
			# check if user_id is superuser
			user_info = User.objects.filter(id=user_id).values('is_staff')

			# if selected user is superuser
			if user_info[0]['is_staff'] == False:
				# get datas of puntoventa related on the logged user. (selected user)
				puntoventa_filter = PuntoVenta.objects.filter(user_id=user_id)
		
				# calculate the premios
				filterd_set_ganadorescab = GanadoresCaballos.objects.all().filter(fecha_ganado_cab__gte=inicial, fecha_ganado_cab__lte=final).filter( id_apuesta_cab__id_cajero__id_pos_pc__id_pv__user_id=user_id )
				
		# auth_user table (superuser + related users)
		filterset_user = User.objects.all().values('id', 'username').annotate(dcount=Count('id'))
	
	# logged user is a superuser but not staff
	elif current_user.is_superuser and current_user.is_staff == False:

		users = User.objects.filter(groups__id=current_user.id)
		user_ids = users.values('id')

		# get datas of puntoventa related on the logged user. (superuser + related users)
		puntoventa_filter = PuntoVenta.objects.filter(Q(user_id__in=user_ids) | Q(user_id=current_user.id))

		if localidad == "" and nombre_pv == "":
			# get all QuerySet

			# allset from ApuestaCaballos
			filterd_set_cab = ApuestaCaballos.objects.all().filter(fecha_apuesta_cab__gte=inicial, fecha_apuesta_cab__lte=final)
			
			if user_id != "0":
				filterd_set_cab = filterd_set_cab.filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			else:
				filterd_set_cab = filterd_set_cab.filter(Q(id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_cajero__id_pos_pc__id_pv__user_id=current_user.id))
			
			filterd_set_cab_aggregate = filterd_set_cab.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_cab'), ventas=Sum('valor_apuesta_cab'))
			
		else:   	 
			# filtered QuerySet
			# filterd_set from ApuestaCaballos
			if user_id != "0":
				filterd_set_cab = ApuestaCaballos.objects.all().filter(fecha_apuesta_cab__gte=inicial, fecha_apuesta_cab__lte=final).filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			else:
				filterd_set_cab = ApuestaCaballos.objects.all().filter(fecha_apuesta_cab__gte=inicial, fecha_apuesta_cab__lte=final).filter(Q(id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_cajero__id_pos_pc__id_pv__user_id=current_user.id))
				
			if nombre_pv != "":	
				filterd_set_cab = filterd_set_cab.filter( id_cajero__id_pos_pc__id_pv__nombre_pv=nombre_pv )
				filterd_set_cab_aggregate = filterd_set_cab.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_cab'), ventas=Sum('valor_apuesta_cab'))
				
				
			if localidad != "":
				filterd_set_cab = filterd_set_cab.filter( id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=localidad )
				filterd_set_cab_aggregate = filterd_set_cab.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_cab'), ventas=Sum('valor_apuesta_cab'))
				
				
		# calculate the premois
		filterd_set_ganadorescab = GanadoresCaballos.objects.all().filter(fecha_ganado_cab__gte=inicial, fecha_ganado_cab__lte=final).filter(Q(id_apuesta_cab__id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_apuesta_cab__id_cajero__id_pos_pc__id_pv__user_id=current_user.id))
		
		if user_id != '0':
			
			# check if user_id is superuser
			user_info = User.objects.filter(id=user_id).values('is_superuser')

			# if selected user is superuser
			if user_info[0]['is_superuser'] == False:
				# get datas of puntoventa related on the logged user. (selected user)
				puntoventa_filter = PuntoVenta.objects.filter(user_id=user_id)
		
				# calculate the premios
				filterd_set_ganadorescab = GanadoresCaballos.objects.all().filter(fecha_ganado_cab__gte=inicial, fecha_ganado_cab__lte=final).filter( id_apuesta_cab__id_cajero__id_pos_pc__id_pv__user_id=user_id )
				
		# auth_user table (superuser + related users)
		filterset_user = User.objects.filter(Q(groups__id=current_user.id) | Q(id=current_user.id)).values('id', 'username').annotate(dcount=Count('id'))

	# if the logged user is not a superuser and staff 
	elif current_user.is_superuser == False and current_user.is_staff == False:
		# get datas of puntoventa related on the logged user. (only logged user)
		puntoventa_filter = PuntoVenta.objects.filter(user_id=user_id)

		# auth_user table (only logged user)
		filterset_user = User.objects.filter(id=user_id).values('id', 'username').annotate(dcount=Count('id'))
	
		if localidad == "" and nombre_pv == "":
			# get all QuerySet

			# allset from ApuestaCaballos
			filterd_set_cab = ApuestaCaballos.objects.all().filter(fecha_apuesta_cab__gte=inicial, fecha_apuesta_cab__lte=final)
			
			# if user_id != "0":
			filterd_set_cab = filterd_set_cab.filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			
			filterd_set_cab_aggregate = filterd_set_cab.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_cab'), ventas=Sum('valor_apuesta_cab'))
			
			
		else:   	 
			# filtered QuerySet
			# filterd_set from ApuestaCaballos
			# if user_id != "0":
			filterd_set_cab = ApuestaCaballos.objects.all().filter(fecha_apuesta_cab__gte=inicial, fecha_apuesta_cab__lte=final).filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			
			if nombre_pv != "":	
				filterd_set_cab = filterd_set_cab.filter( id_cajero__id_pos_pc__id_pv__nombre_pv=nombre_pv )
				filterd_set_cab_aggregate = filterd_set_cab.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_cab'), ventas=Sum('valor_apuesta_cab'))
				
			
			if localidad != "":
				filterd_set_cab = filterd_set_cab.filter( id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=localidad )
				filterd_set_cab_aggregate = filterd_set_cab.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_cab'), ventas=Sum('valor_apuesta_cab'))
				
			
		# calculate the premois
		if user_id != "0":
			filterd_set_ganadorescab = GanadoresCaballos.objects.all().filter(fecha_ganado_cab__gte=inicial, fecha_ganado_cab__lte=final).filter( id_apuesta_cab__id_cajero__id_pos_pc__id_pv__user_id=user_id )
			
		else:
			filterd_set_ganadorescab = GanadoresCaballos.objects.all().filter(fecha_ganado_cab__gte=inicial, fecha_ganado_cab__lte=final)
		
		
	# add ventas from queryset list (ApuestaCaballos)
	table_data_caballos = set_table_caballos(filterd_set_cab_aggregate, current_user.is_staff, user_id, inicial, final)
		
	# append filtered set for datatable
	queryset.append(table_data_caballos) # obj.0

	# get pdvs
	pdvs = len(table_data_caballos)

	# calculate tickets
	# Count( ApuestaCaballos.id_apuesta_cab)
	tickets = filterd_set_cab.count()

	# calculate the ventas
	# SUM( ApuestaCaballos.valor_apuesta_cab )
	vantas_ApuestaCaballos = filterd_set_cab.aggregate(Sum('valor_apuesta_cab'))['valor_apuesta_cab__sum']
	
	if vantas_ApuestaCaballos is not None: 
		ventas += vantas_ApuestaCaballos
	

	if nombre_pv != "":
		filterd_set_ganadorescab = filterd_set_ganadorescab.filter( id_apuesta_cab__id_cajero__id_pos_pc__id_pv__nombre_pv=nombre_pv )
		
	if localidad != "":
		filterd_set_ganadorescab = filterd_set_ganadorescab.filter( id_apuesta_cab__id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=localidad )
				
	premios_ganadorescab = filterd_set_ganadorescab.aggregate(Sum('valor_ganado_cab'))['valor_ganado_cab__sum']


	if premios_ganadorescab is not None: 
		premios += premios_ganadorescab
	
	
	# calculate the saldo
	# SUM( GanadoresBingo.valor_ganado_cab ) - SUM( ApuestaCaballos.valor_apuesta_cab )
	saldo = ventas - premios

	# calculate the percentage
	# SUM( GanadoresBingo.valor_ganado_cab ) * 100 / SUM( ApuestaCaballos.valor_apuesta_cab )
	if ventas != 0:
		percentage = premios * 100 / ventas 

	
	# model:Localidad
	localidads = puntoventa_filter.values('id_localidad')
	filterset_localidad = Localidad.objects.filter(id_localidad__in=localidads).values('nombre_localidad').annotate(dcount=Count('nombre_localidad'))	
	queryset.append(filterset_localidad) # obj.1

	# model:PuntoVenta
	filterset_pdv = puntoventa_filter.values('nombre_pv').annotate(dcount=Count('nombre_pv'))	
	queryset.append(filterset_pdv) # obj.2

	queryset.append(filterset_user) #obj.3

	header_colors = []
	if ventas < 0:
		header_colors.append(0)
	else:
		header_colors.append(1)

	if premios < 0:
		header_colors.append(0)
	else:
		header_colors.append(1)

	if saldo < 0:
		header_colors.append(0)
	else:
		header_colors.append(1)
	# return Response
	# obj : queryset
	# localidad : localidad
	# nombre_pv : nombre_pv
	# selecclonar : selecclonar
	# inicial : inicial
	# final : final
	# tickets : tickets
	# ventas : ventas
	# premios : premios
	# saldo : saldo
	# percentage : percentage		
	# pdvs : pdvs
	# user_id : user_id
	# header_colors: header_colors
	result_dict = {'obj':queryset, 'localidad':localidad, 'nombre_pv':nombre_pv, 'selecclonar':selecclonar, 'inicial':inicial, 'final':final, 'tickets':tickets, 'ventas':'${:0,.2f}'.format(ventas), 'premios':'${:0,.2f}'.format(premios), 'saldo':'${:0,.2f}'.format(saldo), 'percentage':'%{:0,.2f}'.format(percentage), 'pdvs':pdvs, 'user_id':int(user_id), 'header_colors':header_colors}
	if not general_report:
		return TemplateResponse(request, 'reportes_caballos.html', result_dict)
	else:
		return result_dict

def set_table_perros(allset_apuesta_perros_aggregate, is_staff=False, user_id = '0', inicial = '', final=''):
	

	table_data_perros = []

	for i in range(len(allset_apuesta_perros_aggregate)):

		line_perros = allset_apuesta_perros_aggregate[i]

		perros_username = line_perros['id_cajero__id_pos_pc__id_pv__user_id__username']
		perros_localidad = line_perros['id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad']
		perros_pdv = line_perros['id_cajero__id_pos_pc__id_pv__nombre_pv']


		# calculate premios
		if user_id != '0':
			filterd_set_ganadoresper = GanadoresPerros.objects.all().filter( id_apuesta_p__id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=line_perros['id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad'] ).filter( id_apuesta_p__id_cajero__id_pos_pc__id_pv__nombre_pv=line_perros['id_cajero__id_pos_pc__id_pv__nombre_pv'] ).filter( id_apuesta_p__id_cajero__id_pos_pc__id_pv__user_id = user_id )
		else:
			filterd_set_ganadoresper = GanadoresPerros.objects.all().filter( id_apuesta_p__id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=line_perros['id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad'] ).filter( id_apuesta_p__id_cajero__id_pos_pc__id_pv__nombre_pv=line_perros['id_cajero__id_pos_pc__id_pv__nombre_pv'] )
			
		if inicial != '' and final != '':
			filterd_set_ganadoresper = filterd_set_ganadoresper.filter(fecha_ganado_p__gte=inicial, fecha_ganado_p__lte=final)
			
		premios_ganadoresper = filterd_set_ganadoresper.aggregate(valor_ganado_p__sum=Coalesce(Sum('valor_ganado_p'),0))['valor_ganado_p__sum']
		
		sum_perros = line_perros
		
		sum_perros['premios'] = premios_ganadoresper

		# calculate saldo
		sum_perros['saldo'] = sum_perros['ventas'] - sum_perros['premios']

		# calculate percentage
		if sum_perros['ventas'] != 0:
			sum_perros['percentage'] = round(sum_perros['premios'] * 100 / sum_perros['ventas'], 2)
		else:
			sum_perros['percentage'] = 0

		sum_perros['percentage'] = '%{:0,.2f}'.format(sum_perros['percentage'])

		table_data_perros.append(sum_perros)

		
	return table_data_perros


@login_required
def reportes_perros(request, general_report=None):
	
	# model:ApuestaPerros
	template_name=	'reportes_perros.html'
	context_object_name='obj'
	queryset = []

	current_user = request.user

	if current_user.is_staff:
		allset_apuesta_per = ApuestaPerros.objects.all()
		
		#get data for all puntoventa
		puntoventa_filter = PuntoVenta.objects.all()

		# auth_user table (only logged user)
		filterset_user = User.objects.all().values('id', 'username').annotate(dcount=Count('id'))


	elif current_user.is_superuser and current_user.is_staff == False:
		users = User.objects.filter(groups__id=current_user.id)
		user_ids = users.values('id')

		allset_apuesta_per = ApuestaPerros.objects.all()
		
		# for user_id in user_ids: (superuser + related users)
		allset_apuesta_per = allset_apuesta_per.filter(Q(id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_cajero__id_pos_pc__id_pv__user_id=current_user.id))

		# get datas of puntoventa related on the logged user. (superuser + related users)
		puntoventa_filter = PuntoVenta.objects.filter(Q(user_id__in=user_ids) | Q(user_id=current_user.id))

		# auth_user table (superuser + related users)
		filterset_user = User.objects.filter(Q(groups__id=current_user.id) | Q(id=current_user.id)).values('id', 'username').annotate(dcount=Count('id'))
		
	elif current_user.is_superuser == False and current_user.is_staff == False:
		# (only logged user)
		allset_apuesta_per = ApuestaPerros.objects.filter(id_cajero__id_pos_pc__id_pv__user_id=current_user.id)

		# get datas of puntoventa related on the logged user. (only logged user)
		puntoventa_filter = PuntoVenta.objects.filter(user_id=current_user.id)

		# auth_user table (only logged user)
		filterset_user = User.objects.filter(id=current_user.id).values('id', 'username').annotate(dcount=Count('id'))
		

	allset_apuesta_perros_aggregate = allset_apuesta_per.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_p'), ventas=Sum('valor_apuesta_p'))
	
	
	# add ventas from queryset list
	table_data_perros = set_table_perros(allset_apuesta_perros_aggregate, current_user.is_staff)

	queryset.append(table_data_perros) # obj.0


	localidads = puntoventa_filter.values('id_localidad')
	filterset_localidad = Localidad.objects.filter(id_localidad__in=localidads).values('nombre_localidad').annotate(dcount=Count('nombre_localidad'))	
	queryset.append(filterset_localidad) # obj.1

	filterset_pdv = puntoventa_filter.values('nombre_pv').annotate(dcount=Count('nombre_pv'))	
	queryset.append(filterset_pdv) # obj.2


	pdvs = len(table_data_perros)
	tickets = 0
	ventas = 0
	premios = 0
	saldo = 0
	for item in table_data_perros:
		tickets += item['tickets']
		ventas += item['ventas']
		premios += item['premios']
		saldo += item['saldo']

	
	queryset.append(filterset_user) # obj.3

	header_colors = []
	if ventas < 0:
		header_colors.append(0)
	else:
		header_colors.append(1)

	if premios < 0:
		header_colors.append(0)
	else:
		header_colors.append(1)

	if saldo < 0:
		header_colors.append(0)
	else:
		header_colors.append(1)
	
	total_panel = {'pdvs':pdvs, 'tickets':tickets, 'ventas':'${:0,.2f}'.format(ventas), 'premios':'${:0,.2f}'.format(premios), 'saldo':'${:0,.2f}'.format(saldo)}
	queryset.append(total_panel) # obj.4

	result_dict = {'obj':queryset, 'header_colors':header_colors}
	if not general_report:
		return TemplateResponse(request, 'reportes_perros.html', result_dict)
	else:
		return queryset

@login_required
def ajax_reportes_perros(request, general_report=None):
	# get post data
	localidad = request.POST.get('localidad') # localidad
	nombre_pv = request.POST.get('nombre_pv') # nombre_pv
	user_id = request.POST.get('user_id')
	selecclonar = request.POST.get('selecclonar') # selecclonar (hoy, selecclone de)
	inicial = request.POST.get('inicial') # inicial date
	final = request.POST.get('final') # final date
	
	# response queryset as a list
	queryset = []

	# count and sum
	pdvs = 0
	tickets = 0
	ventas = 0 # sum of ventas from two tables (carton_keno & carton_cartas)
	ventas_list = [] # each ventas from two tables (carton_keno & carton_cartas)
	premios = 0 # sum of premios from two tables (carton_keno & carton_cartas)
	premios_list = [] # each premios from two tables (carton_keno & carton_cartas)
	saldo = 0
	percentage = 0

	current_user = request.user

	if current_user.is_staff and current_user.is_superuser == False:

		# get datas of puntoventa for all users.
		puntoventa_filter = PuntoVenta.objects.all()

		if localidad == "" and nombre_pv == "":
			# get all QuerySet

			# allset from CartonBingo
			filterd_set_per = ApuestaPerros.objects.all().filter(fecha_apuesta_p__gte=inicial, fecha_apuesta_p__lte=final)
			
			if user_id != "0":
				filterd_set_per = filterd_set_per.filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
				
			
			filterd_set_per_aggregate = filterd_set_per.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_p'), ventas=Sum('valor_apuesta_p'))
			
			
		else:   	 
			# filtered QuerySet
			filterd_set_per = ApuestaPerros.objects.all().filter(fecha_apuesta_p__gte=inicial, fecha_apuesta_p__lte=final)
			
			if user_id != "0":
				filterd_set_per = filterd_set_per.filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			
			if nombre_pv != "":	
				filterd_set_per = filterd_set_per.filter( id_cajero__id_pos_pc__id_pv__nombre_pv=nombre_pv )
				filterd_set_per_aggregate = filterd_set_per.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_p'), ventas=Sum('valor_apuesta_p'))
				
			if localidad != "":
				filterd_set_per = filterd_set_per.filter( id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=localidad )
				filterd_set_per_aggregate = filterd_set_per.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_p'), ventas=Sum('valor_apuesta_p'))
				
				
		# calculate the premois
		filterd_set_ganadoresper = GanadoresPerros.objects.all().filter(fecha_ganado_p__gte=inicial, fecha_ganado_p__lte=final)#.filter(Q(id_apuesta_p__id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_apuesta_p__id_cajero__id_pos_pc__id_pv__user_id=current_user.id))
		
		if user_id != '0':
			
			# check if user_id is superuser
			user_info = User.objects.filter(id=user_id).values('is_staff')

			# if selected user is superuser
			if user_info[0]['is_staff'] == False:
				# get datas of puntoventa related on the logged user. (selected user)
				puntoventa_filter = PuntoVenta.objects.filter(user_id=user_id)
		
				# calculate the premios
				filterd_set_ganadoresper = GanadoresPerros.objects.all().filter(fecha_ganado_p__gte=inicial, fecha_ganado_p__lte=final).filter( id_apuesta_p__id_cajero__id_pos_pc__id_pv__user_id=user_id )
				
		# auth_user table (superuser + related users)
		filterset_user = User.objects.all().values('id', 'username').annotate(dcount=Count('id'))
	
	# logged user is a superuser but not staff
	elif current_user.is_superuser and current_user.is_staff == False:

		users = User.objects.filter(groups__id=current_user.id)
		user_ids = users.values('id')

		# get datas of puntoventa related on the logged user. (superuser + related users)
		puntoventa_filter = PuntoVenta.objects.filter(Q(user_id__in=user_ids) | Q(user_id=current_user.id))

		if localidad == "" and nombre_pv == "":
			# get all QuerySet

			# allset from ApuestaPerros
			filterd_set_per = ApuestaPerros.objects.all().filter(fecha_apuesta_p__gte=inicial, fecha_apuesta_p__lte=final)
			
			if user_id != "0":
				filterd_set_per = filterd_set_per.filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			else:
				filterd_set_per = filterd_set_per.filter(Q(id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_cajero__id_pos_pc__id_pv__user_id=current_user.id))
			
			filterd_set_per_aggregate = filterd_set_per.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_p'), ventas=Sum('valor_apuesta_p'))
			
		else:   	 
			# filtered QuerySet
			# filterd_set from ApuestaPerros
			if user_id != "0":
				filterd_set_per = ApuestaPerros.objects.all().filter(fecha_apuesta_p__gte=inicial, fecha_apuesta_p__lte=final).filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			else:
				filterd_set_per = ApuestaPerros.objects.all().filter(fecha_apuesta_p__gte=inicial, fecha_apuesta_p__lte=final).filter(Q(id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_cajero__id_pos_pc__id_pv__user_id=current_user.id))
				
			if nombre_pv != "":	
				filterd_set_per = filterd_set_per.filter( id_cajero__id_pos_pc__id_pv__nombre_pv=nombre_pv )
				filterd_set_per_aggregate = filterd_set_per.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_p'), ventas=Sum('valor_apuesta_p'))
				
				
			if localidad != "":
				filterd_set_per = filterd_set_per.filter( id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=localidad )
				filterd_set_per_aggregate = filterd_set_per.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_p'), ventas=Sum('valor_apuesta_p'))
				
				
		# calculate the premois
		filterd_set_ganadoresper = GanadoresPerros.objects.all().filter(fecha_ganado_p__gte=inicial, fecha_ganado_p__lte=final).filter(Q(id_apuesta_p__id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_apuesta_p__id_cajero__id_pos_pc__id_pv__user_id=current_user.id))
		
		if user_id != '0':
			
			# check if user_id is superuser
			user_info = User.objects.filter(id=user_id).values('is_superuser')

			# if selected user is superuser
			if user_info[0]['is_superuser'] == False:
				# get datas of puntoventa related on the logged user. (selected user)
				puntoventa_filter = PuntoVenta.objects.filter(user_id=user_id)
		
				# calculate the premios
				filterd_set_ganadoresper = GanadoresPerros.objects.all().filter(fecha_ganado_p__gte=inicial, fecha_ganado_p__lte=final).filter( id_apuesta_p__id_cajero__id_pos_pc__id_pv__user_id=user_id )
				
		# auth_user table (superuser + related users)
		filterset_user = User.objects.filter(Q(groups__id=current_user.id) | Q(id=current_user.id)).values('id', 'username').annotate(dcount=Count('id'))

	# if the logged user is not a superuser and staff 
	elif current_user.is_superuser == False and current_user.is_staff == False:
		# get datas of puntoventa related on the logged user. (only logged user)
		puntoventa_filter = PuntoVenta.objects.filter(user_id=user_id)

		# auth_user table (only logged user)
		filterset_user = User.objects.filter(id=user_id).values('id', 'username').annotate(dcount=Count('id'))
	
		if localidad == "" and nombre_pv == "":
			# get all QuerySet

			# allset from ApuestaPerros
			filterd_set_per = ApuestaPerros.objects.all().filter(fecha_apuesta_p__gte=inicial, fecha_apuesta_p__lte=final)
			
			# if user_id != "0":
			filterd_set_per = filterd_set_per.filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			
			filterd_set_per_aggregate = filterd_set_per.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_p'), ventas=Sum('valor_apuesta_p'))
			
			
		else:   	 
			# filtered QuerySet
			# filterd_set from ApuestaPerros
			# if user_id != "0":
			filterd_set_per = ApuestaPerros.objects.all().filter(fecha_apuesta_p__gte=inicial, fecha_apuesta_p__lte=final).filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			
			if nombre_pv != "":	
				filterd_set_per = filterd_set_per.filter( id_cajero__id_pos_pc__id_pv__nombre_pv=nombre_pv )
				filterd_set_per_aggregate = filterd_set_per.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_p'), ventas=Sum('valor_apuesta_p'))
				
			
			if localidad != "":
				filterd_set_per = filterd_set_per.filter( id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=localidad )
				filterd_set_per_aggregate = filterd_set_per.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_apuesta_p'), ventas=Sum('valor_apuesta_p'))
				
			
		# calculate the premois
		if user_id != "0":
			filterd_set_ganadoresper = GanadoresPerros.objects.all().filter(fecha_ganado_p__gte=inicial, fecha_ganado_p__lte=final).filter( id_apuesta_p__id_cajero__id_pos_pc__id_pv__user_id=user_id )
			
		else:
			filterd_set_ganadoresper = GanadoresPerros.objects.all().filter(fecha_ganado_p__gte=inicial, fecha_ganado_p__lte=final)
		
		
	# add ventas from queryset list (ApuestaPerros)
	table_data_perros = set_table_perros(filterd_set_per_aggregate, current_user.is_staff, user_id, inicial, final)
		
	# append filtered set for datatable
	queryset.append(table_data_perros) # obj.0

	# get pdvs
	pdvs = len(table_data_perros)

	# calculate tickets
	# Count( ApuestaPerros.id_apuesta_p)
	tickets = filterd_set_per.count()

	# calculate the ventas
	# SUM( ApuestaPerros.valor_apuesta_p )
	vantas_perros = filterd_set_per.aggregate(Sum('valor_apuesta_p'))['valor_apuesta_p__sum']
	
	if vantas_perros is not None: 
		ventas += vantas_perros
	

	if nombre_pv != "":
		filterd_set_ganadoresper = filterd_set_ganadoresper.filter( id_apuesta_p__id_cajero__id_pos_pc__id_pv__nombre_pv=nombre_pv )
		
	if localidad != "":
		filterd_set_ganadoresper = filterd_set_ganadoresper.filter( id_apuesta_p__id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=localidad )
				
	premios_ganadoresper = filterd_set_ganadoresper.aggregate(Sum('valor_ganado_p'))['valor_ganado_p__sum']


	if premios_ganadoresper is not None: 
		premios += premios_ganadoresper
	
	
	# calculate the saldo
	# SUM( GanadoresBingo.valor_ganado_p ) - SUM( ApuestaPerros.valor_apuesta_p )
	saldo = ventas - premios

	# calculate the percentage
	# SUM( GanadoresBingo.valor_ganado_p ) * 100 / SUM( ApuestaPerros.valor_apuesta_p )
	if ventas != 0:
		percentage = premios * 100 / ventas 

	
	# model:Localidad
	localidads = puntoventa_filter.values('id_localidad')
	filterset_localidad = Localidad.objects.filter(id_localidad__in=localidads).values('nombre_localidad').annotate(dcount=Count('nombre_localidad'))	
	queryset.append(filterset_localidad) # obj.1

	# model:PuntoVenta
	filterset_pdv = puntoventa_filter.values('nombre_pv').annotate(dcount=Count('nombre_pv'))	
	queryset.append(filterset_pdv) # obj.2

	queryset.append(filterset_user) #obj.3

	header_colors = []
	if ventas < 0:
		header_colors.append(0)
	else:
		header_colors.append(1)

	if premios < 0:
		header_colors.append(0)
	else:
		header_colors.append(1)

	if saldo < 0:
		header_colors.append(0)
	else:
		header_colors.append(1)
	# return Response
	# obj : queryset
	# localidad : localidad
	# nombre_pv : nombre_pv
	# selecclonar : selecclonar
	# inicial : inicial
	# final : final
	# tickets : tickets
	# ventas : ventas
	# premios : premios
	# saldo : saldo
	# percentage : percentage		
	# pdvs : pdvs
	# user_id : user_id
	# header_colors: header_colors
	result_dict = {'obj':queryset, 'localidad':localidad, 'nombre_pv':nombre_pv, 'selecclonar':selecclonar, 'inicial':inicial, 'final':final, 'tickets':tickets, 'ventas':'${:0,.2f}'.format(ventas), 'premios':'${:0,.2f}'.format(premios), 'saldo':'${:0,.2f}'.format(saldo), 'percentage':'%{:0,.2f}'.format(percentage), 'pdvs':pdvs, 'user_id':int(user_id), 'header_colors':header_colors}
	if not general_report:
		return TemplateResponse(request, 'reportes_perros.html', result_dict)
	else:
		return result_dict	

#  --------------------------- general report start ---------------------------
@login_required
def reportes_general(request):
	# queryset.append(table_data_perros) # obj.0
	# queryset.append(filterset_localidad) # obj.1
	# queryset.append(filterset_pdv) # obj.2
	# queryset.append(filterset_user) # obj.3
	# queryset.append(total_panel) # obj.4
	status = 'general'
	tickets = 0
	ventas = 0
	premios = 0
	saldo = 0
	users = []

	# keno & cartas
	keno_cartas_list = reportes(request, status)
	table_data_keno_cartas = keno_cartas_list[0]
	# pdvs = len(table_data_keno_cartas)
	
	for item in table_data_perros:
		users.append(item['id_cajero__id_pos_pc__id_pv__user_id__username'])
		tickets += item['tickets']
		ventas += item['ventas']
		premios += item['premios']
		saldo += item['saldo']

	# bingo
	bingo_list = reportes_bingo(request, status)
	table_data_bingo = bingo_list[0]
	# pdvs = len(table_data_keno_cartas)
	
	for item in table_data_bingo:
		users.append(item['id_cajero__id_pos_pc__id_pv__user_id__username'])
		tickets += item['tickets']
		ventas += item['ventas']
		premios += item['premios']
		saldo += item['saldo']

	# caballos
	caballos_list = reportes_caballos(request, status)
	table_data_caballos = caballos_list[0]
	# pdvs = len(table_data_keno_cartas)
	
	for item in table_data_caballos:
		users.append(item['id_cajero__id_pos_pc__id_pv__user_id__username'])
		tickets += item['tickets']
		ventas += item['ventas']
		premios += item['premios']
		saldo += item['saldo']

	# perros
	perros_list = reportes_perros(request, status)
	table_data_perros = perros_list[0]
	# pdvs = len(table_data_keno_cartas)
	
	for item in table_data_perros:
		users.append(item['id_cajero__id_pos_pc__id_pv__user_id__username'])
		tickets += item['tickets']
		ventas += item['ventas']
		premios += item['premios']
		saldo += item['saldo']

	# get count of unique users
    users = list(dict.fromkeys(users))
    pdvs = len(users)

	
	# localidad, pdvs, user
	filterset_localidad = perros_list[1]
	filterset_pdv = perros_list[2]
	filterset_user = perros_list[3]

	

	return TemplateResponse(request, 'reportes_general.html', {'obj':queryset, 'header_colors':header_colors})

@login_required
def ajax_reportes_general(request):
	# get post data
	localidad = request.POST.get('localidad') # localidad
	nombre_pv = request.POST.get('nombre_pv') # nombre_pv
	user_id = request.POST.get('user_id')
	selecclonar = request.POST.get('selecclonar') # selecclonar (hoy, selecclone de)
	inicial = request.POST.get('inicial') # inicial date
	final = request.POST.get('final') # final date
	
	# response queryset as a list
	queryset = []

	# count and sum
	pdvs = 0
	tickets = 0
	ventas = 0 # sum of ventas from two tables (carton_keno & carton_cartas)
	ventas_list = [] # each ventas from two tables (carton_keno & carton_cartas)
	premios = 0 # sum of premios from two tables (carton_keno & carton_cartas)
	premios_list = [] # each premios from two tables (carton_keno & carton_cartas)
	saldo = 0
	percentage = 0

	current_user = request.user

	if current_user.is_staff and current_user.is_superuser == False:

		# get datas of puntoventa for all users.
		puntoventa_filter = PuntoVenta.objects.all()

		if localidad == "" and nombre_pv == "":
			# get all QuerySet

			# allset from CartonKeno
			filterd_set_keno = CartonKeno.objects.all().filter(fecha_keno__gte=inicial, fecha_keno__lte=final)
			# allset from CartonCartas
			filterd_set_cartas = CartonCartas.objects.all().filter(fecha_cartas__gte=inicial, fecha_cartas__lte=final)

			if user_id != "0":
				filterd_set_keno = filterd_set_keno.filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
				filterd_set_cartas = filterd_set_cartas.filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			# else:
			# 	filterd_set_keno = filterd_set_keno.filter(id_cajero__id_pos_pc__id_pv__user_id=current_user.id)
			# 	filterd_set_cartas = filterd_set_cartas.filter(id_cajero__id_pos_pc__id_pv__user_id=current_user.id)

			filterd_set_keno_aggregate = filterd_set_keno.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_k'), ventas=Sum('valor_apuesta_k'))
			
			filterd_set_cartas_aggregate = filterd_set_cartas.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__user_id__username').annotate(tickets=Count('id_c_c'), ventas=Sum('valor_apuesta_c'))
			
		else:   	 
			# filtered QuerySet
			# filterd_set from CartonKeno and CartonCartas
			filterd_set_keno = CartonKeno.objects.all().filter(fecha_keno__gte=inicial, fecha_keno__lte=final)
			filterd_set_cartas = CartonCartas.objects.all().filter(fecha_cartas__gte=inicial, fecha_cartas__lte=final)

			if user_id != "0":
				filterd_set_keno = filterd_set_keno.filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
				filterd_set_cartas = filterd_set_cartas.filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			# else:
			# 	filterd_set_keno = CartonKeno.objects.all().filter(fecha_keno__gte=inicial, fecha_keno__lte=final).filter(Q(id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_cajero__id_pos_pc__id_pv__user_id=current_user.id))
			# 	filterd_set_cartas = CartonCartas.objects.all().filter(fecha_cartas__gte=inicial, fecha_cartas__lte=final).filter(Q(id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_cajero__id_pos_pc__id_pv__user_id=current_user.id))

			if nombre_pv != "":	
				filterd_set_keno = filterd_set_keno.filter( id_cajero__id_pos_pc__id_pv__nombre_pv=nombre_pv )
				filterd_set_keno_aggregate = filterd_set_keno.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_k'), ventas=Sum('valor_apuesta_k'))
				
				filterd_set_cartas = filterd_set_cartas.filter( id_cajero__id_pos_pc__id_pv__nombre_pv=nombre_pv )
				filterd_set_cartas_aggregate = filterd_set_cartas.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_c'), ventas=Sum('valor_apuesta_c'))

			if localidad != "":
				filterd_set_keno = filterd_set_keno.filter( id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=localidad )
				filterd_set_keno_aggregate = filterd_set_keno.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_k'), ventas=Sum('valor_apuesta_k'))
				
				filterd_set_cartas = filterd_set_cartas.filter( id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=localidad )
				filterd_set_cartas_aggregate = filterd_set_cartas.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_c'), ventas=Sum('valor_apuesta_c'))
		
		# calculate the premois
		filterd_set_ganadoreskeno = GanadoresKeno.objects.all().filter(fecha_ganadores_k__gte=inicial, fecha_ganadores_k__lte=final)#.filter(Q(id_c_k__id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_c_k__id_cajero__id_pos_pc__id_pv__user_id=current_user.id))
		filterd_set_ganadorescartas = GanadoresCartas.objects.all().filter(fecha_ganadores_c__gte=inicial, fecha_ganadores_c__lte=final)#.filter(Q(id_c_c__id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_c_c__id_cajero__id_pos_pc__id_pv__user_id=current_user.id))

		if user_id != '0':
			
			# check if user_id is superuser
			user_info = User.objects.filter(id=user_id).values('is_staff')

			# if selected user is superuser
			if user_info[0]['is_staff'] == False:
				# get datas of puntoventa related on the logged user. (selected user)
				puntoventa_filter = PuntoVenta.objects.filter(user_id=user_id)
		
				# calculate the premios
				filterd_set_ganadoreskeno = GanadoresKeno.objects.all().filter(fecha_ganadores_k__gte=inicial, fecha_ganadores_k__lte=final).filter( id_c_k__id_cajero__id_pos_pc__id_pv__user_id=user_id )
				filterd_set_ganadorescartas = GanadoresCartas.objects.all().filter(fecha_ganadores_c__gte=inicial, fecha_ganadores_c__lte=final).filter( id_c_c__id_cajero__id_pos_pc__id_pv__user_id=user_id )
		
		# auth_user table (superuser + related users)
		#filterset_user = User.objects.filter(Q(groups__id=current_user.id) | Q(id=current_user.id)).values('id', 'username').annotate(dcount=Count('id'))
		filterset_user = User.objects.all().values('id', 'username').annotate(dcount=Count('id'))
	
	# logged user is a superuser but not staff
	elif current_user.is_superuser and current_user.is_staff == False:

		users = User.objects.filter(groups__id=current_user.id)
		user_ids = users.values('id')

		# get datas of puntoventa related on the logged user. (superuser + related users)
		puntoventa_filter = PuntoVenta.objects.filter(Q(user_id__in=user_ids) | Q(user_id=current_user.id))

		if localidad == "" and nombre_pv == "":
			# get all QuerySet

			# allset from CartonKeno
			filterd_set_keno = CartonKeno.objects.all().filter(fecha_keno__gte=inicial, fecha_keno__lte=final)
			# allset from CartonCartas
			filterd_set_cartas = CartonCartas.objects.all().filter(fecha_cartas__gte=inicial, fecha_cartas__lte=final)

			if user_id != "0":
				filterd_set_keno = filterd_set_keno.filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
				filterd_set_cartas = filterd_set_cartas.filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			else:
				filterd_set_keno = filterd_set_keno.filter(Q(id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_cajero__id_pos_pc__id_pv__user_id=current_user.id))
				filterd_set_cartas = filterd_set_cartas.filter(Q(id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_cajero__id_pos_pc__id_pv__user_id=current_user.id))

			filterd_set_keno_aggregate = filterd_set_keno.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_k'), ventas=Sum('valor_apuesta_k'))
			
			filterd_set_cartas_aggregate = filterd_set_cartas.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__user_id__username').annotate(tickets=Count('id_c_c'), ventas=Sum('valor_apuesta_c'))
			
		else:   	 
			# filtered QuerySet
			# filterd_set from CartonKeno
			if user_id != "0":
				filterd_set_keno = CartonKeno.objects.all().filter(fecha_keno__gte=inicial, fecha_keno__lte=final).filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
				filterd_set_cartas = CartonCartas.objects.all().filter(fecha_cartas__gte=inicial, fecha_cartas__lte=final).filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			else:
				filterd_set_keno = CartonKeno.objects.all().filter(fecha_keno__gte=inicial, fecha_keno__lte=final).filter(Q(id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_cajero__id_pos_pc__id_pv__user_id=current_user.id))
				filterd_set_cartas = CartonCartas.objects.all().filter(fecha_cartas__gte=inicial, fecha_cartas__lte=final).filter(Q(id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_cajero__id_pos_pc__id_pv__user_id=current_user.id))

			if nombre_pv != "":	
				filterd_set_keno = filterd_set_keno.filter( id_cajero__id_pos_pc__id_pv__nombre_pv=nombre_pv )
				filterd_set_keno_aggregate = filterd_set_keno.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_k'), ventas=Sum('valor_apuesta_k'))
				
				filterd_set_cartas = filterd_set_cartas.filter( id_cajero__id_pos_pc__id_pv__nombre_pv=nombre_pv )
				filterd_set_cartas_aggregate = filterd_set_cartas.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_c'), ventas=Sum('valor_apuesta_c'))

			if localidad != "":
				filterd_set_keno = filterd_set_keno.filter( id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=localidad )
				filterd_set_keno_aggregate = filterd_set_keno.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_k'), ventas=Sum('valor_apuesta_k'))
				
				filterd_set_cartas = filterd_set_cartas.filter( id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=localidad )
				filterd_set_cartas_aggregate = filterd_set_cartas.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_c'), ventas=Sum('valor_apuesta_c'))
		
		# calculate the premois
		filterd_set_ganadoreskeno = GanadoresKeno.objects.all().filter(fecha_ganadores_k__gte=inicial, fecha_ganadores_k__lte=final).filter(Q(id_c_k__id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_c_k__id_cajero__id_pos_pc__id_pv__user_id=current_user.id))
		filterd_set_ganadorescartas = GanadoresCartas.objects.all().filter(fecha_ganadores_c__gte=inicial, fecha_ganadores_c__lte=final).filter(Q(id_c_c__id_cajero__id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_c_c__id_cajero__id_pos_pc__id_pv__user_id=current_user.id))

		if user_id != '0':
			
			# check if user_id is superuser
			user_info = User.objects.filter(id=user_id).values('is_superuser')

			# if selected user is superuser
			if user_info[0]['is_superuser'] == False:
				# get datas of puntoventa related on the logged user. (selected user)
				puntoventa_filter = PuntoVenta.objects.filter(user_id=user_id)
		
				# calculate the premios
				filterd_set_ganadoreskeno = GanadoresKeno.objects.all().filter(fecha_ganadores_k__gte=inicial, fecha_ganadores_k__lte=final).filter( id_c_k__id_cajero__id_pos_pc__id_pv__user_id=user_id )
				filterd_set_ganadorescartas = GanadoresCartas.objects.all().filter(fecha_ganadores_c__gte=inicial, fecha_ganadores_c__lte=final).filter( id_c_c__id_cajero__id_pos_pc__id_pv__user_id=user_id )
		
		# auth_user table (superuser + related users)
		filterset_user = User.objects.filter(Q(groups__id=current_user.id) | Q(id=current_user.id)).values('id', 'username').annotate(dcount=Count('id'))

	# if the logged user is not a superuser and staff 
	elif current_user.is_superuser == False and current_user.is_staff == False:
		# get datas of puntoventa related on the logged user. (only logged user)
		puntoventa_filter = PuntoVenta.objects.filter(user_id=user_id)

		# auth_user table (only logged user)
		filterset_user = User.objects.filter(id=user_id).values('id', 'username').annotate(dcount=Count('id'))
	
		if localidad == "" and nombre_pv == "":
			# get all QuerySet

			# allset from CartonKeno
			filterd_set_keno = CartonKeno.objects.all().filter(fecha_keno__gte=inicial, fecha_keno__lte=final)
			# allset from CartonCartas
			filterd_set_cartas = CartonCartas.objects.all().filter(fecha_cartas__gte=inicial, fecha_cartas__lte=final)

			# if user_id != "0":
			filterd_set_keno = filterd_set_keno.filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			filterd_set_cartas = filterd_set_cartas.filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			# else:

			filterd_set_keno_aggregate = filterd_set_keno.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_k'), ventas=Sum('valor_apuesta_k'))
			
			filterd_set_cartas_aggregate = filterd_set_cartas.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__user_id__username').annotate(tickets=Count('id_c_c'), ventas=Sum('valor_apuesta_c'))
			
		else:   	 
			# filtered QuerySet
			# filterd_set from CartonKeno
			# if user_id != "0":
			filterd_set_keno = CartonKeno.objects.all().filter(fecha_keno__gte=inicial, fecha_keno__lte=final).filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			filterd_set_cartas = CartonCartas.objects.all().filter(fecha_cartas__gte=inicial, fecha_cartas__lte=final).filter( id_cajero__id_pos_pc__id_pv__user_id=user_id )
			# else:
			# 	filterd_set_keno = CartonKeno.objects.all().filter(fecha_keno__gte=inicial, fecha_keno__lte=final)
			# 	filterd_set_cartas = CartonCartas.objects.all().filter(fecha_cartas__gte=inicial, fecha_cartas__lte=final)

			if nombre_pv != "":	
				filterd_set_keno = filterd_set_keno.filter( id_cajero__id_pos_pc__id_pv__nombre_pv=nombre_pv )
				filterd_set_keno_aggregate = filterd_set_keno.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_k'), ventas=Sum('valor_apuesta_k'))
				
				filterd_set_cartas = filterd_set_cartas.filter( id_cajero__id_pos_pc__id_pv__nombre_pv=nombre_pv )
				filterd_set_cartas_aggregate = filterd_set_cartas.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_c'), ventas=Sum('valor_apuesta_c'))

			if localidad != "":
				filterd_set_keno = filterd_set_keno.filter( id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=localidad )
				filterd_set_keno_aggregate = filterd_set_keno.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_k'), ventas=Sum('valor_apuesta_k'))
				
				filterd_set_cartas = filterd_set_cartas.filter( id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=localidad )
				filterd_set_cartas_aggregate = filterd_set_cartas.values('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad', 'id_cajero__id_pos_pc__id_pv__nombre_pv', 'id_cajero__id_pos_pc__id_pv__user_id__username').order_by('id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad').annotate(tickets=Count('id_c_c'), ventas=Sum('valor_apuesta_c'))
		
		# calculate the premois
		if user_id != "0":
			filterd_set_ganadoreskeno = GanadoresKeno.objects.all().filter(fecha_ganadores_k__gte=inicial, fecha_ganadores_k__lte=final).filter( id_c_k__id_cajero__id_pos_pc__id_pv__user_id=user_id )
			filterd_set_ganadorescartas = GanadoresCartas.objects.all().filter(fecha_ganadores_c__gte=inicial, fecha_ganadores_c__lte=final).filter( id_c_c__id_cajero__id_pos_pc__id_pv__user_id=user_id )
		else:
			filterd_set_ganadoreskeno = GanadoresKeno.objects.all().filter(fecha_ganadores_k__gte=inicial, fecha_ganadores_k__lte=final)
			filterd_set_ganadorescartas = GanadoresCartas.objects.all().filter(fecha_ganadores_c__gte=inicial, fecha_ganadores_c__lte=final)

		
	# add ventas from two queryset list (CartonKeno + CartonCartas)
	table_data = set_table_general_report(filterd_set_keno_aggregate, filterd_set_cartas_aggregate, current_user.is_staff, user_id, inicial, final)
		
	# append filtered set for datatable
	queryset.append(table_data) # obj.0

	# get pdvs
	pdvs = len(table_data)

	# calculate tickets
	# Count( CartonKeno.id_c_k) + Count( CartonCartas.id_c_c)
	tickets = filterd_set_keno.count() + filterd_set_cartas.count()

	# calculate the ventas
	# SUM( CartonKeno.valor_apuesta_k + CartonCartas.valor_apuesta_c )
	vantas_cartonkeno = filterd_set_keno.aggregate(Sum('valor_apuesta_k'))['valor_apuesta_k__sum']
	
	vantas_cartoncarts = filterd_set_cartas.aggregate(Sum('valor_apuesta_c'))['valor_apuesta_c__sum']
	
	
	if vantas_cartonkeno is not None: 
		ventas += vantas_cartonkeno
	
	if vantas_cartoncarts is not None: 
		ventas += vantas_cartoncarts

	if nombre_pv != "":
		filterd_set_ganadoreskeno = filterd_set_ganadoreskeno.filter( id_c_k__id_cajero__id_pos_pc__id_pv__nombre_pv=nombre_pv )
		filterd_set_ganadorescartas = filterd_set_ganadorescartas.filter( id_c_c__id_cajero__id_pos_pc__id_pv__nombre_pv=nombre_pv )
	if localidad != "":
		filterd_set_ganadoreskeno = filterd_set_ganadoreskeno.filter( id_c_k__id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=localidad )
		filterd_set_ganadorescartas = filterd_set_ganadorescartas.filter( id_c_c__id_cajero__id_pos_pc__id_pv__id_localidad__nombre_localidad=localidad )
		

	premios_ganadoreskeno = filterd_set_ganadoreskeno.aggregate(Sum('valor_ganado_k'))['valor_ganado_k__sum']


	if premios_ganadoreskeno is not None: 
		premios += premios_ganadoreskeno
	
	premios_ganadorescartas = filterd_set_ganadorescartas.aggregate(Sum('valor_ganado_c'))['valor_ganado_c__sum']
	
	if premios_ganadorescartas is not None: 
		premios += premios_ganadorescartas

	# calculate the saldo
	# SUM( GanadoresKeno.valor_ganado_k + GanadoresCartas.valor_ganado_c ) - SUM( CartonKeno.valor_apuesta_k + CartonCartas.valor_apuesta_c )
	saldo = ventas - premios

	# calculate the percentage
	# SUM( GanadoresKeno.valor_ganado_k + GanadoresCartas.valor_ganado_c ) * 100 / SUM( CartonKeno.valor_apuesta_k + CartonCartas.valor_apuesta_c )
	if ventas != 0:
		percentage = premios * 100 / ventas 

	
	# model:Localidad
	# filterset_localidad = Localidad.objects.values('nombre_localidad').annotate(dcount=Count('nombre_localidad'))
	localidads = puntoventa_filter.values('id_localidad')
	filterset_localidad = Localidad.objects.filter(id_localidad__in=localidads).values('nombre_localidad').annotate(dcount=Count('nombre_localidad'))	
	queryset.append(filterset_localidad) # obj.1

	# model:PuntoVenta
	# filterset_pdv = PuntoVenta.objects.values('nombre_pv').annotate(dcount=Count('nombre_pv'))
	filterset_pdv = puntoventa_filter.values('nombre_pv').annotate(dcount=Count('nombre_pv'))	
	queryset.append(filterset_pdv) # obj.2

	queryset.append(filterset_user) #obj.3

	header_colors = []
	if ventas < 0:
		header_colors.append(0)
	else:
		header_colors.append(1)

	if premios < 0:
		header_colors.append(0)
	else:
		header_colors.append(1)

	if saldo < 0:
		header_colors.append(0)
	else:
		header_colors.append(1)
	# return Response
	# obj : queryset
	# localidad : localidad
	# nombre_pv : nombre_pv
	# selecclonar : selecclonar
	# inicial : inicial
	# final : final
	# tickets : tickets
	# ventas : ventas
	# premios : premios
	# saldo : saldo
	# percentage : percentage		
	# pdvs : pdvs
	# user_id : user_id
	# header_colors: header_colors
	return TemplateResponse(request, 'reportes_general.html', {'obj':queryset, 'localidad':localidad, 'nombre_pv':nombre_pv, 'selecclonar':selecclonar, 'inicial':inicial, 'final':final, 'tickets':tickets, 'ventas':'${:0,.2f}'.format(ventas), 'premios':'${:0,.2f}'.format(premios), 'saldo':'${:0,.2f}'.format(saldo), 'percentage':'%{:0,.2f}'.format(percentage), 'pdvs':pdvs, 'user_id':int(user_id), 'header_colors':header_colors})

#  --------------------------- general report end -----------------------------

class CajeroCreate(LoginRequiredMixin,CreateView):
	model = Cajero
	form_class = CajeroForm
	template_name = "cajeros.html"
	context_object_name = "obj"
	success_url = reverse_lazy('core:cajerosall')
	login_url='/login'

	def form_valid(self, form):
		form.instance.user = self.request.user.id
		return super().form_valid(form)

#class CajeroViews(LoginRequiredMixin,ListView):
#	Model:Cajero
#	template_name="cajerosall.html"
#	context_object_name="obj"
#	#queryset = Cajero.objects.all()
#	login_url='/login'

#	def get_queryset(self, *args, **kwargs):

#		if User.is_superuser:
#			return Cajero.objects.all()
#		else:
#			return Cajero.objects.filter(id_pos_pc__id_pv__user=self.request.user)
@login_required		
def CajeroViews(request):

	current_user = request.user
	template_name = "cajerosall.html"
	queryset = []
	if current_user.is_staff:
		Cajero_filter=Cajero.objects.all()
	
	elif current_user.is_superuser:
		users = User.objects.filter(groups__id=current_user.id)
		user_ids = users.values('id')

		Cajero_filter = Cajero.objects.filter(Q(id_pos_pc__id_pv__user_id__in=user_ids) | Q(id_pos_pc__id_pv__user_id=current_user.id))

	else:

		Cajero_filter = Cajero.objects.filter(id_pos_pc__id_pv__user_id=current_user.id)
	

	return TemplateResponse(request, template_name, {'obj':Cajero_filter})		

class CajeroUpdate(LoginRequiredMixin,UpdateView):
	model = Cajero
	form_class = CajeroForm
	template_name = "cajeros_edit.html"
	success_url = reverse_lazy('core:cajerosall')
	context_object_name = "obj"
	

	def form_valid(self, form):
		form.instance.user = self.request.user.id
		return super().form_valid(form)

class CajeroDelete(LoginRequiredMixin,DeleteView):
	model = Cajero
	context_object_name = "obj"
	form_class = CajeroForm
	template_name = "cajeros_delete.html"
	success_url = reverse_lazy('core:cajerosall')
	login_url='/login'

	def form_valid(self, form):
		form.instance.user = self.request.user.id
		return super().form_valid(form)

def cajero_inactivar(request, id_cajero):
	template_name = 'cajeros_delete.html'
	contexto = {}
	cajero = Cajero.objects.filter(pk=id_cajero).first()

	if not cajero:
		return HttpResponse('Cajero no encontrado' + str(id_cajero))

	if request.method=='GET':
		contexto={'obj':cajero}

	if request.method=='POST':
		cajero.estado_cajero="inactivo"
		cajero.save()
		contexto={'obj':'OK'}
		return HttpResponse('Cajero inactivado')

	return render(request,template_name,contexto)

# class PuntoventaViews(LoginRequiredMixin,ListView):

# 	Model:PuntoVenta
# 	template_name="Allpv.html"
# 	context_object_name="obj"
# 	#queryset = PuntoVenta.objects.all()
# 	login_url='/login'

# 	def get_queryset(self, *args, **kwargs):
# 		if User.is_superuser:

# 			return PuntoVenta.objects.all()
# 		else:


# 			return PuntoVenta.objects.filter(user=self.request.user)

@login_required
def PuntoventaViews(request):

	current_user = request.user
	template_name = "Allpv.html"
	queryset = []
	if current_user.is_staff:
		puntoventa_filter=PuntoVenta.objects.all()
	
	elif current_user.is_superuser:
		users = User.objects.filter(groups__id=current_user.id)
		user_ids = users.values('id')

		puntoventa_filter = PuntoVenta.objects.filter(Q(user_id__in=user_ids) | Q(user_id=current_user.id))

	else:

		puntoventa_filter = PuntoVenta.objects.filter(user_id=current_user.id)
	

	return TemplateResponse(request, template_name, {'obj':puntoventa_filter})

class PuntoVentaCreate(LoginRequiredMixin,CreateView):
	model = PuntoVenta
	form_class = PuntoVentaForm
	template_name = "puntoventa.html"
	success_url = reverse_lazy('core:allpv')

class PuntoVentaUpdate(LoginRequiredMixin,UpdateView):
	model = PuntoVenta
	form_class = PuntoVentaForm
	template_name = "puntoventa_edit.html"
	success_url = reverse_lazy('core:allpv')
	context_object_name = "obj"
	

	"""def form_valid(self, form):
		form.instance.user = self.request.user.id
		return super().form_valid(form)"""

def puntoventa_inactivar(request, id_pv):
	template_name = 'puntoventa_delete.html'
	contexto = {}
	puntoventa = PuntoVenta.objects.filter(pk=id_pv).first()

	if not puntoventa:
		return HttpResponse('Punto de Venta no encontrado' + str(id_pv))

	if request.method=='GET':
		contexto={'obj':puntoventa}

	if request.method=='POST':
		puntoventa.estado_pv=False
		puntoventa.save()
		contexto={'obj':'OK'}
		return HttpResponse('Punto de Venta inactivado')

	return render(request,template_name,contexto)

#class TermnalesViews(LoginRequiredMixin,ListView):
#	Model:PosPc
#	template_name="terminalesall.html"
#	context_object_name="obj"
	#queryset = PosPc.objects.all()
#	login_url='/login'

#	def get_queryset(self, *args, **kwargs):


#		if User.is_superuser:
#			return PosPc.objects.all()

#		else:

#			return PosPc.objects.filter(id_pv__user=self.request.user)
@login_required
def terminalesViews(request):

	current_user = request.user
	template_name = "terminalesall.html"
	queryset = []
	
	
	if current_user.is_staff:
		terminales_filter=PosPc.objects.all()
		
	
	elif current_user.is_superuser:
		users = User.objects.filter(groups__id=current_user.id)
		user_ids = users.values('id')

		terminales_filter = PosPc.objects.filter(Q(id_pv__user_id__in=user_ids) | Q(id_pv__user_id=current_user.id))

	else:

		terminales_filter = PosPc.objects.filter(id_pv__user_id=current_user.id)
	

	return TemplateResponse(request, template_name, {'obj':terminales_filter})

class TerminalCreate(LoginRequiredMixin,CreateView):
	model = PosPc
	form_class = TerminalForm
	template_name = "terminal_create.html"
	success_url = reverse_lazy('core:terminalesall')

class TerminalUpdate(LoginRequiredMixin,UpdateView):
	model = PosPc
	form_class = TerminalForm
	template_name = "terminal_edit.html"
	success_url = reverse_lazy('core:terminalesall')
	context_object_name = "obj"
	

	"""def form_valid(self, form):
		form.instance.user = self.request.user.id
		return super().form_valid(form)"""

def terminal_inactivar(request, id_pos_pc):
	template_name = 'terminal_delete.html'
	contexto = {}
	terminal = PosPc.objects.filter(pk=id_pos_pc).first()

	if not terminal:
		return HttpResponse('Terminal no encontrado' + str(id_pv))

	if request.method=='GET':
		contexto={'obj':terminal}

	if request.method=='POST':
		terminal.estado_pos_pc=False
		terminal.save()
		contexto={'obj':'OK'}
		return HttpResponse('Terminal inactivado')

	return render(request,template_name,contexto)

class JackpotKenoView(LoginRequiredMixin,ListView):
	model=JackpotKeno
	template_name="jackpot.html"
	context_object_name="obj"
	queryset = JackpotKeno.objects.all()
	login_url='/login'
	

	
class JackpotKenoUpdate(LoginRequiredMixin,UpdateView):
	model = JackpotKeno
	form_class = JackpotKenoForm
	template_name = "jackpot_keno_editar.html"
	success_url = reverse_lazy('core:jackpotkeno')
	context_object_name = "obj"

class JackpotBingoView(LoginRequiredMixin,ListView):
	model=JackpotBingo
	template_name="jackpot_bingo.html"
	context_object_name="obj"
	queryset = JackpotBingo.objects.all()
	login_url='/login'
	

	
class JackpotBingoUpdate(LoginRequiredMixin,UpdateView):
	model = JackpotBingo
	form_class = JackpotBingoForm
	template_name = "jackpot_bingo_editar.html"
	success_url = reverse_lazy('core:jackpotbingo')
	context_object_name = "obj"


class UsuarioView(LoginRequiredMixin,ListView):
	model = User
	template_name="usuarios_list.html"
	context_object_name="obj"
	queryset = User.objects.all()
	login_url='/login'

class UsuarioCreate(LoginRequiredMixin,CreateView):
	model = User
	form_class = UsuarioForm
	template_name = "Usuario_create.html"
	success_url = reverse_lazy('core:usuariosall')

class UsuarioUpdate(LoginRequiredMixin,UpdateView):
	model = User
	form_class = UsuarioForm
	template_name = "usuario_edit.html"
	success_url = reverse_lazy('core:usuariosall')
	context_object_name = "obj"

def usuario_inactivar(request, id):
	template_name = 'usuarios_delete.html'
	contexto = {}
	user = User.objects.filter(pk=id).first()

	if not user:
		return HttpResponse('Usuario no encontrado' + str(id))

	if request.method=='GET':
		contexto={'obj':user}

	if request.method=='POST':
		user.is_active=0
		user.save()
		contexto={'obj':'OK'}
		return HttpResponse('Usuario inactivado')

	return render(request,template_name,contexto)
	
class ConsultaGanador(LoginRequiredMixin,TemplateView):
	model = GanadoresKeno
	template_name="usuario_ganador.html"
	context_object_name="obj"
	#queryset = PosPc.objects.all()
	login_url='/login'
	
class GrupoView(LoginRequiredMixin,ListView):
	model= Group
	template_name="grupos_list.html"
	context_object_name="obj"
	queryset = Group.objects.all()
	login_url='/login'

class GrupoCreate(LoginRequiredMixin,CreateView):
	model = Group
	form_class = GrupoForm
	template_name = "grupo_create.html"
	success_url = reverse_lazy('core:gruposall')

