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

  function setStatus(message, level) {
    const statusBox = document.getElementById("status-box");
    statusBox.textContent = message;
    statusBox.className = `status ${level || "info"}`;
  }

  function renderPreviewRows(sample) {
    const body = document.querySelector("#preview-table tbody");
    body.innerHTML = "";

    for (const user of sample || []) {
      const row = document.createElement("tr");
      row.innerHTML = PREVIEW_COLUMNS.map((column) => `<td class="meta">${user[column] || ""}</td>`).join("");
      body.appendChild(row);
    }
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

  async function handlePreview() {
    const previewBtn = document.getElementById("preview-btn");

    previewBtn.disabled = true;
    setStatus("Loading preview...", "info");

    try {
      const result = await postJSON("/api/userops/v1/users/preview", {
        filters: collectFilters(),
      });
      document.getElementById("preview-count").textContent = `Count: ${result.count || 0}`;
      renderPreviewRows(result.sample || []);
      setStatus("Preview loaded successfully.", "success");
    } catch (error) {
      setStatus(formatError(error), "error");
    } finally {
      previewBtn.disabled = false;
    }
  }

  async function handleExecute() {
    const executeBtn = document.getElementById("execute-btn");
    const courses = nonEmptyLines(document.getElementById("bulk-courses").value);
    const cohorts = nonEmptyLines(document.getElementById("bulk-cohorts").value);

    if (!courses.length) {
      setStatus("Please provide at least one course key.", "error");
      return;
    }

    if (cohorts.length && cohorts.length !== courses.length) {
      setStatus("If cohorts are provided, their count must match courses count.", "error");
      return;
    }

    executeBtn.disabled = true;
    setStatus("Executing bulk operation...", "info");

    try {
      const result = await postJSON("/api/userops/v1/bulk-enroll/by-metadata", {
        filters: collectFilters(),
        courses,
        cohorts,
        action: document.getElementById("bulk-action").value,
        auto_enroll: document.getElementById("bulk-auto_enroll").checked,
        email_students: document.getElementById("bulk-email_students").checked,
      });

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
    document.getElementById("preview-btn").addEventListener("click", handlePreview);
    document.getElementById("execute-btn").addEventListener("click", handleExecute);
  });
})();
