window.addEventListener('resize', function () {
    const screenWidth = window.innerWidth;
    const screenHeight = window.innerHeight;
    const screenSize = { width: screenWidth, height: screenHeight };
    const event = new CustomEvent("screenSizeChanged", { detail: screenSize });
    window.dispatchEvent(event);
});

window.dispatchEvent(new Event("resize")); // Trigger event on load