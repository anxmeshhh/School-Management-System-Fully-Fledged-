// Ultra Enhanced JavaScript with Advanced Animations and Premium Interactions
// Fixed version without problematic imports

// Advanced Loading System
class AdvancedLoadingScreen {
  constructor() {
    this.loadingScreen = document.getElementById("loading-screen")
    this.progressFill = document.querySelector(".loading-progress-fill")
    this.progressGlow = document.querySelector(".loading-progress-glow")
    this.percentage = document.querySelector(".loading-percentage")
    this.status = document.querySelector(".loading-status")
    this.logoRings = document.querySelectorAll(".logo-ring")

    this.loadingSteps = [
      "Initializing System...",
      "Loading Components...",
      "Connecting Services...",
      "Preparing Interface...",
      "Almost Ready...",
      "Welcome!",
    ]

    this.init()
  }

  init() {
    console.log("Loading screen initialized")
    this.simulateAdvancedLoading()
    this.animateLogoRings()
  }

  simulateAdvancedLoading() {
    let progress = 0
    let stepIndex = 0

    const interval = setInterval(() => {
      const increment = Math.random() * 15 + 5 // Faster increment
      progress += increment

      if (progress >= 100) {
        progress = 100
        clearInterval(interval)
        console.log("Loading complete, hiding screen")
        setTimeout(() => this.hideLoading(), 500) // Shorter delay
      }

      this.updateProgress(progress)

      // Update status text
      const newStepIndex = Math.floor((progress / 100) * this.loadingSteps.length)
      if (newStepIndex !== stepIndex && newStepIndex < this.loadingSteps.length) {
        stepIndex = newStepIndex
        this.updateStatus(this.loadingSteps[stepIndex])
      }
    }, 150) // Faster interval
  }

  updateProgress(progress) {
    if (this.progressFill) {
      this.progressFill.style.width = `${progress}%`
    }
    if (this.percentage) {
      this.percentage.textContent = `${Math.round(progress)}%`
    }

    // Add glow effect when near completion
    if (progress > 80 && this.progressGlow) {
      this.progressGlow.style.opacity = "1"
    }
  }

  updateStatus(status) {
    if (this.status) {
      this.status.style.opacity = "0"
      setTimeout(() => {
        this.status.textContent = status
        this.status.style.opacity = "1"
      }, 100)
    }
  }

  animateLogoRings() {
    this.logoRings.forEach((ring, index) => {
      ring.style.animationDelay = `${index * 0.2}s`
    })
  }

  hideLoading() {
    console.log("Hiding loading screen")
    if (this.loadingScreen) {
      this.loadingScreen.classList.add("hidden")
      setTimeout(() => {
        this.loadingScreen.style.display = "none"
        document.body.style.overflow = "visible"
        this.initializeMainAnimations()
      }, 700)
    }
  }

  initializeMainAnimations() {
    console.log("Initializing main animations")

    // Initialize custom AOS-like animations
    this.initCustomAnimations()

    // Start hero animations
    this.animateHeroElements()
  }

  initCustomAnimations() {
    // Custom animation system to replace AOS
    const animatedElements = document.querySelectorAll("[data-aos]")

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const element = entry.target
            const animationType = element.getAttribute("data-aos")
            const delay = element.getAttribute("data-aos-delay") || 0

            setTimeout(() => {
              element.classList.add("aos-animate")
              this.triggerAnimation(element, animationType)
            }, Number.parseInt(delay))

            observer.unobserve(element)
          }
        })
      },
      {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px",
      },
    )

    animatedElements.forEach((el) => {
      // Set initial state
      el.style.opacity = "0"
      el.style.transform = this.getInitialTransform(el.getAttribute("data-aos"))
      observer.observe(el)
    })
  }

  getInitialTransform(animationType) {
    switch (animationType) {
      case "fade-up":
        return "translateY(30px)"
      case "fade-left":
        return "translateX(30px)"
      case "fade-right":
        return "translateX(-30px)"
      case "fade-down":
        return "translateY(-30px)"
      default:
        return "translateY(30px)"
    }
  }

  triggerAnimation(element, animationType) {
    element.style.transition = "all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)"
    element.style.opacity = "1"
    element.style.transform = "translate(0, 0)"
  }

  animateHeroElements() {
    const titleWords = document.querySelectorAll(".title-word")
    titleWords.forEach((word, index) => {
      setTimeout(() => {
        word.style.opacity = "1"
        word.style.transform = "translateY(0)"
      }, index * 200)
    })
  }
}

