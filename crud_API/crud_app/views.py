'''
Import needed libraries
'''
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime 
import json
import re
from .serializers import EmployeeSerializer
from .models import Employee


@api_view(["GET"])
def welcome(request):
    ''' Construct welcome message '''
    content = {"welcome_msg": "Welcome to the CRUD App, please specify params"}
    return JsonResponse(content)

def build_page_url(request, number):
    ''' Construct a new url given page number '''
    items = request.GET.items()
    url   = request.build_absolute_uri()
    
    reg_page = r'page=\d+'
    replacment   = f'page={number}'
    res = re.findall(reg_page, url)
    if len(list(items)) == 0:
        url += '?'
    if len(res) > 0:
        url = re.sub(reg_page,replacment,url)
    else:
        print(url)
        url += replacment
    
    return url

    
@api_view(["GET"])
def get_employees(request):
    ''' Get requested employee records '''
    employees = Employee.objects
    
    fname_filter = request.GET.get('fname_contains', None)
    start_date   = request.GET.get('start_date', None)
    end_date     = request.GET.get('end_date', None)
    page_number  = request.GET.get('page', 1)
    email_domain = request.GET.get('domain_name', None)
    
    # chaining filters
    if fname_filter != None:
        employees = Employee.objects.filter(first_name__contains=fname_filter)
    if start_date != None:
        employees = employees.filter(join_date__date__gte=start_date)
    if end_date != None:
        employees = employees.filter(join_date__date__lte=end_date)
    if email_domain != None:
        employees = employees.filter(email__endswith=f'@{email_domain}')
    
    ## pagination    
    paginator = Paginator(employees.all(), 3, allow_empty_first_page=False)
    page_obj = paginator.get_page(page_number)
    
    # build meta data regarding pagination
    pg_meta = {}
    pg_meta['output_count']    = paginator.count
    pg_meta['number_of_pages'] = paginator.num_pages
    pg_meta['next_page']       = "No Next Page"
    pg_meta['prev_page']       = "No Previous Page"
    
    # Construing url for next and previous pages
    if page_obj.has_next():
        pg_meta['next_page'] = build_page_url(request, page_obj.next_page_number())
    if page_obj.has_previous():
        pg_meta['prev_page'] = build_page_url(request, page_obj.previous_page_number())
    
    
    serializer = EmployeeSerializer(page_obj, many=True)
    return JsonResponse({'employees': serializer.data, 
                         'pagination':pg_meta},
                        safe=False, status=status.HTTP_200_OK)


@api_view(["POST"])
def add_employee(request):
    ''' Adding employee to DB '''
    payload = json.loads(request.body)
    try:
        employee = Employee.objects.create(
            first_name = payload["first_name"],
            last_name = payload["last_name"],
            phone_number = payload["phone_number"],
            email = payload["email"],
            join_date = payload["join_date"],
        )
        serializer = EmployeeSerializer(employee)
        return JsonResponse({'employees': serializer.data}, safe=False, status=status.HTTP_201_CREATED)
    except ObjectDoesNotExist as e:
        return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
    except Exception:
        return JsonResponse({'error': 'check response header'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(["PUT"])
def update_employee(request, employee_id):
    ''' Updating required employee '''
    payload = json.loads(request.body)
    try:
        employee_item = Employee.objects.filter(id=employee_id)
        employee_item.update(**payload)
        employee = Employee.objects.get(id=employee_id)
        serializer = EmployeeSerializer(employee)
        return JsonResponse({'employees': serializer.data}, safe=False, status=status.HTTP_200_OK)
    except ObjectDoesNotExist as e:
        return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
    except Exception:
        return JsonResponse({'error': 'check response header'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(["DELETE"])
def delete_employee(request, employee_id):
    ''' Delete required employee '''
    try:
        employee = Employee.objects.get(id=employee_id)
        employee.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except ObjectDoesNotExist as e:
        return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
    except Exception:
        return JsonResponse({'error': 'check response header'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)