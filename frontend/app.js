
'use strict';

// HELPER FUNCTIONS
// These functions format prices, choose food emojis,
// communicate with FastAPI, and display notifications.

const $ = id => document.getElementById(id);
const money = cents => `$${(Number(cents) / 100).toFixed(2)}`;

const cuisines = {
  Italian: '🍕',
  Japanese: '🍣',
  Mexican: '🌮',
  American: '🍔',
  Indian: '🍛'
};

// Selects an emoji based on the name of a food item.
function foodEmoji(name) {
  let n = name.toLowerCase();

  if (n.includes('pizza')) return '🍕';
  if (n.includes('roll') || n.includes('sushi')) return '🍣';
  if (n.includes('taco')) return '🌮';
  if (n.includes('burger')) return '🍔';
  if (n.includes('fries')) return '🍟';
  if (n.includes('curry')) return '🍛';
  if (n.includes('naan')) return '🫓';

  return '🍽️';
}

// Stores the restaurants, selected restaurant, shopping cart,
// and previously retrieved menus while the website is running.
const state = {
  restaurants: [],
  restaurant: null,
  cart: [],
  menus: new Map()
};

let toastTimer;

// Sends HTTP requests to the FastAPI backend.
// Converts successful responses into JavaScript data
// and throws an error if the request fails.
async function api(path, opts = {}) {
  let response = await fetch(path, {
    ...opts,
    headers: {
      'Content-Type': 'application/json',
      ...(opts.headers || {})
    }
  });

  let data;

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    let d = data?.detail;

    throw new Error(
      typeof d === 'string'
        ? d
        : Array.isArray(d)
          ? d.map(x => x.msg).join('; ')
          : `Request failed (${response.status})`
    );
  }

  return data;
}

// Displays a temporary notification for four seconds.
function notify(msg) {
  $('toast').textContent = msg;
  $('toast').classList.remove('hidden');

  clearTimeout(toastTimer);

  toastTimer = setTimeout(() => {
    $('toast').classList.add('hidden');
  }, 4000);
}

// Creates HTML elements dynamically using JavaScript.
function el(tag, className = '', text) {
  let x = document.createElement(tag);

  if (className) x.className = className;
  if (text !== undefined) x.textContent = text;

  return x;
}


// ============================================================
// RESTAURANT BROWSING
// ============================================================