// Advanced Cursor System
class AdvancedCursorSystem {
  constructor() {
    this.cursorDot = document.getElementById("cursor-dot")
    this.cursorOutline = document.getElementById("cursor-outline")
    this.cursorTrail = document.getElementById("cursor-trail")
    this.isVisible = false
    this.trails = []

    this.init()
  }

  init() {
    if (window.innerWidth > 768 && this.cursorDot && this.cursorOutline) {
      this.setupEventListeners()
      this.createTrailEffect()
    }
  }

  setupEventListeners() {
    document.addEventListener("mousemove", (e) => {
      this.updateCursorPosition(e.clientX, e.clientY)
      this.addTrailPoint(e.clientX, e.clientY)

      if (!this.isVisible) {
        this.showCursor()
      }
    })

    document.addEventListener("mouseleave", () => {
      this.hideCursor()
    })

    document.addEventListener("mouseenter", () => {
      this.showCursor()
    })

    // Interactive elements
    const interactiveElements = document.querySelectorAll("a, button, .portal-card, .feature-card, .nav-link, .btn")

    interactiveElements.forEach((el) => {
      el.addEventListener("mouseenter", () => {
        if (this.cursorOutline) {
          this.cursorOutline.style.transform = "translate(-50%, -50%) scale(1.5)"
          this.cursorOutline.style.borderColor = "var(--primary-500)"
        }
        if (this.cursorDot) {
          this.cursorDot.style.background = "var(--primary-500)"
        }
      })

      el.addEventListener("mouseleave", () => {
        if (this.cursorOutline) {
          this.cursorOutline.style.transform = "translate(-50%, -50%) scale(1)"
          this.cursorOutline.style.borderColor = "var(--primary-500)"
        }
        if (this.cursorDot) {
          this.cursorDot.style.background = "var(--primary-500)"
        }
      })
    })
  }

  updateCursorPosition(x, y) {
    if (this.cursorDot) {
      this.cursorDot.style.left = x + "px"
      this.cursorDot.style.top = y + "px"
    }

    if (this.cursorOutline) {
      setTimeout(() => {
        this.cursorOutline.style.left = x + "px"
        this.cursorOutline.style.top = y + "px"
      }, 50)
    }
  }

  addTrailPoint(x, y) {
    this.trails.push({ x, y, opacity: 1 })

    if (this.trails.length > 10) {
      this.trails.shift()
    }
  }

  createTrailEffect() {
    setInterval(() => {
      this.trails.forEach((trail, index) => {
        trail.opacity -= 0.1

        if (trail.opacity <= 0) {
          this.trails.splice(index, 1)
        }
      })

      this.renderTrails()
    }, 50)
  }

  renderTrails() {
    // Create visual trail effect
    this.trails.forEach((trail, index) => {
      const trailElement = document.createElement("div")
      trailElement.style.cssText = `
        position: fixed;
        width: ${8 - index}px;
        height: ${8 - index}px;
        background: var(--primary-500);
        border-radius: 50%;
        left: ${trail.x}px;
        top: ${trail.y}px;
        transform: translate(-50%, -50%);
        opacity: ${trail.opacity};
        pointer-events: none;
        z-index: 9998;
      `

      document.body.appendChild(trailElement)

      setTimeout(() => {
        trailElement.remove()
      }, 100)
    })
  }

  showCursor() {
    this.isVisible = true
    if (this.cursorDot) this.cursorDot.style.opacity = "1"
    if (this.cursorOutline) this.cursorOutline.style.opacity = "1"
  }

  hideCursor() {
    this.isVisible = false
    if (this.cursorDot) this.cursorDot.style.opacity = "0"
    if (this.cursorOutline) this.cursorOutline.style.opacity = "0"
  }
}

// Advanced Navigation System
class AdvancedNavigation {
  constructor() {
    this.navbar = document.getElementById("navbar")
    this.navToggle = document.getElementById("nav-toggle")
    this.navMenu = document.getElementById("nav-menu")
    this.navLinks = document.querySelectorAll(".nav-link")
    this.lastScrollY = window.scrollY
    this.scrollThreshold = 100

    this.init()
  }

  init() {
    if (this.navbar) {
      this.setupScrollEffects()
      this.setupMobileMenu()
      this.setupSmoothScroll()
      this.setupActiveLinks()
      this.setupNavAnimations()
    }
  }

