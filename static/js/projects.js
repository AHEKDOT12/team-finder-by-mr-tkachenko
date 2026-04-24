// Project-specific JS: complete project action, toggle participate, toggle favorite.
(function () {
  function getCookie(name) {
    if (window.getCookie) {
      return window.getCookie(name);
    }

    const cookies = document.cookie ? document.cookie.split(";") : [];

    for (let cookie of cookies) {
      cookie = cookie.trim();

      if (cookie.startsWith(name + "=")) {
        return decodeURIComponent(cookie.substring(name.length + 1));
      }
    }

    return "";
  }

  function showError(message) {
    if (window.toast) {
      window.toast(message, { type: "error" });
    } else {
      alert(message);
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    const completeBtn = document.getElementById("complete-project-btn");

    if (completeBtn) {
      completeBtn.addEventListener("click", function (event) {
        event.preventDefault();

        const projectId = completeBtn.dataset.id;

        if (!projectId) {
          return;
        }

        completeBtn.disabled = true;

        fetch(`/projects/${projectId}/complete/`, {
          method: "POST",
          headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
          },
          body: JSON.stringify({}),
        })
          .then(function (response) {
            if (!response.ok) {
              throw new Error("Complete project request failed");
            }

            return response.json();
          })
          .then(function (data) {
            if (data.status === "ok") {
              window.location.reload();
              return;
            }

            completeBtn.disabled = false;
            showError("Ошибка при завершении проекта");
          })
          .catch(function (error) {
            console.error("Ошибка запроса:", error);
            completeBtn.disabled = false;
            showError("Ошибка сети");
          });
      });
    }

    const participateBtn = document.getElementById("participate-btn");

    if (participateBtn) {
      participateBtn.addEventListener("click", function (event) {
        event.preventDefault();

        const projectId = participateBtn.dataset.project;

        if (!projectId) {
          return;
        }

        participateBtn.disabled = true;

        fetch(`/projects/${projectId}/toggle-participate/`, {
          method: "POST",
          headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
          },
          body: JSON.stringify({}),
        })
          .then(function (response) {
            if (!response.ok) {
              throw new Error("Toggle participate request failed");
            }

            return response.json();
          })
          .then(function (data) {
            if (data.status === "ok") {
              window.location.reload();
              return;
            }

            participateBtn.disabled = false;
            showError("Ошибка при изменении участия");
          })
          .catch(function (error) {
            console.error("Ошибка запроса:", error);
            participateBtn.disabled = false;
            showError("Ошибка сети");
          });
      });
    }

    document.addEventListener("click", function (event) {
      const favoriteBtn = event.target.closest("[data-toggle-favorite]");

      if (!favoriteBtn) {
        return;
      }

      event.preventDefault();
      event.stopPropagation();

      const projectId = favoriteBtn.dataset.project;

      console.log("favorite click", { projectId, favoriteBtn });

      if (!projectId) {
        console.error("project id not found on favorite button");
        return;
      }

      favoriteBtn.disabled = true;

      fetch(`/projects/${projectId}/toggle-favorite/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({}),
      })
        .then(function (response) {
          console.log("favorite response status", response.status);

          if (!response.ok) {
            throw new Error("Toggle favorite request failed");
          }

          return response.json();
        })
        .then(function (data) {
          console.log("favorite response data", data);

          if (data.status !== "ok") {
            favoriteBtn.disabled = false;
            showError("Ошибка при изменении избранного");
            return;
          }

          favoriteBtn.classList.toggle("is-active", data.is_favorite);

          if (data.is_favorite) {
            favoriteBtn.setAttribute("aria-label", "Удалить из избранного");
          } else {
            favoriteBtn.setAttribute("aria-label", "Добавить в избранное");
          }

          favoriteBtn.disabled = false;

          if (
            window.location.pathname === "/projects/favorites/" &&
            data.is_favorite === false
          ) {
            const card = favoriteBtn.closest("[data-project-card]");

            if (card) {
              card.remove();
            }

            const remainingCards = document.querySelectorAll("[data-project-card]");

            if (remainingCards.length === 0) {
              window.location.reload();
            }
          }
        })
        .catch(function (error) {
          console.error("favorite error:", error);
          favoriteBtn.disabled = false;
          showError("Ошибка сети при изменении избранного");
        });
    });
  });
})();