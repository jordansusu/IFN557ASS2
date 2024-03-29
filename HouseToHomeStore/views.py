from asyncio.log import logger
from flask import Blueprint, render_template, url_for, request, session, flash, redirect
from .models import Product, ShoppingCart, WishList
from datetime import datetime
from .forms import ProceedToCheckoutForm
from .login import LogInForm
from . import db
import logging

bp = Blueprint('main', __name__, template_folder='templates')


@bp.route('/houseToHome')
def index():
    return render_template('index.html')


@bp.route('/houseToHome/kitchenproducts/')
def kitchenproducts():
    kitchensP = Product.query.filter(Product.category == 'Kitchen')
    return render_template('kitchenIndex.html', kitchensP=kitchensP)


@bp.route('/houseToHome/livingproducts/')
def livingproducts():
    livingsP = Product.query.filter(Product.category == 'LivingRoom')
    return render_template('livingIndex.html', livingsP=livingsP)


@bp.route('/houseToHome/bathroomproducts/')
def bathroomproducts():
    bathroomsP = Product.query.filter(Product.category == 'BathRoom')
    return render_template('bathRoomIndex.html', bathroomsP=bathroomsP)


@bp.route('/houseToHome/outdoors/')
def outdoors():
    outdoorsP = Product.query.filter(Product.category == 'Outdoor')
    return render_template('outDoorsIndex.html', outdoorsP=outdoorsP)


@bp.route('/houseToHome/bedroomproducts/')
def bedroomproducts():
    bedroomsP = Product.query.filter(Product.category == 'BedRoom')
    return render_template('bedRoomIndex.html', bedroomsP=bedroomsP)


@bp.route('/houseToHome/commonproducts/')
def commonproducts():
    commonP = Product.query.filter(Product.category == 'Common')
    return render_template('commonOnesIndex.html', commonP=commonP)

# _______________________________________ SHOPPING CART METHODS ____________________________________________


# Referred to as "Cart" to the user

@bp.route('/houseToHome/placeOrder', methods=['POST', 'GET'])
def placeOrder():
    form = ProceedToCheckoutForm()
    product_id = request.values.get('product_id')

    # retrieve order if there is one
    if 'order_id' in session.keys():
        order = ShoppingCart.query.get(session['order_id'])
       # order will be None if order_id stale
    else:
       # there is no order
        order = None

    # create new order if needed
    if order is None:
        product_all = Product.query.all()
        for product_item in product_all:
            product_item.shoppingCartcount = 1
        order = ShoppingCart(order_place_status=False, cart_net_total_price=0,
                             shipping_charges=0, cart_total_product_price=0)
        try:
            db.session.add(order)
            db.session.commit()
            session['order_id'] = order.cart_id
        except:
            print('failed at creating a new order')
            order = None

    # calcultate totalprice
    total_product_price = 0
    net_total_price = 0
    shipping_charges = 0
    #shoppingcartCount = 0
    if order is not None:
        for product in order.products:
            #totalprice = totalprice + tour.price
            total_product_price += product.price * product.shoppingCartcount
            shipping_charges = product.shippingCost

    net_total_price = total_product_price + shipping_charges

    # are we adding an item?
    if product_id is not None and order is not None:
        product = Product.query.get(product_id)
        if product not in order.products:
            try:
                order.products.append(product)
                db.session.commit()
            except:
                return 'There was an issue adding the item to your basket'
            flash('PRODUCT ADDED SUCCESSFULLY TO SHOPPING CART!!')
            return redirect(url_for('main.placeOrder'))
        else:
            product.shoppingCartcount = product.shoppingCartcount + 1
            order.products.append(product)
            db.session.commit()
            flash(
                'PRODUCT WAS ALREADY IN SHOPPING CART, THE COUNT HAS BEEN SUCCESSFULLY INCREASED!!!')
            return redirect(url_for('main.placeOrder'))

    return render_template('cartIndex.html', order=order, total_product_price=total_product_price, net_total_price=net_total_price, shipping_charges=shipping_charges, form=form)

# Delete specific basket items


@bp.route('/houseToHome/deletecartproduct', methods=['POST'])
def deletecartproduct():
    delete_cart_product_id = request.form['delete_cart_product_id']
    if 'order_id' in session:
        order = ShoppingCart.query.get_or_404(session['order_id'])
        product_to_delete = Product.query.get(delete_cart_product_id)

        try:
            order.products.remove(product_to_delete)
            product_to_delete.shoppingCartcount = 1
            db.session.commit()
            flash('PRODUCT REMOVED SUCCESSFULLY FROM SHOPPING CART!!')
            return redirect(url_for('main.placeOrder'))
        except:
            return 'Problem deleting item from order'
    return redirect(url_for('main.placeOrder'))


# Scrap basket