  setupScrollEffects() {
    let ticking = false

    window.addEventListener("scroll", () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          this.handleScroll()
          ticking = false
        })
        ticking = true
      }
    })
  }

  handleScroll() {
    const currentScrollY = window.scrollY

    // Add scrolled class
    if (currentScrollY > 50) {
      this.navbar.classList.add("scrolled")
    } else {
      this.navbar.classList.remove("scrolled")
    }

    // Hide/show navbar
    if (currentScrollY > this.lastScrollY && currentScrollY > this.scrollThreshold) {
      this.navbar.style.transform = "translateY(-100%)"
    } else {
      this.navbar.style.transform = "translateY(0)"
    }

    this.lastScrollY = currentScrollY
  }

  setupMobileMenu() {
    if (this.navToggle) {
      this.navToggle.addEventListener("click", () => {
        this.toggleMobileMenu()
      })
    }

    this.navLinks.forEach((link) => {
      link.addEventListener("click", () => {
        this.closeMobileMenu()
      })
    })

    document.addEventListener("click", (e) => {
      if (this.navbar && !this.navbar.contains(e.target)) {
        this.closeMobileMenu()
      }
    })
  }

  toggleMobileMenu() {
    if (this.navToggle) this.navToggle.classList.toggle("active")
    if (this.navMenu) this.navMenu.classList.toggle("active")
    document.body.style.overflow = this.navMenu && this.navMenu.classList.contains("active") ? "hidden" : "visible"
  }

  closeMobileMenu() {
    if (this.navToggle) this.navToggle.classList.remove("active")
    if (this.navMenu) this.navMenu.classList.remove("active")
    document.body.style.overflow = "visible"
  }

  setupSmoothScroll() {
    this.navLinks.forEach((link) => {
      link.addEventListener("click", (e) => {
        e.preventDefault()
        const targetId = link.getAttribute("href")
        const targetSection = document.querySelector(targetId)

        if (targetSection) {
          const offsetTop = targetSection.offsetTop - 80
          this.smoothScrollTo(offsetTop)
        }
      })
    })
  }

  smoothScrollTo(targetPosition) {
    const startPosition = window.pageYOffset
    const distance = targetPosition - startPosition
    const duration = 1000
    let start = null

    const animation = (currentTime) => {
      if (start === null) start = currentTime
      const timeElapsed = currentTime - start
      const run = this.easeInOutQuad(timeElapsed, startPosition, distance, duration)
      window.scrollTo(0, run)

      if (timeElapsed < duration) {
        requestAnimationFrame(animation)
      }
    }

    requestAnimationFrame(animation)
  }

  easeInOutQuad(t, b, c, d) {
    t /= d / 2
    if (t < 1) return (c / 2) * t * t + b
    t--
    return (-c / 2) * (t * (t - 2) - 1) + b
  }

  setupActiveLinks() {
    const sections = document.querySelectorAll("section[id]")

    window.addEventListener("scroll", () => {
      const scrollY = window.scrollY + 100

      sections.forEach((section) => {
        const sectionTop = section.offsetTop
        const sectionHeight = section.offsetHeight
        const sectionId = section.getAttribute("id")

        if (scrollY >= sectionTop && scrollY < sectionTop + sectionHeight) {
          this.navLinks.forEach((link) => {
            link.classList.remove("active")
            if (link.getAttribute("href") === `#${sectionId}`) {
              link.classList.add("active")
            }
          })
        }
      })
    })
  }

  setupNavAnimations() {
    // Animate nav items on load
    this.navLinks.forEach((link, index) => {
      link.style.opacity = "0"
      link.style.transform = "translateY(-20px)"

      setTimeout(
        () => {
          link.style.transition = "all 0.5s ease-out"
          link.style.opacity = "1"
          link.style.transform = "translateY(0)"
        },
        100 + index * 100,
      )
    })
  }
}

// Advanced Hero Animations
class AdvancedHeroAnimations {
  constructor() {
    this.heroParticles = document.getElementById("hero-particles")
    this.statNumbers = document.querySelectorAll(".stat-number[data-count]")
    this.floatingCards = document.querySelectorAll(".floating-card")
    this.geometricShapes = document.querySelectorAll(".shape")

    this.init()
  }

  init() {
    this.createAdvancedParticles()
    this.setupStatCounters()
    this.animateFloatingElements()
    this.setupScrollIndicator()
    this.createInteractiveBackground()
  }

