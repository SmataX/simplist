function togglePasswordVisibility(element){
    const passwordInput = document.getElementById("password");
    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        element.textContent = "Hide";
    } else {
        passwordInput.type = "password";
        element.textContent = "Show";
    }
}