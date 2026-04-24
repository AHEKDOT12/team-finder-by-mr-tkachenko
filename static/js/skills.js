console.log("skills.js loaded");

function initSkills() {
  const skillsContainer = document.querySelector("[data-user-skills]");

  if (!skillsContainer) {
    console.log("skills container not found");
    return;
  }

  const userId = skillsContainer.dataset.userId;
  const addButton = document.querySelector("[data-add-skill-button]");
  const formWrapper = document.querySelector("[data-skill-form-wrapper]");
  const input = document.querySelector("[data-skill-input]");
  const suggestionsList = document.querySelector("[data-skill-suggestions]");
  const skillsList = document.querySelector("[data-skills-list]");

  console.log("skills init", {
    userId,
    addButton,
    formWrapper,
    input,
    suggestionsList,
    skillsList,
  });

  if (!userId || !addButton || !formWrapper || !input || !suggestionsList || !skillsList) {
    console.log("some skill elements not found");
    return;
  }

  function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split(";") : [];

    for (let cookie of cookies) {
      cookie = cookie.trim();

      if (cookie.startsWith(name + "=")) {
        return decodeURIComponent(cookie.substring(name.length + 1));
      }
    }

    return null;
  }

  const csrftoken = getCookie("csrftoken");

  function clearSuggestions() {
    suggestionsList.innerHTML = "";
    suggestionsList.hidden = true;
  }

  function renderSkillTag(skillId, skillName) {
    const emptyText = skillsList.querySelector(".skills-empty");
    if (emptyText) {
      emptyText.remove();
    }

    const tag = document.createElement("span");
    tag.className = "skill-tag";
    tag.dataset.skillId = skillId;

    const name = document.createElement("span");
    name.textContent = skillName;

    const removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.className = "skill-remove";
    removeButton.textContent = "×";
    removeButton.setAttribute("data-remove-skill", "");
    removeButton.setAttribute("aria-label", `Удалить навык ${skillName}`);

    removeButton.addEventListener("click", () => {
      removeSkill(skillId, tag);
    });

    tag.appendChild(name);
    tag.appendChild(removeButton);
    skillsList.appendChild(tag);
  }

  async function loadSuggestions(query) {
    const response = await fetch(`/users/skills/?q=${encodeURIComponent(query)}`);

    if (!response.ok) {
      console.log("suggestions failed", response.status);
      clearSuggestions();
      return;
    }

    const skills = await response.json();

    suggestionsList.innerHTML = "";

    const normalizedQuery = query.trim().toLowerCase();

    skills.forEach((skill) => {
      const item = document.createElement("button");
      item.type = "button";
      item.className = "skill-suggestion";
      item.textContent = skill.name;

      item.addEventListener("click", () => {
        addSkill({ skill_id: skill.id });
        input.value = "";
        clearSuggestions();
      });

      suggestionsList.appendChild(item);
    });

    const exactMatch = skills.some(
      (skill) => skill.name.trim().toLowerCase() === normalizedQuery
    );

    if (normalizedQuery && !exactMatch) {
      const createItem = document.createElement("button");
      createItem.type = "button";
      createItem.className = "skill-suggestion";
      createItem.textContent = `Создать «${query.trim()}»`;

      createItem.addEventListener("click", () => {
        addSkill({ name: query.trim() });
        input.value = "";
        clearSuggestions();
      });

      suggestionsList.appendChild(createItem);
    }

    suggestionsList.hidden = suggestionsList.children.length === 0;
  }

  async function addSkill(payload) {
    const formData = new FormData();

    if (payload.skill_id) {
      formData.append("skill_id", payload.skill_id);
    }

    if (payload.name) {
      formData.append("name", payload.name);
    }

    const response = await fetch(`/users/${userId}/skills/add/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrftoken,
      },
      body: formData,
    });

    if (!response.ok) {
      console.log("add skill failed", response.status);
      return;
    }

    const data = await response.json();

    if (data.added) {
      renderSkillTag(data.skill_id, data.name || payload.name);
    }
  }

  async function removeSkill(skillId, tagElement) {
    const response = await fetch(`/users/${userId}/skills/${skillId}/remove/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrftoken,
      },
    });

    if (!response.ok) {
      console.log("remove skill failed", response.status);
      return;
    }

    tagElement.remove();

    if (!skillsList.children.length) {
      const emptyText = document.createElement("p");
      emptyText.className = "skills-empty";
      emptyText.textContent = "Навыки пока не добавлены.";
      skillsList.appendChild(emptyText);
    }
  }

  let searchTimeout = null;

  addButton.addEventListener("click", () => {
    console.log("add skill clicked");
    formWrapper.hidden = !formWrapper.hidden;

    if (!formWrapper.hidden) {
      input.focus();
    }
  });

  input.addEventListener("input", () => {
    const query = input.value.trim();

    clearTimeout(searchTimeout);

    if (!query) {
      clearSuggestions();
      return;
    }

    searchTimeout = setTimeout(() => {
      loadSuggestions(query);
    }, 300);
  });

  skillsList.querySelectorAll("[data-skill-id]").forEach((tag) => {
    const skillId = tag.dataset.skillId;
    const removeButton = tag.querySelector("[data-remove-skill]");

    if (removeButton) {
      removeButton.addEventListener("click", () => {
        removeSkill(skillId, tag);
      });
    }
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initSkills);
} else {
  initSkills();
}