  createAdvancedParticles() {
    if (!this.heroParticles) return

    for (let i = 0; i < 50; i++) {
      // Reduced number for performance
      const particle = document.createElement("div")
      particle.className = "hero-particle"

      const size = Math.random() * 4 + 1
      const x = Math.random() * 100
      const y = Math.random() * 100
      const duration = Math.random() * 20 + 10
      const delay = Math.random() * 5

      particle.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        background: radial-gradient(circle, var(--primary-400) 0%, transparent 70%);
        border-radius: 50%;
        left: ${x}%;
        top: ${y}%;
        animation: particleFloat ${duration}s ease-in-out infinite;
        animation-delay: ${delay}s;
        opacity: ${Math.random() * 0.6 + 0.2};
      `

      this.heroParticles.appendChild(particle)
    }

    // Add CSS for particle animation if not exists
    if (!document.getElementById("particle-styles")) {
      const style = document.createElement("style")
      style.id = "particle-styles"
      style.textContent = `
        @keyframes particleFloat {
          0%, 100% { 
            transform: translateY(0px) translateX(0px) rotate(0deg); 
          }
          25% { 
            transform: translateY(-20px) translateX(10px) rotate(90deg); 
          }
          50% { 
            transform: translateY(-10px) translateX(-15px) rotate(180deg); 
          }
          75% { 
            transform: translateY(-30px) translateX(5px) rotate(270deg); 
          }
        }
      `
      document.head.appendChild(style)
    }
  }

  setupStatCounters() {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            this.animateCounter(entry.target)
            observer.unobserve(entry.target)
          }
        })
      },
      { threshold: 0.5 },
    )

    this.statNumbers.forEach((stat) => observer.observe(stat))
  }

  animateCounter(element) {
    const target = Number.parseInt(element.getAttribute("data-count"))
    const duration = 2500
    const step = target / (duration / 16)
    let current = 0

    const timer = setInterval(() => {
      current += step
      if (current >= target) {
        element.textContent = target.toLocaleString()
        clearInterval(timer)

        // Add completion effect
        element.style.transform = "scale(1.1)"
        setTimeout(() => {
          element.style.transform = "scale(1)"
        }, 200)
      } else {
        element.textContent = Math.floor(current).toLocaleString()
      }
    }, 16)
  }

  animateFloatingElements() {
    this.floatingCards.forEach((card, index) => {
      const randomDelay = Math.random() * 2
      const randomDuration = 4 + Math.random() * 2

      card.style.animationDelay = `${randomDelay}s`
      card.style.animationDuration = `${randomDuration}s`

      // Add hover effects
      card.addEventListener("mouseenter", () => {
        card.style.transform = "translateY(-20px) scale(1.05)"
        card.style.boxShadow = "var(--shadow-2xl)"
      })

      card.addEventListener("mouseleave", () => {
        card.style.transform = ""
        card.style.boxShadow = ""
      })
    })

    this.geometricShapes.forEach((shape, index) => {
      const randomDelay = Math.random() * 3
      const randomDuration = 6 + Math.random() * 4

      shape.style.animationDelay = `${randomDelay}s`
      shape.style.animationDuration = `${randomDuration}s`
    })
  }

  setupScrollIndicator() {
    const scrollIndicator = document.querySelector(".hero-scroll-indicator")
    if (scrollIndicator) {
      scrollIndicator.addEventListener("click", () => {
        const nextSection = document.querySelector(".features-overview")
        if (nextSection) {
          nextSection.scrollIntoView({
            behavior: "smooth",
            block: "start",
          })
        }
      })
    }
  }

  createInteractiveBackground() {
    const heroBackground = document.querySelector(".hero-background")
    if (!heroBackground) return

    heroBackground.addEventListener("mousemove", (e) => {
      const rect = heroBackground.getBoundingClientRect()
      const x = (e.clientX - rect.left) / rect.width
      const y = (e.clientY - rect.top) / rect.height

      const gradients = heroBackground.querySelectorAll(".hero-gradient-1, .hero-gradient-2")
      gradients.forEach((gradient, index) => {
        const intensity = index === 0 ? x : 1 - x
        gradient.style.opacity = 0.3 + intensity * 0.4
      })
    })
  }
}

// Advanced Portal Cards System
class AdvancedPortalCards {
  constructor() {
    this.portalCards = document.querySelectorAll(".portal-card")
    this.init()
  }

  init() {
    this.setupCardAnimations()
    this.setupInteractiveEffects()
    this.setupCardConnections()
  }

  setupCardAnimations() {
    this.portalCards.forEach((card, index) => {
      // Stagger entrance animations
      card.style.opacity = "0"
      card.style.transform = "translateY(50px)"

      setTimeout(
        () => {
          card.style.transition = "all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)"
          card.style.opacity = "1"
          card.style.transform = "translateY(0)"
        },
        200 + index * 150,
      )

      // Setup hover animations
      this.setupCardHover(card)
    })
  }

  setupCardHover(card) {
    const cardGlow = card.querySelector(".card-glow")
    const portalIcon = card.querySelector(".portal-icon")
    const iconPulse = card.querySelector(".icon-pulse")

    card.addEventListener("mouseenter", () => {
      card.style.transform = "translateY(-15px) scale(1.02)"
      cardGlow.style.opacity = "0.15"

      if (iconPulse) {
        iconPulse.style.animation = "pulse 1s ease-in-out infinite"
      }

      // Create ripple effect
      this.createRippleEffect(card)
    })

    card.addEventListener("mouseleave", () => {
      card.style.transform = "translateY(0) scale(1)"
      cardGlow.style.opacity = "0"

      if (iconPulse) {
        iconPulse.style.animation = ""
      }
    })
  }

  createRippleEffect(card) {
    const ripple = document.createElement("div")
    ripple.className = "card-ripple"
    ripple.style.cssText = `
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: radial-gradient(circle, rgba(16, 185, 129, 0.3) 0%, transparent 70%);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            animation: rippleExpand 0.8s ease-out;
            pointer-events: none;
            z-index: 1;
        `

    card.appendChild(ripple)

    setTimeout(() => {
      ripple.remove()
    }, 800)
  }

  setupInteractiveEffects() {
    this.portalCards.forEach((card) => {
      const portalBtn = card.querySelector(".portal-btn")

      if (portalBtn) {
        portalBtn.addEventListener("click", (e) => {
          e.preventDefault()
          this.handlePortalAccess(card)
        })
      }
    })
  }

  handlePortalAccess(card) {
    // Create access animation
    card.style.transform = "scale(0.95)"

    setTimeout(() => {
      card.style.transform = "scale(1.05)"

      setTimeout(() => {
        card.style.transform = "scale(1)"
        this.showAccessModal(card)
      }, 150)
    }, 100)
  }

  showAccessModal(card) {
    const portalType = card.classList.contains("student-portal")
      ? "Student"
      : card.classList.contains("teacher-portal")
        ? "Teacher"
        : card.classList.contains("parent-portal")
          ? "Parent"
          : "Admin"

    // Create modal (simplified for demo)
    const modal = document.createElement("div")
    modal.className = "access-modal"
    modal.innerHTML = `
            <div class="modal-content">
                <h3>Access ${portalType} Portal</h3>
                <p>Redirecting to ${portalType.toLowerCase()} login...</p>
                <div class="modal-loader"></div>
            </div>
        `

    document.body.appendChild(modal)

    setTimeout(() => {
      modal.remove()
    }, 2000)
  }

  setupCardConnections() {
    // Create connecting lines between cards (visual effect)
    const connectionsContainer = document.createElement("div")
    connectionsContainer.className = "card-connections"
    connectionsContainer.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 0;
        `

    const portalsSection = document.querySelector(".portals-section")
    if (portalsSection) {
      portalsSection.appendChild(connectionsContainer)
    }
  }
}

// Advanced Features Showcase
class AdvancedFeaturesShowcase {
  constructor() {
    this.navItems = document.querySelectorAll(".features-navigation .nav-item")
    this.featureCategories = document.querySelectorAll(".feature-category")
    this.featureCards = document.querySelectorAll(".feature-card")

    this.init()
  }

