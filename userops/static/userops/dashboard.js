(function () {
  const FILTER_KEYS = [
    "dealer_id",
    "champion_name",
    "champion_mobile",
    "dealer_name",
    "city",
    "state",
    "dealer_category",
    "cluster",
    "asm_1",
    "asm_2",
    "role",
    "department",
    "brand",
  ];

  const PREVIEW_COLUMNS = [
    "username",
    "email",
    "dealer_id",
    "dealer_name",
    "city",
    "state",
    "dealer_category",
    "cluster",
    "asm_1",
    "asm_2",
    "role",
    "department",
    "brand",
  ];

  const selectedIdentifiers = new Set();

  function getCookie(name) {
    const prefix = `${name}=`;
    const cookies = document.cookie ? document.cookie.split(";") : [];
    for (const rawCookie of cookies) {
      const cookie = rawCookie.trim();
      if (cookie.startsWith(prefix)) {
        return decodeURIComponent(cookie.slice(prefix.length));
      }
    }
    return "";
  }

  function nonEmptyLines(value) {
    return value
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean);
  }

  function getUserIdentifier(user) {
    const email = (user.email || "").trim();
    if (email) {
      return email;
    }
    const username = (user.username || "").trim();
    if (username) {
      return username;
    }
    return "";
  }

  function toSafeCourseId(courseId, index) {
    const normalized = String(courseId || "")
      .replace(/[^a-zA-Z0-9_-]/g, "_")
      .replace(/_+/g, "_")
      .replace(/^_+|_+$/g, "");
    return normalized ? `${normalized}_${index}` : `course_${index}`;
  }

  function collectFilters() {
    const filters = {};
    for (const key of FILTER_KEYS) {
      const value = document.getElementById(`filter-${key}`).value.trim();
      if (value) {
        filters[key] = value;
      }
    }
    return filters;
  }

  function clearStatus() {
    const statusBox = document.getElementById("status-box");
    statusBox.textContent = "";
    statusBox.className = "status";
  }

  function setStatus(message, level) {
    const statusBox = document.getElementById("status-box");
    statusBox.textContent = message;
    statusBox.className = `status ${level || "info"}`;
  }

  function updateSelectionCount() {
    document.getElementById("selectedCount").textContent = `Selected: ${selectedIdentifiers.size}`;
    document.getElementById("execute-scope-hint").textContent = selectedIdentifiers.size
      ? "Enrolling selected users only"
      : "Enrolling all matched users";
  }

  function clearSelectionState() {
    selectedIdentifiers.clear();
    updateSelectionCount();
  }

  function updateSelectedCoursesCount() {
    const selected = document.querySelectorAll(".course-checkbox:checked").length;
    document.getElementById("selectedCoursesCount").textContent = `Selected: ${selected}`;
  }

  function renderCourses(courses) {
    const courseList = document.getElementById("courseList");
    courseList.innerHTML = "";

    if (!courses.length) {
      courseList.textContent = "No courses available.";
      updateSelectedCoursesCount();
      return;
    }

    const grouped = new Map();
    for (const course of courses) {
      const org = (course.org || "Unknown").trim() || "Unknown";
      if (!grouped.has(org)) {
        grouped.set(org, []);
      }
      grouped.get(org).push(course);
    }

    let index = 0;
    for (const [org, groupCourses] of grouped.entries()) {
      const header = document.createElement("div");
      header.className = "course-org-header";
      header.dataset.org = org;
      header.textContent = org;
      courseList.appendChild(header);

      for (const course of groupCourses) {
        const item = document.createElement("div");
        item.className = "course-item";
        item.dataset.org = org;
        item.dataset.search = `${course.display_name || ""} ${course.id || ""} ${course.run || ""} ${course.org || ""}`.toLowerCase();

        const input = document.createElement("input");
        input.type = "checkbox";
        input.className = "course-checkbox";
        input.id = `course_${toSafeCourseId(course.id, index)}`;
        input.value = course.id;
        input.addEventListener("change", updateSelectedCoursesCount);

        const label = document.createElement("label");
        label.htmlFor = input.id;

        const title = document.createElement("div");
        const strong = document.createElement("strong");
        strong.textContent = course.display_name || course.id;
        title.appendChild(strong);

        const meta = document.createElement("div");
        meta.className = "course-meta";
        meta.textContent = `${course.id} (${course.run || ""})`;

        label.appendChild(title);
        label.appendChild(meta);
        item.appendChild(input);
        item.appendChild(label);
        courseList.appendChild(item);
        index += 1;
      }
    }
    updateSelectedCoursesCount();
  }

  function filterCourses() {
    const query = document.getElementById("courseSearch").value.trim().toLowerCase();
    const items = Array.from(document.querySelectorAll(".course-item"));
    const headers = Array.from(document.querySelectorAll(".course-org-header"));

    const visibleOrgCounts = new Map();
    for (const item of items) {
      const isVisible = !query || item.dataset.search.includes(query);
      item.style.display = isVisible ? "" : "none";
      if (isVisible) {
        const org = item.dataset.org;
        visibleOrgCounts.set(org, (visibleOrgCounts.get(org) || 0) + 1);
      }
    }

    for (const header of headers) {
      const org = header.dataset.org;
      header.style.display = visibleOrgCounts.get(org) ? "" : "none";
    }
  }

  function handleSelectAllCourses() {
    const courseItems = document.querySelectorAll(".course-item");
    for (const item of courseItems) {
      if (item.style.display === "none") {
        continue;
      }
      const checkbox = item.querySelector(".course-checkbox");
      if (!checkbox) {
        continue;
      }
      checkbox.checked = true;
    }
    updateSelectedCoursesCount();
  }

  function handleClearAllCourses() {
    const checkboxes = document.querySelectorAll(".course-checkbox");
    for (const checkbox of checkboxes) {
      checkbox.checked = false;
    }
    updateSelectedCoursesCount();
  }

  function renderPreviewRows(sample) {
    const body = document.querySelector("#preview-table tbody");
    body.innerHTML = "";

    for (const user of sample || []) {
      const identifier = getUserIdentifier(user);
      const hasIdentifier = Boolean(identifier);
      const hasEmail = Boolean((user.email || "").trim());
      const row = document.createElement("tr");

      const checkboxCell = document.createElement("td");
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.className = "user-select";

      if (hasIdentifier) {
        checkbox.dataset.identifier = identifier;
        checkbox.dataset.email = (user.email || "").trim();
        checkbox.dataset.username = (user.username || "").trim();
        checkbox.addEventListener("change", function () {
          if (checkbox.checked) {
            selectedIdentifiers.add(identifier);
          } else {
            selectedIdentifiers.delete(identifier);
          }
          updateSelectionCount();
        });
      } else {
        checkbox.disabled = true;
        checkbox.title = "Cannot select user with no email or username";
        checkboxCell.classList.add("no-identifier");
        checkboxCell.textContent = "No email";
      }

      if (hasIdentifier) {
        checkboxCell.appendChild(checkbox);
        if (!hasEmail) {
          const badge = document.createElement("span");
          badge.className = "muted small";
          badge.textContent = " (no email)";
          checkboxCell.appendChild(badge);
        }
      }
      row.appendChild(checkboxCell);

      for (const column of PREVIEW_COLUMNS) {
        const value = user[column] || "";
        const cell = document.createElement("td");
        cell.className = "meta";
        cell.textContent = value;
        row.appendChild(cell);
      }

      body.appendChild(row);
    }
  }

  function resetPreviewResults() {
    document.getElementById("preview-count").textContent = "Count: 0";
    document.querySelector("#preview-table tbody").innerHTML = "";
    clearSelectionState();
  }

  function populateFilterChoices(choices) {
    for (const key of FILTER_KEYS) {
      const select = document.getElementById(`filter-${key}`);
      if (!select) {
        continue;
      }
      select.innerHTML = '<option value="">All</option>';
      const values = Array.isArray(choices[key]) ? choices[key] : [];
      for (const value of values) {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = value;
        select.appendChild(option);
      }
    }
  }

  async function getJSON(url) {
    const response = await fetch(url, {
      method: "GET",
      credentials: "same-origin",
    });

    let data;
    try {
      data = await response.json();
    } catch (error) {
      data = { detail: "Server returned non-JSON response." };
    }

    if (!response.ok) {
      const detail = data.detail || JSON.stringify(data);
      throw { status: response.status, detail };
    }

    return data;
  }

  async function postJSON(url, payload) {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      credentials: "same-origin",
      body: JSON.stringify(payload),
    });

    let data;
    try {
      data = await response.json();
    } catch (error) {
      data = { detail: "Server returned non-JSON response." };
    }

    if (!response.ok) {
      const detail = data.detail || JSON.stringify(data);
      throw { status: response.status, detail };
    }

    return data;
  }

  function formatError(error) {
    if (error && error.status === 403) {
      return "403 Forbidden: staff access is required.";
    }
    if (error && error.status === 400) {
      return `400 Bad Request: ${error.detail}`;
    }
    if (error && error.detail) {
      return `Request failed: ${error.detail}`;
    }
    return "Unexpected error while processing request.";
  }

  async function loadMetadataChoices() {
    try {
      const result = await getJSON("/api/userops/v1/metadata/choices");
      populateFilterChoices(result.choices || {});
    } catch (error) {
      setStatus(`Failed to load filter choices. ${formatError(error)}`, "error");
    }
  }

  async function loadCourses() {
    try {
      const result = await getJSON("/api/userops/v1/courses");
      const courses = Array.isArray(result.courses) ? result.courses : [];
      renderCourses(courses);
      filterCourses();
    } catch (error) {
      setStatus(`Failed to load courses. ${formatError(error)}`, "error");
    }
  }

  async function handlePreview() {
    const previewBtn = document.getElementById("preview-btn");

    previewBtn.disabled = true;
    setStatus("Loading preview...", "info");

    try {
      const result = await postJSON("/api/userops/v1/users/preview", {
        filters: collectFilters(),
      });
      document.getElementById("preview-count").textContent = `Count: ${result.count || 0}`;
      clearSelectionState();
      renderPreviewRows(result.sample || []);
      setStatus("Preview loaded successfully.", "success");
    } catch (error) {
      setStatus(formatError(error), "error");
    } finally {
      previewBtn.disabled = false;
    }
  }

  function handleSelectAll() {
    const checkboxes = document.querySelectorAll(".user-select");
    for (const checkbox of checkboxes) {
      if (checkbox.disabled) {
        continue;
      }
      checkbox.checked = true;
      if (checkbox.dataset.identifier) {
        selectedIdentifiers.add(checkbox.dataset.identifier);
      }
    }
    updateSelectionCount();
  }

  function handleUnselectAll() {
    const checkboxes = document.querySelectorAll(".user-select");
    for (const checkbox of checkboxes) {
      checkbox.checked = false;
    }
    clearSelectionState();
  }

  function handleResetFilters() {
    for (const key of FILTER_KEYS) {
      const select = document.getElementById(`filter-${key}`);
      if (select) {
        select.value = "";
      }
    }
    resetPreviewResults();
    clearStatus();
  }

  async function handleExecute() {
    const executeBtn = document.getElementById("execute-btn");
    const selectedCourses = Array.from(document.querySelectorAll(".course-checkbox:checked")).map((cb) => cb.value);
    const cohorts = nonEmptyLines(document.getElementById("bulk-cohorts").value);

    if (!selectedCourses.length) {
      setStatus("Select at least one course", "error");
      return;
    }

    if (cohorts.length && cohorts.length !== selectedCourses.length) {
      setStatus("If cohorts are provided, their count must match courses count.", "error");
      return;
    }

    const payload = {
      filters: collectFilters(),
      courses: selectedCourses,
      cohorts,
      action: document.getElementById("bulk-action").value,
      auto_enroll: document.getElementById("bulk-auto_enroll").checked,
      email_students: document.getElementById("bulk-email_students").checked,
    };

    if (selectedIdentifiers.size > 0) {
      payload.selected_identifiers = Array.from(selectedIdentifiers);
    }

    executeBtn.disabled = true;
    setStatus("Executing bulk operation...", "info");

    try {
      const result = await postJSON("/api/userops/v1/bulk-enroll/by-metadata", payload);

      const summary = [
        `matched_users: ${result.matched_users}`,
        `used_identifiers: ${result.used_identifiers}`,
        `skipped_no_email: ${result.skipped_no_email}`,
        `upstream_status: ${result.upstream_status}`,
      ].join(" | ");

      setStatus(summary, "success");
    } catch (error) {
      setStatus(formatError(error), "error");
    } finally {
      executeBtn.disabled = false;
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    loadMetadataChoices();
    loadCourses();
    updateSelectionCount();
    document.getElementById("preview-btn").addEventListener("click", handlePreview);
    document.getElementById("execute-btn").addEventListener("click", handleExecute);
    document.getElementById("resetFiltersBtn").addEventListener("click", handleResetFilters);
    document.getElementById("selectAllBtn").addEventListener("click", handleSelectAll);
    document.getElementById("unselectAllBtn").addEventListener("click", handleUnselectAll);
    document.getElementById("courseSearch").addEventListener("input", filterCourses);
    document.getElementById("selectAllCoursesBtn").addEventListener("click", handleSelectAllCourses);
    document.getElementById("clearAllCoursesBtn").addEventListener("click", handleClearAllCourses);
  });
})();
