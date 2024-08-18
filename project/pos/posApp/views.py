from pickle import FALSE
from django.shortcuts import redirect, render
from django.http import HttpResponse
from flask import jsonify
from posApp.models import Category, Products, Sales, salesItems ,Bills,Material, ProductMaterial
from django.db.models import Count, Sum
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
import json, sys
from django.http import HttpResponseNotAllowed
from datetime import date, datetime

# Login
def login_user(request):
    logout(request)
    resp = {"status":'failed','msg':''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status']='success'
            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp),content_type='application/json')

#Logout
def logoutuser(request):
    logout(request)
    return redirect('/')

# Create your views here.
@login_required
def home(request):
    now = datetime.now()
    current_year = now.strftime("%Y")
    current_month = now.strftime("%m")
    current_day = now.strftime("%d")
    categories = len(Category.objects.all())
    products = len(Products.objects.all())
    saled = Sales.objects.filter(
        date_added__year=current_year,
        date_added__month = current_month,
        date_added__day = current_day
    )
    material =  Material.objects.filter(
        date_added__year=current_year,
        date_added__month = current_month,
        date_added__day = current_day
    )
    total_cost = sum([x.cost*x.added_stock for x in material])

    from django.db.models import Count

    sales_items_count = salesItems.objects.values('product_id').annotate(total_sales=Count('product_id')).order_by('-total_sales')
    sales_items_count = [(Products.objects.get(id = x['product_id']),x['total_sales']) for x in sales_items_count[0:3]]
    

    try :
        transaction = len([x for x in saled if Bills.objects.get(sale_id = x.id).checkout])
        today_sales = [x.grand_total for x in Sales.objects.filter(
            date_added__year=current_year,
            date_added__month = current_month,
            date_added__day = current_day
        ) if Bills.objects.get(sale_id = x.id).checkout ]
        total_sales = sum(today_sales)
    except :
        print("none")
        transaction = 0
        today_sales = 0
        total_sales = 0
    context = {
        'page_title':'Home',
        'categories' : categories,
        'products' : products,
        'transaction' : transaction,
        'total_sales' : total_sales,
        'total_cost' : total_cost ,
        'benefit' : total_sales - total_cost,
        'hots' : sales_items_count
    }
    return render(request, 'posApp/home.html',context)


def about(request):
    context = {
        'page_title':'About',
    }
    return render(request, 'posApp/about.html',context)

#Categories
@login_required
def category(request):
    category_list = Category.objects.all()
    # category_list = {}
    context = {
        'page_title':'Category List',
        'category':category_list,
    }
    return render(request, 'posApp/category.html',context)
@login_required
def manage_category(request):
    category = {}
    if request.method == 'GET':
        data =  request.GET
        id = ''
        if 'id' in data:
            id= data['id']
        if id.isnumeric() and int(id) > 0:
            category = Category.objects.filter(id=id).first()
    
    context = {
        'category' : category
    }
    return render(request, 'posApp/manage_category.html',context)