// Displays restaurant cards on the homepage.
// Customers can search by restaurant name or cuisine.
// The selected restaurant is highlighted.
function renderRestaurants(search = '') {
  let grid = $('restaurantGrid');
  grid.replaceChildren();

  let filtered = state.restaurants.filter(r =>
    `${r.name} ${r.cuisine}`
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  if (!filtered.length) {
    grid.append(el('p', 'placeholder', 'No restaurants found.'));
    return;
  }

  filtered.forEach(r => {
    let b = el(
      'button',
      'restaurant-card' +
        (state.restaurant?.id === r.id ? ' active' : '')
    );

    b.type = 'button';

    b.append(
      el('div', 'restaurant-icon', cuisines[r.cuisine] || '🍽️'),
      el('b', '', r.name),
      el('small', '', r.cuisine)
    );

    b.onclick = () => openRestaurant(r);
    grid.append(b);
  });
}

// Retrieves the five restaurants from GET /restaurants.
// Saves the results and automatically opens the first restaurant.
async function loadRestaurants() {
  try {
    let data = await api('/restaurants');

    if (!Array.isArray(data)) {
      throw Error('Unexpected restaurant response');
    }

    state.restaurants = data;
    $('restaurantCount').textContent = data.length;

    renderRestaurants();

    if (data.length) {
      await openRestaurant(data[0], false);
    }
  } catch (e) {
    $('restaurantGrid').replaceChildren(
      el('p', 'error', `Could not load restaurants: ${e.message}`)
    );
  }
}

// Loads the selected restaurant's menu from FastAPI.
// Updates the restaurant information displayed on the page.
// Previously retrieved menus are cached to avoid repeated requests.
async function openRestaurant(r, scroll = true) {
  state.restaurant = r;

  $('crumb').textContent = r.name;
  $('bannerTitle').textContent = r.name;

  $('bannerSubtitle').textContent =
    `${r.cuisine} cuisine · ` +
    `${r.avg_prep_minutes ?? '—'} minute average preparation`;

  $('bannerEmoji').textContent = cuisines[r.cuisine] || '🍽️';

  $('menuHeading').textContent = `Popular at ${r.name}`;
  $('menuDescription').textContent =
    'Pick something delicious for your cart';

  $('restaurantHours').textContent =
    `◷ ${r.opens_at || '—'} – ${r.closes_at || '—'}`;

  renderRestaurants($('searchInput').value);

  $('menuGrid').replaceChildren(
    el('p', 'placeholder', 'Loading dishes…')
  );

  try {
    let items = state.menus.get(r.id);

    if (!items) {
      items = await api(`/restaurants/${r.id}/menu`);

      if (!Array.isArray(items)) {
        throw Error('Unexpected menu response');
      }

      state.menus.set(r.id, items);
    }

    renderMenu(r, items);

    if (scroll) {
      $('menuGrid').scrollIntoView({
        behavior: 'smooth',
        block: 'nearest'
      });
    }
  } catch (e) {
    $('menuGrid').replaceChildren(
      el('p', 'error', `Could not load menu: ${e.message}`)
    );
  }
}


// ============================================================
// MENU DISPLAY
// ============================================================

// Creates food cards for the selected restaurant.
// Each card shows the food name, price, emoji,
// and a button to add the item to the shopping cart.
function renderMenu(r, items) {
  let grid = $('menuGrid');
  grid.replaceChildren();

  if (!items.length) {
    grid.append(el('p', 'placeholder', 'No dishes available.'));
    return;
  }

  items.forEach(item => {
    let card = el('article', 'dish-card');
    let icon = el('div', 'dish-icon', foodEmoji(item.name));
    let info = el('div', 'dish-info');

    info.append(
      el('h3', '', item.name),
      el('p', '', 'Freshly prepared · Made to order')
    );

    let bottom = el('div', 'dish-bottom');
    let add = el('button', 'add-btn', '+');

    add.type = 'button';
    add.setAttribute('aria-label', `Add ${item.name}`);
    add.onclick = () => addItem(r, item);

    bottom.append(
      el('strong', '', money(item.price_cents)),
      add
    );

    info.append(bottom);
    card.append(icon, info);
    grid.append(card);
  });
}


// ============================================================
// SHOPPING CART
// ============================================================

// Adds food to the cart and increases the quantity if
// the item is already there. Prevents mixing food from
// different restaurants in the same order.
function addItem(r, item) {
  if (
    state.cart.length &&
    state.cart[0].restaurantId !== r.id
  ) {
    if (!confirm(
      'Your cart has food from another restaurant. ' +
      'Clear it to start a new order?'
    )) {
      return;
    }

    state.cart = [];
  }

  let existing = state.cart.find(x => x.id === item.id);

  if (existing) {
    existing.quantity++;
  } else {
    state.cart.push({
      id: item.id,
      name: item.name,
      price_cents: item.price_cents,
      quantity: 1,
      restaurantId: r.id,
      restaurantName: r.name
    });
  }

  renderCart();
  notify(`${item.name} added to cart`);
}

// Increases or decreases the quantity of a cart item.
// Removes the item if its quantity reaches zero.
function adjust(id, delta) {
  let item = state.cart.find(x => x.id === id);

  if (!item) return;

  item.quantity += delta;
  state.cart = state.cart.filter(x => x.quantity > 0);

  renderCart();
}

// Updates the shopping cart display, including item quantities,
// subtotal, restaurant name, and checkout button.
// Prices are displayed in dollars but stored in cents.
function renderCart() {
  let count = state.cart.reduce(
    (s, x) => s + x.quantity, 0
  );

  let total = state.cart.reduce(
    (s, x) => s + x.price_cents * x.quantity, 0
  );

  $('cartCount').textContent = count;
  $('mobileCount').textContent = count;
  $('subtotal').textContent = money(total);

  $('cartRestaurant').textContent = state.cart.length
    ? `Ordering from ${state.cart[0].restaurantName}`
    : 'Choose a restaurant to begin';

  $('checkoutButton').disabled = !count;

  let box = $('cartItems');
  box.replaceChildren();

  if (!count) {
    let empty = el('div', 'empty', '🛍️');
    empty.append(el('p', '', 'Your cart is empty.'));
    box.append(empty);
    return;
  }

  state.cart.forEach(item => {
    let row = el('div', 'cart-item');
    let info = el('div', 'cart-item-info');
    let qty = el('div', 'qty');

    info.append(
      el('b', '', item.name),
      el('small', '', money(item.price_cents * item.quantity))
    );

    let minus = el('button', '', '−');
    let plus = el('button', '', '+');

    minus.type = plus.type = 'button';

    minus.setAttribute('aria-label', `Remove one ${item.name}`);
    plus.setAttribute('aria-label', `Add one ${item.name}`);

    minus.onclick = () => adjust(item.id, -1);
    plus.onclick = () => adjust(item.id, 1);

    qty.append(
      minus,
      el('span', '', item.quantity),
      plus
    );

    info.append(qty);

    row.append(
      el('div', 'cart-item-icon', foodEmoji(item.name)),
      info
    );

    box.append(row);
  });
}


// ============================================================
// CHECKOUT AND SCHEDULED DELIVERY
// ============================================================

// Converts the selected delivery date and time into UTC ISO format,
// which the FastAPI backend can process.
function scheduledISO(value) {
  let date = new Date(value);

  if (!value || Number.isNaN(date.getTime())) {
    throw Error('Choose a valid scheduled delivery time');
  }

  return date.toISOString();
}

// Handles checkout for regular and scheduled orders.
// Collects the address, restaurant ID, menu items, and quantities.
// Sends the order to POST /orders and displays its order number.
// The backend performs the final validation and price calculation.
async function checkout(e) {
  e.preventDefault();

  if (!state.cart.length) {
    return notify('Choose food first');
  }

  let address = $('address').value.trim();

  if (address.length < 5) {
    return notify('Enter a delivery address');
  }

  let payload = {
    restaurant_id: state.cart[0].restaurantId,
    address,
    items: state.cart.map(x => ({
      menu_item_id: x.id,
      quantity: x.quantity
    }))
  };

  // For scheduled orders, include the future delivery time.
  // The backend checks the 45-minute minimum, seven-day maximum,
  // and restaurant operating hours.
  if (
    document.querySelector('input[name="timing"]:checked').value
      === 'later'
  ) {
    try {
      payload.scheduled_for = scheduledISO(
        $('scheduledFor').value
      );
    } catch (err) {
      return notify(err.message);
    }
  }

  let btn = $('checkoutButton');
  btn.disabled = true;
  btn.textContent = 'Placing order…';

  try {
    let order = await api('/orders', {
      method: 'POST',
      body: JSON.stringify(payload)
    });

    // After successful checkout, clear the cart,
    // reset the form, and automatically show order tracking.
    state.cart = [];
    renderCart();

    $('checkoutForm').reset();
    $('scheduleWrap').classList.add('hidden');
    $('scheduledFor').required = false;

    let id = order.id ?? order.order_id;

    notify(`Order placed! ${id ? 'Order #' + id : ''}`);

    if (id) {
      $('trackId').value = id;
      await trackOrder(id);

      $('tracking').scrollIntoView({
        behavior: 'smooth'
      });
    }
  } catch (err) {
    notify(`Order failed: ${err.message}`);
  } finally {
    btn.textContent = 'Checkout →';
    btn.disabled = !state.cart.length;
  }
}


// ============================================================
// ORDER TRACKING AND CANCELLATION
// ============================================================

// Retrieves an order using GET /orders/{id}.
// Displays its status, address, total, and ordered items.
// Scheduled orders also display a cancellation button.
// The backend decides whether cancellation is still allowed.
async function trackOrder(id) {
  let box = $('trackingResult');

  box.replaceChildren(el('p', '', 'Loading order…'));

  try {
    let o = await api(
      `/orders/${encodeURIComponent(id)}`
    );

    let result = el('div', 'order-result');

    result.append(
      el('h3', '', `Order #${o.id ?? o.order_id ?? id}`),
      el('span', 'status', o.status || 'UNKNOWN')
    );

    if (o.address) {
      result.append(el('p', '', `📍 ${o.address}`));
    }

    if (o.total_cents != null) {
      result.append(
        el('p', '', `Total: ${money(o.total_cents)}`)
      );
    }

    if (o.scheduled_for) {
      result.append(
        el(
          'p',
          '',
          `Scheduled: ${new Date(o.scheduled_for).toLocaleString()}`
        )
      );
    }

    if (Array.isArray(o.items)) {
      let ul = el('ul');

      o.items.forEach(x => {
        ul.append(
          el(
            'li',
            '',
            `${x.quantity} × ${x.name ?? 'Item #' + x.menu_item_id}`
          )
        );
      });

      result.append(ul);
    }

    // Only SCHEDULED orders display the cancellation button.
    // Clicking it sends PATCH /orders/{id}/status with CANCELLED.
    // Cancellation is rejected at or after the 30-minute cutoff.
    if (o.status === 'SCHEDULED') {
      let cancel = el(
        'button',
        'primary',
        'Cancel scheduled order'
      );

      cancel.type = 'button';

      cancel.onclick = async () => {
        if (!confirm('Cancel this scheduled order?')) {
          return;
        }

        try {
          await api(`/orders/${id}/status`, {
            method: 'PATCH',
            body: JSON.stringify({
              status: 'CANCELLED'
            })
          });

          notify('Order cancelled');
          await trackOrder(id);
        } catch (err) {
          notify(`Cancellation failed: ${err.message}`);
        }
      };

      result.append(cancel);
    }

    box.replaceChildren(result);
  } catch (err) {
    box.replaceChildren(
      el('p', 'error', `Unable to find order: ${err.message}`)
    );
  }
}


// ============================================================
// EVENT LISTENERS
// ============================================================

// Connects website interactions to JavaScript functions.
// These respond to searching, navigation, checkout,
// order tracking, and selecting scheduled delivery.

// Filter restaurants when the customer types in the search bar.
$('searchInput').addEventListener('input', e => {
  renderRestaurants(e.target.value);
});

// Reset the restaurant search when "View all" is clicked.
$('showAll').onclick = () => {
  $('searchInput').value = '';
  renderRestaurants();

  $('restaurantGrid').scrollIntoView({
    behavior: 'smooth'
  });
};

// Scroll to the order tracking section.
$('trackNav').onclick = () => {
  $('tracking').scrollIntoView({
    behavior: 'smooth'
  });
};

// Scroll to the shopping cart on mobile.
$('mobileCart').onclick = () => {
  $('cart').scrollIntoView({
    behavior: 'smooth'
  });
};

// Scroll to the cart items.
$('closeCart').onclick = () => {
  $('cartItems').scrollIntoView({
    behavior: 'smooth'
  });
};

// Track an order when the tracking form is submitted.
$('trackForm').onsubmit = e => {
  e.preventDefault();
  trackOrder($('trackId').value);
};

// Run checkout when the customer submits the checkout form.
$('checkoutForm').onsubmit = checkout;

// Show the date and time input only when scheduled delivery
// is selected. Regular orders do not require this input.
document.querySelectorAll('input[name="timing"]').forEach(x => {
  x.onchange = () => {
    let later =
      document.querySelector('input[name="timing"]:checked').value
      === 'later';

    $('scheduleWrap').classList.toggle('hidden', !later);
    $('scheduledFor').required = later;
  };
});


// ============================================================
// APPLICATION STARTUP
// ============================================================

// Initialize the empty shopping cart and load the restaurants
// when the MiniDash website first opens.
renderCart();
loadRestaurants();