@bp.route('/houseToHome/emptycart')
def deleteorder():
    if 'order_id' in session:
        order = ShoppingCart.query.get(session['order_id'])
        if order is not None:
            for product in order.products:
                product.shoppingCartcount = 1
        db.session.commit()
        del session['order_id']
        flash('ALL PRODUCTS DELETED FROM SHOPPING CART')
    return redirect(url_for('main.placeOrder'))

# _______________________________________ WISHLIST METHODS __________________________________________


# Referred to as "Add Product To WishList" by the user

@bp.route('/houseToHome/addProductToWishList', methods=['POST', 'GET'])
def addProductToWishList():
    product_id = request.values.get('product_id')

    # retrieve order if there is one
    if 'wishListorder_id' in session.keys():
        requestByUser = WishList.query.get(session['wishListorder_id'])
        # order will be None if wishListorder_id stale
    else:
        # there is no order
        requestByUser = None

    # create new request if needed
    if requestByUser is None:
        product_all = Product.query.all()
        for product_item in product_all:
            product_item.wishListCount = 1
        requestByUser = WishList(
            item_add_status=False, individual_product_count=0)
        try:
            db.session.add(requestByUser)
            db.session.commit()
            session['wishListorder_id'] = requestByUser.wishList_id
        except:
            print('failed at add product to wishlist')
            requestByUser = None

    # are we adding an item?
    if product_id is not None and requestByUser is not None:
        product = Product.query.get(product_id)
        if product not in requestByUser.products:
            try:
                requestByUser.products.append(product)
                db.session.commit()
            except:
                return 'There was an issue adding the item to your basket'
            flash('PRODUCT ADDED SUCCESSFULLY TO WISHING LIST!!')
            return redirect(url_for('main.addProductToWishList'))
        else:
            product.wishListCount = product.wishListCount + 1
            requestByUser.products.append(product)
            db.session.commit()
            flash(
                'PRODUCT WAS ALREADY IN WISHING LIST, THE COUNT HAS BEEN SUCCESSFULLY INCREASED!!!')
            return redirect(url_for('main.addProductToWishList'))

    return render_template('wishListIndex.html', requestByUser=requestByUser)


# Delete specific WishList items

@bp.route('/houseToHome/deletewishListproduct', methods=['POST'])
def deletewishListproduct():
    wishlist_item_id = request.form['wishlist_item_id']
    if 'wishListorder_id' in session:
        requestByUser = WishList.query.get_or_404(session['wishListorder_id'])
        product_to_delete = Product.query.get(wishlist_item_id)
        try:
            requestByUser.products.remove(product_to_delete)
            product_to_delete.wishListCount = 1
            db.session.commit()
            flash('PRODUCT DELETED SUCCESSFULLY FROM WISHING LIST!!')
            return redirect(url_for('main.addProductToWishList'))
        except:
            return 'Problem deleting item from order'
    return redirect(url_for('main.addProductToWishList'))


# _______________________________________ PROCEED TO CHECKOUT FORM METHOD __________________________________________

@bp.route('/houseToHome/proceedtocheckout', methods=['POST', 'GET'])
def proceedtocheckout():
    form = ProceedToCheckoutForm()
    if 'order_id' in session:
        order = ShoppingCart.query.get_or_404(session['order_id'])
        if form.validate_on_submit():
            order.order_place_status = True
            order.buyerFullName = form.buyerFullName.data
            order.shippingHomeAddressDetails = form.shippingHomeAddressDetails.data
            order.city = form.city.data
            order.state = form.state.data
            order.postCode = form.postCode.data
            try:
                db.session.commit()
                del session['order_id']
                flash(
                    'THANK YOU FOR FILLING DETAILS. YOUR ORDER WILL BE DELIVERED AS PER THE INFORMATION PROVIDED...')
                return redirect(url_for('main.placeOrder'))
            except:
                return 'There was an issue completing your order'
    return render_template('checkout.html', form=form)


# _______________________________________ ADD PRODUCT TO CART FROM WISHLIST METHOD __________________________________________


