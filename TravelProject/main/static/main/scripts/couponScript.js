document.addEventListener("DOMContentLoaded", () => {
  const applyBtn = document.getElementById("apply-coupon-btn");
  const paymentForm = document.getElementById("payment-form"); // Get form
  const couponInput = document.getElementById("coupon-input");
  const couponMsg = document.getElementById("coupon-message");
  const discountRow = document.getElementById("coupon-discount-row");
  const discountAmountEl = document.getElementById("coupon-discount-amount");
  const totalAmountEl = document.getElementById("total-amount-value");
  const hiddenCouponInput = document.getElementById("applied-coupon-code");

  // --- Get data from HTML data-* attributes ---
  const validateUrl = applyBtn ? applyBtn.dataset.validateUrl : null;
  const registrationId = paymentForm
    ? paymentForm.dataset.registrationId
    : null;
  const initialTotalString = paymentForm
    ? paymentForm.dataset.initialTotal
    : "0.00";
  const initialTotal = parseFloat(initialTotalString); // Use initial total from data attribute
  const csrfTokenInput = document.querySelector("[name=csrfmiddlewaretoken]");
  const csrfToken = csrfTokenInput ? csrfTokenInput.value : null;
  // --- Removed lines that used invalid Django template tags ---

  // Check if essential elements/data exist before adding listener
  if (
    !applyBtn ||
    !couponInput ||
    !couponMsg ||
    !discountRow ||
    !discountAmountEl ||
    !totalAmountEl ||
    !hiddenCouponInput ||
    !validateUrl ||
    !registrationId ||
    !csrfToken
  ) {
    console.error(
      "Coupon JS Error: Could not find all required elements or data attributes (Button, Inputs, URL, RegistrationID, CSRF Token)."
    );
    if (applyBtn) applyBtn.disabled = true; // Disable button if setup fails
    return; // Stop script execution
  }

  // Store original total text (including currency symbol if any)
  const originalTotalHTML = totalAmountEl
    ? totalAmountEl.innerHTML
    : `$${initialTotal.toFixed(2)}`;

  applyBtn.addEventListener("click", async (event) => {
    event.preventDefault(); // Prevent button default behavior
    const couponCode = couponInput.value.trim();
    couponMsg.textContent = ""; // Clear previous messages
    discountRow.style.display = "none"; // Hide discount row initially
    hiddenCouponInput.value = ""; // Clear hidden input

    if (!couponCode) {
      couponMsg.textContent = "Please enter a coupon code.";
      couponMsg.style.color = "red";
      totalAmountEl.innerHTML = originalTotalHTML; // Reset total display
      return;
    }

    applyBtn.textContent = "Applying...";
    applyBtn.disabled = true;
    couponInput.disabled = true;

    // --- AJAX Call ---
    const formData = new FormData();
    formData.append("coupon_code", couponCode);
    formData.append("registration_id", registrationId); // Use registrationId read from data attribute
    formData.append("csrfmiddlewaretoken", csrfToken);

    try {
      const response = await fetch(validateUrl, {
        // Use validateUrl read from data attribute
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Server error response:", response.status, errorText);
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();

      if (data.valid) {
        couponMsg.style.color = "green";
        couponMsg.textContent = data.message;
        discountAmountEl.textContent = `-$${parseFloat(
          data.discount_amount
        ).toFixed(2)}`;
        discountRow.style.display = "flex";
        totalAmountEl.textContent = `$${parseFloat(data.final_total).toFixed(
          2
        )}`;
        hiddenCouponInput.value = data.applied_code;
        couponInput.value = data.applied_code; // Update input box (optional)
      } else {
        couponMsg.style.color = "red";
        couponMsg.textContent = data.message || "Invalid coupon code.";
        totalAmountEl.innerHTML = originalTotalHTML; // Reset total
        discountRow.style.display = "none";
        hiddenCouponInput.value = "";
      }
    } catch (error) {
      console.error("Error applying coupon:", error);
      couponMsg.style.color = "red";
      couponMsg.textContent = "Could not apply coupon. Please try again.";
      totalAmountEl.innerHTML = originalTotalHTML; // Reset total
      discountRow.style.display = "none";
      hiddenCouponInput.value = "";
    } finally {
      // Restore button state
      applyBtn.textContent = "Apply";
      applyBtn.disabled = false;
      couponInput.disabled = false;
    }
  });
}); // End DOMContentLoaded
