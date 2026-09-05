(() => {
  const menuControl = document.querySelector("#menu-control");
  const tocControl = document.querySelector("#toc-control");
  const menu = document.querySelector("#book-menu");
  const mobileToc = document.querySelector("#book-mobile-toc");
  const menuTrigger = document.querySelector("[data-book-menu-trigger]");
  const tocTrigger = document.querySelector("[data-book-toc-trigger]");
  const skipLink = document.querySelector(".book-skip-link");
  const page = document.querySelector(".book-page");
  const pageContent = page
    ? [...page.children].filter(element =>
        !element.matches(".book-header, .book-menu-overlay, .book-toc-overlay")
      )
    : [];
  const mobile = window.matchMedia("(max-width: 56rem)");

  if (!menuControl || !tocControl || !menu) return;

  const setHidden = (element, hidden) => {
    if (!element) return;
    element.inert = hidden;
    if (hidden) {
      element.setAttribute("aria-hidden", "true");
    } else {
      element.removeAttribute("aria-hidden");
    }
  };

  const sync = () => {
    const isMobile = mobile.matches;
    const menuOpen = !isMobile || menuControl.checked;
    const tocOpen = isMobile && tocControl.checked;
    const drawerOpen = isMobile && (menuControl.checked || tocControl.checked);

    setHidden(menu, !menuOpen);
    setHidden(mobileToc, !tocOpen);
    setHidden(skipLink, drawerOpen);
    pageContent.forEach(element => setHidden(element, drawerOpen));
    document.body.classList.toggle("book-drawer-open", drawerOpen);
    menuTrigger?.setAttribute("aria-expanded", String(isMobile && menuControl.checked));
    tocTrigger?.setAttribute("aria-expanded", String(tocOpen));
  };

  const enableKeyboardToggle = trigger => {
    trigger?.addEventListener("keydown", event => {
      if (event.key !== "Enter" && event.key !== " ") return;
      event.preventDefault();
      trigger.click();
    });
  };

  enableKeyboardToggle(menuTrigger);
  enableKeyboardToggle(tocTrigger);

  menuControl.addEventListener("change", () => {
    if (menuControl.checked) tocControl.checked = false;
    sync();
  });
  tocControl.addEventListener("change", () => {
    if (tocControl.checked) menuControl.checked = false;
    sync();
  });

  if (typeof mobile.addEventListener === "function") {
    mobile.addEventListener("change", sync);
  } else {
    mobile.addListener(sync);
  }

  mobileToc?.querySelectorAll("a").forEach(link => {
    link.addEventListener("click", () => {
      tocControl.checked = false;
      sync();
    });
  });

  document.addEventListener("keydown", event => {
    if (event.key !== "Escape" || !mobile.matches) return;
    if (tocControl.checked) {
      tocControl.checked = false;
      sync();
      tocTrigger?.focus();
    } else if (menuControl.checked) {
      menuControl.checked = false;
      sync();
      menuTrigger?.focus();
    }
  });

  sync();
})();