@bp.route('/houseToHome/addProductToWishListFromCart', methods=['POST', 'GET'])
def addProductToWishListFromCart():
    product_id = request.values.get('product_id')

    # retrieve order if there is one
    if 'wishListorder_id' in session.keys():
        requestByUser = WishList.query.get(session['wishListorder_id'])
        # order will be None if wishListorder_id stale
    else:
        # there is no order
        requestByUser = None

    # create new request if needed
    if requestByUser is None:
        requestByUser = WishList(
            item_add_status=False, individual_product_count=0)
        try:
            db.session.add(requestByUser)
            db.session.commit()
            session['wishListorder_id'] = requestByUser.wishList_id
        except:
            print('failed at add product to wishlist')
            requestByUser = None

    # are we adding an item?
    if product_id is not None and requestByUser is not None:
        product = Product.query.get(product_id)
        if product not in requestByUser.products:
            product.wishListCount = product.shoppingCartcount
            product.shoppingCartcount = 1
            try:
                requestByUser.products.append(product)
                if 'order_id' in session:
                    order = ShoppingCart.query.get_or_404(session['order_id'])
                    product_to_delete = Product.query.get(product_id)
                    try:
                        order.products.remove(product_to_delete)
                        db.session.commit()
                        flash('PRODUCT ADDED SUCCESSFULLY TO WISHING LIST!!')
                        return redirect(url_for('main.addProductToWishList'))
                    except:
                        return 'Problem deleting item from order'
            except:
                return 'There was an issue adding the item to your basket'

            flash('PRODUCT ADDED SUCCESSFULLY TO WISHING LIST!!')
            return redirect(url_for('main.addProductToWishList'))
        else:
            product.wishListCount += product.shoppingCartcount
            product.shoppingCartcount = 1
            requestByUser.products.append(product)
            if 'order_id' in session:
                order = ShoppingCart.query.get_or_404(session['order_id'])
                product_to_delete = Product.query.get(product_id)
                try:
                    order.products.remove(product_to_delete)
                    db.session.commit()
                    flash(
                        'PRODUCT WAS ALREADY IN WISHINGLIST, THE COUNT HAS BEEN SUCCESSFULLY INCREASED!!!')
                    return redirect(url_for('main.addProductToWishList'))
                except:
                    return 'Problem deleting item from order'
            db.session.commit()
            flash(
                'PRODUCT WAS ALREADY IN WISHINGLIST, THE COUNT HAS BEEN SUCCESSFULLY INCREASED!!!')
            return redirect(url_for('main.addProductToWishList'))

    return render_template('wishListIndex.html', requestByUser=requestByUser)


# _______________________________________ ADD PRODUCT FROM WISHLIST TO SHOPPING CART __________________________________________


@bp.route('/houseToHome/addProductToCartFromWishList', methods=['POST', 'GET'])
def addProductToCartFromWishList():
    product_id = request.values.get('product_id')

    # retrieve order if there is one
    if 'order_id' in session.keys():
        order = ShoppingCart.query.get(session['order_id'])
       # order will be None if order_id stale
    else:
       # there is no order
        order = None

    # create new order if needed
    if order is None:
        order = ShoppingCart(order_place_status=False, cart_net_total_price=0,
                             shipping_charges=0, cart_total_product_price=0)
        try:
            db.session.add(order)
            db.session.commit()
            session['order_id'] = order.cart_id
        except:
            print('failed at creating a new order')
            order = None

    # calcultate totalprice
    total_product_price = 0
    net_total_price = 0
    shipping_charges = 0
    if order is not None:
        for product in order.products:
            #totalprice = totalprice + tour.price
            total_product_price += product.price * product.shoppingCartcount
            shipping_charges = product.shippingCost

    net_total_price = total_product_price + shipping_charges

    # are we adding an item?
    if product_id is not None and order is not None:
        product = Product.query.get(product_id)
        if product not in order.products:
            product.shoppingCartcount = product.wishListCount
            product.wishListCount = 1
            try:
                order.products.append(product)
                if 'wishListorder_id' in session:
                    requestByUser = WishList.query.get_or_404(
                        session['wishListorder_id'])
                    product_to_delete = Product.query.get(product_id)
                    try:
                        requestByUser.products.remove(product_to_delete)
                        db.session.commit()
                        flash('PRODUCT ADDED SUCCESSFULLY TO SHOPPING CART!!')
                        return redirect(url_for('main.placeOrder'))
                    except:
                        return 'Problem deleting item from order'
                db.session.commit()
            except:
                return 'There was an issue adding the item to your basket'
            flash('PRODUCT ADDED SUCCESSFULLY TO SHOPPING CART!!')
            return redirect(url_for('main.placeOrder'))
        else:
            product.shoppingCartcount += product.wishListCount
            product.wishListCount = 1
            order.products.append(product)
            if 'wishListorder_id' in session:
                requestByUser = WishList.query.get_or_404(
                    session['wishListorder_id'])
                product_to_delete = Product.query.get(product_id)
                try:
                    requestByUser.products.remove(product_to_delete)
                    db.session.commit()
                    flash(
                        'PRODUCT WAS ALREADY IN SHOPPING CART, THE COUNT HAS BEEN SUCCESSFULLY INCREASED!!!')
                    return redirect(url_for('main.placeOrder'))
                except:
                    return 'Problem deleting item from order'
            db.session.commit()
            flash(
                'PRODUCT WAS ALREADY IN SHOPPING CART, THE COUNT HAS BEEN SUCCESSFULLY INCREASED!!!')
            return redirect(url_for('main.placeOrder'))

    return render_template('cartIndex.html', order=order, total_product_price=total_product_price, net_total_price=net_total_price, shipping_charges=shipping_charges)
