function toggleMenu() {
    const navLinks = document.querySelector('.navlinks');
    navLinks.classList.toggle('active');
}

setTimeout(function() {
    let flashMessages = document.getElementById('flash-messages');
    if (flashMessages) {
      flashMessages.style.display = 'none';
    }
  }, 100);