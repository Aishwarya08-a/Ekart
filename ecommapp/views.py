from django.shortcuts import render, HttpResponse, redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from ecommapp.models import Product, Cart, Order
from django.db.models import Q
import random
import razorpay

# Create your views here.
   
def home(request):
    context={}
    p=Product.objects.filter(is_active=True)
    context['products']=p
    print(p)
    #userid=request.user.id
    #print("id of logged in user",userid)
    #print("result",request.user.is_authenticated)
    return render(request,'index.html',context)

def about(request):
    return render(request,'about.html')

def contact(request):
    return render(request,'contact.html')

def place_order(request):
    return render(request,'place_order.html')

def product_detail(request,pid):
    context={}
    context['products']=Product.objects.filter(id=pid)
    return render(request,'product_detail.html',context)

def register(request):
    context={}
    if request.method=="POST":
        fname=request.POST['fname']
        umob=request.POST['umob']
        uname=request.POST['uname']
        upass=request.POST['upass']
        cpass=request.POST['cpass']
        if fname=="" or umob=="" or uname=="" or upass=="" or cpass=="":
            context['Errormsg']="Field cannot be empty"
            return render(request,'register.html',context)
        elif upass!=cpass:
            context['Errormsg']="Passwoard did not match"
            return render(request,'register.html',context)
                       
        else:
            try:
                u=User.objects.create(first_name=fname,last_name=umob,username=uname,email=uname,password=upass)
                u.set_password(upass)
                u.save()
                context['Success']="User added successfully"
                return HttpResponse("User added successfully")
            except Exception:
                context['Errormsg']="Username already exits"
                return render(request,'register.html',context)
                             
    else:
        return render(request,'register.html')
    
def user_login(request):
    context={}
    if request.method=="POST":
        uname=request.POST['uname']
        upass=request.POST['upass']
        print(uname)
        print(upass)
        
        
        if uname=="" or upass=="":
            context['Errormsg']="Field cannot be empty"
            return render(request,'login.html',context)
        
        else:
            u=authenticate(username=uname,password=upass) # is work as select qurey....  when user name password not match is written none 
            if u is not None :
                login(request,u) #login inbuilt fn
                return redirect('/home')
            else:
                context['Errormsg']="Invalid username and password"
                return render(request,'login.html',context)
    else:
        return render(request,'login.html')
    
def user_logout(request):
    logout(request) #logout inbuilt fn
    return redirect("/home")

def catfilter(request,cv):
    q1=Q(is_active=True)
    q2=Q(cat=cv)
    p=Product.objects.filter(q1 & q2)
    print(p)
    context={}
    context['products']=p
    return render(request,'index.html',context)

def sort(request,sv):
    if sv=='0':
        col='price'
    else:
        col='-price'

    p=Product.objects.filter(is_active=True).order_by(col)
    context={}
    context['products']=p
    return render(request,'index.html',context)

def range(request):
    min=request.GET['min']
    max=request.GET['max']
    q1=Q(price__gte=min)
    q2=Q(price__lte=max)
    q3=Q(is_active=True)
    p=Product.objects.filter(q1 & q2 & q3)
    context={}
    context['products']=p
    return render(request,'index.html',context)

def addtocart(request,pid):
    if request.user.is_authenticated:
        userid=request.user.id
        u=User.objects.filter(id=userid)
        print(u[0])
        p=Product.objects.filter(id=pid)
        print(p[0])
        c=Cart.objects.create(uid=u[0], pid=p[0])
        c.save()
        return redirect('/viewcart')
    else:
        return redirect('/user_login')
    
def remove(request,cid):
    c=Cart.objects.filter(id=cid)
    c.delete()
    return redirect('/viewcart')

def viewcart(request):
    userid=request.user.id
    c=Cart.objects.filter(uid=userid)
    s=0
    np=len(c)
    for x in c:
        print(x)
        #print(x.pid.price)
        s=s+x.pid.price*x.qty
        context={}
        context['products']=c
        context['n']=np
        context['total']=s
    return render(request,'cart.html',context)

def updateqty(request,qv,cid):
    #print(type(qv))
    c=Cart.objects.filter(id=cid)
    # print(c)
    # print(c[0])
    # print(c[0].qty)
    if qv=='1':
        t=c[0].qty+1
        c.update(qty=t)
    else:
        if c[0].qty>1:
            t=c[0].qty-1
            c.update(qty=t)
    return redirect('/viewcart')

def placeorder(request):
    userid=request.user.id
    
    c=Cart.objects.filter(uid=userid)
    oid=random.randrange(1000,9999)
    print("Order_id=",oid)
    for x in c:
        o=Order.objects.create(order_id=oid,pid=x.pid,uid=x.uid,qty=x.qty)
        o.save()
        x.delete()
    orders=Order.objects.filter(uid=request.user.id)
    s=0
    np=len(orders)
    for x in orders:
        print(x)
        #print(x.pid.price)
        s=s+x.pid.price*x.qty
        context={}
        context['products']=orders
        context['n']=np
        context['total']=s
    return render(request,'place_order.html',context)

def makepayment(request):
    orders=Order.objects.filter(uid=request.user.id)
    s=0
    for x in orders:
        print(x)
        s=s+x.pid.price*x.qty
        oid=x.order_id
    client = razorpay.Client(auth=("rzp_test_9qscTv5XlXqAd7", "5tqFdxgriGTSmwziDRpqWmee"))
    data = { "amount": s*100, "currency": "INR", "receipt": oid }
    payment = client.order.create(data=data)
    print(payment)

    # Delete orders
    orders.delete()

    context={}
    context['data']=payment
    return render(request,'pay.html',context)





def hello(request):
    context={}
    context['name']='itvedant'
    context['ct']='pune'
    context['x']=40
    context['y']=70
    context['list']=[10,20,30,40,50]
    context['product']=[ {'id': 1,'name': 'samsung', 'cat': 'mobile', 'price':70000},
                         {'id': 2,'name': 'jeans', 'cat': 'clothes', 'price':4000},
                         {'id': 3,'name': 'adidas', 'cat': 'shoes', 'price':3000},
                         {'id': 4,'name': 'vivo', 'cat': 'mobile', 'price':20000} ]
    return render(request,'hello.html',context)