  init() {
    this.setupNavigation()
    this.setupCardAnimations()
    this.setupInteractiveEffects()
  }

  setupNavigation() {
    this.navItems.forEach((item) => {
      item.addEventListener("click", () => {
        const category = item.getAttribute("data-category")
        this.switchCategory(category)
        this.updateActiveNav(item)
      })
    })
  }

  switchCategory(category) {
    // Hide all categories
    this.featureCategories.forEach((cat) => {
      cat.classList.remove("active")
      cat.style.opacity = "0"
      cat.style.transform = "translateX(30px)"
    })

    // Show selected category with animation
    setTimeout(() => {
      const targetCategory = document.getElementById(category)
      if (targetCategory) {
        targetCategory.classList.add("active")
        targetCategory.style.opacity = "1"
        targetCategory.style.transform = "translateX(0)"

        // Animate feature cards
        const cards = targetCategory.querySelectorAll(".feature-card")
        cards.forEach((card, index) => {
          card.style.opacity = "0"
          card.style.transform = "translateY(30px)"

          setTimeout(() => {
            card.style.transition = "all 0.5s ease-out"
            card.style.opacity = "1"
            card.style.transform = "translateY(0)"
          }, index * 100)
        })
      }
    }, 200)
  }

  updateActiveNav(activeItem) {
    this.navItems.forEach((item) => {
      item.classList.remove("active")
      const indicator = item.querySelector(".nav-indicator")
      if (indicator) {
        indicator.style.opacity = "0"
      }
    })

    activeItem.classList.add("active")
    const activeIndicator = activeItem.querySelector(".nav-indicator")
    if (activeIndicator) {
      activeIndicator.style.opacity = "1"
    }
  }

