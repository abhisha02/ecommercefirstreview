from django.shortcuts import render
from .forms import RegistrationForm,MessageHandler
from django.shortcuts import redirect
from .models import Account
from django.contrib import messages,auth
from .models import Profile
import random
from django.http import HttpResponse
import secrets
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control, never_cache
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import User, Permission, Group
from django.shortcuts import get_object_or_404
from category.models import Category
from category.forms import CategoryForm
from store.models import Product,ProductImage,Variation
from store.forms import ProductForm,AdditionalImageForm,VariantForm
from django.forms import formset_factory





# Create your views here.
#user registration
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def register(request):
  if 'key2' in request.session:
        del request.session['key2']
        return redirect('home')

  if request.method=='POST':
    form=RegistrationForm(request.POST)
    if form.is_valid():
      first_name=form.cleaned_data['first_name']
      last_name=form.cleaned_data['last_name']
      phone_number=form.cleaned_data['phone_number']
      email=form.cleaned_data['email']
      password=form.cleaned_data['password']


    
      user=Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,password=password,phone_number=phone_number)
     
      user.save()
      
      #user activation
      otp = ''.join(secrets.choice('0123456789') for _ in range(4))
      profile=Profile.objects.create(user=user,otp=f'{otp}')
      profile.save()
      user_details = {
            'uid':profile.uid,
            'phone_number':profile.user.phone_number,
            
        }
      request.session['user_details'] = user_details
      request.session['key2']=2
      messagehandler=MessageHandler(request.POST['phone_number'],otp).send_otp_via_message()
      red=redirect(f'otp/{profile.uid}/')
      red.set_cookie("can_otp_enter",True,max_age=60)
      return red  

      messages.success(request,'Registration Sucessful')
      return redirect('register')

  else:
    form=RegistrationForm
  context={
    'form':form
    }
  return render(request,'accounts/register.html',context)

#user login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def login(request):
  if 'key1' in request.session:
      
      profile = request.session.get('profile')
      products=Product.objects.all().filter(is_available=True)
      context = {'profile': profile,'products':products}
      return render(request,'home.html',{'products': products, 'profile': profile}) 
  
  
  
  if request.method == 'POST':
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        # Check if a profile with the given phone number exists
        user=Account.objects.filter(email=email).first()
        if not user:
            messages.error(request, "User does not exist.")
            return redirect('login')
        if not user.is_active:
            messages.error(request, "Your account has been temporarily blocked. Please contact support for further assistance.")
            return redirect('login')
        profile=Profile.objects.get(user=user)
        otp = ''.join(secrets.choice('0123456789') for _ in range(4))
        profile.otp=f'{otp}'
        profile.save()
        
        
        user_details = {
            'uid':profile.uid,
            'phone_number':profile.user.phone_number,
            
           }
        
        request.session['user_details'] = user_details
        request.session['key5']=5
        
        messagehandler = MessageHandler(profile.user.phone_number, otp).send_otp_via_message()
        red = redirect(f'otp_login/{profile.uid}/')
        red.set_cookie("can_otp_enter",True,max_age=60)
        return red
        
        
  return render(request, 'accounts/login.html')
#login_otp_verify
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def otpVerify_login(request,uid):
    if 'key1' in request.session:
      
      profile = request.session.get('profile')
      products=Product.objects.all().filter(is_available=True)
      context = {'profile': profile,'products':products}
      return render(request,'home.html',{'products': products, 'profile': profile}) 
    
    if request.method == "POST":
        otp = request.POST.get('otp')
        try:
            profile = Profile.objects.filter(uid=uid).first()
        except Profile.DoesNotExist:
            return HttpResponse("Profile not found", status=404)
        
        if request.COOKIES.get('can_otp_enter')!=None:  
            if otp == profile.otp:
                if profile.user is not None:
                   auth.login(request, profile.user)
                   
                
                   profile.user.session = {'profile.user.id': profile.user.id}
                   profile.user.save()
                   profile={
                       'id':profile.id,
                       'first_name':profile.user.first_name
                   }
                   products=Product.objects.all().filter(is_available=True)
                   context = {'profile': profile,'products':products}
                   request.session['profile']=profile
                   request.session['key1']=1
                   
                   return render(request,'home.html',{'products': products, 'profile': profile})
                return redirect('login')
            else:
             messages.error(request, 'You have entered wrong OTP.Try again')
             return redirect(request.path)
        messages.error(request,'60 seconds over.Try again')
        return redirect(request.path)
    return render(request, "accounts/otp_login.html", {'uid': uid})