@login_required
def save_category(request):
    data =  request.POST
    resp = {'status':'failed'}
    try:
        if (data['id']).isnumeric() and int(data['id']) > 0 :
            save_category = Category.objects.filter(id = data['id']).update(name=data['name'], description = data['description'],status = data['status'])
        else:
            save_category = Category(name=data['name'], description = data['description'],status = data['status'])
            save_category.save()
        resp['status'] = 'success'
        messages.success(request, 'Category Successfully saved.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def delete_category(request):
    data =  request.POST
    resp = {'status':''}
    try:
        Category.objects.filter(id = data['id']).delete()
        resp['status'] = 'success'
        messages.success(request, 'Category Successfully deleted.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

# Products
@login_required
def products(request):
    product_list = Products.objects.all()
    context = {
        'page_title':'Product List',
        'products':product_list,
    }
    return render(request, 'posApp/products.html',context)
@login_required
def manage_products(request):
    product = {}
    categories = Category.objects.filter(status = 1).all()
    if request.method == 'GET':
        data =  request.GET
        id = ''
        if 'id' in data:
            id= data['id']
        if id.isnumeric() and int(id) > 0:
            product = Products.objects.filter(id=id).first()
    
    context = {
        'product' : product,
        'categories' : categories
    }
    return render(request, 'posApp/manage_product.html',context)

def test(request):
    categories = Category.objects.all()
    context = {
        'categories' : categories
    }
    return render(request, 'posApp/test.html',context)

@login_required
def save_product(request):
    data =  request.POST
    resp = {'status':'failed'}
    id= ''
    if 'id' in data:
        id = data['id']
    if id.isnumeric() and int(id) > 0:
        check = Products.objects.exclude(id=id).filter(code=data['code']).all()
    else:
        check = Products.objects.filter(code=data['code']).all()
    if len(check) > 0 :
        resp['msg'] = "Product Code Already Exists in the database"
    else:
        category = Category.objects.filter(id = data['category_id']).first()
        try:
            if (data['id']).isnumeric() and int(data['id']) > 0 :
                save_product = Products.objects.filter(id = data['id']).update(code=data['code'], category_id=category, name=data['name'], description = data['description'], price = float(data['price']),status = data['status'])
            else:
                save_product = Products(code=data['code'], category_id=category, name=data['name'], description = data['description'], price = float(data['price']),status = data['status'])
                save_product.save()
            resp['status'] = 'success'
            messages.success(request, 'Product Successfully saved.')
        except:
            resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def delete_product(request):
    data =  request.POST
    resp = {'status':''}
    try:
        Products.objects.filter(id = data['id']).delete()
        resp['status'] = 'success'
        messages.success(request, 'Product Successfully deleted.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def pos(request):
    products = Products.objects.filter(status = 1)
    product_json = []
    for product in products:
        product_json.append({'id':product.id, 'name':product.name, 'price':float(product.price)})
    context = {
        'page_title' : "Point of Sale",
        'products' : products,
        'product_json' : json.dumps(product_json)
    }
    # return HttpResponse('')
    return render(request, 'posApp/pos.html',context)

@login_required
def checkout_modal(request):
    grand_total = 0
    if 'grand_total' in request.GET:
        grand_total = request.GET['grand_total']
    context = {
        'grand_total' : grand_total,
    }
    return render(request, 'posApp/checkout.html',context)

@login_required
def save_pos(request):
    # resp = {'status':'failed','msg':''}
    # data = request.POST
    # pref = datetime.now().year + datetime.now().year
    # i = 1
    # while True:
    #     code = '{:0>5}'.format(i)
    #     i += int(1)
    #     check = Sales.objects.filter(code = str(pref) + str(code)).all()
    #     if len(check) <= 0:
    #         break
    # code = str(pref) + str(code)

    # try:
    #     sales = Sales(code=code, sub_total = data['sub_total'], tax = data['tax'], tax_amount = data['tax_amount'], grand_total = data['grand_total'], tendered_amount = data['tendered_amount'], amount_change = data['amount_change']).save()
    #     sale_id = Sales.objects.last().pk
    #     i = 0
    #     for prod in data.getlist('product_id[]'):
    #         product_id = prod 
    #         sale = Sales.objects.filter(id=sale_id).first()
    #         product = Products.objects.filter(id=product_id).first()
    #         qty = data.getlist('qty[]')[i] 
    #         price = data.getlist('price[]')[i] 
    #         total = float(qty) * float(price)
    #         print({'sale_id' : sale, 'product_id' : product, 'qty' : qty, 'price' : price, 'total' : total})
    #         salesItems(sale_id = sale, product_id = product, qty = qty, price = price, total = total).save()
    #         i += int(1)
    #     resp['status'] = 'success'
    #     resp['sale_id'] = sale_id
    #     messages.success(request, "Sale Record has been saved.")
    # except:
    #     resp['msg'] = "An error occured"
    #     print("Unexpected error:", sys.exc_info()[0])
    return HttpResponse(json.dumps(resp),content_type="application/json")

@login_required
def salesList(request):
    bill = Bills.objeact.all()
    sales = Sales.objects.all()
    sale_data = []
    for sale in bill:
        data = {}
        for field in sale._meta.get_fields(include_parents=False):
            if field.related_model is None:
                data[field.name] = getattr(sale,field.name)
        data['items'] = salesItems.objects.filter(sale_id = sale).all()
        data['item_count'] = len(data['items'])
        if 'tax_amount' in data:
            data['tax_amount'] = format(float(data['tax_amount']),'.2f')
        # print(data)
        sale_data.append(data)
    # print(sale_data)
    context = {
        'page_title':'Sales Transactions',
        'sale_data':sale_data,
    }
    # return HttpResponse('')
    return render(request, 'posApp/sales.html',context)

@login_required
def receipt(request):
    id = request.GET.get('id')
    sales = Sales.objects.filter(id = id).first()
    transaction = {}
    for field in Sales._meta.get_fields():
        if field.related_model is None:
            transaction[field.name] = getattr(sales,field.name)
    if 'tax_amount' in transaction:
        transaction['tax_amount'] = format(float(transaction['tax_amount']))
    ItemList = salesItems.objects.filter(sale_id = sales).all()
    context = {
        "transaction" : transaction,
        "salesItems" : ItemList
    }

    return render(request, 'posApp/receipt.html',context)
    # return HttpResponse('')

@login_required
def delete_sale(request):
    resp = {'status':'failed', 'msg':''}
    id = request.POST.get('id')
    try:
        delete = Sales.objects.filter(id = id).delete()
        resp['status'] = 'success'
        messages.success(request, 'Sale Record has been deleted.')
    except:
        resp['msg'] = "An error occured"
        print("Unexpected error:", sys.exc_info()[0])
    return HttpResponse(json.dumps(resp), content_type='application/json')

@login_required
def employees(request):
    return HttpResponse('')

@login_required
def bill(request):
    b = Bills.objects.filter(checkout = False).order_by('-date')
    [x.save() for x in b]
    context = {
        'bills':b
    }
    return render(request, 'posApp/bill.html',context= context)

@login_required
def createbill(request):
    resp = {'status':'failed', 'msg':''}
    print(len(Sales.objects.all()))
    i = 0
    for x in Sales.objects.all():
        i = i+1
    sale = Sales.objects.create(code = 'S'+str(datetime.now().year)+str(i+1))
    sale.save()
    bill = Bills()   
    bill.sale_id = sale
    bill.user = request.user
    bill.save() 
    resp['status'] = 'success'
    return HttpResponse(json.dumps(resp), content_type='application/json')

@login_required
def delete_bill(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    data =  request.POST
    resp = {'status':''}
    bill = Bills.objects.get(id = data['id'])
    sale = bill.sale_id
    try:
        sale.delete()
        resp['status'] = 'success'
        messages.success(request, 'Bill Successfully deleted.')
    except Exception as e: 
        print(e)
        resp['status'] = 'failed'
        print(resp)
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def manage_bill(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    id = request.POST.get('id')
    #print(id)
    context = {
        'bill_id':id,
        'orders':salesItems.objects.filter(sale_id = id),
        'products':Products.objects.filter(status = 1),
        'bill':Bills.objects.get(id = id)
    }
    return render(request,'posApp/manage_bill.html',context)

@login_required
def manage_bill_addProduct(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    id = request.POST.get('id')
    context = {
            'bill_id':id,
            'orders':salesItems.objects.filter(sale_id = id),
            'products':Products.objects.filter(status = 1)
        }
    
    if request.POST.get('product_id') != None:
            product = Products.objects.get(id= request.POST.get('product_id'))
            Matlist = ProductMaterial.objects.filter(product = product)
            qty = int(request.POST.get('product_qty'))
            sale = Sales.objects.get(id = Bills.objects.get(id = id).sale_id.id)
            price = product.price
            total = price*int(qty)
            Matlist = ProductMaterial.objects.filter(product = product)
            #check part
            valid = False
            for mat in Matlist:
                print(mat.quantity*qty,mat.material.name,mat.material.stock)
                if mat.material.stock -  mat.quantity*qty >= 0:
                    valid = True
                else:
                    print("invalid!!!!!!!!")
                    valid = False
                    break
            if valid or len(mat) == 0 :
                #save part
                for mat in Matlist:
                    mat.material.stock =  mat.material.stock - mat.quantity*qty
                    mat.material.save()
                    print(mat.material.stock)
                if  len(salesItems.objects.filter(sale_id = sale,product_id = product)) > 0:
                    addprod = salesItems.objects.get(sale_id = sale,product_id = product)
                    addprod.qty += int(qty)
                    addprod.total += total
                    addprod.save()
                else:
                    salesItems(sale_id = sale, product_id = product, qty = qty, price = price, total = total).save()
            return render(request,'posApp/manage_bill.html',context)
        
    return render(request,'posApp/manage_bill.html',context)

@login_required
def manage_bill_deleteProduct(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    id = request.POST.get('id')
    item_id = request.POST.get('item_id')
    si = salesItems.objects.get(id = item_id)
    pm = ProductMaterial.objects.filter(product = si.product_id)
    for i in pm:
        i.material.stock +=  i.quantity*si.qty
        i.material.save()
    si.delete()
    context = {
            'bill_id':id,
            'orders':salesItems.objects.filter(sale_id = id),
            'products':Products.objects.filter(status = 1)
        }
    return render(request,'posApp/manage_bill.html',context)

@login_required
def manage_bill_checkout(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    id = request.POST.get('id')
    print(id,'-----------------------------')
    bill = Bills.objects.get(id = id)
    bill.checkout = True
    bill.save()
    sales = Sales.objects.get(id = bill.sale_id.id)
    transaction = {}
    for field in Sales._meta.get_fields():
        if field.related_model is None:
            transaction[field.name] = getattr(sales,field.name)
    if 'tax_amount' in transaction:
        transaction['tax_amount'] = format(float(transaction['tax_amount']))
    new_sub_total = salesItems.objects.filter(sale_id = sales.id).aggregate(Sum('total'))['total__sum']
    if new_sub_total != None:
        sales.sub_total =  new_sub_total
        sales.grand_total = new_sub_total
        sales.save()
    ItemList = salesItems.objects.filter(sale_id = sales).all()
    context = {
        "transaction" : sales,
        "salesItems" : ItemList
    }
    print(context)
    print(sales.sub_total)
    return render(request, 'posApp/precheckout.html',context)


@login_required
def material(request):
    material = Material.objects.all()
    product = Products.objects.all()
    context = {
        'materials':material,
        'products':product
    }
    return render(request,'posApp/materials.html',context)

@login_required
def manage_material(request):
    id = request.GET.get('id')
    if id != None:
        context = {
            'material':Material.objects.get(id = id)
        }
        return render(request,'posApp/manage_material.html',context)
    return render(request,'posApp/manage_material.html')

@login_required
def save_material(request):
    data = request.POST
    print(data)
    if data['id'] == '':
        print(dict(data))
        Material.objects.create(name = data['name'],description = data['description'],supplier = data['supplier'],cost = data['cost'],status = data['status'],stock = data['stock'],added_stock = data['stock'])
    else:
        mat = Material.objects.get(id = data['id'])
        mat.name = data['name']
        mat.description = data['description']
        mat.supplier = data['supplier']
        mat.cost = data['cost']
        mat.status = data['status']
        mat.stock = data['stock']
        mat.added_stock = data['stock']
        mat.save()
    material = Material.objects.all()
    product = Products.objects.all()
    context = {
        'materials':material,
        'products':product
    }
    return render(request,'posApp/materials.html',context)

@login_required
def delete_material(request):
    data =  request.POST
    resp = {'status':''}
    try:
        Material.objects.get(id = data['id']).delete()
        resp['status'] = 'success'
        messages.success(request, 'Product Successfully deleted.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def manage_product_material(request):
    id  = request.GET.get('id')
    material = Material.objects.get(id = id)
    PM = ProductMaterial.objects.filter(material = material)
    product = Products.objects.all()
    context = {
        'id':id,
        'products':product,
        'PM':PM,
        'material':material
    }
    return render(request,'posApp/manage_product_material.html',context)

@login_required
def link_product_material(request):
    id = request.POST.get('id')
    material = Material.objects.get(id = id)
    if request.POST.get('product_id') != None:
        product = Products.objects.get(id = request.POST.get('product_id'))
        pm = ProductMaterial.objects.create(product = product,material = material,quantity = request.POST.get('material_qty'))
        pm.save()
    context = {
        'id':id,
        'products':Products.objects.all(),
        'PM':ProductMaterial.objects.filter(material = material),
        'material':Material.objects.get(id = id)
    }
    return render(request,'posApp/manage_product_material.html',context)

def unlink_product_material(request):
    id = request.POST.get('id')
    pm = ProductMaterial.objects.filter(id = request.POST.get('pm_id')).delete()
    material = Material.objects.get(id = id)
    #print(ProductMaterial.objects.get(id = int(request.POST.get('pm_id'))))
    #pm.save()

    # 

    context = {
        'id':id,
        'products':Products.objects.all(),
        'PM':ProductMaterial.objects.filter(material = material),
        'material':Material.objects.get(id = id)
    }
    return render(request,'posApp/manage_product_material.html',context)

@login_required
def paidList(request):
    b = [x.sale_id for x in Bills.objects.filter(checkout = True)]
    countitem = [len(salesItems.objects.filter(sale_id = x)) for x in b]
    x  = list(zip(b,countitem))
    context = {
        'sales':(x)
    }
    print(x)
    return render(request, 'posApp/paidlist.html',context= context)

@login_required
def review_bill_checkout(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    id = request.POST.get('id')
    print(id,'-----------------------------')
    bill = Bills.objects.get(id = id)
    bill.checkout = True
    bill.save()
    sales = Sales.objects.get(id = bill.sale_id.id)
    transaction = {}
    for field in Sales._meta.get_fields():
        if field.related_model is None:
            transaction[field.name] = getattr(sales,field.name)
    if 'tax_amount' in transaction:
        transaction['tax_amount'] = format(float(transaction['tax_amount']))
    new_sub_total = salesItems.objects.filter(sale_id = sales.id).aggregate(Sum('total'))['total__sum']
    if new_sub_total != None:
        sales.sub_total =  new_sub_total
        sales.grand_total = new_sub_total
        sales.save()
    ItemList = salesItems.objects.filter(sale_id = sales).all()
    context = {
        "transaction" : sales,
        "salesItems" : ItemList
    }
    print(context)
    print(sales.sub_total)
    return render(request, 'posApp/reviewcheckout.html',context)


@login_required 
def editbill(request):
    id = request.POST['id']
    table = request.POST['table']
    print(table)
    bill = Bills.objects.get(id =  id)
    bill.sale_id.tablename = table
    bill.sale_id.save()
    context = {
        'bill_id':id,
        'orders':salesItems.objects.filter(sale_id = id),
        'products':Products.objects.filter(status = 1)
    }
    return render(request,'posApp/manage_bill.html',context)