  setupCardAnimations() {
    this.featureCards.forEach((card) => {
      const cardGlow = card.querySelector(".card-glow")
      const iconOrbit = card.querySelector(".icon-orbit")

      card.addEventListener("mouseenter", () => {
        card.style.transform = "translateY(-8px) scale(1.02)"
        if (cardGlow) cardGlow.style.opacity = "0.1"
        if (iconOrbit) iconOrbit.style.opacity = "1"
      })

      card.addEventListener("mouseleave", () => {
        card.style.transform = "translateY(0) scale(1)"
        if (cardGlow) cardGlow.style.opacity = "0"
        if (iconOrbit) iconOrbit.style.opacity = "0"
      })
    })
  }

  setupInteractiveEffects() {
    // Add click effects to feature cards
    this.featureCards.forEach((card) => {
      card.addEventListener("click", () => {
        this.showFeatureDetails(card)
      })
    })
  }

  showFeatureDetails(card) {
    const title = card.querySelector(".feature-title").textContent
    const description = card.querySelector(".feature-description").textContent

    // Create detail modal (simplified)
    console.log(`Feature: ${title}\nDescription: ${description}`)
  }
}

// Advanced Button Effects System
class AdvancedButtonEffects {
  constructor() {
    this.buttons = document.querySelectorAll(".btn")
    this.init()
  }

  init() {
    this.setupRippleEffects()
    this.setupMagneticEffects()
    this.setupGlowEffects()
  }

  setupRippleEffects() {
    this.buttons.forEach((button) => {
      button.addEventListener("click", (e) => {
        this.createAdvancedRipple(button, e)
      })
    })
  }

  createAdvancedRipple(button, event) {
    const rect = button.getBoundingClientRect()
    const size = Math.max(rect.width, rect.height)
    const x = event.clientX - rect.left - size / 2
    const y = event.clientY - rect.top - size / 2

    const ripple = document.createElement("span")
    ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: radial-gradient(circle, rgba(255, 255, 255, 0.6) 0%, transparent 70%);
            border-radius: 50%;
            transform: scale(0);
            animation: advancedRipple 0.6s ease-out;
            pointer-events: none;
            z-index: 10;
        `

    button.appendChild(ripple)

    setTimeout(() => {
      ripple.remove()
    }, 600)
  }

  setupMagneticEffects() {
    this.buttons.forEach((button) => {
      button.addEventListener("mousemove", (e) => {
        const rect = button.getBoundingClientRect()
        const x = e.clientX - rect.left - rect.width / 2
        const y = e.clientY - rect.top - rect.height / 2

        const distance = Math.sqrt(x * x + y * y)
        const maxDistance = Math.max(rect.width, rect.height)

        if (distance < maxDistance) {
          const strength = (maxDistance - distance) / maxDistance
          const moveX = x * strength * 0.3
          const moveY = y * strength * 0.3

          button.style.transform = `translate(${moveX}px, ${moveY}px)`
        }
      })

      button.addEventListener("mouseleave", () => {
        button.style.transform = ""
      })
    })
  }

  setupGlowEffects() {
    this.buttons.forEach((button) => {
      const btnGlow = button.querySelector(".btn-glow")

      if (btnGlow) {
        button.addEventListener("mouseenter", () => {
          btnGlow.style.opacity = "0.6"
        })

        button.addEventListener("mouseleave", () => {
          btnGlow.style.opacity = "0"
        })
      }
    })
  }
}

// Advanced Scroll Animations
class AdvancedScrollAnimations {
  constructor() {
    this.elements = document.querySelectorAll("[data-aos]")
    this.init()
  }

  init() {
    this.setupIntersectionObserver()
    this.setupParallaxEffects()
    this.setupScrollProgress()
  }

  setupIntersectionObserver() {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            this.animateElement(entry.target)
            observer.unobserve(entry.target)
          }
        })
      },
      {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px",
      },
    )

    this.elements.forEach((el) => observer.observe(el))
  }

  animateElement(element) {
    const animationType = element.getAttribute("data-aos")
    const delay = element.getAttribute("data-aos-delay") || 0

    setTimeout(() => {
      element.classList.add("aos-animate")
      this.triggerCustomAnimation(element, animationType)
    }, Number.parseInt(delay))
  }

  triggerCustomAnimation(element, type) {
    switch (type) {
      case "fade-up":
        element.style.opacity = "1"
        element.style.transform = "translateY(0)"
        break
      case "fade-left":
        element.style.opacity = "1"
        element.style.transform = "translateX(0)"
        break
      case "fade-right":
        element.style.opacity = "1"
        element.style.transform = "translateX(0)"
        break
      default:
        element.style.opacity = "1"
        element.style.transform = "none"
    }
  }

  setupParallaxEffects() {
    const parallaxElements = document.querySelectorAll(".hero-visual, .geometric-shapes")

    window.addEventListener("scroll", () => {
      const scrolled = window.pageYOffset

      parallaxElements.forEach((element, index) => {
        const rate = scrolled * (0.3 + index * 0.1)
        element.style.transform = `translateY(${rate}px)`
      })
    })
  }

  setupScrollProgress() {
    const progressBar = document.createElement("div")
    progressBar.className = "scroll-progress"
    progressBar.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 0%;
            height: 3px;
            background: var(--gradient-primary);
            z-index: 9999;
            transition: width 0.1s ease-out;
        `

    document.body.appendChild(progressBar)

    window.addEventListener("scroll", () => {
      const scrollTop = window.pageYOffset
      const docHeight = document.body.scrollHeight - window.innerHeight
      const scrollPercent = (scrollTop / docHeight) * 100

      progressBar.style.width = scrollPercent + "%"
    })
  }
}

// Performance Optimization System
class PerformanceOptimizer {
  constructor() {
    this.init()
  }

