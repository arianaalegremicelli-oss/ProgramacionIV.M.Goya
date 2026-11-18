// TaskFlow Frontend - JavaScript Asincrónico
// Alumna: Ariana Alegre Micelli

const API_URL = "http://127.0.0.1:8000/api";
let accessToken = sessionStorage.getItem("taskflow_access_token") || null;
let nextPageUrl = null;
let prevPageUrl = null;
let currentPageNumber = 1;
let currentSocket = null;

function authHeaders() {
  return { Authorization: `Bearer ${accessToken}` };
}

// Inicialización automática si existe sesión guardada
window.addEventListener("DOMContentLoaded", () => {
  if (accessToken) {
    showApp();
  }
});

async function login() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const errorBox = document.getElementById("login-error");
  errorBox.textContent = "";

  try {
    const response = await fetch(`${API_URL}/token/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      errorBox.textContent =
        response.status === 429
          ? "Demasiados intentos. Esperen un minuto (Rate limit)."
          : "Usuario o contraseña incorrectos.";
      return;
    }

    const data = await response.json();
    accessToken = data.access;
    sessionStorage.setItem("taskflow_access_token", accessToken);
    showApp();
  } catch (err) {
    errorBox.textContent = "Error de conexión con el backend o bloqueo de CORS.";
  }
}

function logout() {
  accessToken = null;
  sessionStorage.removeItem("taskflow_access_token");
  if (currentSocket) {
    currentSocket.close();
    currentSocket = null;
  }
  document.getElementById("app-box").style.display = "none";
  document.getElementById("login-box").style.display = "block";
  document.getElementById("password").value = "";
}

function showApp() {
  document.getElementById("login-box").style.display = "none";
  document.getElementById("app-box").style.display = "block";
  loadProjects();
  loadTasks();
}

async function loadProjects() {
  try {
    const response = await fetch(`${API_URL}/projects/`, { headers: authHeaders() });
    if (response.status === 401) {
      logout();
      return;
    }
    const data = await response.json();
    const select = document.getElementById("project");
    select.innerHTML = "";
    const projectsList = data.results || data;
    projectsList.forEach((project) => {
      const option = document.createElement("option");
      option.value = project.id;
      option.textContent = project.name;
      select.appendChild(option);
    });

    // Conectar WebSocket al primer proyecto para tiempo real
    if (projectsList.length > 0) {
      connectWebSocket(projectsList[0].id);
    }
  } catch (err) {
    console.error("Error al cargar proyectos:", err);
  }
}

async function loadTasks(url = `${API_URL}/tasks/`) {
  try {
    const response = await fetch(url, { headers: authHeaders() });
    if (response.status === 401) {
      logout();
      return;
    }
    const data = await response.json();
    const list = document.getElementById("tasks");
    list.innerHTML = "";

    const tasks = data.results || data;
    nextPageUrl = data.next || null;
    prevPageUrl = data.previous || null;

    document.getElementById("next-btn").disabled = !nextPageUrl;
    document.getElementById("prev-btn").disabled = !prevPageUrl;
    document.getElementById("page-info").textContent = `Página ${currentPageNumber}`;

    tasks.forEach((task) => {
      const li = document.createElement("li");

      const titleSpan = document.createElement("span");
      titleSpan.textContent = task.title;

      const statusSpan = document.createElement("span");
      statusSpan.className = "status-pill";
      statusSpan.textContent = task.status;

      li.appendChild(titleSpan);
      li.appendChild(statusSpan);
      list.appendChild(li);
    });
  } catch (err) {
    console.error("Error al cargar tareas:", err);
  }
}

function loadNextPage() {
  if (nextPageUrl) {
    currentPageNumber++;
    loadTasks(nextPageUrl);
  }
}

function loadPreviousPage() {
  if (prevPageUrl && currentPageNumber > 1) {
    currentPageNumber--;
    loadTasks(prevPageUrl);
  }
}

async function createTask() {
  const title = document.getElementById("new-title").value.trim();
  const project = document.getElementById("project").value;
  const errorBox = document.getElementById("app-error");
  errorBox.textContent = "";

  if (!title || !project) return;

  try {
    const response = await fetch(`${API_URL}/tasks/`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({ title, project: Number(project) }),
    });

    if (!response.ok) {
      const data = await response.json();
      errorBox.textContent = JSON.stringify(data.detail || data);
      return;
    }

    document.getElementById("new-title").value = "";
    loadTasks();
  } catch (err) {
    errorBox.textContent = "Error al intentar crear la tarea.";
  }
}

function connectWebSocket(projectId) {
  if (currentSocket) {
    currentSocket.close();
  }
  const wsUrl = `ws://127.0.0.1:8000/ws/projects/${projectId}/?token=${accessToken}`;
  try {
    currentSocket = new WebSocket(wsUrl);
    currentSocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.event === "task_created" || data.event === "task_updated") {
        loadTasks();
      }
    };
  } catch (e) {
    console.warn("No se pudo abrir WebSocket:", e);
  }
}
