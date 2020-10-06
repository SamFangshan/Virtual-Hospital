// A reference to Stripe.js initialized with your real test publishable API key.
var stripe = Stripe(publishableKey);

var paymentData;

function registerElements(elements) {
  var formClass = '.example3';
  var payment = document.querySelector(formClass);

  var form = payment.querySelector('form');
  var resetButton = payment.querySelector('a.reset');
  var error = form.querySelector('.error');
  var errorMessage = error.querySelector('.message');

  function enableInputs() {
    Array.prototype.forEach.call(
      form.querySelectorAll(
        "input[type='text'], input[type='email'], input[type='tel']"
      ),
      function(input) {
        input.removeAttribute('disabled');
      }
    );
  }

  function disableInputs() {
    Array.prototype.forEach.call(
      form.querySelectorAll(
        "input[type='text'], input[type='email'], input[type='tel']"
      ),
      function(input) {
        input.setAttribute('disabled', 'true');
      }
    );
  }

  function triggerBrowserValidation() {
    // The only way to trigger HTML5 form validation UI is to fake a user submit
    // event.
    var submit = document.createElement('input');
    submit.type = 'submit';
    submit.style.display = 'none';
    form.appendChild(submit);
    submit.click();
    submit.remove();
  }

  // Listen for errors from each Element, and show error messages in the UI.
  var savedErrors = {};
  elements.forEach(function(element, idx) {
    element.on('change', function(event) {
      if (event.error) {
        error.classList.add('visible');
        savedErrors[idx] = event.error.message;
        errorMessage.innerText = event.error.message;
      } else {
        savedErrors[idx] = null;

        // Loop over the saved errors and find the first one, if any.
        var nextError = Object.keys(savedErrors)
          .sort()
          .reduce(function(maybeFoundError, key) {
            return maybeFoundError || savedErrors[key];
          }, null);

        if (nextError) {
          // Now that they've fixed the current error, show another one.
          errorMessage.innerText = nextError;
        } else {
          // The user fixed the last error; no more errors.
          error.classList.remove('visible');
        }
      }
    });
  });

  // Show the customer the error from Stripe if their card fails to charge
  var showError = function(errorMsgText) {
    // loading(false);
    error.classList.add('visible');
    savedErrors[100] = errorMsgText;
    error.innerText = errorMsgText;
  };

  // Calls stripe.confirmCardPayment
  // If the card requires authentication Stripe shows a pop-up modal to
  // prompt the user to enter authentication details without leaving your page.
  var payWithCard = function(stripe, cardNumber, clientSecret, additionalData) {
    payment.classList.remove('submitting');
    // loading(true);
    stripe
      .confirmCardPayment(clientSecret, {
        payment_method: {
          card: cardNumber,
          billing_details: {
            name: additionalData.name,
            phone: additionalData.phone,
            email: additionalData.email
          }
        }
      })
      .then(function(result) {
        if (result.error) {
          // Show error to your customer
          enableInputs();
          showError(result.error.message);
        } else {
          // The payment succeeded!
          payment.classList.add('submitted');
          setTimeout(function() {
            window.location.href = '/payment-success/' + result.paymentIntent.id
          }, 4000);
        }
      });
  };

  form.addEventListener("submit", function(event) {
    event.preventDefault();
    // Trigger HTML5 validation UI on the form if any of the inputs fail
    // validation.
    var plainInputsValid = true;
    Array.prototype.forEach.call(form.querySelectorAll('input'), function(
      input
    ) {
      if (input.checkValidity && !input.checkValidity()) {
        plainInputsValid = false;
        return;
      }
    });
    if (!plainInputsValid) {
      triggerBrowserValidation();
      return;
    }

    // Listen on the form's 'submit' handler...
    var name = form.querySelector('#name');
    var email = form.querySelector('#email');
    var phone = form.querySelector('#phone');

    var additionalData = {
      name: name.value,
      email: email.value,
      phone: phone.value,
    };

    // Show a loading screen...
    payment.classList.add('submitting');

    // Disable all inputs.
    disableInputs();

    payWithCard(stripe, elements[0], paymentData.clientSecret, additionalData);
  });
}

// Disable the button until we have Stripe set up on the page
document.querySelector("button").disabled = true;
fetch("/create-payment-intent", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(purchase)
  })
  .then(function(result) {
    return result.json();
  })
  .then(function(data) {
    'use strict';
    
    paymentData = data;

    var elements = stripe.elements({
      fonts: [{
        cssSrc: 'https://fonts.googleapis.com/css?family=Quicksand',
      }, ],
      // Stripe's examples are localized to specific languages, but if
      // you wish to have Elements automatically detect your user's locale,
      // use `locale: 'auto'` instead.
      locale: window.__exampleLocale,
    });

    var elementStyles = {
      base: {
        color: '#fff',
        fontWeight: 600,
        fontFamily: 'Quicksand, Open Sans, Segoe UI, sans-serif',
        fontSize: '16px',
        fontSmoothing: 'antialiased',

        ':focus': {
          color: '#424770',
        },

        '::placeholder': {
          color: '#9BACC8',
        },

        ':focus::placeholder': {
          color: '#CFD7DF',
        },
      },
      invalid: {
        color: '#fff',
        ':focus': {
          color: '#FA755A',
        },
        '::placeholder': {
          color: '#FFCCA5',
        },
      },
    };

    var elementClasses = {
      focus: 'focus',
      empty: 'empty',
      invalid: 'invalid',
    };

    var cardNumber = elements.create('cardNumber', {
      style: elementStyles,
      classes: elementClasses,
    });
    cardNumber.mount('#card-number');
    cardNumber.on("change", function(event) {
      // Disable the Pay button if there are no card details in the Element
      document.querySelector("button").disabled = event.empty;
      document.querySelector(".error").textContent = event.error ? event.error.message : "";
    });

    var cardExpiry = elements.create('cardExpiry', {
      style: elementStyles,
      classes: elementClasses,
    });
    cardExpiry.mount('#card-expiry');

    var cardCvc = elements.create('cardCvc', {
      style: elementStyles,
      classes: elementClasses,
    });
    cardCvc.mount('#card-cvc');

    registerElements([cardNumber, cardExpiry, cardCvc]);

  });