  init() {
    this.optimizeImages()
    this.optimizeScrollEvents()
    this.preloadCriticalResources()
    this.setupLazyLoading()
  }

  optimizeImages() {
    const images = document.querySelectorAll("img")

    images.forEach((img) => {
      if (!img.hasAttribute("loading")) {
        img.setAttribute("loading", "lazy")
      }

      // Add intersection observer for fade-in effect
      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.style.opacity = "1"
            observer.unobserve(entry.target)
          }
        })
      })

      img.style.opacity = "0"
      img.style.transition = "opacity 0.5s ease-out"
      observer.observe(img)
    })
  }

  optimizeScrollEvents() {
    let ticking = false

    const optimizedScrollHandler = () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          // Scroll-based animations go here
          ticking = false
        })
        ticking = true
      }
    }

    window.addEventListener("scroll", optimizedScrollHandler, { passive: true })
  }

  preloadCriticalResources() {
    const criticalResources = ["/placeholder.svg?height=80&width=80", "/placeholder.svg?height=500&width=700"]

    criticalResources.forEach((resource) => {
      const link = document.createElement("link")
      link.rel = "preload"
      link.as = "image"
      link.href = resource
      document.head.appendChild(link)
    })
  }

  setupLazyLoading() {
    const lazyElements = document.querySelectorAll("[data-src]")

    const lazyObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const element = entry.target
          element.src = element.dataset.src
          element.classList.remove("lazy")
          lazyObserver.unobserve(element)
        }
      })
    })

    lazyElements.forEach((el) => lazyObserver.observe(el))
  }
}

// Accessibility Enhancement System
class AccessibilityEnhancer {
  constructor() {
    this.init()
  }

  init() {
    this.addSkipLinks()
    this.enhanceKeyboardNavigation()
    this.setupFocusManagement()
    this.addAriaLabels()
    this.setupReducedMotion()
  }

  addSkipLinks() {
    const skipLink = document.createElement("a")
    skipLink.href = "#main-content"
    skipLink.textContent = "Skip to main content"
    skipLink.className = "skip-link"
    skipLink.style.cssText = `
            position: absolute;
            top: -40px;
            left: 6px;
            background: var(--primary-600);
            color: white;
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 4px;
            z-index: 10000;
            transition: top 0.3s ease;
            font-weight: 600;
        `

    skipLink.addEventListener("focus", () => {
      skipLink.style.top = "6px"
    })

    skipLink.addEventListener("blur", () => {
      skipLink.style.top = "-40px"
    })

    document.body.insertBefore(skipLink, document.body.firstChild)
  }

  enhanceKeyboardNavigation() {
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        // Close any open modals or menus
        const navMenu = document.getElementById("nav-menu")
        const navToggle = document.getElementById("nav-toggle")

        if (navMenu && navMenu.classList.contains("active")) {
          navMenu.classList.remove("active")
          navToggle.classList.remove("active")
          document.body.style.overflow = "visible"
        }
      }