#login_otp_resend
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def resend_otp_login(request):
 
 if 'resend_otp' in request.POST:
    user_details = request.session.get('user_details')
   
    if user_details:
        # Access user details from the session
             uid = user_details['uid']
             phone_number = user_details['phone_number']
          
             otp = ''.join(secrets.choice('0123456789') for _ in range(4))
             profile = Profile.objects.filter(uid=uid).first()
             profile.otp=otp
             profile.save()
             messagehandler=MessageHandler(profile.user.phone_number,otp).send_otp_via_message()
             red=redirect(f'login/otp_login/{profile.uid}/')
             red.set_cookie("can_otp_enter",True,max_age=60)
             messages.success(request, 'OTP has been resent')
             return red 
    return render(request, 'login.html')
 return render(request, 'accounts/login.html')  






def home1(request):
    if request.COOKIES.get('verified') and request.COOKIES.get('verified')!=None:
        messages.success(request, 'This is a success message.')
        return redirect("register")
    else:
        messages.error(request, 'This is an error message.')
        return redirect("register")


#user registration_otp_verify
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def otpVerify(request,uid):
    if'key3' in request.session:
        return redirect('register')
    if request.method == "POST":
        otp = request.POST.get('otp')
        try:
            profile = Profile.objects.filter(uid=uid).first()
        except Profile.DoesNotExist:
            return HttpResponse("Profile not found", status=404)
        if request.COOKIES.get('can_otp_enter')!=None:  
            if otp == profile.otp:
                if profile.user is not None:
                
                   profile.user.session = {'profile.user.id': profile.user.id}
                   profile.user.is_active=True
                   profile.user.save()
                   request.session['key3']=3
                   messages.success(request, 'Your Account has been activated.You can log in now')
                   return redirect("login")
                return redirect('register')
            messages.error(request, 'You have entered wrong OTP.Try again')
            return redirect(request.path)
        messages.error(request,'60 seconds over.Try again')
        return redirect(request.path)
    return render(request, "accounts/otp.html", {'uid': uid})
#userregistration_resend_otp
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def resend_otp(request):
  if 'resend_otp' in request.POST:
    user_details = request.session.get('user_details')
 
    if user_details:
        # Access user details from the session
             uid = user_details['uid']
             phone_number = user_details['phone_number']
          
             otp = ''.join(secrets.choice('0123456789') for _ in range(4))
             profile = Profile.objects.filter(uid=uid).first()
             profile.otp=otp
             profile.save()
             messagehandler=MessageHandler(profile.user.phone_number,otp).send_otp_via_message()
             red=redirect(f'register/otp/{profile.uid}/')
             red.set_cookie("can_otp_enter",True,max_age=60)
             messages.success(request, 'OTP has been resent')
             return red 
    return render(request, 'register.html')
  return render(request, 'accounts/register.html')  

@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout(request):
  if 'key1' in request.session:
        del request.session['key1']
  if 'user_details' in request.session:
        del request.session['user_details']     
  auth.logout(request)
  messages.success(request, 'Lougout Successful')
  return redirect('login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login')
def dashboard(request):
    return render(request,'accounts/dashboard.html')

@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login_admin(request):
     if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('dashboard_admin')
        else:
            messages.error(request, "Invalid Credentials")
            return redirect('login_admin')
     return render(request,'accounts/login_admin.html')

