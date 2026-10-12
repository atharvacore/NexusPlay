function showToast(message, isError = false) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    
    if (isError) {
        toast.classList.add('error');
    } else {
        toast.classList.remove('error');
    }
    
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

async function launchGame(gameId) {
    showToast(`Preparing to launch...`);
    
    try {
        const response = await fetch(`/api/launch/${gameId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            if (data.status === 'already_running') {
                showToast('Game is already running! Check your taskbar.');
            } else {
                showToast(data.message);
                
                // For FM Sim, since it starts another web server locally,
                // we could redirect there or open it in a new tab if we know the port.
                // Assuming it starts on port 5000:
                if (gameId === 'fm_sim') {
                    setTimeout(() => {
                        window.open('http://127.0.0.1:5000', '_blank');
                    }, 2000);
                }
            }
        } else {
            showToast(data.error || 'Failed to launch game', true);
        }
    } catch (error) {
        showToast('Network error while connecting to launcher backend', true);
        console.error('Launch error:', error);
    }
}

// Scroll reveal observer for fading elements
document.addEventListener('DOMContentLoaded', () => {
    // Collect all elements we styled to fade in via CSS (.content-section > *, etc)
    const fadeSelectors = [
        '.hero-section > *',
        '.content-section > *',
        '.features-grid > *',
        '.grid > *'
    ];
    
    const elementsToFade = document.querySelectorAll(fadeSelectors.join(', '));
    
    // Add staggered delay for grid children automatically if they are in the same grid
    let currentGrid = null;
    let gridIndex = 0;
    
    elementsToFade.forEach((el) => {
        // Slight stagger for things like cards in grids
        if (el.classList.contains('feature-card') || el.classList.contains('game-card')) {
            const parent = el.parentElement;
            if (parent !== currentGrid) {
                currentGrid = parent;
                gridIndex = 0;
            }
            el.style.transitionDelay = `${(gridIndex % 3) * 150}ms`;
            gridIndex++;
        }
    });

    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.15
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-visible');
                // Unobserve after revealing to prevent repeating if scrolling back up
                observer.unobserve(entry.target); 
            }
        });
    }, observerOptions);

    // Give a tiny timeout so the CSS transform takes hold if JS loads fast
    setTimeout(() => {
        elementsToFade.forEach(el => observer.observe(el));
    }, 50);
});
