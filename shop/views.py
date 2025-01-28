from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Purchase
from .forms import ProductForm, CategoryForm, UserProfileForm, AddToCartForm
from decimal import Decimal

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. Welcome!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def product_content(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    context = {'product': product}
    return render(request, 'product_content.html', context)

@login_required
def purchases(request):
    user_purchases = Purchase.objects.filter(user=request.user)
    context = {'purchases': user_purchases}
    return render(request, 'purchases.html', context)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
    else:
        cart_item.quantity = 1
    cart_item.save()
    messages.success(request, f'Товар "{product.name}" додано до кошика.')
    return redirect('cart')

def home(request):
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'home.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, available=True)
    form = AddToCartForm()
    if request.method == 'POST':
        form = AddToCartForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            cart, _ = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            cart_item.quantity = cart_item.quantity + quantity if not created else quantity
            cart_item.save()
            messages.success(request, f'{quantity} {product.name}(s) added to your cart.')
            return redirect('cart')
    return render(request, 'product_detail.html', {'product': product, 'form': form})
def category_list(request):
    categories = Category.objects.all()
    context = {
        'categories': categories
    }
    return render(request, 'category_list.html', context)

def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    products = Product.objects.filter(category=category, available=True)
    context = {
        'category': category,
        'products': products
    }
    return render(request, 'category_detail.html', context)

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.author = request.user
            product.save()
            messages.success(request, 'Product added successfully.')
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})

@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, 'Category added successfully.')
            return redirect('category_detail', pk=category.pk)
    else:
        form = CategoryForm()
    return render(request, 'add_category.html', {'form': form})

@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.user == product.author or request.user.is_staff:
        product.delete()
        messages.success(request, 'Product deleted successfully.')
    else:
        messages.error(request, 'You do not have permission to delete this product.')
    return redirect('home')

@login_required
def delete_category(request, pk):
    if request.user.is_staff:
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        messages.success(request, 'Category deleted successfully.')
    else:
        messages.error(request, 'You do not have permission to delete categories.')
    return redirect('home')

@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.user == product.author or request.user.is_staff:
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                form.save()
                messages.success(request, 'Product updated successfully.')
                return redirect('product_detail', pk=product.pk)
        else:
            form = ProductForm(instance=product)
        return render(request, 'edit_product.html', {'form': form, 'product': product})
    else:
        messages.error(request, 'You do not have permission to edit this product.')
        return redirect('product_detail', pk=product.pk)

@login_required
def edit_category(request, pk):
    if request.user.is_staff:
        category = get_object_or_404(Category, pk=pk)
        if request.method == 'POST':
            form = CategoryForm(request.POST, instance=category)
            if form.is_valid():
                form.save()
                messages.success(request, 'Category updated successfully.')
                return redirect('category_detail', pk=category.pk)
        else:
            form = CategoryForm(instance=category)
        return render(request, 'edit_category.html', {'form': form, 'category': category})
    else:
        messages.error(request, 'You do not have permission to edit categories.')
        return redirect('home')

def custom_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def profile(request):
    user_products = Product.objects.filter(author=request.user)
    return render(request, 'profile.html', {'user_products': user_products})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'edit_profile.html', {'form': form})

def search(request):
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
    else:
        products = Product.objects.all()
    
    context = {
        'products': products,
        'query': query
    }
    return render(request, 'search_results.html', context)


@login_required
def cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cartitem_set.all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, f'{cart_item.product.name} removed from your cart.')
    return redirect('cart')

@login_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cartitem_set.all()
    total = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        if request.user.balance >= total:
            order = Order.objects.create(user=request.user, total_amount=total)
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                # Create Purchase objects
                Purchase.objects.create(
                    user=request.user,
                    product=cart_item.product,
                    quantity=cart_item.quantity
                )
            request.user.balance -= total
            request.user.save()
            cart.cartitem_set.all().delete()
            messages.success(request, 'Your order has been placed successfully!')
            return redirect('order_confirmation', order_id=order.id)
        else:
            messages.error(request, 'Insufficient balance. Please add funds to your account.')

    return render(request, 'checkout.html', {'cart_items': cart_items, 'total': total})

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_confirmation.html', {'order': order})

@login_required
def add_funds(request):
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount', 0))
        if amount > 0:
            request.user.balance += amount
            request.user.save()
            messages.success(request, f'{amount} added to your balance successfully.')
        else:
            messages.error(request, 'Please enter a valid amount.')
    return redirect('profile')

def paginate(request, objects, per_page):
    paginator = Paginator(objects, per_page)
    page = request.GET.get('page')
    try:
        paginated_objects = paginator.page(page)
    except PageNotAnInteger:
        paginated_objects = paginator.page(1)
    except EmptyPage:
        paginated_objects = paginator.page(paginator.num_pages)
    return {'page_obj': paginated_objects}