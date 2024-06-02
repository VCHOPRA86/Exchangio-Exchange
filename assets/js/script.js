//api key
let apiKey = "7d085f100a4037cc8fc00029";
let api = `https://v6.exchangerate-api.com/v6/${apiKey}/latest/USD`;
const fromDropDown = document.getElementById("from-currency-select");
const toDropDown = document.getElementById("to-currency-select");
const result = document.getElementById("result"); // Add this line
const exchangeRateInput = document.getElementById("exchange-rate"); // Line to get input element for exchange rate


// Create dropdown from the currencies in array
currencies.forEach((currency) => {
  const option = document.createElement("option");
  option.value = currency;
  option.text = currency;
  fromDropDown.add(option.cloneNode(true)); // Using cloneNode to avoid adding the same option to both dropdowns
  toDropDown.add(option);
});

// Default values
fromDropDown.value = "GBP";
toDropDown.value = "EUR";

let convertCurrency = () => {
  // Create References
  const amount = document.querySelector("#amount").value;
  const fromCurrency = fromDropDown.value;
  const toCurrency = toDropDown.value;

  // If the amount input field is not empty
  if (amount.length != 0) {
    fetch(api)
      .then((resp) => resp.json())
      .then((data) => {
        let fromExchangeRate = data.conversion_rates[fromCurrency];
        let toExchangeRate = data.conversion_rates[toCurrency];
        const convertedAmount = (amount / fromExchangeRate) * toExchangeRate;
        const exchangeRate = toExchangeRate / fromExchangeRate; // Calculate the exchange rate

        result.innerHTML = `${amount} ${fromCurrency} = ${convertedAmount.toFixed(2)} ${toCurrency}`; // Display the exchange rate
        exchangeRateInput.value = `${exchangeRate.toFixed(2)} ${toCurrency}`; // Display the exchange rate in the input box
      })
      .catch((error) => {
        console.error("Error converting currency:", error);
        alert("Sorry an error occurred while converting currency. Please try again later.");
      });
  } else {
    alert("Please fill in the amount");
    // Clear result if amount is empty
    result.innerHTML = "";
  }
};


// Added event listener to the second button
document.querySelector("#exchange_button").addEventListener("click", convertCurrency);


//swap the selected values between the "from" and "to" currency dropdowns
document.querySelector("#exchange").addEventListener("click", () => {
    // Swap the values between "from" and "to" currency dropdowns
    [fromDropDown.value, toDropDown.value] = [toDropDown.value, fromDropDown.value];
    // Call the calculate function to update the result based on the new values
    convertCurrency();
});