def dashboard_admin(request):
    return render(request,'admin/dashboard_admin.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login_admin')
def logout_admin(request):
    auth.logout(request)
    messages.success(request, 'Lougout Successful')
    return redirect('login_admin')

def forgot_passwrod(request):
   pass


def users_list(request):
    users_list = Account.objects.all()
    
    return render(request, 'admin/users_list.html', {'users_list' : users_list })

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login_admin')
def toggle_user_status(request, user_id):
    user = get_object_or_404(Account, id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('users_list')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login_admin')
def category_list(request):
    category_list = Category.objects.all()
    return render(request, 'admin/category_list.html', {'category_list' : category_list})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login_admin')
def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            slug = form.cleaned_data['slug']
            description = form.cleaned_data['description']
            cat_image = form.cleaned_data['cat_image']

            category = Category.objects.create(category_name=category_name, slug=slug, description=description, cat_image=cat_image)
            category.save()
            messages.success(request, 'Category Added Successfully.')
            return redirect('category_list')
    else:
        form = CategoryForm()
    context = {
        'form': form
    }
    return render(request, 'admin/category_create.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login_admin')
def category_update(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category Updated Successfully.')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'admin/category_update.html', {'form': form, 'category_id': category_id})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login_admin')
def category_delete(request, id):
    category_to_delete = Category.objects.filter(id=id)
    category_to_delete.delete()
    messages.success(request, 'Category deleted.')
    return redirect('category_list')



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login_admin')
def product_list(request):
    product_list = Product.objects.all()
    return render(request, 'admin/product_list.html', {'product_list' : product_list})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login_admin')
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product_name = form.cleaned_data['product_name']
            slug = form.cleaned_data['slug']
            description = form.cleaned_data['description']
            price = form.cleaned_data['price']
            stock = form.cleaned_data['stock']
            category = form.cleaned_data['category']
            image = form.cleaned_data['image']

            product = Product.objects.create(product_name=product_name, slug=slug, description=description, price=price,
                                             stock=stock, category=category, image=image)
            product.save()
            messages.success(request, 'Product Added Successfull.')
            return redirect('product_list')
    else:
        form = ProductForm()
    context = {
        'form': form
    }
    return render(request, 'admin/product_create.html', context)



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login_admin')
def product_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated Successfull.')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'admin/product_update.html', {'form': form, 'product_id': product_id})



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login_admin')
def product_delete(request, id):
    product_to_delete = Product.objects.filter(id=id)
    product_to_delete.delete()
    messages.success(request, 'Product deleted.')
    return redirect('product_list')



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login_admin')
def variant_list(request):
    variant_list = Variation.objects.all()
    return render(request, 'admin/variant_list.html', {'variant_list': variant_list})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login_admin')
def variant_add(request):
    if request.method == 'POST':
        form = VariantForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            variation_category = form.cleaned_data['variation_category']
            variation_value = form.cleaned_data['variation_value']

            variant = Variation.objects.create(product=product, variation_category=variation_category, variation_value=variation_value)
            variant.save()
            messages.success(request, 'Variant Added Successfully.')
            return redirect('variant_list')
    else:
        form = VariantForm()
    context = {
        'form': form
    }
    return render(request, 'admin/variant_create.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login_admin')
def variant_update(request, variant_id):
    variant = get_object_or_404(Variation, pk=variant_id)

    if request.method == 'POST':
        form = VariantForm(request.POST, instance=variant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Variant updated Successfully.')
            return redirect('variant_list')
    else:
        form = VariantForm(instance=variant)
    return render(request, 'admin/variant_update.html', {'form': form, 'variant_id': variant_id})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login_admin')
def variant_delete(request, variant_id):
    variant_to_delete = Variation.objects.filter(id=variant_id)
    variant_to_delete.delete()
    messages.success(request, 'Variant deleted.')
    return redirect('variant_list')