      if (e.key === "Tab") {
        document.body.classList.add("keyboard-navigation")
      }
    })

    document.addEventListener("mousedown", () => {
      document.body.classList.remove("keyboard-navigation")
    })
  }

  setupFocusManagement() {
    const focusableElements = document.querySelectorAll(
      'a, button, input, textarea, select, [tabindex]:not([tabindex="-1"])',
    )

    focusableElements.forEach((el) => {
      el.addEventListener("focus", () => {
        if (document.body.classList.contains("keyboard-navigation")) {
          el.style.outline = "2px solid var(--primary-500)"
          el.style.outlineOffset = "2px"
        }
      })

      el.addEventListener("blur", () => {
        el.style.outline = ""
        el.style.outlineOffset = ""
      })
    })
  }

  addAriaLabels() {
    // Add aria-labels to interactive elements without text
    const buttons = document.querySelectorAll("button:not([aria-label])")
    buttons.forEach((button) => {
      const icon = button.querySelector("i")
      if (icon && !button.textContent.trim()) {
        const iconClass = icon.className
        let label = "Button"

        if (iconClass.includes("play")) label = "Play video"
        if (iconClass.includes("arrow")) label = "Navigate"
        if (iconClass.includes("menu")) label = "Open menu"

        button.setAttribute("aria-label", label)
      }
    })
  }

  setupReducedMotion() {
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)")

    if (prefersReducedMotion.matches) {
      document.body.classList.add("reduced-motion")

      // Disable complex animations
      const style = document.createElement("style")
      style.textContent = `
                .reduced-motion *,
                .reduced-motion *::before,
                .reduced-motion *::after {
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                }
            `
      document.head.appendChild(style)
    }
  }
}

// Utility Functions
const utils = {
  // Smooth scroll to section
  scrollToSection: (sectionId) => {
    const section = document.getElementById(sectionId)
    if (section) {
      const offsetTop = section.offsetTop - 80
      window.scrollTo({
        top: offsetTop,
        behavior: "smooth",
      })
    }
  },

  // Debounce function
  debounce: (func, wait) => {
    let timeout
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout)
        func(...args)
      }
      clearTimeout(timeout)
      timeout = setTimeout(later, wait)
    }
  },

  // Generate random ID
  generateId: () => {
    return Math.random().toString(36).substr(2, 9)
  },

  // Format numbers
  formatNumber: (num) => {
    return new Intl.NumberFormat().format(num)
  },
}

// Global scroll function for buttons
window.scrollToSection = utils.scrollToSection

// Initialize all systems when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  console.log("DOM loaded, initializing systems...")

  try {
    // Initialize all advanced systems
    new AdvancedLoadingScreen()
    new AdvancedCursorSystem()
    new AdvancedNavigation()
    new AdvancedHeroAnimations()

    // Add main content id for skip link
    const heroSection = document.getElementById("home")
    if (heroSection) {
      heroSection.id = "main-content"
    }

    // Add dynamic CSS animations
    addDynamicStyles()

    console.log("All systems initialized successfully")
  } catch (error) {
    console.error("Error initializing systems:", error)
  }
})

// Add dynamic CSS styles
const addDynamicStyles = () => {
  if (document.getElementById("dynamic-styles")) return // Prevent duplicate styles

  const style = document.createElement("style")
  style.id = "dynamic-styles"
  style.textContent = `
    @keyframes advancedRipple {
      to {
        transform: scale(4);
        opacity: 0;
      }
    }
    
    @keyframes rippleExpand {
      to {
        width: 300px;
        height: 300px;
        opacity: 0;
      }
    }
    
    .aos-animate {
      transition: all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }
    
    .keyboard-navigation *:focus {
      outline: 2px solid var(--primary-500) !important;
      outline-offset: 2px !important;
    }
    
    .access-modal {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.8);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 10000;
      animation: modalFadeIn 0.3s ease-out;
    }
    
    .modal-content {
      background: white;
      padding: 2rem;
      border-radius: 1rem;
      text-align: center;
      max-width: 400px;
      width: 90%;
    }
    
    .modal-loader {
      width: 40px;
      height: 40px;
      border: 3px solid #f3f3f3;
      border-top: 3px solid var(--primary-500);
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 1rem auto;
    }
    
    @keyframes modalFadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
  `
  document.head.appendChild(style)
}

// Handle window resize
window.addEventListener(
  "resize",
  utils.debounce(() => {
    // Reinitialize cursor system for mobile
    if (window.innerWidth <= 768) {
      const cursorSystem = document.querySelector(".cursor-system")
      if (cursorSystem) cursorSystem.style.display = "none"
    } else {
      const cursorSystem = document.querySelector(".cursor-system")
      if (cursorSystem) cursorSystem.style.display = "block"
    }
  }, 250),
)

// Console welcome message
console.log(`
🎓 Welcome to Manavargal School Management System
📚 Information at Ease - Ultra Enhanced Version
🚀 Built with cutting-edge animations and premium interactions
✨ Features: Advanced particles, magnetic buttons, smart cursors, and more!

🔧 Technical Stack:
- Advanced CSS animations with 60fps performance
- Intersection Observer API for smooth scrolling
- Custom cursor system with trail effects
- Magnetic button interactions
- Advanced loading screen with progress tracking
- Accessibility-first design with WCAG compliance
- Performance optimized with lazy loading
- Mobile-first responsive design

For support, contact: info@manavargalsms.com
`)
